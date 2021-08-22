from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery_progress.backend import ProgressRecorder

from .models import *
from . import amazon_scrapper
from .amazon_DBHandler import *


@shared_task(bind=True)
def category_validator(self, category):

	progress_recorder = ProgressRecorder(self)

	category_items = productPagesScrapper.objects.filter(source__startswith='amazon',category=category)

	for counting,item in enumerate(category_items, start=1):

		dbhandler_ins = amazon_DBHandler_cls(item.productID)
		dbhandler_ins.get_valid()

		item_new = productPagesScrapper.objects.filter(productID=item.productID, description_en=True, description_ar=True)
		if item_new:
			dbhandler_ins.get_product_data(item_new[0])

		progress_recorder.set_progress(counting, len(category_items), f"on {item.productID}")

	return 'Done'


