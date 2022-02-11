from __future__ import absolute_import, unicode_literals

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q

from .models import *
from . import amazon_scrapper
from . import noon_scrapper
from .filters import *
from .variations import *
from . import tasks
from .amazon_DBHandler import *
from .noon_DBHandler import *
from api.formats import productClass, excelFormating

from django_celery_results.models import TaskResult
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

import json
import html
import csv
import pandas as pd
import datetime
import os
import concurrent.futures
import xlsxwriter

from time import perf_counter


# Create your views here.

def loginPage(request):

	if request.method == 'POST':
		name = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(request, username=name, password=password)
		if user is not None:
			login(request, user)
			# login(request, user)
			return redirect('home')
		else:
			messages.success(request, 'Invalid Username or Password')
	context = {

	}

	return render(request, 'scrapper/login.html', context)

def logoutPage(request):
    logout(request)
    return redirect('login')

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

# @login_required(login_url='login')
def searchTitles(request):

	# If an item was last checked 15 days ago
	def check_latest(item_db):
		two_weeks_ago = timezone.now() - datetime.timedelta(weeks=2)

		if two_weeks_ago > item_db.last_checked:
			item_db.description_ar = False
			item_db.description_en = False
			item_db.save()

	def asin_manager(item, results, validated, results_ksa, results_india, results_aus, results_uk, results_com, variations, filename):

		item_db = productPagesScrapper.objects.filter(productID=item)
		if item_db:

			item_db = item_db[0]

			# To Get the latest
			# check_latest(item_db)

			# Differentiating SA and AE products
			(lambda x: results_ksa.append(x) if x.source == 'amazon.sa' else (results_india.append(x) if x.source == 'amazon.in' else (results_aus.append(x) if x.source=='amazon.com.au' else (results_uk.append(x) if x.source == 'amazon.co.uk' else (results_com.append(x) if x.source == 'amazon.com' else results.append(x))))))(item_db)
			
			# Get variations
			variations.append([i for x in variationSettings.objects.filter(current_asin=item_db.productID) for i in variationSettings.objects.filter(productID=x.productID) if x])

			# adding batch name with asin
			if not item_db.batchname:
				item_db.batchname = filename
				item_db.save()
		else:
			productPagesScrapper.objects.create(productID=item, source='amazon.ae', batchname=filename)

			single_item = productPagesScrapper.objects.get(productID=item)
			results.append(single_item)
			
			print(counting)

		return results, validated, results_ksa, variations

	# Initializing Lists
	results = []
	validated = []
	results_ksa = []
	results_india = []
	results_aus = []
	results_uk = []
	results_com = []
	variations = []
	variations_lst = []
	filename = ''
	
	if request.method == 'POST':
		file = request.FILES.get(u'titles_file')
		filename = file.name
		# try:

		# global global_file
		global_file = pd.read_csv(file, encoding='unicode_escape', converters={'ASIN': lambda x: str(x)})
		strt = perf_counter()
		nan_value = float("NaN")
		global_file.replace("", nan_value, inplace=True)
		global_file.dropna(subset=['ASIN'],inplace=True)
		global_file = global_file.drop_duplicates(['ASIN'],keep= 'last')
		global_file.fillna('', inplace=True)
		global_file['ASIN'] = global_file['ASIN'].str.strip()

		request.session['global_file'] = global_file.to_json()
		request.session['file_name'] = filename
		request.session.modified = True

		end = perf_counter()

		print(f'file cleaning : {end-strt}')

		strt = perf_counter()

		if 'Amazon_Category' in global_file.columns:
			print('Amazon_Category given')
			for counting,(item,category) in enumerate(zip(global_file['ASIN'], global_file['Amazon_Category']), start=1):
				asin_manager(item, results, validated, results_ksa, results_india, results_aus, results_uk, results_com, variations, filename)

				if category:
					category = category.replace('>','›')
					productPagesScrapper.objects.filter(productID=item).update(category=category)
		else:
			print('Amazon_Category not given')
			for counting,item in enumerate(global_file['ASIN'], start=1):

				asin_manager(item, results, validated, results_ksa, results_india, results_aus, results_uk, results_com, variations, filename)


		variations_lst = [i for sub in variations for i in sub]
		# results = sorted(results, key=lambda k: k.title_en)

		# except Exception as e:
		# 	messages.info(request, e)

		end = perf_counter()
		print(f'file displaying : {end-strt}')
	
		validated = productPagesScrapper.objects.filter(Q(productID__in=global_file['ASIN'], description_en=True, description_ar=True) | Q(productID__in=global_file['ASIN'], description_en=True, source__in=('amazon.in','amazon.com','amazon.com.au','amazon.co.uk')))

	context = {
		'results' : results,
		'results_ksa' : results_ksa,
		'results_india': results_india,
		'results_aus' : results_aus,
		'results_uk' : results_uk,
		'results_com' : results_com,
		'counting' : len(results + results_ksa + results_india + results_aus + results_uk + results_com),
		'accepted' : len(validated),
		'variations' : variations_lst,
		'filename' : filename
	}
	
	return render(request, 'scrapper/search_titles.html', context)

# Saving Varience at import
def saveVariations(request):

	global_file = request.session['global_file']
	global_file = json.loads(global_file)
	global_file = pd.DataFrame(global_file)
	results_data = []

	for countings, product in enumerate(global_file['ASIN'], start=1):

		dbhandler_ins = amazon_DBHandler_cls(product)
		status = dbhandler_ins.saveVariations()

		if status == 'found':

			single = [i for x in variationSettings.objects.filter(current_asin=product) for i in variationSettings.objects.filter(productID=x.productID) if x] or variationSettings.objects.filter(parent_asin=product)
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
		context["source"] = data.productID.source

		context_lst.append(context)

	updated_record = productPagesScrapper.objects.filter(productID__in=global_file['ASIN'], source__in=('amazon.ae','amazon.sa','amazon.in','amazon.com','amazon.co.uk','amazon.com.au'))
	uae_list = []
	ksa_list = []
	ind_list = []
	uk_list = []
	usa_list = []
	au_list = []
	for item_db in updated_record:
		context = {}
		if item_db.source == 'amazon.ae':
			context["productID"] = item_db.productID
			context["description_en"] = item_db.description_en
			context["description_ar"] = item_db.description_ar

			uae_list.append(context)

		elif item_db.source == 'amazon.sa':
			context["productID"] = item_db.productID
			context["description_en"] = item_db.description_en
			context["description_ar"] = item_db.description_ar
			
			ksa_list.append(context)

		elif item_db.source == 'amazon.in':
			context["productID"] = item_db.productID
			context["description_en"] = item_db.description_en
			
			ind_list.append(context)

		elif item_db.source == 'amazon.com.au':
			context["productID"] = item_db.productID
			context["description_en"] = item_db.description_en
			
			au_list.append(context)

		elif item_db.source == 'amazon.co.uk':
			context["productID"] = item_db.productID
			context["description_en"] = item_db.description_en
			
			uk_list.append(context)

		elif item_db.source == 'amazon.com':
			context["productID"] = item_db.productID
			context["description_en"] = item_db.description_en
			
			usa_list.append(context)

	validated = [item for item in updated_record if (item.description_en and item.description_ar) or (item.description_en and (item.source=='amazon.in' or item.source=='amazon.com.au' or item.source=='amazon.com' or item.source=='amazon.co.uk'))]

	return JsonResponse({'report':context_lst, 'type':"variation report", 'uae':uae_list, 'ksa':ksa_list, 'uk':uk_list, 'au':au_list, 'ind':ind_list, 'usa':usa_list, 'valid_count':len(validated)})

# Varience Crawler
def varienceCrawler(request):

	global_file = request.session['global_file']
	global_file = json.loads(global_file)
	global_file = pd.DataFrame(global_file)
	results_data = []

	for countings, product in enumerate(global_file['ASIN'], start=1):

		dbhandler_ins = amazon_DBHandler_cls(product)
		all_asins = dbhandler_ins.varienceCrawler()

		if all_asins:

			chunks = 20
			asins_chunks = [all_asins[i:i+chunks] for i in range(0,len(all_asins),chunks)]
			counting = 0

			for chunk in asins_chunks:
				with concurrent.futures.ThreadPoolExecutor() as executor:
					results = [executor.submit(Variant(item).saveResponse) for item in chunk]
					resultsAR = [executor.submit(Variant(item).saveResponseAR) for item in chunk]

					for r1, r2 in zip(results, resultsAR):
						r1.result()
						r2.result()
						counting +=1
						print(f'{countings}-{counting}')

			single = [i for x in variationSettings.objects.filter(current_asin=product) for i in variationSettings.objects.filter(productID=x.productID) if x] or variationSettings.objects.filter(parent_asin=product)
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
		context["source"] = data.productID.source

		context_lst.append(context)

	return JsonResponse({'report':context_lst, 'type':"variation crawler report"})

# Product total variences
def productTotalVarience(request):

	global_file = request.session['global_file']
	global_file = json.loads(global_file)
	global_file = pd.DataFrame(global_file)
	for countings, product in enumerate(global_file['ASIN'], start=1):

		item_CA = [i for x in variationSettings.objects.filter(current_asin=product) for i in variationSettings.objects.filter(Q(productID=x.productID,description_ar=True, description_en=True) | Q(productID=x.productID, description_en=True, productID__source__in=('amazon.in','amazon.co.uk','amazon.com','amazon.com.au'))) if x]
		item_PA = variationSettings.objects.filter(Q(parent_asin=product, description_ar=True, description_en=True) | Q(parent_asin=product, description_en=True, productID__source__in=('amazon.in','amazon.co.uk','amazon.com','amazon.com.au')))

		items = item_CA or item_PA

		if items:

			for asin in items:

				dbhandler_ins = amazon_DBHandler_cls(product)
				dbhandler_ins.vaienceDetails(asin)
		
		print(countings)

	return JsonResponse({'report':'Okay'})

def robustSearchValid(request):

	global_file = request.session['global_file']
	global_file = json.loads(global_file)
	global_file = pd.DataFrame(global_file)
	results_lst = []
	results_lst_ksa = []
	validated = []

	asins = global_file['ASIN']
	chunks = 20
	asins_chunks = [asins[i:i+chunks] for i in range(0,len(asins),chunks)]
	counting = 0

	for chunk in asins_chunks:
		with concurrent.futures.ThreadPoolExecutor() as executor:
			results = [executor.submit(amazon_DBHandler_cls(item).get_valid) for item in chunk]

			for f in results:
				f.result()
				counting +=1
				print(counting)
	
	items_db = productPagesScrapper.objects.filter(productID__in=asins)
	for item_db in items_db:
		# Sending updated details
		context = {}
		if item_db.source  == 'amazon.ae':
			context["productID"] = item_db.productID
			context["description_en"] = item_db.description_en
			context["description_ar"] = item_db.description_ar
			results_lst.append(context)

		elif item_db.source == 'amazon.sa':
			context["productID"] = item_db.productID
			context["description_en"] = item_db.description_en
			context["description_ar"] = item_db.description_ar
			results_lst_ksa.append(context)

	validated = productPagesScrapper.objects.filter(Q(productID__in=global_file['ASIN'], description_en=True, description_ar=True) | Q(productID__in=global_file['ASIN'], description_en=True, source__in=('amazon.in','amazon.com','amazon.com.au','amazon.co.uk')))

	return JsonResponse({'report':results_lst, 'ksa': results_lst_ksa, 'valid_count':len(validated), 'type':'crawler report'})

def robustSearchValidKSA(request):

	global_file = request.session['global_file']
	global_file = json.loads(global_file)
	global_file = pd.DataFrame(global_file)
	results_lst = []
	results_lst_uae = []

	asins = global_file['ASIN']
	chunks = 20
	asins_chunks = [asins[i:i+chunks] for i in range(0,len(asins),chunks)]
	counting = 0
	
	for chunk in asins_chunks:
		with concurrent.futures.ThreadPoolExecutor() as executor:
			results = [executor.submit(amazon_DBHandler_cls(item).get_valid_ksa) for item in chunk]

			for f in results:
				f.result()
				counting +=1
				print(counting)

	items_db = productPagesScrapper.objects.filter(productID__in=asins)
	for item_db in items_db:

		context = {}
		if item_db.source == 'amazon.sa':
			context["productID"] = item_db.productID
			context["description_en"] = item_db.description_en
			context["description_ar"] = item_db.description_ar

			results_lst.append(context)

		elif item_db.source == 'amazon.ae':
			context["productID"] = item_db.productID
			context["description_en"] = item_db.description_en
			context["description_ar"] = item_db.description_ar

			results_lst_uae.append(context)

	validated = productPagesScrapper.objects.filter(Q(productID__in=global_file['ASIN'], description_en=True, description_ar=True) | Q(productID__in=global_file['ASIN'], description_en=True, source__in=('amazon.in','amazon.com','amazon.com.au','amazon.co.uk')))

	return JsonResponse({'report':results_lst, 'uae':results_lst_uae, 'valid_count':len(validated), 'type':'ksa report'})

def robustSearchValidIndia(request):

	global_file = request.session['global_file']
	global_file = json.loads(global_file)
	global_file = pd.DataFrame(global_file)
	results_lst = []
	results_lst_uae = []

	asins = global_file['ASIN']
	chunks = 20
	asins_chunks = [asins[i:i+chunks] for i in range(0,len(asins),chunks)]
	counting = 0
	
	for chunk in asins_chunks:
		with concurrent.futures.ThreadPoolExecutor() as executor:
			results = [executor.submit(amazon_DBHandler_cls(item).get_valid_india) for item in chunk]

			for f in results:
				f.result()
				counting +=1
				print(counting)

	items_db = productPagesScrapper.objects.filter(productID__in=asins)
	for item_db in items_db:

		context = {}
		if item_db.source == 'amazon.in':
			context["productID"] = item_db.productID
			context["description_en"] = item_db.description_en

			results_lst.append(context)

		elif item_db.source == 'amazon.ae':
			context["productID"] = item_db.productID
			context["description_en"] = item_db.description_en
			context["description_ar"] = item_db.description_ar

			results_lst_uae.append(context)

	validated = productPagesScrapper.objects.filter(Q(productID__in=global_file['ASIN'], description_en=True, description_ar=True) | Q(productID__in=global_file['ASIN'], description_en=True, source__in=('amazon.in','amazon.com','amazon.com.au','amazon.co.uk')))

	return JsonResponse({'report':results_lst, 'uae':results_lst_uae, 'valid_count':len(validated), 'type':'india report'})


def robustSearchValidAus(request):

	global_file = request.session['global_file']
	global_file = json.loads(global_file)
	global_file = pd.DataFrame(global_file)
	results_lst = []
	results_lst_uae = []

	asins = global_file['ASIN']
	chunks = 20
	asins_chunks = [asins[i:i+chunks] for i in range(0,len(asins),chunks)]
	counting = 0
	
	for chunk in asins_chunks:
		with concurrent.futures.ThreadPoolExecutor() as executor:
			results = [executor.submit(amazon_DBHandler_cls(item).get_valid_aus) for item in chunk]

			for f in results:
				f.result()
				counting +=1
				print(counting)

	items_db = productPagesScrapper.objects.filter(productID__in=asins)
	for item_db in items_db:

		context = {}
		if item_db.source == 'amazon.com.au':
			context["productID"] = item_db.productID
			context["description_en"] = item_db.description_en

			results_lst.append(context)

		elif item_db.source == 'amazon.ae':
			context["productID"] = item_db.productID
			context["description_en"] = item_db.description_en
			context["description_ar"] = item_db.description_ar

			results_lst_uae.append(context)

	validated = productPagesScrapper.objects.filter(Q(productID__in=global_file['ASIN'], description_en=True, description_ar=True) | Q(productID__in=global_file['ASIN'], description_en=True, source__in=('amazon.in','amazon.com','amazon.com.au','amazon.co.uk')))

	return JsonResponse({'report':results_lst, 'uae':results_lst_uae, 'valid_count':len(validated), 'type':'aus report'})


def robustSearchValidUk(request):

	global_file = request.session['global_file']
	global_file = json.loads(global_file)
	global_file = pd.DataFrame(global_file)
	results_lst = []
	results_lst_uae = []

	asins = global_file['ASIN']
	chunks = 20
	asins_chunks = [asins[i:i+chunks] for i in range(0,len(asins),chunks)]
	counting = 0
	
	for chunk in asins_chunks:
		with concurrent.futures.ThreadPoolExecutor() as executor:
			results = [executor.submit(amazon_DBHandler_cls(item).get_valid_uk) for item in chunk]

			for f in results:
				f.result()
				counting +=1
				print(counting)

	items_db = productPagesScrapper.objects.filter(productID__in=asins)
	for item_db in items_db:

		context = {}
		if item_db.source == 'amazon.co.uk':
			context["productID"] = item_db.productID
			context["description_en"] = item_db.description_en

			results_lst.append(context)

		elif item_db.source == 'amazon.ae':
			context["productID"] = item_db.productID
			context["description_en"] = item_db.description_en
			context["description_ar"] = item_db.description_ar

			results_lst_uae.append(context)

	validated = productPagesScrapper.objects.filter(Q(productID__in=global_file['ASIN'], description_en=True, description_ar=True) | Q(productID__in=global_file['ASIN'], description_en=True, source__in=('amazon.in','amazon.com','amazon.com.au','amazon.co.uk')))

	return JsonResponse({'report':results_lst, 'uae':results_lst_uae, 'valid_count':len(validated), 'type':'uk report'})


def robustSearchValidCom(request):

	global_file = request.session['global_file']
	global_file = json.loads(global_file)
	global_file = pd.DataFrame(global_file)
	results_lst = []
	results_lst_uae = []

	asins = global_file['ASIN']
	chunks = 20
	asins_chunks = [asins[i:i+chunks] for i in range(0,len(asins),chunks)]
	counting = 0
	
	for chunk in asins_chunks:
		with concurrent.futures.ThreadPoolExecutor() as executor:
			results = [executor.submit(amazon_DBHandler_cls(item).get_valid_com) for item in chunk]

			for f in results:
				f.result()
				counting +=1
				print(counting)

	items_db = productPagesScrapper.objects.filter(productID__in=asins)
	for item_db in items_db:

		context = {}
		if item_db.source == 'amazon.com':
			context["productID"] = item_db.productID
			context["description_en"] = item_db.description_en

			results_lst.append(context)

		elif item_db.source == 'amazon.ae':
			context["productID"] = item_db.productID
			context["description_en"] = item_db.description_en
			context["description_ar"] = item_db.description_ar

			results_lst_uae.append(context)

	validated = productPagesScrapper.objects.filter(Q(productID__in=global_file['ASIN'], description_en=True, description_ar=True) | Q(productID__in=global_file['ASIN'], description_en=True, source__in=('amazon.in','amazon.com','amazon.com.au','amazon.co.uk')))

	return JsonResponse({'report':results_lst, 'uae':results_lst_uae, 'valid_count':len(validated), 'type':'usa report'})


def robustSearchDetails(request):

	global_file = request.session['global_file']
	global_file = json.loads(global_file)
	global_file = pd.DataFrame(global_file)
	for counting, item in enumerate(global_file['ASIN'], start=1):

		product = productPagesScrapper.objects.filter(productID=item, description_ar=True, description_en=True)
		en_product = productPagesScrapper.objects.filter(productID=item, description_en=True, source__in=("amazon.in","amazon.com.au","amazon.co.uk","amazon.com"))

		if product:

			print(counting)
			dbhandler_ins = amazon_DBHandler_cls(item)
			dbhandler_ins.get_product_data(product[0])

		if en_product:

			print("EN - ",counting)
			dbhandler_ins = amazon_DBHandler_cls(item)
			dbhandler_ins.get_product_data_EN(en_product[0])


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


def viewCategories(request):

	# global_category = productPagesScrapper.objects.values('category').distinct()
	global_category = Categories.objects.all()
	total_category = len(global_category)
	print(global_category[0])

	categoryFilter = ProductCategoryFilter(request.GET, queryset=global_category)
	global_category = categoryFilter.qs

	request.session['global_category'] = [category.name for category in global_category]

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

		sel_cats = productPagesScrapper.objects.filter(Q(source__in=('amazon.ae','amazon.sa'),category__id=category,description_en=True,description_ar=True) | Q(source__in=('amazon.in','amazon.com.au','amazon.co.uk','amazon.com'),category__id=category,description_en=True))
		print(len(sel_cats))
		
		for countings, cat in enumerate(sel_cats, start=1):

			dbhandler_ins = amazon_DBHandler_cls(cat.productID)
			if cat.source == 'amazon.ae' or 'amazon.sa':
				dbhandler_ins.get_product_data(cat)
			elif cat.source == 'amazon.com' or 'amazon.co.uk' or 'amazon.com.au' or 'amazon.in':
				dbhandler_ins.get_product_data_EN(cat)
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

		if not TaskResult.objects.filter(task_args=f'"(\'{category}\',)"', status__in=('PROGRESS','PENDING')).exists():

			print("Revoking task for :",category)
			task_ins = tasks.category_validator.delay(category)
			task_id = task_ins.task_id
		else:
			try:
				task_ins = TaskResult.objects.get(task_args=f'"(\'{category}\',)"', status__in=('PROGRESS','PENDING'))
				task_id = task_ins.task_id
			except Exception:
				task_id = None
			print("Task already in queue : ",category)

		context = {'report':'Okay', 'task_id':task_id}

	return JsonResponse(context)


def viewCategoryAttributes(request,pk):

	category = Categories.objects.get(id=pk)

	categories = productPagesScrapper.objects.filter(productID__startswith='B',category=category,description_en=True,description_ar=True)

	product_details_en = productDetails.objects.filter(productID__in=tuple([cate for cate in categories]), language='EN').exclude(attributes__in=('Brand','Asin','ASIN')).values('attributes').distinct()
	product_details_ar = productDetails.objects.filter(productID__in=tuple([cate for cate in categories]), language='AR').exclude(attributes__in=('Brand','Asin','العلامة التجارية','ASIN')).values('attributes').distinct()

	
	context = {
		'product_details_en': product_details_en,
		'product_details_ar': product_details_ar,
		'category': category,

	}
	return render(request, 'scrapper/category_attributes.html', context)

@login_required(login_url='login')
def viewProducts(request):

	total_products = productPagesScrapper.objects.count()
	all_products = productPagesScrapper.objects.all()

	valid_products_count = productPagesScrapper.objects.filter(description_en=True, description_ar=True).count()

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

	return render(request, 'scrapper/home.html', context)

def singleProductValidate(request):

	if request.is_ajax():

		context = {}
		asin = request.POST['text']

		item = productPagesScrapper.objects.get(productID=asin)
		dbhandler_ins = amazon_DBHandler_cls(asin)
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

		product = productPagesScrapper.objects.filter(productID=asin, description_ar=True, description_en=True)

		if product:
			dbhandler_ins.get_product_data(product[0])

			item_new = productPagesScrapper.objects.get(productID=asin)
			context["pk"] = item_new.id
			context["productID"] = item_new.productID
			context["category"] = item_new.category.name
			context["title_en"] = item_new.title_en
			context['status'] = 'Ok'
		else:
			context['status'] = 'fail'


		return JsonResponse(context)


def deleteAsin(request):
	if request.is_ajax():
		asin = request.POST['asin']

		product = productPagesScrapper.objects.get(productID=asin)
		product.delete()

		product_variations = variationSettings.objects.filter(productID=product)

		for vari in product_variations:
			lst_exists = [f'static/docs/productPages/EN_{vari.current_asin}.txt',f'static/docs/productPages/AR_{vari.current_asin}.txt']

			for i in lst_exists:
				print(i)
				if os.path.exists(i):
					os.remove(i)

		context = {
			'report': 'okay'
		}
	return JsonResponse(context)

# Product Details English
def amazonProductDetails(request, pk):

	def fun_details(asin):

		details = productDetails.objects.filter(productID=asin, language='EN')
		pictures = productImages.objects.filter(productID=asin)
		about = productHighlights.objects.filter(productID=asin, language='EN')
		long_desc = productDescription.objects.filter(productID=asin, language='EN')

		return details,pictures,about,long_desc

	asin = productPagesScrapper.objects.get(id=pk)
	
	# Amazon product 
	if asin.source == 'amazon.ae':
		db_handler_ins = amazon_DBHandler_cls(asin.productID)
		db_handler_ins.get_valid()
		db_handler_ins.get_product_data(asin)

		details,pictures,about,long_desc = fun_details(asin)

	elif asin.source == 'amazon.sa':
		db_handler_ins = amazon_DBHandler_cls(asin.productID)
		db_handler_ins.get_valid_ksa()
		db_handler_ins.get_product_data(asin)

		details,pictures,about,long_desc = fun_details(asin)

	elif asin.source == 'amazon.in':
		db_handler_ins = amazon_DBHandler_cls(asin.productID)
		db_handler_ins.get_valid_india()
		db_handler_ins.get_product_data_EN(asin)

		details,pictures,about,long_desc = fun_details(asin)

	elif asin.source == 'amazon.com.au':
		db_handler_ins = amazon_DBHandler_cls(asin.productID)
		db_handler_ins.get_valid_aus()
		db_handler_ins.get_product_data_EN(asin)

		details,pictures,about,long_desc = fun_details(asin)

	elif asin.source == 'amazon.co.uk':
		db_handler_ins = amazon_DBHandler_cls(asin.productID)
		db_handler_ins.get_valid_uk()
		db_handler_ins.get_product_data_EN(asin)

		details,pictures,about,long_desc = fun_details(asin)

	elif asin.source == 'amazon.com':
		db_handler_ins = amazon_DBHandler_cls(asin.productID)
		db_handler_ins.get_valid_com()
		db_handler_ins.get_product_data_EN(asin)

		details,pictures,about,long_desc = fun_details(asin)

	# Noon product
	elif asin.source == 'noon.com':

		db_handler_ins = noon_DBHandler_cls(asin.productID)
		db_handler_ins.get_valid()
		db_handler_ins.get_product_data(asin)

		details,pictures,about,long_desc = fun_details(asin)

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

	def fun_details_arabic(asin):
		pictures = productImages.objects.filter(productID=asin)
		details = productDetails.objects.filter(productID=asin, language='AR')
		about = productHighlights.objects.filter(productID=asin, language='AR')
		long_desc = productDescription.objects.filter(productID=asin, language='AR')

		return pictures, details, about, long_desc

	asin = productPagesScrapper.objects.get(id=pk)
	
	# Amazon product 
	if asin.source == 'amazon.ae' or asin.source == 'amazon.sa':

		db_handler_ins = amazon_DBHandler_cls(asin.productID)

		if asin.source == 'amazon.ae':
			db_handler_ins.get_valid()
		elif asin.source == 'amazon.sa':
			db_handler_ins.get_valid_ksa()

		db_handler_ins.get_product_data(asin)

		pictures, details, about, long_desc = fun_details_arabic(asin)

	# If a product arabic response was already available and english found later
	if asin.source == 'amazon.in' or 'amazon.com' or 'amazon.co.uk' or 'amazon.com.au':

		db_handler_ins = amazon_DBHandler_cls(asin.productID)
		db_handler_ins.get_product_data(asin)

		pictures, details, about, long_desc = fun_details_arabic(asin)

	# Noon product
	elif asin.source == 'noon.com':

		db_handler_ins = noon_DBHandler_cls(asin.productID)
		db_handler_ins.get_valid()
		db_handler_ins.get_product_data(asin)

		pictures, details, about, long_desc = fun_details_arabic(asin)

	context = {
		'details': details,
		'images': pictures,
		'highlights': about,
		'title': asin,
		'language': 'AR',
		'Description': long_desc,
	}

	return render(request, 'scrapper/product_details.html', context)

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

	global_category = request.session['global_category']
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

	global_category = request.session['global_category']
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

	global_category = request.session['global_category']
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

# New One
def requiredJsonFormat(request):

	current_date = str(datetime.date.today())
	name = current_date+'_Scrapped.json'

	# Uploaded File
	global_file = request.session['global_file']
	global_file = json.loads(global_file)
	global_file = pd.DataFrame(global_file)

	# File Name
	filename = request.session['file_name']
	data = []

	# Avoid Repeating Products
	check_dict = {i.parent_asin:item for item in global_file['ASIN'] for i in variationSettings.objects.filter(current_asin=item)}
	no_vari_list = [i for i in global_file['ASIN'] if not variationSettings.objects.filter(current_asin=i).exists()]
	check_list = set(list(check_dict.values()) + no_vari_list)

	# Formulating export format
	for weight,grades_provided,category,item in zip(global_file['weight_class'],global_file['Conditions'],global_file['Category'],global_file['ASIN']):

		if item in check_list:
			
			productClassIns = productClass(item)
			print(item)
			data_dict = productClassIns.mainProductData(weight_class=weight, conditions=grades_provided, category=category, filename=filename)

			if data_dict:

				data.append(data_dict)


	response = HttpResponse(content_type='application/json')
	response['Content-Disposition'] = f'attachment; filename={name}'

	json.dump(data, response, ensure_ascii = False, indent=4)

	return response

def categoryAttributesManager(request):

	current_date = str(datetime.date.today())
	name = current_date+'_Category_Scrapped.json'

	global_file = request.session['global_file']
	global_file = json.loads(global_file)
	global_file = pd.DataFrame(global_file)
	data = []

	# Identifying unique cartlow category ids
	file_category = list(global_file['Category'].unique())

	for categories in file_category:
		category_dic = {}

		# Seprating asins which matched with cartlow category id
		match_file = global_file[global_file['Category'] == categories]

		category_qs = productPagesScrapper.objects.filter(Q(productID__in=tuple(match_file['ASIN']),description_en=True,description_ar=True) | Q(productID__in=tuple(match_file['ASIN']),description_en=True, source='amazon.in'))

		category_dic['category'] = str(categories)

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
					prod_dic['possible_values'] = [{'name':v['values']} for v in possible_val_en]

				else:
					prod_dic['type'] = 'text'
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
					prod_dic['possible_values'] = [{'name':av['values']} for av in possible_val_ar]

				else:
					prod_dic['type'] = 'text'
					prod_dic['possible_values'] = [{'name':av['values']} for av in possible_val_ar]

				attributes_lst.append(prod_dic)

		category_dic['attributes'] = attributes_lst

		data.append(category_dic)

	response = HttpResponse(content_type='application/json')
	response['Content-Disposition'] = f'attachment; filename="{name}"'

	json.dump(data, response, ensure_ascii = False, indent=4)

	return response


def uploadStats(request):

	file_name = request.session['file_name']
	current_date = str(datetime.date.today())
	name = f'{file_name}{current_date}.csv'

	response = HttpResponse(
		content_type='text/csv',
		headers={'Content-Disposition': f'attachment; filename="{name}"'},
	)

	global_file = request.session['global_file']
	global_file = json.loads(global_file)
	global_file = pd.DataFrame(global_file)

	writer = csv.writer(response)
	writer.writerow(['Uploaded ASIN', 'Parent Asin', 'Child Asin', 'Asin Available'])

	csv_data = []
	for asin in global_file['ASIN']:
		data_lst = []

		data_lst.append(asin)

		parent_asin = variationSettings.objects.filter(current_asin=asin) or variationSettings.objects.filter(parent_asin=asin)
		if parent_asin:
			variation_asins = variationSettings.objects.filter(productID=parent_asin[0].productID)

			for vari in variation_asins:
				data_lst = []
				data_lst.append(asin)
				data_lst.append(vari.parent_asin)
				data_lst.append(vari.current_asin)
				data_lst.append(True)

				csv_data.append(data_lst)

		else:
			single_asin = productPagesScrapper.objects.filter(Q(productID=asin, description_en=True, description_ar=True) | Q(productID=asin, description_en=True, source__in=('amazon.in','amazon.co.uk','amazon.com.au','amazon.com')))
			data_lst = []

			if single_asin:
				data_lst.append(single_asin[0].productID)
				data_lst.append(single_asin[0].productID)
				data_lst.append(single_asin[0].productID)
				data_lst.append(True)

			else:
				data_lst.append(asin)
				data_lst.append(asin)
				data_lst.append(asin)
				data_lst.append(False)

			csv_data.append(data_lst)


	writer.writerows(csv_data)

	return response

def exportExcel(request):

	global_file = request.session['global_file']
	global_file = json.loads(global_file)
	global_file = pd.DataFrame(global_file)

	# Avoid Repeating Products
	check_dict = {i.parent_asin:item for item in global_file['ASIN'] for i in variationSettings.objects.filter(current_asin=item)}
	no_vari_list = [i for i in global_file['ASIN'] if not variationSettings.objects.filter(current_asin=i).exists()]
	check_list = set(list(check_dict.values()) + no_vari_list)

	current_date = str(datetime.date.today())
	name = current_date+'_Excel.xlsx'

	workbook = xlsxwriter.Workbook(f'static/docs/excels/{name}')

	worksheet = workbook.add_worksheet('family')

	# Formating
	bold = workbook.add_format({'bold': True, 'color':'black','font':'20','border':True, 'align':'center'})


	# Single Product Headings
	headings = [
		'Provided Asin', 
		'Category', 
		'Weight Class', 
		'Brand', 
		'Title', 
		'Title Arabic', 
		'Market Price', 
		'Description', 
		'Description Arabic', 
		'GTIN', 
		'EAN', 
		'UPC',
		'Parent Asin',
		'Images',
	]

	worksheet.set_column('A:D', 20)
	worksheet.set_row(0, 20)
	worksheet.set_column('E:AC', 30)
	worksheet.merge_range('O1:P1', 'Category Attributes', bold)
	worksheet.merge_range('Q1:R1', 'Category Attributes Arabic', bold)
	worksheet.merge_range('S1:T1', 'Variation Settings', bold)
	worksheet.merge_range('U1:V1', 'Variation Settings Arabic', bold)
	worksheet.merge_range('W1:AC1', 'Variations', bold)

	worksheet.write_row(0,0,headings,bold)
	worksheet.write_row(1,14,['key','value'],bold)
	worksheet.write_row(1,16,['key','value'],bold)
	worksheet.write_row(1,18,['Name','Values'],bold)
	worksheet.write_row(1,20,['Name','Values'],bold)
	worksheet.write_row(1,22,['Index', 'Variation', 'Asin', 'Title', 'Title Arabic', 'Market Price', 'Images (Comma Seprated)'],bold)

	worksheet.freeze_panes(1, 1)
	data = []

	# Formulating export format
	for weight,grades_provided,category,item in zip(global_file['weight_class'],global_file['Conditions'],global_file['Category'],global_file['ASIN']):

		if item in check_list:
			data_list = excelFormating(weight_class=weight, conditions=grades_provided, category=category, asin=item)

			data.append(data_list)
	row = 2
	row_len = 0
	for asin_data in data:
		for col, d in enumerate(asin_data):
			worksheet.write_column(row, col, d)
			if len(d) > row_len:
				row_len = len(d)
		row += row_len
	
	workbook.close()
	return redirect(f"http://{request.META['HTTP_HOST']}/static/docs/excels/{name}")