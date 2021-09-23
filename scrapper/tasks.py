from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery_progress.backend import ProgressRecorder
from django.db.models import Q

from .models import *
from . import amazon_scrapper
from .amazon_DBHandler import *


@shared_task(bind=True)
def category_validator(self, category):

	def fun_validator(dbhandler_ins,item):
		if item.source == "amazon.ae":
			dbhandler_ins.get_valid()

		elif item.source == 'noon.com':
			noonDbhandler_ins = noon_DBHandler_cls(asin)
			noonDbhandler_ins.get_valid()

		elif item.source == "amazon.sa":
			dbhandler_ins.get_valid_ksa()

		elif item.source == "amazon.in":
			dbhandler_ins.get_valid_india()

		elif item.source == "amazon.com.au":
			dbhandler_ins.get_valid_aus()

		elif item.source == "amazon.co.uk":
			dbhandler_ins.get_valid_uk()

		elif item.source == "amazon.com":
			dbhandler_ins.get_valid_com()

	progress_recorder = ProgressRecorder(self)

	category_items = productPagesScrapper.objects.filter(source__startswith='amazon',category=category)

	for counting,item in enumerate(category_items, start=1):
		dbhandler_ins = amazon_DBHandler_cls(item.productID)
		fun_validator(dbhandler_ins,item)

		item_new = productPagesScrapper.objects.filter(Q(productID=item.productID, description_en=True, description_ar=True) | Q(productID=item.productID, description_en=True, source__in=('amazon.in','amazon.com','amazon.com.au','amazon.co.uk')))
		if item_new:
			item_new = item_new[0]

			if item_new.source in ['amazon.ae','amazon.sa']:
				dbhandler_ins.get_product_data(item_new)
			elif item_new.source in ['amazon.in','amazon.com','amazon.com.au','amazon.co.uk']:
				dbhandler_ins.get_product_data_EN(item_new)

		progress_recorder.set_progress(counting, len(category_items), f"on {item.productID}")

	return 'Done'


