from .formats import productClass, categoryClass

from scrapper.models import *
from scrapper import amazon_scrapper
from scrapper.variations import *


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

		# Returning format
		db_item = productPagesScrapper.objects.filter(productID=asin)

		productClassIns = productClass(asin)
		items = productClassIns.productAttributes(db_item, data_dict={})

		return items

	except Exception as e:
		print(e)
		return "Item Not Found"


def child_item(asin):

	def vaienceDetails(item):
		
		if not item.images:
			varience = varienceDetail(item)

			title_en = varience.titleParser()
			title_ar = varience.titleParserAR()
			all_images = varience.allImages()

			variationSettings.objects.filter(current_asin=item.current_asin).update(title_en=title_en, title_ar=title_ar, images=all_images)

	def get_child_valid(asin):

		item = variationSettings.objects.get(current_asin=asin)
		if not item.description_en:
			variance = Variant(item)
			variance.saveResponse()

		if not item.description_ar:
			variance = Variant(item)
			variance.saveResponseAR()

	get_child_valid(asin)

	item = variationSettings.objects.filter(current_asin=asin, description_en=True, description_ar=True)
	if item:
		item = item[0]

		vaienceDetails(item)

		# Returning Format
		productClassIns = productClass(asin)
		items = productClassIns.childProduct(item)

		return items

	else:

		return "item not found"