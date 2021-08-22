import requests
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup, SoupStrainer
import random
import io
import json
import re
from time import sleep

import datetime
from django.utils import timezone

from .models import *


class VariationsSoup():

	def __init__(self,item):

		print("I'm the one : ",item)

		# Tag to parse
		only_tags = SoupStrainer('script',{'type':'text/javascript'})

		# Reading English File
		with io.open(f'static/docs/productPages/EN_{item}.txt', 'r', encoding='UTF-8') as html_file:
			soup = BeautifulSoup(html_file.read(), 'lxml', parse_only=only_tags)

			try:
				pattern = re.compile(r"P\.register\('twister-js-init-dpx-data', function\(\) \{")
				soup_en = soup.find('script',string=pattern).contents[0]
			except AttributeError:
				soup_en = ''

		# Reading Arabic File
		with io.open(f'static/docs/productPages/AR_{item}.txt', 'r', encoding='UTF-8') as html_file:
			soup = BeautifulSoup(html_file.read(), 'lxml', parse_only=only_tags)
			try:
				pattern = re.compile(r"P\.register\('twister-js-init-dpx-data', function\(\) \{")
				soup_ar = soup.find('script',string=pattern).contents[0]
			except AttributeError:
				soup_ar = ''

		self.soup_en = soup_en
		self.soup_ar = soup_ar

	
	# "currentAsin" : "B08L5NLF53"
	def CurrentAsin(self):
		javascript_tag = self.soup_en

		if javascript_tag:
			crnt_st = javascript_tag.find('"currentAsin"')+16
			crnt_end = javascript_tag.find(',\n"parentAsin"')
			crnt_asin = json.loads(javascript_tag[crnt_st:crnt_end])

			return crnt_asin


	# 'Parent Asin': 'B08SDP1RJR'
	def ParentAsin(self):
		javascript_tag = self.soup_en

		if javascript_tag:

			prt_st = javascript_tag.find('"parentAsin"')+15
			prt_end = javascript_tag.find(',\n"dimensionToAsinMap"')
			prt_asin = json.loads(javascript_tag[prt_st:prt_end])

			return prt_asin

	# 'configuration': ['64 GB', '128 GB', '256 GB']
	def TotalVariation(self):
		javascript_tag = self.soup_en

		if javascript_tag:
			val_start = javascript_tag.find('"variationValues"')+20
			variationValues = javascript_tag[val_start:].split('\n')[0][:-1]
			variations = json.loads(variationValues)

			return variations

	# 'configuration': ['64 GB', '128 GB', '256 GB']
	def TotalVariationAR(self):
		javascript_tag = self.soup_ar

		if javascript_tag:
			val_start = javascript_tag.find('"variationValues"')+20
			variationValues = javascript_tag[val_start:].split('\n')[0][:-1]
			variations = json.loads(variationValues)

			return variations

	# 'B08L5RJ392': ['International Version', '(PRODUCT)RED', '128 GB']
	def DimensionsDetails(self):
		javascript_tag = self.soup_en

		if javascript_tag:
			dimstr_str = javascript_tag.find('"dimensionValuesDisplayData"')+31
			dimstr_end = javascript_tag.find(',\n"pwASINs"')
			dimstr = json.loads(javascript_tag[dimstr_str:dimstr_end])
			print(len(dimstr))

			return dimstr

	# 'B08L5RJ392': ['International Version', '(PRODUCT)RED', '128 GB']
	def DimensionsDetailsAR(self):
		javascript_tag = self.soup_ar

		if javascript_tag:
			dimstr_str = javascript_tag.find('"dimensionValuesDisplayData"')+31
			dimstr_end = javascript_tag.find(',\n"pwASINs"')
			dimstr = json.loads(javascript_tag[dimstr_str:dimstr_end])
			print(len(dimstr))

			return dimstr

	# '0_0_0': 'B08L5RJ392'
	def Dimensions(self):

		javascript_tag = self.soup_en

		if javascript_tag:
			dim_st = javascript_tag.find('"dimensionToAsinMap"')+23
			dim_end =javascript_tag.find(',\n"variationValues"')
			dimenstions = json.loads(javascript_tag[dim_st:dim_end])

			return dimenstions

	# '0_0_0': 'B08L5RJ392'
	def DimensionsAR(self):

		javascript_tag = self.soup_ar

		if javascript_tag:
			dim_st = javascript_tag.find('"dimensionToAsinMap"')+23
			dim_end =javascript_tag.find(',\n"variationValues"')
			dimenstions = json.loads(javascript_tag[dim_st:dim_end])

			return dimenstions


class varienceDetail():

	def __init__(self,item):

		self.item = item

		# Reading English File
		with io.open(f'static/docs/productPages/EN_{item.current_asin}.txt', 'r', encoding='UTF-8') as html_file:
			self.html_file = html_file.read()

		# Reading Arabic File
		with io.open(f'static/docs/productPages/AR_{item.current_asin}.txt', 'r', encoding='UTF-8') as html_file:
			self.html_file_ar = html_file.read()

	def price(self):

		html_file = self.html_file
		price_only = SoupStrainer('div' , {'id':'price'})
		soup = BeautifulSoup(html_file, 'lxml', parse_only=price_only)

		try:
			price = soup.find('span',{'id':'priceblock_ourprice'}).text.split('\xa0')[-1].split('.')[0].replace(',','')
		except Exception:
			try:
				price = soup.find('span',{'id':'priceblock_dealprice'}).text.split('\xa0')[-1].split('.')[0].replace(',','')
			except Exception:
				price = ''

		return price

	def old_price(self):

		html_file = self.html_file
		price_only = SoupStrainer('div' , {'id':'price'})
		soup = BeautifulSoup(html_file, 'lxml', parse_only=price_only)
		
		try:
			old_price = soup.find('span','priceBlockStrikePriceString').text.strip().split('\xa0')[-1].split('.')[0].replace(',','')
		except Exception:
			old_price = ''

		return old_price

	def titleParser(self):

		html_file = self.html_file
		item = self.item

		title_only = SoupStrainer('span' , {'id':'productTitle'})
		soup = BeautifulSoup(html_file, 'lxml', parse_only=title_only)

		# Initialization
		title = ''
		
		try:
			title = soup.find('span', {'id': 'productTitle'}).text.strip().split('】')[-1].split('𝐆𝐢𝐟𝐭 ')[-1]

		except AttributeError:

			variationSettings.objects.filter(current_asin=item.current_asin).update(
					description_en=False
				)

		return title

	def titleParserAR(self):

		html_file = self.html_file_ar
		item = self.item

		title_only = SoupStrainer('span' , {'id':'productTitle'})
		soup = BeautifulSoup(html_file, 'lxml', parse_only=title_only)

		# Initialization
		title = ''
		
		try:
			title = soup.find('span', {'id': 'productTitle'}).text.strip().split('】')[-1].split('𝐆𝐢𝐟𝐭 ')[-1]

		except AttributeError:

			variationSettings.objects.filter(current_asin=item.current_asin).update(
					description_ar=False
				)

		return title

	def allImages(self):

		html_file = self.html_file
		item = self.item

		scripts_only = SoupStrainer('script' , {'type':'text/javascript'})
		soup = BeautifulSoup(html_file, 'lxml', parse_only=scripts_only)

		try:

			# JavaScript Tag for images
			pattern = re.compile(r"P\.when\('A'\)\.register\(\"ImageBlockATF\", function\(A\)\{")
			javascript_img = soup.find('script',string=pattern).contents[0]

			# All images
			strt = javascript_img.find("'colorImages\':")+15
			start2 = javascript_img[strt:].find("'initial\': ")+11+strt
			end = javascript_img.find("},\n\'colorToAsin\'")
			all_imgs = json.loads(javascript_img[start2:end])

			all_image = [imgs['hiRes'] if imgs['hiRes'] else imgs['large'] for imgs in all_imgs]

			all_images = ','.join(all_image)

		except Exception:

		    # All Book Images
		    strt = javascript_img.find("'imageGalleryData'")+20
		    end = javascript_img.find(",\n\'centerColMargin\'")
		    all_imgs = json.loads(javascript_img[strt:end])
		    all_image = [imgs['mainUrl'] for imgs in all_imgs if imgs['mainUrl']]

		    all_images = ','.join(all_image)

		return all_images


class Variant():

	def __init__(self, item):

		self.item = item


	def soupParser(self, link):

		try:

			session = requests.Session()
			session.mount('https://www.amazon.ae', HTTPAdapter(max_retries=10))

			HEADERS = [{
				'authority': 'www.amazon.ae',
				'pragma': 'no-cache',
				'cache-control': 'no-cache',
				'dnt': '1',
				'upgrade-insecure-requests': '1',
				'accept': '*/*',
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
				'sec-fetch-site': 'none',
				'sec-fetch-mode': 'navigate',
				'sec-fetch-dest': 'document',
				'referer': 'https://www.amazon.ae/'
			}, {
				'authority': 'www.amazon.ae',
				'pragma': 'no-cache',
				'cache-control': 'no-cache',
				'dnt': '1',
				'upgrade-insecure-requests': '1',
				'accept': '*/*',
				'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4',
				'sec-fetch-site': 'none',
				'sec-fetch-mode': 'navigate',
				'sec-fetch-dest': 'document',
				'referer': 'https://www.google.com/'
			}, {
				'authority': 'www.amazon.ae',
				'pragma': 'no-cache',
				'cache-control': 'no-cache',
				'dnt': '1',
				'upgrade-insecure-requests': '1',
				'accept': '*/*',
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
				'sec-fetch-site': 'none',
				'sec-fetch-mode': 'navigate',
				'sec-fetch-dest': 'document',
				'referer': 'https://www.amazon.ae/'
			}, {
				'authority': 'www.amazon.ae',
				'pragma': 'no-cache',
				'cache-control': 'no-cache',
				'dnt': '1',
				'upgrade-insecure-requests': '1',
				'accept': '*/*',
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
				'sec-fetch-site': 'none',
				'sec-fetch-mode': 'navigate',
				'sec-fetch-dest': 'document',
				'referer': 'https://www.google.com/'
			}]

			proxies = [
				{'http': 'http://151.253.165.70:8080'},
				{'http': 'http://185.106.121.176:9050'},
				{'http': 'http://193.223.100.81:1080'},
				{'http': 'http://217.138.193.62:1080'},
				{'http': 'http://20.46.192.92:9300'},
				{'http': 'http://178.80.156.227:8080'},
				{'http': 'http://5.42.224.18:8080'},
				{'http': 'http://2.88.5.196:8080'},
				{'http': 'http://37.104.112.202:8080'},
				{'http': 'http://37.56.37.130:8080'},
				{'http': 'http://177.11.84.254:8080'},
				{'http': 'http://202.29.237.211:3128'},
				{'http': 'http://167.99.131.11:80'},
				{'http': 'http://178.72.74.40:31372'},
				{'http': 'http://1.32.59.217:47045'},
				{'http': 'http://112.78.162.208:8080'},
				{'http': 'http://95.208.208.233:8080'},
				{'http': 'http://5.252.161.48:8080'},
				{'http': 'http://79.120.177.106:8080'},
				{'http': 'http://218.88.204.136:3256'},
			]

			session.proxies.update(random.choice(proxies))
			session.headers.update(random.choice(HEADERS))

			response = session.get(link, stream=True)

			return response

		except RequestException:
			response = None

			return response

		
	def saveResponse(self):

		item = self.item
		title_only = SoupStrainer(['script',{'type':'text/javascript'}, 'span' , {'id':'productTitle'}])

		print("From Save Response Current Asin : ",item.current_asin)

		# English response
		response = self.soupParser(f'https://www.amazon.ae/-/en/dp/{item.current_asin}')
		if response:

			soup_en = BeautifulSoup(response.text, 'lxml', parse_only=title_only)

			title_en = ''

			# English validate check
			try:

				title_en = soup_en.find('span', {'id': 'productTitle'}).text.strip().split('】')[-1].split('𝐆𝐢𝐟𝐭 ')[-1]

				# JavaScript Tag
				pattern = re.compile(r"P\.register\('twister-js-init-dpx-data', function\(\) \{")
				javascript_tag = soup_en.find('script',string=pattern).contents[0]

				# "currentAsin" : "B08L5NLF53"
				crnt_st = javascript_tag.find('"currentAsin"')+16
				crnt_end = javascript_tag.find(',\n"parentAsin"')
				crnt_asin = json.loads(javascript_tag[crnt_st:crnt_end])

				if crnt_asin == item.current_asin:
					# Writing File
					with io.open(f'static/docs/productPages/EN_{item.current_asin}.txt', 'w', encoding='UTF-8') as responseFile:
						responseFile.writelines(response.text)
						variationSettings.objects.filter(current_asin=item.current_asin).update(
							description_en=True,
							available=True,
							last_checked = timezone.now(),
						)
				else:
					# Writing File
					with io.open(f'static/docs/productPages/EN_{item.current_asin}.txt', 'w', encoding='UTF-8') as responseFile:
						responseFile.writelines(response.text)
						variationSettings.objects.filter(current_asin=item.current_asin).update(
							description_en=True,
							last_checked = timezone.now(),
						)

			except AttributeError:
				
				if title_en:
					# Writing File
					with io.open(f'static/docs/productPages/EN_{item.current_asin}.txt', 'w', encoding='UTF-8') as responseFile:
						responseFile.writelines(response.text)
						variationSettings.objects.filter(current_asin=item.current_asin).update(
							description_en=True,
							available=True,
							last_checked = timezone.now(),
						)

		else:
			pass

	def saveResponseAR(self):

		item = self.item
		title_only = SoupStrainer('span' , {'id':'productTitle'})

		# Arabic response
		response_ar = self.soupParser(f'https://www.amazon.ae/-/ar/dp/{item.current_asin}')
		if response_ar:

			soup_ar = BeautifulSoup(response_ar.text, 'lxml', parse_only=title_only)

			# Arabic validate check
			try:
				title_ar = soup_ar.find('span', {'id': 'productTitle'}).text.strip().split('】')[-1].split('𝐆𝐢𝐟𝐭 ')[-1]

				# Writing File
				with io.open(f'static/docs/productPages/AR_{item.current_asin}.txt', 'w', encoding='UTF-8') as responseFile:
					responseFile.writelines(response_ar.text)
					variationSettings.objects.filter(current_asin=item.current_asin).update(
						description_ar=True
					)
			except AttributeError:
				pass

		else:
			pass