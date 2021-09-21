import requests
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import io
import random
from time import sleep
import re
import json

import datetime
from django.utils import timezone

from .models import productPagesScrapper
from .models import productDetails

def soupParser(link):

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
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
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
		soup = BeautifulSoup(response.text, 'html.parser')

		return soup, response

	except RequestException:
		response = None
		soup = None

		return soup, response

# Category Scrapper
def amazonCategoryScrapper(url):

	# Category Parser
	def func_category(url):

		def extracting(container):

			# ID
			p_id = container.get('data-asin')

			# title
			atag = container.find_all('a','a-link-normal s-no-outline')[0]
			title = atag.img.get('alt')

			# Price
			try:
				price = container.find('span','a-price-whole').replace(".","").replace(",","").replace('₹','').replace('$','')
			except AttributeError:
				price = ""

			# old price
			try:
				old = container.find('span','a-text-price')
				old_price = old.find('span',{'aria-hidden':'true'}).text.split("D")[-1].split(".")[0].replace(",","").replace('₹','').replace('$','')
			except AttributeError:
				old_price = ""

			return p_id, title, price, old_price

		soup, _ = soupParser(url)

		if soup:

			containers = soup.find_all('div', {'data-component-type': 's-search-result'})

			for each in containers:
				try:
					# Sponsored
					each.find('span', 's-label-popover-default').text
				except AttributeError:
					p_id, title, price, old_price = extracting(each)
					if not productPagesScrapper.objects.filter(productID=p_id).exists():
						productPagesScrapper.objects.create(productID=p_id, title_en=title, price=price, old_price=old_price, source='amazon.ae')
					else:
						productPagesScrapper.objects.filter(productID=p_id).update(price=price, old_price=old_price, last_checked = timezone.now())
		else:
			pass

	soup, response = soupParser(url)

	if soup:

		# Last page
		try:
			try:
				total_pages = int(soup.find_all('span',{'class':'s-pagination-item','aria-disabled':'true'})[-1].text)
				total_pages +=1
			except AttributeError:
				soup, response = soupParser(url)
				total_pages = int(soup.find_all('span',{'class':'s-pagination-item','aria-disabled':'true'})[-1].text)
				total_pages +=1
		except Exception:
			total_pages = 0

		# For Category for more than one pages
		if total_pages:
			for page in range(1, total_pages):

				url = url + f'&page={page}'

				func_category(url)

				print(page)

		# For Category of one page
		else:
			func_category(url)

	else:
		pass

# Product Response Saving in English
def amazonProductServerResponse(product):
	
	def titleParser(soup):

		# Intializting
		title = ''
		category = ''
		valid = False

		# Title
		try:
			title = soup.find('span', {'id': 'productTitle'}).text.strip().split('】')[-1].split('𝐆𝐢𝐟𝐭 ')[-1]
			valid = True
		except AttributeError:
			pass

		# Category
		try:
			category_div = soup.find('div',{'id':'wayfinding-breadcrumbs_feature_div'})
			category_ul = category_div.ul.find_all('li')
			for category_li in category_ul:
				category += category_li.text.strip()+" "
			category = category.strip()
		except AttributeError:
			pass

		return category, title, valid

	soup, response = soupParser(f'https://www.amazon.ae/dp/{product.productID}')

	if soup:

		category, title, valid = titleParser(soup)

		# Writing File
		with io.open(f'static/docs/productPages/EN_{product.productID}.txt', 'w', encoding='UTF-8') as responseFile:
			responseFile.writelines(response.text)
			productPagesScrapper.objects.filter(id=product.id).update(
				source='amazon.ae',
				category=category,
				title_en=title,
				description_en=valid,
				last_checked = timezone.now(),
			)

	else:
		pass
		

# Product Specifications and Images
class AmazonProductDetails:

	def __init__(self, product):

		# Reading File
		with io.open(f'static/docs/productPages/EN_{product.productID}.txt', 'r', encoding='UTF-8') as html_file:
			soup = BeautifulSoup(html_file.read(), 'html.parser')

		self.product = product
		self.soup = soup

	def price(self):

		soup = self.soup

		try:
			price = soup.find('span',{'id':'priceblock_ourprice'}).text.split('\xa0')[-1].split('.')[0].replace(',','').replace('₹','').replace('$','')
		except Exception:
			try:
				# Deal price
				price = soup.find('span',{'id':'priceblock_dealprice'}).text.split('\xa0')[-1].split('.')[0].replace(',','').replace('₹','').replace('$','')
			except Exception:
				try:
					# Book price
					price = soup.find('span',{'id':'price'}).text.split('\xa0')[-1].split('.')[0].replace(',','').replace('₹','').replace('$','')
				except Exception:
					price = ''

		return price

	def old_price(self):

		soup = self.soup

		try:
			old_price = soup.find('span','priceBlockStrikePriceString').text.strip().split('\xa0')[-1].split('.')[0].replace(',','').replace('₹','').replace('$','')
		except Exception:
			try:
				# Book price
				old_price = soup.find('span',{'id':'listPrice'}).text.strip().split('\xa0')[-1].split('.')[0].replace(',','').replace('₹','').replace('$','')
			except Exception:
				old_price = ''

		return old_price

	# To retrieve only brands
	def Brand(self):
		soup = self.soup

		# Brand
		try:
			# brand = soup.find('a',{'id':'bylineInfo'}).text.split(':')[-1].strip()
			brand = soup.find('a',{'id':'bylineInfo'}).text
			brand = brand.split('Visit the')[-1].split('Store')[0].split(':')[-1].strip()
		except AttributeError:
			try:
				brand = soup.find('span','author').text.strip().replace('\n','')
			except AttributeError:
				brand = ''

		return brand


	def Specifications(self):

		def SpecificationsNorm(soup,product,specifications):
			
			# Specifications
			try:
				specifications_table = soup.find('table', {'id': 'productDetails_techSpec_section_1'})
				table_rows = specifications_table.find_all('tr')
				for rows in table_rows:
					keys = rows.th.text.strip()
					values = rows.td.text.strip().replace('\u200e','')
					specifications.append((keys, values))

			except AttributeError:
				# For the watches
				try:
					specifications_table = soup.find('table', {'id': 'technicalSpecifications_section_1'})
					table_rows = specifications_table.find_all('tr')
					for rows in table_rows:
						keys = rows.th.text.strip()
						values = rows.td.text.strip().replace('\u200e','')
						specifications.append((keys, values))

				except AttributeError:
					# Some products didn't have specification table
					try:
						specs_div = soup.find('div',{'id':'detailBulletsWrapper_feature_div'})
						specs_div = specs_div.find('div',{'id':'detailBullets_feature_div'})
						specs_li = specs_div.find_all('li')
						for spec_li in specs_li:
							keys = spec_li.span.span.text.split('\n')[0]
							values = spec_li.span.find_all('span')[-1].text
							specifications.append((keys, values))

					except AttributeError:
						pass
					
			if not 'ASIN' in str(specifications):
				specifications.append(('ASIN',product.productID))

			return specifications

		def SpecificationsApple(soup,specifications):

			try:
				specifications_div = soup.find('div',{'id':'btfContent35_feature_div'})
				for specification_table in specifications_div.find_all('table'):
					for specification_tr in specification_table.find_all('tr'):
						specification_tds = specification_tr.find_all('td')
						specifications.append((specification_tds[0].text.strip(),specification_tds[1].text.strip()))
			except AttributeError:
				pass
		
			return specifications

			
		# Initializes Specifications List
		specifications = []

		soup = self.soup
		product = self.product

		specifications = (lambda x,y : x if x else y)(SpecificationsNorm(soup,product,specifications),SpecificationsApple(soup,specifications))
		brand = self.Brand()
		if brand and not ('Brand' in str(specifications)):
			specifications.insert(0,('Brand',brand))
			

		return specifications

	
	def ImagesList(self):	

		soup = self.soup
		product = self.product

		# JavaScript Tag for images
		pattern = re.compile(r"P\.when\('A'\).register\(\"ImageBlockATF\", function\(A\)\{")
		javascript_img = soup.find('script',string=pattern).contents[0]

		try:

			# All images
			strt = javascript_img.find("'colorImages\':")+15
			start2 = javascript_img[strt:].find("'initial\': ")+11+strt
			end = javascript_img.find("},\n\'colorToAsin\'")
			all_imgs = json.loads(javascript_img[start2:end])

			all_image = [imgs['hiRes'] if imgs['hiRes'] else imgs['large'] for imgs in all_imgs]

		except Exception as e:

			try:
				print(e)

				# All Book Images
				strt = javascript_img.find("'imageGalleryData'")+20
				end = javascript_img.find(",\n\'centerColMargin\'")
				all_imgs = json.loads(javascript_img[strt:end])
				all_image = [imgs['mainUrl'] for imgs in all_imgs if imgs['mainUrl']]

			except Exception:
				all_image = []
				productPagesScrapper.objects.filter(id=product.id).update(
					description_en=False
					)

		return all_image


	def Highlights(self):

		# Highlights
		highlights = []
		soup = self.soup

		try:
			highlights_div = soup.find('div',{'id':'feature-bullets'})
			highlights_ul = highlights_div.ul.find_all('li')
			for highlights_li in highlights_ul:
				if highlights_li.text.strip():
					highlights.append(highlights_li.text.strip())
		except AttributeError:
			
			'''Book Highlights'''
			book_highlight = soup.find_all('noscript')[1].text.strip()

			if book_highlight:
				highlights.append(book_highlight)

		return highlights

	# Product Description
	def ProductDescription(self):

		# Initializing
		long_descriptionEN = ''
		soup = self.soup

		# Product Description
		try:
			long_descriptionEN_div = soup.find('div',{'id':'productDescription'})
			long_descriptionEN_p = long_descriptionEN_div.find_all('p')
			for p_tag in long_descriptionEN_p:
				if p_tag.text:
					long_descriptionEN = p_tag.text.strip()
					break
		except AttributeError:
			pass

		return long_descriptionEN

# Product Specifications and Images in Arabic
class AmazonProductDetailsArabic:

	def __init__(self, product):

		# Reading File
		with io.open(f'static/docs/productPages/AR_{product.productID}.txt', 'r', encoding='UTF-8') as html_file:
			soup = BeautifulSoup(html_file.read(), 'html.parser')

		self.product = product
		self.soup = soup

	# To parse only Brands
	def Brand(self):
		soup = self.soup

		# Brand
		try:
			brand = soup.find('a',{'id':'bylineInfo'}).text
			brand = brand.split('متجر')[-1].split(':')[-1].strip()
		except AttributeError:
			try:
				brand = soup.find('span','author').text.strip().replace('\n','')
			except AttributeError:
				brand = ''

		return brand

	def Specifications(self):

		def SpecificationsNorm(soup,product,specifications):
			
			# Specifications
			try:
				specifications_table = soup.find('table', {'id': 'productDetails_techSpec_section_1'})
				table_rows = specifications_table.find_all('tr')
				for rows in table_rows:
					keys = rows.th.text.strip()
					values = rows.td.text.strip().replace('\u200e','')
					specifications.append((keys, values))

			except AttributeError:
				# For the watches
				try:
					specifications_table = soup.find('table', {'id': 'technicalSpecifications_section_1'})
					table_rows = specifications_table.find_all('tr')
					for rows in table_rows:
						keys = rows.th.text.strip()
						values = rows.td.text.strip().replace('\u200e','')
						specifications.append((keys, values))

				except AttributeError:
					# Some products didn't have specification table
					try:
						specs_div = soup.find('div',{'id':'detailBulletsWrapper_feature_div'})
						specs_div = specs_div.find('div',{'id':'detailBullets_feature_div'})
						specs_li = specs_div.find_all('li')
						for spec_li in specs_li:
							keys = spec_li.span.span.text.split('\n')[0]
							values = spec_li.span.find_all('span')[-1].text
							specifications.append((keys, values))

					except AttributeError:
						pass
					
			if not 'ASIN' in str(specifications):
				specifications.append(('ASIN',product.productID))

			return specifications

		def SpecificationsApple(soup,specifications):

			try:
				specifications_div = soup.find('div',{'id':'btfContent35_feature_div'})
				for specification_table in specifications_div.find_all('table'):
					for specification_tr in specification_table.find_all('tr'):
						specification_tds = specification_tr.find_all('td')
						specifications.append((specification_tds[0].text.strip(),specification_tds[1].text.strip()))
			except AttributeError:
				pass
		
			return specifications

			
		# Initializes Specifications List
		specifications = []

		soup = self.soup
		product = self.product

		specifications = (lambda x,y : x if x else y)(SpecificationsNorm(soup,product,specifications),SpecificationsApple(soup,specifications))
		brand = self.Brand()
		if brand and not ('Brand' in str(specifications)):
			specifications.insert(0,('Brand',brand))

		return specifications


	# Highliights
	def Highlights(self):

		# Highlights
		highlights = []
		soup = self.soup

		try:
			highlights_div = soup.find('div',{'id':'feature-bullets'})
			highlights_ul = highlights_div.ul.find_all('li')
			for highlights_li in highlights_ul:
				if highlights_li.text.strip():
					highlights.append(highlights_li.text.strip())
		except AttributeError:
			
			'''Book Highlights'''
			book_highlight = soup.find_all('noscript')[1].text.strip()

			if book_highlight:
				highlights.append(book_highlight)

		return highlights

	# Arabic Product Description
	def ProductDescription(self):

		# Initialization
		long_descriptionAR = ''
		soup = self.soup

		try:
			long_descriptionAR_div = soup.find('div',{'id':'productDescription'})
			long_descriptionAR_p = long_descriptionAR_div.find_all('p')
			for p_tag in long_descriptionAR_p:
				if p_tag.text:
					long_descriptionAR = p_tag.text.strip()
					break
		except AttributeError:
			pass

		return long_descriptionAR

# If file data is not valid
def ResponseValidate(productResponse):

	def titleParser(soup):

		# Intializting
		title = ''
		category = ''
		valid = False

		# Title
		try:
			title = soup.find('span', {'id': 'productTitle'}).text.strip().split('】')[-1].split('𝐆𝐢𝐟𝐭 ')[-1]
			valid = True
		except AttributeError:
			pass

		# Category
		try:
			category_div = soup.find('div',{'id':'wayfinding-breadcrumbs_feature_div'})
			category_ul = category_div.ul.find_all('li')
			for category_li in category_ul:
				category += category_li.text.strip()+" "
			category = category.strip()
		except AttributeError:
			pass

		return category, title, valid

	soup, response = soupParser(f'https://www.amazon.ae/dp/{productResponse.productID}')

	if soup:

		category, title, valid = titleParser(soup)

		# Writing File
		if valid:
			with io.open(f'static/docs/productPages/EN_{productResponse.productID}.txt', 'w', encoding='UTF-8') as responseFile:

				responseFile.writelines(response.text)

				if category:

					productPagesScrapper.objects.filter(id=productResponse.id).update(
						category=category,
						description_en=valid,
						title_en=title,
						last_checked = timezone.now(),
						source = "amazon.ae",
					)
				else:
					productPagesScrapper.objects.filter(id=productResponse.id).update(
						description_en=valid,
						title_en=title,
						last_checked = timezone.now(),
					)

	else:
		pass
	
def ResponseValidateArabic(productResponse):

	# For Arabic title validation
	soup, response = soupParser(f'https://www.amazon.ae/-/ar/dp/{productResponse.productID}')

	if soup:

		valid = False
		try:
			# Finding title
			title = soup.find('span', {'id': 'productTitle'}).text.strip().split('】')[-1].split('𝐆𝐢𝐟𝐭 ')[-1]
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
			)

	else:
		pass
