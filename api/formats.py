import itertools

from scrapper.models import *
from django.db.models import Q


# Work in progress
class productClass:

	def __init__(self, product_asin):
		self.product_asin = product_asin

	def productAttributes(self, item_db, data_dict, category, weight_class):

		def specifications(specs, category_lst):

			for spec in specs:
				spec_dict = {}

				try:
					spec_dict['key'] = spec.attributes
					spec_dict['value'] = [spec.values]

					category_lst.append(spec_dict)
				except Exception:
					break

			return category_lst

		def description_solver(item_db, language):
			description = ' '.join([long_desc.long_description for long_desc in item_db.productdescription_set.filter(language=language)])
			description = description if description else '0'
			if not description.isdigit():
				return description
			else:
				description = '. '.join([highlight.highlight for highlight in item_db.producthighlights_set.filter(language=language)])
				description = description if description else None if description.isdigit() else description
				return description

		# Amazon category
		'''
		try:
			category = item_db.category
		except Exception:
			category = ''
		'''

		data_dict['category'] = category
		data_dict['weight_class'] = weight_class

		# Brand
		brand = ''
		brand_db = item_db.productdetails_set.filter(Q(language='EN', attributes="Brand") | Q(language='EN', attributes__in=('Brand, Seller, or Collection Name','Manufacturer','Brand Name')))
		if brand_db:
			brand = brand_db[0].values

		data_dict['brand'] = brand or 'Others'
		data_dict['title'] = item_db.title_en
		data_dict['title_ar'] = item_db.title_ar
		data_dict['market_price'] = int(item_db.old_price or 0)
		data_dict['description'] = description_solver(item_db, 'EN') or data_dict['title']
		data_dict['description_ar'] = description_solver(item_db, 'AR') or data_dict['title_ar']
		# data_dict['highlights'] = [highlight.highlight for highlight in item_db.producthighlights_set.filter(language='EN')]
		# data_dict['highlights_ar'] = [highlight.highlight for highlight in item_db.producthighlights_set.filter(language='AR')]

		data_dict['gtin'] = ''
		data_dict['ean'] = ''
		data_dict['upc'] = ''

		data_dict['asin'] = ''
		data_dict['is_original'] = True

		data_dict['default_images'] = [images.image for images in item_db.productimages_set.all()]

		# Specifications
		category_lst = []

		specs_en = item_db.productdetails_set.filter(language='EN').exclude(attributes__in=('Brand','Asin','ASIN'))
		specs_ar = item_db.productdetails_set.filter(language='AR').exclude(attributes__in=('Brand','Asin','العلامة التجارية','ASIN'))


		category_lst = specifications(specs_en, category_lst)
		category_lst = specifications(specs_ar, category_lst)
			
		data_dict['category_attributes'] = category_lst

		return data_dict

	
	def variations(self, item_db, data_dict, grades_provided, provided_asin):

		product_asin = self.product_asin

		# Lambda Function
		lambda_variant_func = lambda x,y: x if x else y

		# Variation_Settings
		single_variant_db = lambda_variant_func(variationSettings.objects.filter(current_asin=item_db.productID),variationSettings.objects.filter(parent_asin=item_db.productID))

		if single_variant_db:
			variations_settings = totalVariations.objects.filter(parent_asin=single_variant_db[0].parent_asin).order_by('-id') or totalVariations.objects.filter(productID=single_variant_db[0].productID).order_by('-id')

			data_dict['asin'] = variations_settings[0].parent_asin
			data_dict['is_original'] = True if variations_settings[0].parent_asin == provided_asin else False

			variations_settings_list = []

			# Grades Variations
			variations_settings_list.append({'name':'Conditions', 'values':grades_provided.split(','),'name_ar':'الظروف', 'values_ar':grades_provided.split(',')})

			for variations in variations_settings:

				variations_settings_dict = {}

				variations_settings_dict['name'] = variations.name_en.replace('_',' ').title()
				variations_settings_dict['values'] = [i.replace("/","-") for i in variations.value_en.split(':||:')]

				if variations.productID.source == 'amazon.ae' or variations.productID.source == 'amazon.sa':
					variations_settings_dict['name_ar'] = variations.name_ar.replace('_',' ').title()
					variations_settings_dict['values_ar'] = [i.replace("/","-") for i in variations.value_ar.split(':||:')]

				variations_settings_list.append(variations_settings_dict)

			data_dict['variation_settings'] = variations_settings_list

			# Variations
			variations_list = []

			# Variation Possible Values
			variations_possibilities_list = []
			for variations in data_dict['variation_settings']:
				variations_possibilities_dict = dict(zip(itertools.count(), variations['values']))
				variations_possibilities_list.append(variations_possibilities_dict)

			# variations_possibilities_list = variations_possibilities_list[::-1]
			indexes_list = [[x for x in i.keys()] for i in variations_possibilities_list]
			values_list = [[x for x in i.values()] for i in variations_possibilities_list]

			result_keys = [i for i in itertools.product(*indexes_list)]
			result_values = [i for i in itertools.product(*values_list)]

			for countings,(k,v) in enumerate(zip(result_keys,result_values)):

				if countings < 9999:

					index_dimension = '_'.join(map(str,k))
					index_value = '/'.join(v)

					# Initializing variation dictionary
					variations_dict = {}

					# Match variation despute of order
					new_v = [i.replace("-","/") for i in v]
					dimension_list = new_v[1:]
					total_variations = ''

					for match_variation in variationSettings.objects.filter(productID=single_variant_db[0].productID, available=True):
						if set(dimension_list) == set([i.replace("-","/") for i in match_variation.dimension_val_en.split(':||:')]):
							total_variations = match_variation
							break

					if total_variations:

						# Variation Found
						variations_dict['variation_index'] = index_dimension
						variations_dict['variation'] = index_value
						variations_dict['asin'] = total_variations.current_asin
						variations_dict['title'] = total_variations.title_en
						variations_dict['title_ar'] = total_variations.title_ar
						variations_dict['market_price'] = int(total_variations.old_price or 0)
						variations_dict['description'] = data_dict['description']
						variations_dict['description_ar'] = data_dict['description_ar']
						variations_dict['gtin'] = ''
						variations_dict['ean'] = ''
						variations_dict['upc'] = ''
						variations_dict['is_original'] = True if total_variations.current_asin == provided_asin else False
						variations_dict['images'] = total_variations.images.split(',')
					else:

						# Variation Not Found
						variations_dict['variation_index'] = index_dimension
						variations_dict['variation'] = index_value
						variations_dict['asin'] = '' # data_dict['asin']
						variations_dict['title'] = '' # item_db.title_en
						variations_dict['title_ar'] = ''# item_db.title_ar
						variations_dict['market_price'] = 0
						variations_dict['description'] = ''
						variations_dict['description_ar'] = ''
						variations_dict['gtin'] = ''
						variations_dict['ean'] = ''
						variations_dict['upc'] = ''
						variations_dict['is_original'] = False
						variations_dict['images'] =[] # [images.image for images in item_db.productimages_set.all()]

					variations_list.append(variations_dict)

			data_dict['variations'] = variations_list


		# If variations is not given
		else:
			data_dict['asin'] = product_asin
			data_dict['variation_settings'] = [{'name':'Conditions', 'values':grades_provided.split(','),'name_ar':'الظروف', 'values_ar':grades_provided.split(',')}]

			# Possible variations
			variations_list = []


			for indexes, grading in enumerate(grades_provided.split(',')):
				variations_dict = {}

				variations_dict['variation_index'] = indexes
				variations_dict['variation'] = grading
				variations_dict['asin'] = data_dict['asin']
				variations_dict['title'] = data_dict['title']
				variations_dict['title_ar'] = data_dict['title_ar']
				variations_dict['market_price'] = data_dict['market_price']
				variations_dict['description'] = data_dict['description']
				variations_dict['description_ar'] = data_dict['description_ar']
				variations_dict['gtin'] = ''
				variations_dict['ean'] = ''
				variations_dict['upc'] = ''
				variations_dict['is_original'] = True
				variations_dict['images'] = data_dict['default_images']

				variations_list.append(variations_dict)

			data_dict['variations'] = variations_list

		return data_dict

	def mainProductData(self, weight_class="light", conditions="DBW,DB,BNW,BN,OBB,OBBW,OB,OBW,PO,POA,POB,CRA,CRB", category=61003, filename=None):

		data_dict = {}

		product_asin = self.product_asin
		item_db = productPagesScrapper.objects.filter(Q(productID=product_asin, description_en=True, description_ar=True, batchname=filename) | Q(productID=product_asin, description_en=True, source__in=('amazon.in','amazon.co.uk','amazon.com','amazon.com.au'), batchname=filename))

		if item_db:
			data_dict = self.productAttributes(item_db[0], data_dict, category, weight_class)
			data_dict = self.variations(item_db[0], data_dict, conditions, product_asin)

		else:
			vari = variationSettings.objects.filter(Q(current_asin=product_asin, description_en=True, description_ar=True) | Q(parent_asin=product_asin, description_en=True, description_ar=True) | Q(current_asin=product_asin, description_en=True, productID__source__in=('amazon.in','amazon.com','amazon.com.au','amazon.co.uk')))

			if vari:

				if vari[0].productID.batchname==filename:
			
					data_dict = self.productAttributes(vari[0].productID, data_dict, category, weight_class)
					data_dict = self.variations(vari[0].productID, data_dict, conditions, product_asin)

				elif not vari[0].productID.batchname:
					productPagesScrapper.objects.filter(productID=vari[0].productID.productID).update(batchname=filename)

					data_dict = self.productAttributes(vari[0].productID, data_dict, category, weight_class)
					data_dict = self.variations(vari[0].productID, data_dict, conditions, product_asin)

		return data_dict

	def childProduct(self, variation_item):
		items = {}
		items['category'] = variation_item.productID.category
		items['weight_class'] = ''

		# Brand
		brand = ''
		brand_db = productDetails.objects.filter(productID= variation_item.productID, language='EN', attributes__in=('Brand','Brand, Seller, or Collection Name','Manufacturer'))
		if brand_db:
			brand = brand_db[0].values

		items['brand'] = brand
		items['title_en'] = variation_item.title_en
		items['title_ar'] = variation_item.title_ar
		items['description'] = ''.join([i.long_description for i in productDescription.objects.filter(productID=variation_item.productID, language='EN') if i])
		items['description_ar'] = ''.join([i.long_description for i in productDescription.objects.filter(productID=variation_item.productID, language='AR') if i])
		items['gtin'] = ''
		items['ean'] = ''
		items['upc'] = ''
		items['asin'] = variation_item.current_asin
		items['default_images'] = variation_item.images.split(',')
		items['category_attributes'] = []

		specs = productDetails.objects.filter(productID=variation_item.productID).exclude(attributes__in=('Brand','Asin','العلامة التجارية','ASIN'))
		if specs:
			for spec in specs:
				spec_dict = {}
				spec_dict['key'] = spec.attributes
				spec_dict['values'] = [spec.values]

				items['category_attributes'].append(spec_dict)

		return items





class categoryClass:

	def __init__(self, category):
		self.category = category

	def categoryAttributes(self):

		category = self.category

		category_dic = {}

		category_qs = productPagesScrapper.objects.filter(productID__startswith='B',category__icontains=category,description_en=True,description_ar=True)

		# Category
		category_dic['category'] = category_qs[0].category
		# category_dic['category'] = cid

		# Attributes
		attributes_lst = []

		if category_qs:

			product_details_en = productDetails.objects.filter(productID__in=tuple([cate for cate in category_qs]), language='EN').exclude(attributes__in=('Brand','Asin','ASIN')).values('attributes').distinct()
			product_details_ar = productDetails.objects.filter(productID__in=tuple([cate for cate in category_qs]), language='AR').exclude(attributes__in=('Brand','Asin','العلامة التجارية','ASIN')).values('attributes').distinct()
			
			for prod_en in product_details_en:
				prod_dic = {}
				prod_dic['type'] = ''
				prod_dic['language'] = 'EN'
				prod_dic['name'] = prod_en['attributes']

				possible_val_en = productDetails.objects.filter(productID__in=tuple([cate for cate in category_qs]),attributes=prod_en['attributes'], language='EN').values('values').distinct()
				if len(possible_val_en) > 1:
					prod_dic['type'] = 'select'
					# prod_dic['default_values'] = [{'name_en':possible_val_en[0]['values']}]
					prod_dic['possible_values'] = [{'name':v['values']} for v in possible_val_en]

				else:
					prod_dic['type'] = 'text'
					# prod_dic['default_values'] = ''
					prod_dic['possible_values'] = [{'name':v['values']} for v in possible_val_en]

				attributes_lst.append(prod_dic)

			for prod_ar in product_details_ar:
				prod_dic = {}
				prod_dic['type'] = ''
				prod_dic['language'] = 'AR'
				prod_dic['name'] = prod_ar['attributes']

				possible_val_ar = productDetails.objects.filter(productID__in=tuple([cate for cate in category_qs]),attributes=prod_ar['attributes'], language='AR').values('values').distinct()
				if len(possible_val_ar) > 1:
					prod_dic['type'] = 'select'
					# prod_dic['default_values'] = [{'name_ar':possible_val_ar[0]['values']}]
					prod_dic['possible_values'] = [{'name':av['values']} for av in possible_val_ar]

				else:
					prod_dic['type'] = 'text'
					# prod_dic['default_values'] = ''
					prod_dic['possible_values'] = [{'name':av['values']} for av in possible_val_ar]

				attributes_lst.append(prod_dic)

		category_dic['attributes'] = attributes_lst

		return category_dic

def excelFormating(weight_class, conditions, category, asin):
	def specifications(specs):
		k = []
		v = []
		for spec in specs:
			try:
				k.append(spec.attributes)
				v.append(spec.values)
			except Exception:
				break

		return k,v
	data = []

	data.append([asin])
	data.append([category])
	data.append([weight_class])

	item_db = productPagesScrapper.objects.filter(Q(productID=asin, description_en=True, description_ar=True) | Q(productID=asin, description_en=True, source__in=('amazon.in','amazon.co.uk','amazon.com','amazon.com.au')))

	if item_db:
		item_db=item_db[0]

		# Brand
		brand_db = item_db.productdetails_set.filter(Q(language='EN', attributes="Brand") | Q(language='EN', attributes__in=('Brand, Seller, or Collection Name','Manufacturer','Brand Name')))
		brand = brand_db[0].values if brand_db else ''

		data.append([brand])
		data.append([item_db.title_en])
		data.append([item_db.title_ar])
		data.append([int(item_db.old_price or 0)])
		data.append([' '.join([long_desc.long_description for long_desc in item_db.productdescription_set.filter(language='EN')]) or '. '.join([highlight.highlight for highlight in item_db.producthighlights_set.filter(language='EN')]) or data[4][0]])
		data.append([' '.join([long_desc.long_description for long_desc in item_db.productdescription_set.filter(language='AR')]) or '. '.join([highlight.highlight for highlight in item_db.producthighlights_set.filter(language='AR')]) or data[5][0]])

		data.append([''])
		data.append([''])
		data.append([''])

		data.append([images.image for images in item_db.productimages_set.all()])

		specs_en = item_db.productdetails_set.filter(language='EN').exclude(attributes__in=('Brand','Asin','ASIN'))
		specs_ar = item_db.productdetails_set.filter(language='AR').exclude(attributes__in=('Brand','Asin','العلامة التجارية','ASIN'))

		
		k,v = specifications(specs_en)
		data.append(k)
		data.append(v)
		k,v = specifications(specs_ar)
		data.append(k)
		data.append(v)


		# Lambda Function
		lambda_variant_func = lambda x,y: x if x else y

		# Variation_Settings
		single_variant_db = lambda_variant_func(variationSettings.objects.filter(current_asin=item_db.productID),variationSettings.objects.filter(parent_asin=item_db.productID))

		if single_variant_db:
			variations_settings = totalVariations.objects.filter(parent_asin=single_variant_db[0].parent_asin).order_by('-id') or totalVariations.objects.filter(productID=single_variant_db[0].productID).order_by('-id')

			data.insert(12,[variations_settings[0].parent_asin])

			variations_settings_values = conditions.split(',')
			variations_settings_names = ['Conditions' for _ in range(len(variations_settings_values))]

			variations_settings_values_ar = conditions.split(',')
			variations_settings_names_ar = ['الظروف' for _ in range(len(variations_settings_values))]
						
			# Grades Variations
			variations_settings_list = []
			variations_settings_list.append({'name':'Conditions', 'values':conditions.split(','),'name_ar':'الظروف', 'values_ar':conditions.split(',')})
			data_dict = {}

			for variations in variations_settings:

				variations_settings_dict = {}

				variations_settings_dict['name'] = variations.name_en.replace('_',' ').title()
				variations_settings_dict['values'] = [i.replace("/","-") for i in variations.value_en.split(':||:')]
				variations_settings_list.append(variations_settings_dict)

				variations_settings_names.extend(variations.name_en.replace('_',' ').title() for _ in range(len(variations.value_en.split(':||:'))))
				variations_settings_values.extend(i.replace("/","-") for i in variations.value_en.split(':||:'))

				if variations.productID.source == 'amazon.ae' or variations.productID.source == 'amazon.sa':
					variations_settings_names_ar.extend(variations.name_ar.replace('_',' ').title() for _ in range(len(variations.value_ar.split(':||:'))))
					variations_settings_values_ar.extend(i.replace("/","-") for i in variations.value_ar.split(':||:'))
			
			data_dict['variation_settings'] = variations_settings_list
			data.append(variations_settings_names)
			data.append(variations_settings_values)
			data.append(variations_settings_names_ar)
			data.append(variations_settings_values_ar)

			# Variations
			index_list = []
			variation_list = []
			asin_list = []
			title_list = []
			title_ar_list = []
			price_list = []
			images_list = []

			# Variation Possible Values
			variations_possibilities_list = []
			for variations in data_dict['variation_settings']:
				variations_possibilities_dict = dict(zip(itertools.count(), variations['values']))
				variations_possibilities_list.append(variations_possibilities_dict)

			# variations_possibilities_list = variations_possibilities_list[::-1]
			indexes_list = [[x for x in i.keys()] for i in variations_possibilities_list]
			values_list = [[x for x in i.values()] for i in variations_possibilities_list]

			result_keys = [i for i in itertools.product(*indexes_list)]
			result_values = [i for i in itertools.product(*values_list)]

			for countings,(k,v) in enumerate(zip(result_keys,result_values)):

				if countings < 9999:

					index_dimension = '_'.join(map(str,k))
					index_value = '/'.join(v)

					# Match variation despute of order
					new_v = [i.replace("-","/") for i in v]
					dimension_list = new_v[1:]
					total_variations = ''

					for match_variation in variationSettings.objects.filter(productID=single_variant_db[0].productID, available=True):
						if set(dimension_list) == set([i.replace("-","/") for i in match_variation.dimension_val_en.split(':||:')]):
							total_variations = match_variation
							break

					if total_variations:

						# Variation Found
						index_list.append(index_dimension)
						variation_list.append(index_value)
						asin_list.append(total_variations.current_asin)
						title_list.append(total_variations.title_en)
						title_ar_list.append(total_variations.title_ar)
						price_list.append(int(total_variations.old_price or 0))
						images_list.append(','.join(total_variations.images.split(',')))
					else:

						# Variation Not Found
						index_list.append(index_dimension)
						variation_list.append(index_value)
						asin_list.append('')
						title_list.append('')
						title_ar_list.append('')
						price_list.append(0)
						images_list.append('')

			data.append(index_list)
			data.append(variation_list)
			data.append(asin_list)
			data.append(title_list)
			data.append(title_ar_list)
			data.append(price_list)
			data.append(images_list)

		elif not single_variant_db:
			data.insert(12,[])


			
		return data		