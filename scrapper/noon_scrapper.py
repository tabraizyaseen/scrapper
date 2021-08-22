import requests
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import io
import random
import json

import datetime
from django.utils import timezone

from .models import productPagesScrapper


def soupParser(link):

	try:

		session = requests.Session()
		session.mount('https://www.noon.com', HTTPAdapter(max_retries=10))

		HEADERS =[{
			'authority': 'www.noon.com',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer' : 'https://www.noon.com/'
		},{
			'authority': 'www.noon.com',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer' : 'https://www.google.com/'
		},{
			'authority': 'www.noon.com',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer' : 'https://www.noon.com/'
		},{
			'authority': 'www.noon.com',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer' : 'https://www.google.com/'
		}]


		proxies = [{ 
			"http": "http://10.10.10.10:8000"
		},{
			"http": "http://195.169.35.228"
		},{
			"http": "http://209.97.150.167"
		},{
			"http": "http://198.199.86.11"
		},{
			"http": "http://45.159.23.198"
		},{
			"http": "http://191.101.39.191"
		},{
			"http": "http://139.99.105.185"
		},{
			"http": "http://139.99.102.114"
		},{
			"http": "http://185.198.188.50"
		},{
			"http": "http://185.198.188.55"
		},{
			"http": "http://118.69.219.185"
		},{
			"http": "http://127.0.0.1"
		},{
			"http": "http://50.192.195.69"
		},{
			"http": "http://89.187.177.91"
		},{
			"http": "http://192.168.0.179"
		},{
			"http": "http://139.59.1.14"
		},{
			"http": "http://103.240.77.98"
		},{
			"http": "http://58.69.161.161"
		},{
			"http": "http://103.197.49.165"
		},{
			"http": "http://103.15.140.140"
		}]

		session.proxies.update(random.choice(proxies))
		session.headers.update(random.choice(HEADERS))

		response = session.get(link, stream=True)
		soup = BeautifulSoup(response.text, 'html.parser')

		return soup, response

	except RequestException:
		response = None
		soup = None

		return soup, response

# Noon url noon crawler
def noonCategoryScrapper(url):

	def extracting(each):

		p_id = each['sku']
		title = each['name']

		price = each['sale_price']

		if price:
			old_price = each['price']
		else:
			price = each['price']
			old_price = None

		price = each['sale_price']

		if price:
		    price = str(int(price))
		    old_price = str(int(each['price']))
		else:
		    price = str(int(each['price']))
		    old_price = None


		return p_id, title, price, old_price

	def pageParser(soup):

		json_data = soup.find('script',{'id':'__NEXT_DATA__'})
		json_format = json_data.contents[0]
		data_json = json.loads(json_format)
		containers = data_json['props']['pageProps']['catalog']['hits']

		for each in containers:
			p_id, title, price, old_price = extracting(each)
			if not productPagesScrapper.objects.filter(productID=p_id).exists():
				productPagesScrapper.objects.create(productID=p_id, title_en=title, price=price, old_price=old_price, source='noon.com')
			else:
				productPagesScrapper.objects.filter(productID=p_id).update(title_en=title, price=price, old_price=old_price, source='noon.com')


	if '?' in url:
		url = url + '&page={}'
	else:
		url = url + '?page={}'

	soup, response = soupParser(url.format(1))

	if soup:
	
		# Last Page 
		try:
			last_page_div = soup.find('div','jTPOKY')
			last_page = int(last_page_div.ul.find_all('a','pageLink')[-1].text)
		except AttributeError:
			try:
				soup, response = soupParser(url.format(1))
				last_page_div = soup.find('div','jTPOKY')
				last_page = int(last_page_div.ul.find_all('a','pageLink')[-1].text)
			except Exception:
				last_page = 0

		if last_page > 50:
			for page in range(1, 51):

				soup, response = soupParser(url.format(page))

				if soup:

					pageParser(soup)
				else:
					pass

				print(page)
		elif last_page > 0 and last_page < 50:
			for page in range(1, last_page+1):

				soup, response = soupParser(url.format(page))

				if soup:

					pageParser(soup)
				else:
					pass

				print(page)

		else:

			pageParser(soup)
	else:
		pass

# Product Response Saving in English
def noonProductServerResponse(product):
	
	def dataParser(product_json):

		# Title
		title = product_json['product_title']

		# Asins
		Asins = []
		# Available Asins
		Asins = []
		groups = product_json['groups']
		for group in groups:
			options = group['options']
			for option in options:
				Asins.append(option['sku'])

		# Category
		category = ""
		breadcrumbs = product_json['breadcrumbs']
		for breadcrumb in breadcrumbs:
			category += f"{breadcrumb['name']} > "
		category = category[:-3]

		return title, category, Asins

	def titleParser(product_json):
		# Title
		title = product_json['product_title']

		# Category
		category = ""
		breadcrumbs = product_json['breadcrumbs']
		for breadcrumb in breadcrumbs:
			category += f"{breadcrumb['name']} > "
		category = category[:-3]

		return title, category
	
	soup, response = soupParser(f'https://www.noon.com/uae-en/{product.productID}/p')

	if soup:

		# Valid Check
		valid = False
		try:
			json_data = soup.find('script',{'id':'__NEXT_DATA__'})
			json_format = json_data.contents[0]
			data_json = json.loads(json_format)
			product_json = data_json['props']['pageProps']['catalog']['product']
			valid = True
		except AttributeError:
			pass

		if valid:
			title, category, Asins = dataParser(product_json)

			# Writing File
			with io.open(f'static/docs/productPages/EN_{product.productID}.txt', 'w', encoding='UTF-8') as responseFile:
				responseFile.writelines(response.text)
				productPagesScrapper.objects.filter(id=product.id).update(
					category=category,
					title_en=title,
					description_en=valid,
					last_checked = timezone.now(),
				)

			for asin in Asins:

				if asin:

					if not productPagesScrapper.objects.filter(productID=asin).exists():

						soup, response = soupParser(f'https://www.noon.com/uae-en/{asin}/p')

						if soup:

							# Valid Check
							try:
								json_data = soup.find('script',{'id':'__NEXT_DATA__'})
								json_format = json_data.contents[0]
								data_json = json.loads(json_format)
								product_json = data_json['props']['pageProps']['catalog']['product']

								title, category = titleParser(product_json)

								# Writing File
								with io.open(f'static/docs/productPages/EN_{asin}.txt', 'w', encoding='UTF-8') as responseFile:
									responseFile.writelines(response.text)
									productPagesScrapper.objects.create(
										category=category,
										productID=asin,
										title_en=title,
										description_en=True,
										source='noon.com',
									)

							except AttributeError:

								# Saving that sku
								productPagesScrapper.objects.create(productID=asin)

						else:
							pass

	else:
		pass

# Product Specifications and Images
# def noonProductDetails(product):
class NoonProductDetails:

	def __init__(self, product):

		# Reading File
		with io.open(f'static/docs/productPages/EN_{product.productID}.txt', 'r', encoding='UTF-8') as html_file:
			soup = BeautifulSoup(html_file.read(), 'html.parser')

			try:
				json_data = soup.find('script',{'id':'__NEXT_DATA__'})
				json_format = json_data.contents[0]
				data_json = json.loads(json_format)
				product_json = data_json['props']['pageProps']['catalog']['product']
			except Exception as e:
				productPagesScrapper.objects.filter(id=product.id).update(
					description_en=False,
					last_checked = timezone.now(),
				)
				print(e)

		self.product = product
		self.product_json = product_json

	def price(self):

		product_json = self.product_json

		try:
			price = product_json['variants'][0]['offers'][0]['sale_price']
			if price:
				price = str(int(price))
			else:
				price = str(int(product_json['variants'][0]['offers'][0]['price']))
		except Exception:
			price = None

		return price

	def old_price(self):

		product_json = self.product_json

		try:
			price = product_json['variants'][0]['offers'][0]['sale_price']
			if price:
				old_price = str(int(product_json['variants'][0]['offers'][0]['price']))
			else:
				old_price = None

		except Exception:
			old_price = None

		return old_price

	def Brand(self):

		product_json = self.product_json
		brand = product_json['brand']

		return brand

	def Specifications(self):

		# Initializing Lists
		specifications = []
		product_json = self.product_json
		product = self.product

		# Brand
		brand = product_json['brand']
		if brand:
			specifications.append(('Brand', brand))

		# Specifications
		specs = product_json['specifications']
		for spec in specs:
			keys = spec['name']
			values = spec['value']
			specifications.append((keys,values))
		specifications.append(('product SKU',product.productID))

		return specifications

	def Highlights(self):
		# Initialization
		highlights = []
		product_json = self.product_json

		# Highlights
		highlights = product_json['feature_bullets']

		return highlights

	def ProductDescription(self):

		product_json = self.product_json

		long_description = product_json['long_description']

		return long_description

	def ImagesList(self):
		# Initialization
		images_lst = []
		product_json = self.product_json
		product = self.product

		# Images
		try:
			images = product_json['image_keys']
			for image in images:
				images_lst.append(f'https://k.nooncdn.com/t_desktop-pdp-v1/{image}.jpg')

		except Exception as e:
			productPagesScrapper.objects.filter(id=product.id).update(
				description_en=False,
				last_checked = timezone.now(),
			)

		return images_lst

# Product Specifications and Images
class NoonProductDetailsArabic:

	def __init__(self, product):

		# Reading File
		with io.open(f'static/docs/productPages/AR_{product.productID}.txt', 'r', encoding='UTF-8') as html_file:
			soup = BeautifulSoup(html_file.read(), 'html.parser')

			try:
				json_data = soup.find('script',{'id':'__NEXT_DATA__'})
				json_format = json_data.contents[0]
				data_json = json.loads(json_format)
				product_json = data_json['props']['pageProps']['catalog']['product']
			except Exception as e:
				productPagesScrapper.objects.filter(id=product.id).update(
					description_ar=False,
					last_checked = timezone.now(),
				)
				print(e)

		self.product = product
		self.product_json = product_json

	def Brand(self):

		product_json = self.product_json
		brand = product_json['brand']

		return brand

	def Specifications(self):

		# Initializing Lists
		specifications = []
		product_json = self.product_json
		product = self.product

		# Brand
		brand = product_json['brand']
		if brand:
			specifications.append(('Brand', brand))

		# Specifications
		specs = product_json['specifications']
		for spec in specs:
			keys = spec['name']
			values = spec['value']
			specifications.append((keys,values))
		specifications.append(('product SKU',product.productID))

		return specifications

	def Highlights(self):
		# Initialization
		highlights = []
		product_json = self.product_json

		# Highlights
		highlights = product_json['feature_bullets']

		return highlights

	def ProductDescription(self):

		product_json = self.product_json

		long_description = product_json['long_description']

		return long_description


# If file data is not valid
def noonResponseValidate(productResponse):

	soup, response = soupParser(f'https://www.noon.com/uae-en/{productResponse.productID}/p')

	if soup:

		# Valid Check
		try:
			json_data = soup.find('script',{'id':'__NEXT_DATA__'})
			json_format = json_data.contents[0]
			data_json = json.loads(json_format)

			# Title
			title = data_json['props']['pageProps']['catalog']['product']['product_title']

			# Category
			category = ""
			breadcrumbs = data_json['props']['pageProps']['catalog']['product']['breadcrumbs']
			for breadcrumb in breadcrumbs:
				category += f"{breadcrumb['name']} > "
			category = category[:-3]

			# Writing File
			with io.open(f'static/docs/productPages/EN_{productResponse.productID}.txt', 'w', encoding='UTF-8') as responseFile:

				responseFile.writelines(response.text)

				productPagesScrapper.objects.filter(id=productResponse.id).update(
					category=category,
					description_en=True,
					title_en=title,
					last_checked = timezone.now(),
				)

		except Exception as e:
			print(e)
	else:
		pass

# Product Response Saving in Arabic
def noonResponseValidateArabic(product):
	
	soup, response = soupParser(f'https://www.noon.com/uae-ar/{product.productID}/p')

	if soup:

		# Valid Check
		try:
			json_data = soup.find('script',{'id':'__NEXT_DATA__'})
			json_format = json_data.contents[0]
			data_json = json.loads(json_format)

			# Title
			title = data_json['props']['pageProps']['catalog']['product']['product_title']

			# Writing File
			with io.open(f'static/docs/productPages/AR_{product.productID}.txt', 'w', encoding='UTF-8') as responseFile:
				responseFile.writelines(response.text)
				productPagesScrapper.objects.filter(id=product.id).update(
					title_ar=title,
					description_ar=True,
					last_checked = timezone.now(),
				)

		except Exception as e:
			print(e)

	else:
		pass