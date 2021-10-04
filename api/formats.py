import itertools
from collections import Counter

from scrapper.models import *
from django.db.models import Q


# Work in progress
class productClass:

	def __init__(self, product_asin):
		self.product_asin = product_asin

	def productAttributes(self, item_db, data_dict):

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

		try:
			category = item_db.category
		except Exception:
			category = ''

		data_dict['category'] = category
		data_dict['weight_class'] = 'light'

		# Brand
		brand = ''
		brand_db = item_db.productdetails_set.filter(Q(language='EN', attributes="Brand") | Q(language='EN', attributes__in=('Seller, or Collection Name','Brand Name','Manufacturer')))
		if brand_db:
			brand = brand_db[0].values

		data_dict['brand'] = brand
		data_dict['title'] = item_db.title_en
		data_dict['title_ar'] = item_db.title_ar
		data_dict['description'] = ' '.join([long_desc.long_description for long_desc in item_db.productdescription_set.filter(language='EN')]) or '. '.join([highlight.highlight for highlight in item_db.producthighlights_set.filter(language='EN')]) or data_dict['title']
		data_dict['description_ar'] = ' '.join([long_desc.long_description for long_desc in item_db.productdescription_set.filter(language='AR')]) or '. '.join([highlight.highlight for highlight in item_db.producthighlights_set.filter(language='AR')]) or data_dict['title_ar']
		# data_dict['highlights'] = [highlight.highlight for highlight in item_db.producthighlights_set.filter(language='EN')]
		# data_dict['highlights_ar'] = [highlight.highlight for highlight in item_db.producthighlights_set.filter(language='AR')]

		data_dict['gtin'] = ''
		data_dict['ean'] = ''
		data_dict['upc'] = ''

		data_dict['asin'] = item_db.productID

		data_dict['default_images'] = [images.image for images in item_db.productimages_set.all()]

		# Specifications
		category_lst = []

		specs_en = item_db.productdetails_set.filter(language='EN').exclude(attributes__in=('Brand','Asin','ASIN'))
		specs_ar = item_db.productdetails_set.filter(language='AR').exclude(attributes__in=('Brand','Asin','العلامة التجارية','ASIN'))


		category_lst = specifications(specs_en, category_lst)
		category_lst = specifications(specs_ar, category_lst)
			
		data_dict['category_attributes'] = category_lst

		return data_dict

	
	def variations(self, item_db, data_dict):

		grades_provided='DBW,DB,BNW,BN,OBB,OBBW,OB,OBW,PO,POA,POB,CRA,CRB'

		product_asin = self.product_asin

		# Lambda Function
		lambda_variant_func = lambda x,y: x if x else y

		# Variation_Settings
		single_variant_db = lambda_variant_func(variationSettings.objects.filter(current_asin=item_db.productID),variationSettings.objects.filter(parent_asin=item_db.productID))

		if single_variant_db:
			variations_settings = totalVariations.objects.filter(parent_asin=single_variant_db[0].parent_asin).order_by('-id')

			data_dict['asin'] = variations_settings[0].parent_asin

			variations_settings_list = []

			# Grades Variations
			variations_settings_list.append({'name':'Conditions', 'values':grades_provided.split(','),'name_ar':'الظروف', 'values_ar':grades_provided.split(',')})

			for variations in variations_settings:

				variations_settings_dict = {}

				variations_settings_dict['name'] = variations.name_en.replace('_',' ').title()
				variations_settings_dict['values'] = [i.replace("/","-") for i in variations.value_en.split(':||:')]

				if variations.productID.source == 'amazon.ae' or variations.productID.source == 'amazon.ae':
					variations_settings_dict['name_ar'] = variations.name_ar.replace('_',' ').title()
					variations_settings_dict['values_ar'] = variations.value_ar.split(':||:')

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

					lamda_total_variations = lambda x,y : x if x else y

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
						variations_dict['variation_index'] = f'{index_dimension}'
						variations_dict['variation'] = f"{index_value}"
						variations_dict['asin'] = total_variations.current_asin
						variations_dict['title'] = f"{total_variations.title_en}"
						variations_dict['title_ar'] = f"{total_variations.title_ar}"
						variations_dict['gtin'] = ''
						variations_dict['ean'] = ''
						variations_dict['upc'] = ''
						variations_dict['images'] = total_variations.images.split(',')
					else:

						# Variation Not Found
						variations_dict['variation_index'] = f'{index_dimension}'
						variations_dict['variation'] = f"{index_value}"
						variations_dict['asin'] = '' 
						variations_dict['title'] = '' 
						variations_dict['title_ar'] = ''
						variations_dict['gtin'] = ''
						variations_dict['ean'] = ''
						variations_dict['upc'] = ''
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

				variations_dict['variation_index'] = f'{indexes}'
				variations_dict['variation'] = f"{grading}"
				variations_dict['asin'] = data_dict['asin']
				variations_dict['title'] = data_dict['title']
				variations_dict['title_ar'] = data_dict['title_ar']
				variations_dict['gtin'] = ''
				variations_dict['ean'] = ''
				variations_dict['upc'] = ''
				variations_dict['images'] = data_dict['default_images']

				variations_list.append(variations_dict)

			data_dict['variations'] = variations_list

		return data_dict

	def mainProductData(self):

		data_dict = {}

		product_asin = self.product_asin
		item_db = productPagesScrapper.objects.filter(Q(productID=product_asin, description_en=True, description_ar=True) | Q(productID=product_asin, description_en=True, source__in=('amazon.in','amazon.co.uk','amazon.com','amazon.com.au')))

		if item_db:
			data_dict = self.productAttributes(item_db[0], data_dict)
			data_dict = self.variations(item_db[0], data_dict)

		else:
			vari = variationSettings.objects.filter(Q(current_asin=product_asin, description_en=True, description_ar=True) | Q(parent_asin=product_asin, description_en=True, description_ar=True) | Q(current_asin=product_asin, description_en=True, productID__source__in=('amazon.in','amazon.com','amazon.com.au','amazon.co.uk')))

			if vari:
			
				data_dict = self.productAttributes(vari[0].productID, data_dict)
				data_dict = self.variations(vari[0].productID, data_dict)

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


