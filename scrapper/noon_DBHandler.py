from .models import *
from . import noon_scrapper

class noon_DBHandler_cls():

	def __init__(self, asin):
		self.asin = asin

	def get_valid(self):
		asin = self.asin

		item_db = productPagesScrapper.objects.get(productID=asin)
		if not item_db.description_en:
			noon_scrapper.noonResponseValidate(item_db)

		if not item_db.description_ar:
			noon_scrapper.noonResponseValidateArabic(item_db)


	# write this for noon.com instead of amazon.ae
	def get_product_data(self, item):

		def get_product_detail(item, language, product_details_class):

			if not productDetails.objects.filter(productID=item, language=language).exists():
				specifications = product_details_class.Specifications()

				data = [
					productDetails(productID=item, language=language, attributes=attr, values=val)
					for attr, val in specifications
				]

				productDetails.objects.bulk_create(data)

			if not productDescription.objects.filter(productID=item, language=language).exists():
				long_description = product_details_class.ProductDescription()

				productDescription.objects.create(productID=item, language=language, long_description=long_description)

			if not productHighlights.objects.filter(productID=item, language=language).exists():
				highlights = product_details_class.Highlights()

				highlights_data = [
					productHighlights(productID=item, language=language, highlight=highlight)
					for highlight in highlights
				]

				productHighlights.objects.bulk_create(highlights_data)

		
		if item.description_en and item.description_ar:

			product_details_class = noon_scrapper.NoonProductDetails(item)

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
					product_details_class = noon_scrapper.NoonProductDetails(item)

				else:
					product_details_class = noon_scrapper.NoonProductDetailsArabic(item)

				get_product_detail(item, language, product_details_class)
		else:
			pass