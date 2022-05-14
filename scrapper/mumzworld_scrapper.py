import requests
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
import random
from bs4 import BeautifulSoup
import io
from django.utils import timezone

from .models import productPagesScrapper

def soupParser(link):

	try:

		session = requests.Session()
		session.mount('https://www.mumzworld.com', HTTPAdapter(max_retries=10))

		HEADERS = [{
			'authority': 'www.mumzworld.com',
			'method': 'GET',
			'scheme': 'https',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'Connection': 'keep-alive',
			'Accept-Encoding': 'gzip, deflate, br',
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer': 'https://www.mumzworld.com/'
		}, {
			'authority': 'www.mumzworld.com',
			'method': 'GET',
			'scheme': 'https',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'Connection': 'keep-alive',
			'Accept-Encoding': 'gzip, deflate, br',
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 15_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer': 'https://www.google.com/'
		}, {
			'authority': 'www.mumzworld.com',
			'method': 'GET',
			'scheme': 'https',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'Connection': 'keep-alive',
			'Accept-Encoding': 'gzip, deflate, br',
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.30',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer': 'https://www.mumzworld.com/'
		}, {
			'authority': 'www.mumzworld.com',
			'method': 'GET',
			'scheme': 'https',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'Connection': 'keep-alive',
			'Accept-Encoding': 'gzip, deflate, br',
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer': 'https://www.google.com/'
		},{
			'authority': 'www.mumzworld.com',
			'method': 'GET',
			'scheme': 'https',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'Connection': 'keep-alive',
			'Accept-Encoding': 'gzip, deflate, br',
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer': 'https://www.google.com/'
		}]

		proxies = [
			{'HTTP': 'HTTP://185.181.166.209:8080'},
			{'HTTPS': 'HTTPS://181.129.43.3:8080'},
			{'HTTP': 'HTTP://45.70.198.195:999'},
			{'HTTP': 'HTTP://103.101.17.170:8080'},
			{'HTTP': 'HTTP://181.10.171.234:8080'},
			{'HTTP': 'HTTP://92.60.26.58:8089'},
			{'HTTPS': 'HTTPS://92.249.122.108:61778'},
			{'HTTPS': 'HTTPS://91.92.94.69:41890'},
			{'HTTPS': 'HTTPS://85.234.126.107:55555'},
			{'HTTPS': 'HTTPS://116.105.87.134:3128'},
			{'HTTP': 'HTTP://190.103.74.236:999'},
			{'HTTPS': 'HTTPS://46.35.249.189:41419'},
			{'HTTP': 'HTTP://45.116.229.183:8080'},
			{'HTTP': 'HTTP://46.147.110.7:8080'},
			{'HTTP': 'HTTP://98.154.21.253:3128'},
			{'HTTP': 'HTTP://170.254.230.201:999'},
			{'HTTPS': 'HTTPS://177.136.84.164:999'},
			{'HTTP': 'HTTP://34.208.39.27:3128'},
			{'HTTP': 'HTTP://195.97.124.164:8080'},
			{'HTTP': 'HTTP://80.66.81.35:53281'},
			{'HTTP': 'HTTP://170.79.235.3:999'},
			{'HTTP': 'HTTP://82.114.97.157:1256'},
			{'HTTPS': 'HTTPS://178.151.205.154:45099'},
			{'HTTPS': 'HTTPS://125.25.206.28:8080'},
			{'HTTPS': 'HTTPS://203.150.113.190:57322'},
			{'HTTP': 'HTTP://77.70.35.87:37475'},
			{'HTTPS': 'HTTPS://187.189.132.173:999'},
		]

		session.proxies.update(random.choice(proxies))
		session.headers.update(random.choice(HEADERS))

		response = session.get(link, stream=True)

		if response.status_code == 200:
			soup = BeautifulSoup(response.text, 'lxml')
			return response, soup

		response, soup = None, None
		return response, soup

	except RequestException:
		response, soup = None, None

		return response, soup

# Product Specifications and Images
class mumzProductDetailsEN:

	def __init__(self, product):

		# Reading File
		with io.open(f'static/docs/productPages/EN_{product.productID}.txt', 'r', encoding='UTF-8') as html_file:
			soup = BeautifulSoup(html_file.read(), 'html.parser')

		self.product = product
		self.soup = soup

		feature_tag = soup.find('div',{'id':'full-desc'})
		self.feature_tag = feature_tag

	def price(self):

		soup = self.soup

		# current price
		try:
			price = soup.find('div','special-price').text.strip().split('\n')[-1].replace(',','')
		except AttributeError:
			try:
				price = soup.find('div','regular-price').text.strip().split('\n')[-1].replace(',','')
			except AttributeError:
				price = 0.0
		
		return price

	def old_price(self):

		soup = self.soup

		# Old Price
		try:
			old_price = soup.find('div','old-price').text.strip().split('\n')[-1].replace(',','')
		except AttributeError:
			old_price = 0.0

		return old_price

	# To retrieve only brands
	def Brand(self):
		soup = self.soup

		# Brand
		try:
			brand = soup.find('a','see_all_prd icon-arrowright font-book pos-rel').text.strip().replace('See all products from  ','')
		except AttributeError:
			brand = ''

		return brand

	def Highlights(self):

		# Highlights
		highlights = []
		feature_tag = self.feature_tag

		# Highlights
		try:
			highlights = []
			highlights_tag = feature_tag.find('div','desc_divider')

			for li_tag in highlights_tag.find_all('li'):
				if li_tag.text:
					highlights.append(li_tag.text)
		except Exception as e:
			print('No Highlights ',e)

		return highlights

	# Product Description
	def ProductDescription(self):

		# Initializing
		highlights = self.Highlights()
		feature_tag = self.feature_tag

		# Product Description
		try:
			desc = feature_tag.find_all('div','col-sm-6')[0]
			if highlights:
				desc.div.decompose()
			desc.strong.decompose()

			long_descriptionEN = desc.text
			
		except Exception as E:
			print(E)
			long_descriptionEN = ''

		return long_descriptionEN


	def Specifications(self):
			
		# Initializes Specifications List
		specifications = []
		
		product = self.product
		feature_tag = self.feature_tag

		try:
			cat_attributes = feature_tag.find_all('div','col-sm-6')[-1]

			for single in cat_attributes.find_all('strong','overvw_label'):
				value = single.next_sibling.strip()
				if value:
					specifications.append((single.text.strip(), value))
			
		except Exception as e:
			print('No specifications >>>',e)
		
		if not 'URL_SLUGIFY' in str(specifications):
				specifications.append(('URL_SLUGIFY',product.productID))
		
		brand = self.Brand()
		if brand and not ("'Brand'," in str(specifications)):
			specifications.insert(0,('Brand',brand))
			

		return specifications

	
	def ImagesList(self):	

		soup = self.soup

		images_list = []
		try:
			all_images = soup.find_all('a',{'class':'fancybox_img', 'rel':'gallery_fancy'})
			for imgs in all_images:
				img = imgs.get('href')
				if img not in images_list:
					images_list.append(img)
		except Exception as e:
			print('Why Images not scrapped >>> ',e)

		return images_list


# Product Specifications and Images Arabic
class mumzProductDetailsAR:

	def __init__(self, product):

		# Reading File
		with io.open(f'static/docs/productPages/AR_{product.productID}.txt', 'r', encoding='UTF-8') as html_file:
			soup = BeautifulSoup(html_file.read(), 'html.parser')

		self.product = product
		self.soup = soup

		feature_tag = soup.find('div',{'id':'full-desc'})
		self.feature_tag = feature_tag

	# To retrieve only brands
	def Brand(self):
		soup = self.soup

		# Brand
		try:
			brand = soup.find('a','see_all_prd icon-arrowright font-book pos-rel').text.strip().replace('عرض جميع منتجات ','')
		except AttributeError:
			brand = ''

		return brand

	def Highlights(self):

		# Highlights
		highlights = []
		feature_tag = self.feature_tag

		# Highlights
		try:
			highlights = []
			highlights_tag = feature_tag.find('div','desc_divider')

			for li_tag in highlights_tag.find_all('li'):
				if li_tag.text:
					highlights.append(li_tag.text)
		except Exception as e:
			print('No Highlights ',e)

		return highlights

	# Product Description
	def ProductDescription(self):

		# Initializing
		highlights = self.Highlights()
		feature_tag = self.feature_tag

		# Product Description
		try:
			desc = feature_tag.find_all('div','col-sm-6')[0]
			if highlights:
				desc.div.decompose()
			desc.strong.decompose()

			long_descriptionEN = desc.text
			
		except Exception as E:
			print(E)
			long_descriptionEN = ''

		return long_descriptionEN


	def Specifications(self):
			
		# Initializes Specifications List
		specifications_list = []
		
		product = self.product
		feature_tag = self.feature_tag

		try:
			cat_attributes = feature_tag.find_all('div','col-sm-6')[-1]

			for single in cat_attributes.find_all('strong','overvw_label'):
				value = single.next_sibling.strip()
				if value:
					specifications_list.append((single.text.strip(), value))
			
		except Exception as e:
			print('No specifications >>>',e)
		
		if not 'URL_SLUGIFY' in str(specifications_list):
				specifications_list.append(('URL_SLUGIFY',product.productID))
		
		brand = self.Brand()
		if brand and not ("'Brand'," in str(specifications_list)):
			specifications_list.insert(0,('Brand',brand))
			

		return specifications_list


def mumzResponseValidate(productResponse):

	def titleParser(soup):

		# Intializting
		title = ''
		valid = False

		# Title
		try:
			title = soup.find('h1','mtop0').text
			valid = True
		except AttributeError as e:
			print('error', e)

		# No Category at Display

		return title, valid

	response, soup = soupParser(f'https://www.mumzworld.com/en/{productResponse.productID}')

	if soup:

		title, valid = titleParser(soup)

		# Writing File
		if valid:
			with io.open(f'static/docs/productPages/EN_{productResponse.productID}.txt', 'w', encoding='UTF-8') as responseFile:

				responseFile.writelines(response.text)

				productPagesScrapper.objects.filter(id=productResponse.id).update(
					description_en=valid,
					title_en=title,
					last_checked = timezone.now(),
					source = "mumzworld.com",
				)

def mumzResponseValidateArabic(productResponse):

	# For Arabic title validation
	response, soup = soupParser(f'https://www.mumzworld.com/ar/{productResponse.productID}')

	if soup:

		valid = False
		try:
			# Finding title
			title = soup.find('h1','mtop0').text
			valid = True
		except AttributeError:
			title = ''

		# Writing File
		with io.open(f'static/docs/productPages/AR_{productResponse.productID}.txt', 'w', encoding='UTF-8') as responseFile:

			responseFile.writelines(response.text)
			productPagesScrapper.objects.filter(id=productResponse.id).update(
				description_ar=valid,
				title_ar=title,
				last_checked = timezone.now(),
				source='mumzworld.com',
			)

	