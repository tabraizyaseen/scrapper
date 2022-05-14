
from .models import *
from . import mumzworld_scrapper

class mumz_DBHandler_cls():

    def __init__(self, asin):
        self.asin = asin

    def get_valid(self):
        asin = self.asin

        item_db = productPagesScrapper.objects.get(productID=asin)
        if item_db.source == 'mumzworld.com':
            if not item_db.description_en:
                mumzworld_scrapper.mumzResponseValidate(item_db)

            if not item_db.description_ar:
                mumzworld_scrapper.mumzResponseValidateArabic(item_db)

    def get_product_data(self, item):

        def get_product_detail(item, language, product_details_class):

            if not productHighlights.objects.filter(productID=item, language=language).exists():
                highlights = product_details_class.Highlights()

                if highlights:
                    highlights_data = [
                        productHighlights(productID=item, language=language, highlight=highlight)
                        for highlight in highlights
                    ]

                    productHighlights.objects.bulk_create(highlights_data)

            
            if not productDescription.objects.filter(productID=item, language=language).exists():
                long_description = product_details_class.ProductDescription()

                productDescription.objects.create(productID=item, language=language, long_description=long_description)

            if not productDetails.objects.filter(productID=item, language=language).exists():
                specifications = product_details_class.Specifications()

                if specifications:
                    data = [
                        productDetails(productID=item, language=language, attributes=attr, values=val)
                        for attr, val in specifications
                    ]

                    productDetails.objects.bulk_create(data)

        
        if item.description_en and item.description_ar:

            product_details_class = mumzworld_scrapper.mumzProductDetailsEN(item)

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
                    product_details_class = mumzworld_scrapper.mumzProductDetailsEN(item)

                else:
                    product_details_class = mumzworld_scrapper.mumzProductDetailsAR(item)

                get_product_detail(item, language, product_details_class)