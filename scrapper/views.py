from __future__ import absolute_import, unicode_literals

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q

from .models import *
from . import amazon_scrapper
from . import amazon_ksa
from . import noon_scrapper
from .filters import *
from .variations import *
from . import tasks
from .amazon_DBHandler import *
from .noon_DBHandler import *

from django_celery_results.models import TaskResult
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

import re
import json
import html
import csv
import pandas as pd
import itertools
from collections import Counter
import datetime

from bs4 import BeautifulSoup
import io


# Create your views here.

def home(request):

	context = {
	}

	return render(request, 'scrapper/home.html', context)

def productVaraitions(request):

	variation = variationSettings.objects.all()
	valid_count = variationSettings.objects.filter(description_en=True, description_ar=True)

	variationsFilter = VariationSettingsFilter(request.GET, queryset=variation)
	variations = variationsFilter.qs


	# Pagination
	product_paginator = Paginator(variations, 50)
	total_pages = [i for i in range(1, product_paginator.num_pages + 1)]
	page_num = request.GET.get('page', 1)
	try:
		page = product_paginator.page(page_num)
	except EmptyPage:
		page = product_paginator.page(product_paginator.num_pages)

	context = {
		'countVariations': len(variation),
		'valid_count': len(valid_count),
		'variationsFilter': variationsFilter,
		'page': page,
		'total_pages': total_pages,
	}

	return render(request, 'scrapper/product_variations.html', context)


def productTotalVariations(request):

	total = totalVariations.objects.all()

	totalsFilter = TotalVariationsFilter(request.GET, queryset=total)
	totals = totalsFilter.qs


	# Pagination
	product_paginator = Paginator(totals, 50)
	total_pages = [i for i in range(1, product_paginator.num_pages + 1)]
	page_num = request.GET.get('page', 1)
	try:
		page = product_paginator.page(page_num)
	except EmptyPage:
		page = product_paginator.page(product_paginator.num_pages)

	context = {
		'count_total': len(total),
		'totalsFilter': totalsFilter,
		'page': page,
		'total_pages': total_pages,
	}

	return render(request, 'scrapper/product_total_variations.html', context)

def searchTitles(request):

	# If an item was last checked 15 days ago
	def check_latest(item_db):
		two_weeks_ago = timezone.now() - datetime.timedelta(weeks=2)

		if two_weeks_ago > item_db.last_checked:
			item_db.description_ar = False
			item_db.description_en = False
			item_db.save()

	def asin_manager(item, results, validated, results_ksa, variations):

		item_db = productPagesScrapper.objects.filter(productID=item)
		if item_db:

			item_db = item_db[0]

			# To Get the latest
			# check_latest(item_db)

			# Differentiating SA and AE products
			(lambda x: results_ksa.append(x) if x.source == 'amazon.sa' else results.append(x))(item_db)

			# Get count of validated items
			(lambda x: validated.append(x) if x.description_en and x.description_ar else x)(item_db)

			# Get variations
			variations.append([i for x in variationSettings.objects.filter(current_asin=item_db.productID) for i in variationSettings.objects.filter(parent_asin=x.parent_asin) if x])

		else:
			productPagesScrapper.objects.create(productID=item.strip(), source='amazon.ae')

			single_item = productPagesScrapper.objects.get(productID=item)
			results.append(single_item)
			
			print(counting)

		return results, validated, results_ksa, variations

	# Initializing Lists
	results = []
	validated = []
	results_ksa = []
	variations = []
	variations_lst = []
	
	if request.method == 'POST':
		file = request.FILES['titles_file']
		try:
			global global_file
			global_file = pd.read_csv(file, low_memory=False, encoding='unicode_escape')
			print(global_file.columns)
			global_file.dropna(subset=['ASIN'],inplace=True)
			global_file.fillna('', inplace=True)

			if 'Amazon_Category' in global_file.columns:
				for counting,(item,category) in enumerate(zip(global_file['ASIN'], global_file['Amazon_Category']), start=1):
					asin_manager(item, results, validated, results_ksa, variations)

					if category:
						category = category.replace('>','›')
						productPagesScrapper.objects.filter(productID=item).update(category=category)
			else:
				for counting,item in enumerate(global_file['ASIN'], start=1):

					asin_manager(item, results, validated, results_ksa, variations)


			variations_lst = [i for sub in variations for i in sub]

		except Exception as e:
			messages.info(request, e)

	context = {
		'results' : results,
		'results_ksa' : results_ksa,
		'counting' : len(results + results_ksa),
		'accepted' : len(validated),
		'variations' : variations_lst
	}
	
	return render(request, 'scrapper/search_titles.html', context)

# Saving Varience at import
def saveVariations(request):

	results_data = []

	for countings, product in enumerate(global_file['ASIN'], start=1):

		dbhandler_ins = amazon_DBHandler_cls(product)
		status = dbhandler_ins.saveVariations()

		if status == 'found':

			single = [i for x in variationSettings.objects.filter(current_asin=product) for i in variationSettings.objects.filter(parent_asin=x.parent_asin) if x] or variationSettings.objects.filter(parent_asin=product)
			for s in single:
				results_data.append(s)
			
		print(countings)

	context_lst = []
	for data in results_data:
		context = {}
		context["asin"] = data.productID.productID
		context["current_asin"] = data.current_asin
		context["parent_asin"] = data.parent_asin
		context["description_en"] = data.description_en
		context["description_ar"] = data.description_ar

		context_lst.append(context)

	updated_record = productPagesScrapper.objects.filter(productID__in=global_file['ASIN'])
	product_list = []
	for item_db in updated_record:
		context = {}
		context["productID"] = item_db.productID
		context["description_en"] = item_db.description_en
		context["description_ar"] = item_db.description_ar
		product_list.append(context)

	validated = [item for item in updated_record if item.description_en and item.description_ar]

	return JsonResponse({'report':context_lst, 'type':"variation report", 'products':product_list, 'valid_count':len(validated)})

# Varience Crawler
def varienceCrawler(request):

	results_data = []

	for countings, product in enumerate(global_file['ASIN'], start=1):

		dbhandler_ins = amazon_DBHandler_cls(product)
		all_asins = dbhandler_ins.varienceCrawler()

		if all_asins:

			for num_childern,single_asin in enumerate(all_asins, start=1):

				if not single_asin.description_en:
					variance = Variant(single_asin)
					variance.saveResponse()

				if not single_asin.description_ar:
					variance = Variant(single_asin)
					variance.saveResponseAR()

				print(f'{countings}-{num_childern}')

			single = [i for x in variationSettings.objects.filter(current_asin=product) for i in variationSettings.objects.filter(parent_asin=x.parent_asin) if x] or variationSettings.objects.filter(parent_asin=product)
			if single:
				for s in single:
					results_data.append(s)


		print(countings)

	context_lst = []
	for data in results_data:
		context = {}
		context["asin"] = data.productID.productID
		context["current_asin"] = data.current_asin
		context["parent_asin"] = data.parent_asin
		context["description_en"] = data.description_en
		context["description_ar"] = data.description_ar

		context_lst.append(context)

	return JsonResponse({'report':context_lst, 'type':"variation report"})

# Product total variences
def productTotalVarience(request):

	for countings, product in enumerate(global_file['ASIN'], start=1):

		item_CA = [i for x in variationSettings.objects.filter(current_asin=product) for i in variationSettings.objects.filter(parent_asin=x.parent_asin,description_ar=True, description_en=True) if x]
		item_PA = variationSettings.objects.filter(parent_asin=product, description_ar=True, description_en=True)

		items = item_CA or item_PA

		if items:

			for asin in items:

				dbhandler_ins = amazon_DBHandler_cls(product)
				dbhandler_ins.vaienceDetails(asin)
		
		print(countings)

	return JsonResponse({'report':'Okay'})

def robustSearchValid(request):

	results_lst = []
	validated = []

	# Calling global variable here
	for counting, item in enumerate(global_file['ASIN'], start=1 ):

		dbhandler_ins = amazon_DBHandler_cls(item)
		dbhandler_ins.get_valid()

		# Sending updated details
		context = {}

		item_db = productPagesScrapper.objects.get(productID=item)
		context["productID"] = item_db.productID
		context["description_en"] = item_db.description_en
		context["description_ar"] = item_db.description_ar

		results_lst.append(context)

		print(counting)

	validated = [item for item in results_lst if item['description_en'] and item['description_ar']]

	return JsonResponse({'report':results_lst, 'valid_count':len(validated), 'type':'crawler report'})

def robustSearchValidKSA(request):

	results_lst = []

	# Calling global variable here
	for counting, item in enumerate(global_file['ASIN'], start=1 ):

		dbhandler_ins = amazon_DBHandler_cls(item)
		dbhandler_ins.get_valid_ksa()

		context = {}
		item_db = productPagesScrapper.objects.filter(productID=item, source='amazon.sa')
		if item_db:
			item_db = item_db[0]
			context["productID"] = item_db.productID
			context["description_en"] = item_db.description_en
			context["description_ar"] = item_db.description_ar

			results_lst.append(context)

		print(counting)

	return JsonResponse({'report':results_lst, 'type':'ksa report'})

def robustSearchDetails(request):

	# Call global variable here
	for counting, item in enumerate(global_file['ASIN'], start=1):

		product = productPagesScrapper.objects.filter(productID=item, description_ar=True, description_en=True)

		if product:

			print(counting)
			dbhandler_ins = amazon_DBHandler_cls(item)
			dbhandler_ins.get_product_data(product[0])

	return JsonResponse({'report':'Okay'})

def amazonScrapper(request):

	if request.is_ajax():

		category_link = request.POST['category-link']

		try:

			amazon_scrapper.amazonCategoryScrapper(category_link)
		except Exception as e:
			return JsonResponse({'Exception':e})

		return JsonResponse({'report':'Okay'})

	context = {}

	return render(request, 'scrapper/amazon_scrapper.html', context)

def noonScrapper(request):

	if request.is_ajax():

		category_link = request.POST['category-link']

		try:

			noon_scrapper.noonCategoryScrapper(category_link)
		except Exception as e:
			return JsonResponse({'Exception':e})

		return JsonResponse({'report':'Okay'})

	context = {}

	return render(request, 'scrapper/noon_scrapper.html', context)

def dataStats(request):

	if request.is_ajax():

		total_products = productPagesScrapper.objects.count()
		valid_products_count = productPagesScrapper.objects.filter(description_en=True, description_ar=True).count()

		amazon_products = productPagesScrapper.objects.filter(source='amazon.ae').count()
		amazonSA_products = productPagesScrapper.objects.filter(source='amazon.sa').count()
		noon_products = productPagesScrapper.objects.filter(source='noon.com').count()

		valid_english = productPagesScrapper.objects.filter(description_en=True).count()
		valid_arabic = productPagesScrapper.objects.filter(description_ar=True).count()

		total_images = productImages.objects.values('productID').distinct().count()
		total_highlights = productHighlights.objects.values('productID').distinct().count()
		total_specs = productDetails.objects.values('productID').distinct().count()
		total_desc = productDescription.objects.values('productID').distinct().count()

		context = {
			'labels': ['Total','Valid Save','Amazon UAE','Amazon KSA','Noon','English Valid','Arabic Valid'],
			'labels_data': [total_products,valid_products_count,amazon_products,amazonSA_products,noon_products,valid_english,valid_arabic],
			'detail_label': ['Total Images','Total Highlights','Total Specifications','Total Descriptions'],
			'detail_data': [total_images, total_highlights, total_specs,total_desc]
		}

		return JsonResponse(context)

	
	context = {
		
	}

	return render(request, 'scrapper/stats.html', context)


def viewCategories(request):

	global global_category
	global_category = productPagesScrapper.objects.filter(productID__startswith='B').values('category').distinct()
	total_category = len(global_category)

	categoryFilter = ProductCategoryFilter(request.GET, queryset=global_category)
	global_category = categoryFilter.qs


	# Pagination
	product_paginator = Paginator(global_category, 50)
	total_pages = [i for i in range(1, product_paginator.num_pages + 1)]
	page_num = request.GET.get('page', 1)
	try:
		page = product_paginator.page(page_num)
	except EmptyPage:
		page = product_paginator.page(product_paginator.num_pages)

	if request.is_ajax():
		category = request.POST['text']

		sel_cats = productPagesScrapper.objects.filter(productID__startswith='B',category=category,description_en=True,description_ar=True)
		print(len(sel_cats))
		
		for countings, cat in enumerate(sel_cats, start=1):

			dbhandler_ins = amazon_DBHandler_cls(cat.productID)
			dbhandler_ins.get_product_data(cat)

			print(countings)

		return JsonResponse({'report':'Okay'})

	context = {
		'category': global_category,
		'total_category': total_category,
		'page': page,
		'total_pages': total_pages,
		'categoryFilter': categoryFilter,
		'curret_selected': len(global_category),
	}
	return render(request, 'scrapper/view_categories.html',context)


def categoryJob(request):

	if request.is_ajax():
		category = request.POST['text']

		match_category = category.replace('›',r'\u203a')

		if not TaskResult.objects.filter(task_args=f'"(\'{match_category}\',)"', status__in=('PROGRESS','PENDING')).exists():

			print("Revoking task for :",category)
			task_ins = tasks.category_validator.delay(category)
			task_id = task_ins.task_id
		else:
			try:
				task_ins = TaskResult.objects.get(task_args=f'"(\'{match_category}\',)"', status__in=('PROGRESS','PENDING'))
				task_id = task_ins.task_id
			except Exception:
				task_id = None
			print("Task already in queue : ",category)

		context = {'report':'Okay', 'task_id':task_id}

	return JsonResponse(context)


def viewCategoryAttributes(request,pk):

	category = pk

	categories = productPagesScrapper.objects.filter(productID__startswith='B',category=category,description_en=True,description_ar=True)

	product_details_en = productDetails.objects.filter(productID__in=tuple([cate for cate in categories]), language='EN').exclude(attributes__in=('Brand','Asin','ASIN')).values('attributes').distinct()
	product_details_ar = productDetails.objects.filter(productID__in=tuple([cate for cate in categories]), language='AR').exclude(attributes__in=('Brand','Asin','العلامة التجارية','ASIN')).values('attributes').distinct()

	
	context = {
		'product_details_en': product_details_en,
		'product_details_ar': product_details_ar,
		'category': category,

	}
	return render(request, 'scrapper/category_attributes.html', context)

def viewProducts(request):

	total_products = productPagesScrapper.objects.count()
	all_products = productPagesScrapper.objects.all()

	global valid_products
	valid_products = productPagesScrapper.objects.filter(description_en=True, description_ar=True).order_by('title_en')

	valid_products_count = valid_products.count()

	myFilter = ProductFilter(request.GET, queryset=all_products)
	all_products = myFilter.qs

	# Pagination
	product_paginator = Paginator(all_products, 50)
	total_pages = [i for i in range(1, product_paginator.num_pages + 1)]
	page_num = request.GET.get('page', 1)
	try:
		page = product_paginator.page(page_num)
	except EmptyPage:
		page = product_paginator.page(product_paginator.num_pages)

	context = {
		'total_products': total_products,
		'valid_products_count': valid_products_count,
		'myFilter': myFilter,
		'page': page,
		'total_pages': total_pages,
		'download_count': len(all_products),
	}

	return render(request, 'scrapper/view_products.html', context)

def singleProductValidate(request):

	if request.is_ajax():

		context = {}
		asin = request.POST['text']

		item = productPagesScrapper.objects.get(productID=asin)
		if item.source == "amazon.ae" or item.source == "amazon.sa":

			dbhandler_ins = amazon_DBHandler_cls(asin)

		elif item.source == 'noon.com':

			dbhandler_ins = noon_DBHandler_cls(asin)

		dbhandler_ins.get_valid()

		product = productPagesScrapper.objects.filter(productID=asin, description_ar=True, description_en=True)

		if product:
			dbhandler_ins.get_product_data(product[0])

			item_new = productPagesScrapper.objects.get(productID=asin)
			context["pk"] = item_new.id
			context["productID"] = item_new.productID
			context["category"] = item_new.category
			context["title_en"] = item_new.title_en
			context['status'] = 'Ok'
		else:
			context['status'] = 'fail'


		return JsonResponse(context)

# Product Details English
def amazonProductDetails(request, pk):
	asin = productPagesScrapper.objects.get(id=pk)
	
	# Amazon product 
	if asin.source == 'amazon.ae' or asin.source == 'amazon.sa':

		db_handler_ins = amazon_DBHandler_cls(asin.productID)
		db_handler_ins.get_valid()
		db_handler_ins.get_product_data(asin)

		details = productDetails.objects.filter(productID=asin, language='EN')
		pictures = productImages.objects.filter(productID=asin)
		about = productHighlights.objects.filter(productID=asin, language='EN')
		long_desc = productDescription.objects.filter(productID=asin, language='EN')

	# Noon product
	elif asin.source == 'noon.com':

		db_handler_ins = noon_DBHandler_cls(asin.productID)
		db_handler_ins.get_valid()
		db_handler_ins.get_product_data(asin)

		details = productDetails.objects.filter(productID=asin, language='EN')
		pictures = productImages.objects.filter(productID=asin)
		about = productHighlights.objects.filter(productID=asin, language='EN')
		long_desc = productDescription.objects.filter(productID=asin, language='EN')

	context = {
		'details': details,
		'images': pictures,
		'highlights': about,
		'title': asin,
		'language': 'EN',
		'Description': long_desc,
	}

	return render(request, 'scrapper/product_details.html', context)

# Product Details Arabic
def productDetailsArabic(request, pk):
	asin = productPagesScrapper.objects.get(id=pk)
	
	# Amazon product 
	if asin.source == 'amazon.ae' or asin.source == 'amazon.sa':

		db_handler_ins = amazon_DBHandler_cls(asin.productID)
		db_handler_ins.get_valid()
		db_handler_ins.get_product_data(asin)

		pictures = productImages.objects.filter(productID=asin)
		details = productDetails.objects.filter(productID=asin, language='AR')
		about = productHighlights.objects.filter(productID=asin, language='AR')
		long_desc = productDescription.objects.filter(productID=asin, language='AR')

	# Noon product
	elif asin.source == 'noon.com':

		db_handler_ins = noon_DBHandler_cls(asin.productID)
		db_handler_ins.get_valid()
		db_handler_ins.get_product_data(asin)

		pictures = productImages.objects.filter(productID=asin)
		details = productDetails.objects.filter(productID=asin, language='AR')
		about = productHighlights.objects.filter(productID=asin, language='AR')
		long_desc = productDescription.objects.filter(productID=asin, language='AR')

	context = {
		'details': details,
		'images': pictures,
		'highlights': about,
		'title': asin,
		'language': 'AR',
		'Description': long_desc,
	}

	return render(request, 'scrapper/product_details.html', context)

# Downloading data into json
def sampleJson(request):

	# products_data = amazonProductPagesScrapper.objects.all()

	
	# data = {}
	# for prod_data in products_data:

	# 	data[prod_data.title] = {}
	# 	data[prod_data.title]['category'] = prod_data.category
	# 	data[prod_data.title]['asin'] = prod_data.productID
	# 	data[prod_data.title]['link'] = prod_data.link

	# 	try:
	# 		data[prod_data.title]['images'] = list(prod_data.productimages_set.values('image'))
	# 	except AttributeError:
	# 		data[prod_data.title]['images'] = None

	# 	try:
	# 		data[prod_data.title]['specifications'] = list(prod_data.amazonproductdetails_set.values('attributes','values'))
	# 	except AttributeError:
	# 		data[prod_data.title]['specifications'] = None

	''' As valid_products is a global variable '''
	data = {}
	for prod_data in valid_products: # As valid_products is a global variable

		data[prod_data.productID] = {}

		# English
		data[prod_data.productID]['English'] = {}
		data[prod_data.productID]['English']['category'] = prod_data.category
		data[prod_data.productID]['English']['title'] = prod_data.title_en

		data[prod_data.productID]['English']['images'] = list(prod_data.productimages_set.all().values('image'))

		# If data already not available for English
		if prod_data.source == 'amazon.ae':
			if not data[prod_data.productID]['English']['images']:
				# highlights, specifications, images = amazon_scrapper.amazonProductDetails(prod_data)
				product_details_class = amazon_scrapper.AmazonProductDetails(prod_data)

				highlights = product_details_class.Highlights()
				specifications = product_details_class.Specifications()
				images = product_details_class.ImagesList()

				details_data = [
				productDetails(productID=prod_data, language='EN', attributes=attr, values=val)
				for attr, val in specifications
				]

				productDetails.objects.bulk_create(details_data)

				images_data = [
				productImages(productID=prod_data, image=image)
				for image in images
				]

				productImages.objects.bulk_create(images_data)

				highlights_data = [
					productHighlights(productID=prod_data, language='EN', highlight=highlight)
					for highlight in highlights
				]

				productHighlights.objects.bulk_create(highlights_data)

				data[prod_data.productID]['English']['images'] = list(prod_data.productimages_set.all().values('image'))

		data[prod_data.productID]['English']['specifications'] = list(prod_data.productdetails_set.filter(language='EN').values('attributes','values'))
		data[prod_data.productID]['English']['highlights'] = [highlight.highlight for highlight in prod_data.producthighlights_set.filter(language='EN')]


		# Arabic
		data[prod_data.productID]['Arabic'] = {}
		data[prod_data.productID]['Arabic']['category'] = prod_data.category
		data[prod_data.productID]['Arabic']['title'] = prod_data.title_ar

		data[prod_data.productID]['Arabic']['images'] = list(prod_data.productimages_set.all().values('image'))
		data[prod_data.productID]['Arabic']['specifications'] = list(prod_data.productdetails_set.filter(language='AR').values('attributes','values'))

		# If data already not available for Arabic
		if prod_data.source == 'amazon.ae':
			if not data[prod_data.productID]['Arabic']['specifications']:
				# highlights, specifications, images = amazon_scrapper.amazonProductDetailsArabic(prod_data)
				product_detailsAR_class = amazon_scrapper.AmazonProductDetailsArabic(prod_data)

				highlights = product_detailsAR_class.Highlights()
				specifications = product_detailsAR_class.Specifications()

				details_data = [
				productDetails(productID=prod_data, language='AR', attributes=attr, values=val)
				for attr, val in specifications
				]

				productDetails.objects.bulk_create(details_data)

				highlights_data = [
					productHighlights(productID=prod_data, language='AR', highlight=highlight)
					for highlight in highlights
				]

				productHighlights.objects.bulk_create(highlights_data)

				data[prod_data.productID]['Arabic']['specifications'] = list(prod_data.productdetails_set.filter(language='AR').values('attributes','values'))
		
		data[prod_data.productID]['Arabic']['highlights'] = [highlight.highlight for highlight in prod_data.producthighlights_set.filter(language='AR')]

	response = HttpResponse(content_type='application/json')
	response['Content-Disposition'] = 'attachment; filename="sample.json"'

	json.dump(data, response, ensure_ascii = False, indent=2)

	return response

def categoryExportJsonBoth(request):

	data = {}
	if request.is_ajax():

		data_en = json.loads(request.POST.get('text_en',False))
		data_ar = json.loads(request.POST.get('text_ar',False))
		cat = html.unescape(request.POST['Category'])

		if len(data_en) == len(data_ar):
			sorted(data_ar)
		elif len(data_en) > len(data_ar):
			left = []
			for i in data_en.keys():
				if not i in data_ar.keys():
					left.append(i)
			for i in left:
				data_en.pop(i)
			sorted(data_ar)
		else:
			left = []
			for i in data_ar.keys():
				if not i in data_en.keys():
					left.append(i)
			for i in left:
				data_ar.pop(i)
			sorted(data_ar)


		# Category
		print(cat)
		data['category'] = cat
		category_qs = productPagesScrapper.objects.filter(productID__startswith='B',category=cat,description_ar=True,description_en=True)

		# Attributes
		attributes_lst = []
			
		for prod_en,prod_ar in zip(data_en.values(),data_ar.values()):
			prod_dic = {}
			prod_dic['type'] = ''
			prod_dic['name_en'] = prod_en
			prod_dic['name_ar'] = prod_ar

			possible_val_en = productDetails.objects.filter(productID__in=tuple([cate for cate in category_qs]),attributes=prod_en, language='EN').values('values').distinct()
			possible_val_ar = productDetails.objects.filter(productID__in=tuple([cate for cate in category_qs]),attributes=prod_ar, language='AR').values('values').distinct()
			print(len(possible_val_ar))
			print(len(possible_val_en))
			if len(possible_val_en) > 1 and len(possible_val_ar) > 1:
				prod_dic['type'] = 'select'
				prod_dic['possible_values_english'] = [{'name_en':v['values']} for v in possible_val_en]
				prod_dic['possible_values_arabic'] = [{'name_ar':v['values']} for v in possible_val_ar]

			else:
				prod_dic['type'] = 'text'
				prod_dic['default_values'] = ''
				prod_dic['possible_values'] = [{'name_en':v['values'],'name_ar':k['values']} for v,k in zip(possible_val_en,possible_val_ar)]

			attributes_lst.append(prod_dic)

		data['attributes'] = attributes_lst

	# response = HttpResponse(content_type='application/json')
	# response['Content-Disposition'] = 'attachment; filename="Category_Both_Sample.json"'

	# json.dump(data, response, ensure_ascii = False, indent=4)

	return JsonResponse({'data':data})
	# return response

# English and Arabic both
def categoryRequiredExportJson(request,cid):

	data = []
	for categories in global_category: # As global_category is a global variable
		category_dic = {}
		category_qs = productPagesScrapper.objects.filter(productID__startswith='B',category__icontains=categories['category'],description_en=True,description_ar=True)

		# Category
		# category_dic['category'] = category_qs[0].category
		category_dic['category'] = cid

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

		data.append(category_dic)



	response = HttpResponse(content_type='application/json')
	response['Content-Disposition'] = f'attachment; filename="{cid}.json"'

	json.dump(data, response, ensure_ascii = False, indent=4)

	return response


# Category wise export data
# English
def categoryExportJson(request):

	data = []
	for categories in global_category: # As global_category is a global variable
		category_dic = {}
		category_qs = productPagesScrapper.objects.filter(productID__startswith='B',category=categories['category'],description_en=True,description_ar=True)

		# Category
		category_dic['category'] = category_qs[0].category

		# Attributes
		attributes_lst = []
		if category_qs:
			product_details_en = productDetails.objects.filter(productID__in=tuple([cate for cate in category_qs]), language='EN').exclude(attributes__in=('Brand','Asin','ASIN')).values('attributes').distinct()
			
			for prod_en in product_details_en:
				prod_dic = {}
				prod_dic['type'] = ''
				prod_dic['name_en'] = prod_en['attributes']

				possible_val_en = productDetails.objects.filter(productID__in=tuple([cate for cate in category_qs]),attributes=prod_en['attributes'], language='EN').values('values').distinct()
				if len(possible_val_en) > 1:
					prod_dic['type'] = 'select'
					prod_dic['default_values'] = [{'name_en':possible_val_en[0]['values']}]
					prod_dic['possible_values'] = [{'name_en':v['values']} for v in possible_val_en]

				else:
					prod_dic['type'] = 'text'
					prod_dic['default_values'] = ''
					prod_dic['possible_values'] = [{'name_en':v['values']} for v in possible_val_en]

				attributes_lst.append(prod_dic)

		category_dic['attributes'] = attributes_lst

		data.append(category_dic)



	response = HttpResponse(content_type='application/json')
	response['Content-Disposition'] = 'attachment; filename="Category_English_Sample.json"'

	json.dump(data, response, ensure_ascii = False, indent=4)

	return response

# Arabic
def categoryExportARJson(request):

	data = []
	for categories in global_category: # As global_category is a global variable
		category_dic = {}
		category_qs = productPagesScrapper.objects.filter(productID__startswith='B',category=categories['category'],description_en=True,description_ar=True)

		# Category
		category_dic['category'] = category_qs[0].category

		# Attributes
		attributes_lst = []
		if category_qs:
			product_details_ar = productDetails.objects.filter(productID__in=tuple([cate for cate in category_qs]), language='AR').exclude(attributes__in=('Brand','Asin','العلامة التجارية','ASIN')).values('attributes').distinct()
			

			for prod_ar in product_details_ar:
				prod_dic = {}
				prod_dic['type'] = ''
				prod_dic['name_ar'] = prod_ar['attributes']

				possible_val_ar = productDetails.objects.filter(productID__in=tuple([cate for cate in category_qs]),attributes=prod_ar['attributes'], language='AR').values('values').distinct()
				if len(possible_val_ar) > 1:
					prod_dic['type'] = 'select'
					prod_dic['default_values'] = [{'name_ar':possible_val_ar[0]['values']}]
					prod_dic['possible_values'] = [{'name_ar':av['values']} for av in possible_val_ar]

				else:
					prod_dic['type'] = 'text'
					prod_dic['default_values'] = ''
					prod_dic['possible_values'] = [{'name_ar':av['values']} for av in possible_val_ar]

				attributes_lst.append(prod_dic)

		category_dic['attributes'] = attributes_lst

		data.append(category_dic)



	response = HttpResponse(content_type='application/json')
	response['Content-Disposition'] = 'attachment; filename="Category_Arabic_Sample.json"'

	json.dump(data, response, ensure_ascii = False, indent=4)

	return response


def export_csv(request):

	current_date = str(datetime.date.today())
	name = current_date+'_Scrapped.csv'

	# Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
	response['Content-Disposition'] = f'attachment; filename={name}'

	writer = csv.writer(response)
	writer.writerow([
		'product_id','Asin','Category', 'SKU' ,'Brand','Title',
		'Title Arabic','Description','Description Arabic','Long Description',
		'Long Description Arabic','product_id.1', 'Market Price (AED)', 
		'Price (AED)', 'Quantity', 'Ship To UAE','Ship To KSA', 'GradeId', 
		'WeightClassId', 'Ship to Dubai Cost (AED)', 
		'Ship to Everywhere Cost (AED)', 'ImageLinks (Comma Separated)'])

	# Calling global variable global_file
	for item in global_file['ASIN']:
		item_db = productPagesScrapper.objects.filter(productID=item, description_en=True, description_ar=True)
		if item_db:
			# Category
			try:
				category = item_db[0].category
			except Exception:
				category = ''

			# Brand
			brand = ''
			brand_db = item_db[0].productdetails_set.filter(language='EN', attributes='Brand')
			if brand_db:
				brand = brand_db[0].values

			asin = item_db[0].productID
			title_en = item_db[0].title_en
			title_ar = item_db[0].title_ar

			try:
				description_en = ', '.join([highlight.highlight for highlight in item_db[0].producthighlights_set.filter(language='EN')])
			except Exception:
				description_en = ''

			try:
				description_ar = ', '.join([highlight.highlight for highlight in item_db[0].producthighlights_set.filter(language='AR')])
			except Exception:
				description_ar = ''
			
			# English Long Description
			long_descriptionEN_db = item_db[0].productdescription_set.filter(language='EN')
			long_descriptionEN = long_descriptionEN_db[0].long_description

			# Arabic Long Description
			long_descriptionAR_db = item_db[0].productdescription_set.filter(language='AR')
			long_descriptionAR = long_descriptionAR_db[0].long_description

			images = ','.join([images.image for images in item_db[0].productimages_set.all()])
			
			writer.writerow([
				'',asin,category,'',brand,title_en,title_ar,description_en,description_ar, 
				long_descriptionEN,long_descriptionAR,'','','','','','','','','','',images])


	return response

	# Quick Solution
	'''
	# Reading English File
	with io.open(f'static/docs/productPages/EN_{asin}.txt', 'r', encoding='UTF-8') as html_file:
		soup_en = BeautifulSoup(html_file.read(), 'html.parser')

	#Description English
	try:
		long_descriptionEN_div = soup_en.find('div',{'id':'productDescription'})
		long_descriptionEN_p = long_descriptionEN_div.find_all('p')
		for p_tag in long_descriptionEN_p:
			if p_tag.text:
				long_descriptionEN = p_tag.text.strip()
				break
	except AttributeError:
		long_descriptionEN=''

	# Reading Arabic File
	with io.open(f'static/docs/productPages/AR_{asin}.txt', 'r', encoding='UTF-8') as html_file:
		soup_ar = BeautifulSoup(html_file.read(), 'html.parser')

	#Description Arabic
	try:
		long_descriptionAR_div = soup_ar.find('div',{'id':'productDescription'})
		long_descriptionAR_p = long_descriptionAR_div.find_all('p')
		for p_tag in long_descriptionAR_p:
			if p_tag.text:
				long_descriptionAR = p_tag.text.strip()
				break
	except AttributeError:
		long_descriptionAR=''
	'''

def export_csv_ksa(request):

	current_date = str(datetime.date.today())
	name = 'KSA_'+current_date+'_Scrapped.csv'

	# Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
	response['Content-Disposition'] = f'attachment; filename={name}'

	writer = csv.writer(response)
	writer.writerow([
		'product_id','Asin','Category', 'SKU' ,'Brand','Title',
		'Title Arabic','Description','Description Arabic','Long Description',
		'Long Description Arabic','product_id.1', 'Market Price (AED)', 
		'Price (AED)', 'Quantity', 'Ship To UAE','Ship To KSA', 'GradeId', 
		'WeightClassId', 'Ship to Dubai Cost (AED)', 
		'Ship to Everywhere Cost (AED)', 'ImageLinks (Comma Separated)'])

	# Calling global variable global_file
	for item in global_file['ASIN']:
		item_db = productPagesScrapper.objects.filter(productID=item, description_en=True, description_ar=True, source='amazon.sa')
		if item_db:
			# Category
			try:
				category = item_db[0].category
			except Exception:
				category = ''

			# Brand
			brand = ''
			brand_db = item_db[0].productdetails_set.filter(language='EN', attributes='Brand')
			if brand_db:
				brand = brand_db[0].values

			asin = item_db[0].productID
			title_en = item_db[0].title_en
			title_ar = item_db[0].title_ar

			try:
				description_en = ', '.join([highlight.highlight for highlight in item_db[0].producthighlights_set.filter(language='EN')])
			except Exception:
				description_en = ''

			try:
				description_ar = ', '.join([highlight.highlight for highlight in item_db[0].producthighlights_set.filter(language='AR')])
			except Exception:
				description_ar = ''
			
			# English Long Description
			long_descriptionEN_db = item_db[0].productdescription_set.filter(language='EN')
			long_descriptionEN = long_descriptionEN_db[0].long_description

			# Arabic Long Description
			long_descriptionAR_db = item_db[0].productdescription_set.filter(language='AR')
			long_descriptionAR = long_descriptionAR_db[0].long_description

			images = ','.join([images.image for images in item_db[0].productimages_set.all()])
			
			writer.writerow([
				'',asin,category,'',brand,title_en,title_ar,description_en,description_ar, 
				long_descriptionEN,long_descriptionAR,'','','','','','','','','','',images])


	return response


# Old one
def export_demanded_json(request):

	current_date = str(datetime.date.today())
	name = current_date+'_Scrapped.json'

	data = []
	for item in global_file['ASIN']: # As global_file is a global variable

		item_db = productPagesScrapper.objects.filter(productID=item, description_en=True, description_ar=True)
		if item_db:
			print(item_db[0].productID)
			data_dict = {}

			# Category
			try:
				category = item_db[0].category
			except Exception:
				category = ''

			data_dict['category'] = category
			data_dict['weight_class'] = ''

			# Brand
			brand = ''
			brand_db = item_db[0].productdetails_set.filter(language='EN', attributes='Brand')
			if brand_db:
				brand = brand_db[0].values

			data_dict['brand'] = brand
			data_dict['title'] = item_db[0].title_en
			data_dict['title_ar'] = item_db[0].title_ar
			data_dict['description'] = ' '.join([long_desc.long_description for long_desc in item_db[0].productdescription_set.filter(language='EN')])
			data_dict['description_ar'] = ' '.join([long_desc.long_description for long_desc in item_db[0].productdescription_set.filter(language='AR')])
			data_dict['highlights'] = [highlight.highlight for highlight in item_db[0].producthighlights_set.filter(language='EN')]
			data_dict['highlights_ar'] = [highlight.highlight for highlight in item_db[0].producthighlights_set.filter(language='AR')]

			data_dict['gtin'] = ''
			data_dict['ean'] = ''
			data_dict['upc'] = ''

			data_dict['default_images'] = [images.image for images in item_db[0].productimages_set.all()]

			# Specifications
			category_lst = []

			specs_en = item_db[0].productdetails_set.filter(language='EN').exclude(attributes__in=('Brand','Asin','ASIN'))
			specs_ar = item_db[0].productdetails_set.filter(language='AR').exclude(attributes__in=('Brand','Asin','العلامة التجارية','ASIN'))

			for indexes,specs in enumerate(specs_en):
				spec_dict = {}

				try:
					spec_dict['type'] = 'text'
					spec_dict['name_en'] = specs.attributes
					spec_dict['name_ar'] = specs_ar[indexes].attributes
					spec_dict['value'] = specs.values
					spec_dict['value_ar'] = specs_ar[indexes].values

					category_lst.append(spec_dict)
				except Exception:
					break
				
			data_dict['category_attributes'] = category_lst

			# Reading English File
			with io.open(f'static/docs/productPages/EN_{item_db[0].productID}.txt', 'r', encoding='UTF-8') as html_file:
				soup_en = BeautifulSoup(html_file.read(), 'html.parser')

			# Javascript Tag
			try:
				pattern = re.compile(r"P\.register\('twister-js-init-dpx-data', function\(\) \{")
				javascript_tag = soup_en.find('script',string=pattern).contents[0]
				val_start = javascript_tag.find('"variationValues"')+20
				variationValues = javascript_tag[val_start:].split('\n')[0][:-1]
				variations = json.loads(variationValues)

			except Exception:
				variations = {}

			# Variation_Data
			if variations:
				variation_lst = []
				variation_lst.append({"name":"Conditions","values":['FRA','FRB']})

				for k,v in variations.items():
					variation_dict = {}
					variation_dict["name"] = k
					variation_dict["values"] = v
					variation_lst.append(variation_dict)

				data_dict['variation_settings'] = variation_lst

			else:
				data_dict['variation_settings'] = []

			data_dict['variations'] = []


			data.append(data_dict)


	response = HttpResponse(content_type='application/json')
	response['Content-Disposition'] = f'attachment; filename={name}'

	json.dump(data, response, ensure_ascii = False, indent=4)

	return response

# New One
def requiredJsonFormat(request):

	current_date = str(datetime.date.today())
	name = current_date+'_Scrapped.json'

	data = []

	# Avoid Repeating Products
	check_dict = {i.parent_asin:item for item in global_file['ASIN'] for i in variationSettings.objects.filter(current_asin=item)}
	no_vari_list = [i for i in global_file['ASIN'] if not variationSettings.objects.filter(current_asin=i).exists()]
	check_list = set(list(check_dict.values()) + no_vari_list)


	# global_file is a global file of Asins
	for weight,grades_provided,category,item in zip(global_file['weight_class'],global_file['Conditions'],global_file['Category'],global_file['ASIN']):
	# for category,item in zip(global_file['Category'],global_file['ASIN']):

		if item in check_list:

			item_db = productPagesScrapper.objects.filter(productID=item, description_en=True, description_ar=True)
			if item_db:
				print(item_db[0].productID)
				data_dict = {}

				# Category
				# try:
				# 	category = item_db[0].category
				# except Exception:
				# 	category = ''

				data_dict['category'] = category
				data_dict['weight_class'] = weight

				# Brand
				brand = ''
				brand_db = item_db[0].productdetails_set.filter(language='EN', attributes='Brand') or item_db[0].productdetails_set.filter(language='EN', attributes__in=('Brand, Seller, or Collection Name','Manufacturer'))
				if brand_db:
					brand = brand_db[0].values

				data_dict['brand'] = brand
				data_dict['title'] = item_db[0].title_en
				data_dict['title_ar'] = item_db[0].title_ar
				data_dict['market_price'] = int(item_db[0].old_price or 0)
				data_dict['description'] = ' '.join([long_desc.long_description for long_desc in item_db[0].productdescription_set.filter(language='EN')]) or '. '.join([highlight.highlight for highlight in item_db[0].producthighlights_set.filter(language='EN')]) or data_dict['title']
				data_dict['description_ar'] = ' '.join([long_desc.long_description for long_desc in item_db[0].productdescription_set.filter(language='AR')]) or '. '.join([highlight.highlight for highlight in item_db[0].producthighlights_set.filter(language='AR')]) or data_dict['title_ar']
				# data_dict['highlights'] = [highlight.highlight for highlight in item_db[0].producthighlights_set.filter(language='EN')]
				# data_dict['highlights_ar'] = [highlight.highlight for highlight in item_db[0].producthighlights_set.filter(language='AR')]

				data_dict['gtin'] = ''
				data_dict['ean'] = ''
				data_dict['upc'] = ''

				data_dict['asin'] = ''

				data_dict['default_images'] = [images.image for images in item_db[0].productimages_set.all()]

				# Specifications
				category_lst = []

				specs_en = item_db[0].productdetails_set.filter(language='EN').exclude(attributes__in=('Brand','Asin','ASIN'))
				specs_ar = item_db[0].productdetails_set.filter(language='AR').exclude(attributes__in=('Brand','Asin','العلامة التجارية','ASIN'))

				for en_spec in specs_en:
					spec_dict = {}

					try:
						# spec_dict['type'] = 'text'
						spec_dict['key'] = en_spec.attributes
						# spec_dict['name_ar'] = specs_ar[indexes].attributes
						spec_dict['value'] = [en_spec.values]

						category_lst.append(spec_dict)
					except Exception:
						break

				for ar_spec in specs_ar:
					spec_dict = {}

					try:
						# spec_dict['type'] = 'text'
						spec_dict['key'] = ar_spec.attributes
						# spec_dict['name_ar'] = specs_ar[indexes].attributes
						spec_dict['value'] = [ar_spec.values]

						category_lst.append(spec_dict)
					except Exception:
						break
					
				data_dict['category_attributes'] = category_lst

				# Lambda Function
				lambda_variant_func = lambda x,y: x if x else y

				# Variation_Settings
				single_variant_db = lambda_variant_func(variationSettings.objects.filter(current_asin=item_db[0].productID),variationSettings.objects.filter(parent_asin=item_db[0].productID))

				if single_variant_db:
					variations_settings = totalVariations.objects.filter(parent_asin=single_variant_db[0].parent_asin).order_by('-id') or totalVariations.objects.filter(productID=single_variant_db[0].productID).order_by('-id')

					data_dict['asin'] = variations_settings[0].parent_asin

					variations_settings_list = []

					# Grades Variations
					variations_settings_list.append({'name':'Conditions', 'values':grades_provided.split(','),'name_ar':'الظروف', 'values_ar':grades_provided.split(',')})

					for variations in variations_settings:

						variations_settings_dict = {}

						variations_settings_dict['name'] = variations.name_en.replace('_',' ').title()
						variations_settings_dict['values'] = variations.value_en.split(',')
						variations_settings_dict['name_ar'] = variations.name_ar.replace('_',' ').title()
						variations_settings_dict['values_ar'] = variations.value_ar.split(',')

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
							dimension_list = v[1:]
							total_variations = ''

							for match_variation in variationSettings.objects.filter(productID=single_variant_db[0].productID, available=True):
								if set(dimension_list) == set(match_variation.dimension_val_en.split(',')):
									total_variations = match_variation
			
							if total_variations:

								# Variation Found
								variations_dict['variation_index'] = f'{index_dimension}'
								variations_dict['variation'] = f"{index_value}"
								variations_dict['asin'] = total_variations.current_asin
								variations_dict['title'] = f"{total_variations.title_en}"
								variations_dict['title_ar'] = f"{total_variations.title_ar}"
								variations_dict['market_price'] = int(total_variations.old_price or 0)
								variations_dict['description'] = data_dict['description']
								variations_dict['description_ar'] = data_dict['description_ar']
								variations_dict['gtin'] = ''
								variations_dict['ean'] = ''
								variations_dict['upc'] = ''
								variations_dict['images'] = total_variations.images.split(',')
							else:

								# Variation Not Found
								variations_dict['variation_index'] = f'{index_dimension}'
								variations_dict['variation'] = f"{index_value}"
								variations_dict['asin'] = '' # data_dict['asin']
								variations_dict['title'] = '' # f"{item_db[0].title_en}"
								variations_dict['title_ar'] = ''# f"{item_db[0].title_ar}"
								variations_dict['market_price'] = 0
								variations_dict['description'] = ''
								variations_dict['description_ar'] = ''
								variations_dict['gtin'] = ''
								variations_dict['ean'] = ''
								variations_dict['upc'] = ''
								variations_dict['images'] =[] # [images.image for images in item_db[0].productimages_set.all()]

							variations_list.append(variations_dict)

					data_dict['variations'] = variations_list


				# If variations is not given
				else:
					data_dict['asin'] = item

					# all_grades = fc_grades.objects.all()
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
						variations_dict['market_price'] = data_dict['market_price']
						variations_dict['description'] = data_dict['description']
						variations_dict['description_ar'] = data_dict['description_ar']
						variations_dict['gtin'] = ''
						variations_dict['ean'] = ''
						variations_dict['upc'] = ''
						variations_dict['images'] = data_dict['default_images']

						variations_list.append(variations_dict)

					data_dict['variations'] = variations_list

				data.append(data_dict)


	response = HttpResponse(content_type='application/json')
	response['Content-Disposition'] = f'attachment; filename={name}'

	json.dump(data, response, ensure_ascii = False, indent=4)

	return response