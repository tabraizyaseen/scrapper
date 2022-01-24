from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery_progress.backend import ProgressRecorder

from scrapper.models import *
from scrapper import amazon_scrapper
from scrapper.variations import *

@shared_task()
def single_item(asin):

	def get_valid(asin):

		item_db = productPagesScrapper.objects.create(productID=asin, source='amazon.ae')
		if not item_db.description_en:
			amazon_scrapper.ResponseValidate(item_db)

		if not item_db.description_ar:
			amazon_scrapper.ResponseValidateArabic(item_db)


	def get_product_data(item, language, product_details_class):

		if not productImages.objects.filter(productID=item).exists():

			images = product_details_class.ImagesList()

			images_data = [
				productImages(productID=item, image=image)
				for image in images
			]

			productImages.objects.bulk_create(images_data)


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


	get_valid(asin)

	try:
		item_new = productPagesScrapper.objects.get(productID=asin, description_en=True, description_ar=True)

		languages = ['EN','AR']

		for language in languages:

			if language == 'EN':
				product_details_class = amazon_scrapper.AmazonProductDetails(item_new)

			else:
				product_details_class = amazon_scrapper.AmazonProductDetailsArabic(item_new)

			get_product_data(item_new, language, product_details_class)

		return "Done"		

	except Exception as e:
		print(e)
		return "Item Not Found"


@shared_task()
def child_item(asin):

	def vaienceDetails(asin):

		item = variationSettings.objects.filter(current_asin=asin, description_en=True, description_ar=True)

		if item:

			item = item[0]
			if not item.images:
				varience = varienceDetail(item)

				title_en = varience.titleParser()
				title_ar = varience.titleParserAR()
				all_images = varience.allImages()

				variationSettings.objects.filter(current_asin=item.current_asin).update(title_en=title_en, title_ar=title_ar, images=all_images)

	item = variationSettings.objects.get(current_asin=asin)
	if not item.description_en:
		variance = Variant(item)
		variance.saveResponse()

	if not item.description_ar:
		variance = Variant(item)
		variance.saveResponseAR()

	vaienceDetails(item.current_asin)

	return "Done"


@shared_task(bind=True)
def item_variations(self, asin):

	def get_valid(asin):

		item_db = productPagesScrapper.objects.get(productID=asin)
		if not item_db.description_en:
			amazon_scrapper.ResponseValidate(item_db)

		if not item_db.description_ar:
			amazon_scrapper.ResponseValidateArabic(item_db)


		return productPagesScrapper.objects.filter(productID=asin, description_en=True, description_ar=True)


	def get_product_data(item, language, product_details_class):

		if not productImages.objects.filter(productID=item).exists():

			images = product_details_class.ImagesList()

			images_data = [
				productImages(productID=item, image=image)
				for image in images
			]

			productImages.objects.bulk_create(images_data)


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


	def saveVariations(product):

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



		items = productPagesScrapper.objects.filter(productID=product, description_en=True, description_ar=True, source__startswith='amazon')

		if items:
			item = items[0]

			# instance of VariationsSoup
			variation = VariationsSoup(product)
			parent_asin = variation.ParentAsin()
			
			if parent_asin:

				try:

					# working with update_or_create here 
					lambda_instance_func = lambda x,y : x if x else y

					variationSettings_instance = lambda_instance_func(variationSettings.objects.filter(current_asin=product), variationSettings.objects.filter(parent_asin=product))

					func_totalVariations(variation,parent_asin,item)
					func_variationSettings(variation,parent_asin,variationSettings_instance,item)
					
				except Exception as e:
					print(e)
					print("Error that forced productPagesScrapper to invalid : Parent Asin : ",parent_asin," productID : ",item.productID)
					productPagesScrapper.objects.filter(productID=product).update(description_en=False, description_ar=False)




	def varienceCrawler(product, progress_recorder):

		def vaienceDetails(asin):

			item = variationSettings.objects.filter(current_asin=asin, description_en=True, description_ar=True)

			if item:

				item = item[0]
				if not item.images:
					varience = varienceDetail(item)

					title_en = varience.titleParser()
					title_ar = varience.titleParserAR()
					all_images = varience.allImages()

					variationSettings.objects.filter(current_asin=item.current_asin).update(title_en=title_en, title_ar=title_ar, images=all_images)


		items = productPagesScrapper.objects.filter(productID=product, description_en=True, description_ar=True, source__startswith='amazon')

		if items:
			item = items[0]

			total_asins_en = [i for x in variationSettings.objects.filter(current_asin=item.productID) for i in variationSettings.objects.filter(parent_asin=x.parent_asin, description_en=False) if x] or variationSettings.objects.filter(parent_asin=item.productID, description_en=False)
			total_asins_ar = [i for x in variationSettings.objects.filter(current_asin=item.productID) for i in variationSettings.objects.filter(parent_asin=x.parent_asin, description_ar=False) if x] or variationSettings.objects.filter(parent_asin=item.productID, description_ar=False)

			all_asins = list(total_asins_en)

			for single in all_asins:
				if single not in total_asins_en:
					all_asins.append(single)

			if all_asins:

				for counting,single_asin in enumerate(all_asins, start=1):
					if not single_asin.description_en:
						variance = Variant(single_asin)
						variance.saveResponse()

					if not single_asin.description_ar:
						variance = Variant(single_asin)
						variance.saveResponseAR()

					vaienceDetails(single_asin.current_asin)
			
					progress_recorder.set_progress(counting, len(all_asins), f"on {single_asin.current_asin}")


	progress_recorder = ProgressRecorder(self)

	item = productPagesScrapper.objects.filter(productID=asin, description_ar=True, description_en=True) or get_valid(asin)

	if item:
		item = item[0]

		# Product Data
		languages = ['EN','AR']

		for language in languages:

			if language == 'EN':
				product_details_class = amazon_scrapper.AmazonProductDetails(item)

			else:
				product_details_class = amazon_scrapper.AmazonProductDetailsArabic(item)

			get_product_data(item, language, product_details_class)

		variation = VariationsSoup(asin)
		parent_asin = variation.ParentAsin()
		
		if parent_asin:

			# Saving Possible Variations
			saveVariations(asin)

			# Running crawler for the variation products and save their details
			varienceCrawler(asin, progress_recorder)

			return "Done"

		else:

			return "Item don't contains variations"

	else:
		return "Item not found"

