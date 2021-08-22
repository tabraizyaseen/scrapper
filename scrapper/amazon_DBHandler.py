from .models import *
from . import amazon_scrapper
from . import amazon_ksa
from .variations import *

class amazon_DBHandler_cls():

	def __init__(self, asin):
		self.asin = asin

	def get_valid(self):
		asin = self.asin

		item_db = productPagesScrapper.objects.get(productID=asin)
		if not item_db.description_en:
			amazon_scrapper.ResponseValidate(item_db)

		if not item_db.description_ar:
			amazon_scrapper.ResponseValidateArabic(item_db)

	def get_valid_ksa(self):
		asin = self.asin

		item_db = productPagesScrapper.objects.get(productID=asin)
		if not item_db.description_en:
			amazon_ksa.ResponseValidate(item_db)

		if not item_db.description_ar:
			amazon_ksa.ResponseValidateArabic(item_db)

	def get_product_data(self, item):

		def get_product_detail(item, language, product_details_class):

			if not productDetails.objects.filter(productID=item, language=language):
				specifications = product_details_class.Specifications()

				data = [
					productDetails(productID=item, language=language, attributes=attr, values=val)
					for attr, val in specifications
				]

				productDetails.objects.bulk_create(data)

			if not productDescription.objects.filter(productID=item, language=language):
				long_description = product_details_class.ProductDescription()

				productDescription.objects.create(productID=item, language=language, long_description=long_description)

			if not productHighlights.objects.filter(productID=item, language=language):
				highlights = product_details_class.Highlights()

				highlights_data = [
					productHighlights(productID=item, language=language, highlight=highlight)
					for highlight in highlights
				]

				productHighlights.objects.bulk_create(highlights_data)

		
		if item.description_en and item.description_ar:

			product_details_class = amazon_scrapper.AmazonProductDetails(item)

			if productImages.objects.filter(productID=item).exists():

				images = product_details_class.ImagesList()

				images_db = productImages.objects.filter(productID=item)

				for image, image_db in zip(images,images_db):
					image_db.image = image

				productImages.objects.bulk_update(images_db, ['image'])

			if not productImages.objects.filter(productID=item).exists():

				images = product_details_class.ImagesList()

				images_data = [
					productImages(productID=item, image=image)
					for image in images
				]

				productImages.objects.bulk_create(images_data)

			if not item.price:
				price = product_details_class.price()
				item.price = price
				item.save()

			if not item.old_price:
				old_price = product_details_class.old_price()
				item.old_price = old_price
				item.save()

			languages = ['EN','AR']

			for language in languages:

				if language == 'EN':
					product_details_class = amazon_scrapper.AmazonProductDetails(item)

				else:
					product_details_class = amazon_scrapper.AmazonProductDetailsArabic(item)

				get_product_detail(item, language, product_details_class)
		else:
			pass


	# Saving product variations
	def saveVariations(self):

		def func_variationSettings(variation,parent_asin,variationSettings_instance,item):

			dimensions = variation.Dimensions()
			dimensionsDetails = variation.DimensionsDetails()
			dimensionsDetailsAR = variation.DimensionsDetailsAR()
			
			if variationSettings_instance:
				for countings, (k,v) in enumerate(dimensions.items()):

					create_dict = {'parent_asin':parent_asin,'dimension':k, 'dimension_val_en':','.join(dimensionsDetails[v]), 'dimension_val_ar':','.join(dimensionsDetailsAR[v])}
					variationSettings.objects.get_or_create(productID=variationSettings_instance[0].productID, current_asin=v, defaults=create_dict)
					

					# if parent asin is the same
					'''
					create_dict = {'dimension':k, 'dimension_val_en':','.join(dimensionsDetails[v]), 'dimension_val_ar':','.join(dimensionsDetailsAR[v])}
					variationSettings.objects.get_or_create(productID=variationSettings_instance[0].productID, parent_asin=parent_asin, current_asin=v, defaults=create_dict)
					'''
			else:
				for k,v in dimensions.items():
					variationSettings.objects.create(productID=item, parent_asin=parent_asin, current_asin=v, dimension=k, dimension_val_en=','.join(dimensionsDetails[v]), dimension_val_ar=','.join(dimensionsDetailsAR[v]))


		def func_totalVariations(variation,parent_asin,item):

			total_variations = variation.TotalVariation()
			total_variationsAR = variation.TotalVariationAR()

			# multiple parent Asin Solution
			lambda_presence_check = lambda x,y: x if x else y

			for (k1,v1),(k2,v2) in zip(total_variations.items(),total_variationsAR.items()):
				
				instance_check = lambda_presence_check(totalVariations.objects.filter(productID=item, name_en=k1, name_ar=k2), totalVariations.objects.filter(parent_asin=parent_asin, name_en=k1, name_ar=k2))

				if instance_check:
					instance_check = instance_check[0]
					value_en = instance_check.value_en.split(',') + list(set(v1).difference(instance_check.value_en.split(',')))
					value_ar = instance_check.value_ar.split(',') + list(set(v2).difference(instance_check.value_ar.split(',')))

					update_dict = {'value_en':','.join(value_en), 'value_ar':','.join(value_ar)}
					_, created = totalVariations.objects.update_or_create(productID=instance_check.productID, name_en=k1, name_ar=k2, defaults=update_dict)
				else:
					totalVariations.objects.create(productID=item, parent_asin=parent_asin, name_en=k1, name_ar=k2, value_en=','.join(v1), value_ar=','.join(v2))


		asin = self.asin
		items = productPagesScrapper.objects.filter(productID=asin, description_en=True, description_ar=True, source__startswith='amazon')

		if items:
			item = items[0]

			# instance of VariationsSoup
			variation = VariationsSoup(asin)
			parent_asin = variation.ParentAsin()
			
			if parent_asin:

				try:

					variationSettings_instance = variationSettings.objects.filter(current_asin=asin) or variationSettings.objects.filter(parent_asin=asin)

					func_totalVariations(variation,parent_asin,item)
					func_variationSettings(variation,parent_asin,variationSettings_instance,item)
					
				except Exception as e:
					print(e)
					print("Error that forced productPagesScrapper to invalid : Parent Asin : ",parent_asin," productID : ",item.productID)
					productPagesScrapper.objects.filter(productID=asin).update(description_en=False, description_ar=False)

					return 'update product'


				return 'found'

			else:
				return 'not found'


	def vaienceDetails(self, item):
		

		if item:

			if not item.images:
				varience = varienceDetail(item)

				item.title_en = varience.titleParser()
				item.title_ar = varience.titleParserAR()
				item.images = varience.allImages()

				item.save()

			if not item.price:
				varience = varienceDetail(item)

				item.price = varience.price()
				item.old_price = varience.old_price()

				item.save()

				# variationSettings.objects.filter(current_asin=item.current_asin).update(title_en=title_en, title_ar=title_ar, images=all_images)
	

	def varienceCrawler(self):

		asin = self.asin

		items = productPagesScrapper.objects.filter(productID=asin, description_en=True, description_ar=True, source__startswith='amazon')

		if items:
			item = items[0]

			total_asins_en = [i for x in variationSettings.objects.filter(current_asin=item.productID) for i in variationSettings.objects.filter(parent_asin=x.parent_asin) if x] or variationSettings.objects.filter(parent_asin=item.productID)
			total_asins_ar = [i for x in variationSettings.objects.filter(current_asin=item.productID) for i in variationSettings.objects.filter(parent_asin=x.parent_asin) if x] or variationSettings.objects.filter(parent_asin=item.productID)

			all_asins = list(total_asins_en)

			for single in total_asins_ar:
				if single not in total_asins_en:
					all_asins.append(single)

			return all_asins

			'''
			# Focus Here
			if all_asins:

				for counting,single_asin in enumerate(all_asins, start=1):
					if not single_asin.description_en:
						variance = Variant(single_asin)
						variance.saveResponse()

					if not single_asin.description_ar:
						variance = Variant(single_asin)
						variance.saveResponseAR()

					self.vaienceDetails(single_asin.current_asin)
			
					progress_recorder.set_progress(counting, len(all_asins), f"on {single_asin.current_asin}")
			'''
