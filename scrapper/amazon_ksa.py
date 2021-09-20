import requests
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import io
import random

from .models import productPagesScrapper

def soupParser(link):

	try:

		session = requests.Session()
		session.mount('https://www.amazon.sa', HTTPAdapter(max_retries=10))

		HEADERS =[{
			'authority': 'www.amazon.sa',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer' : 'https://www.amazon.sa/'
		},{
			'authority': 'www.amazon.sa',
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
			'authority': 'www.amazon.sa',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer' : 'https://www.amazon.sa/'
		},{
			'authority': 'www.amazon.sa',
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
			"http": "http://151.253.165.70:8080"
		}, {
			"http": "http://185.106.121.176:9050"
		}, {
			"http": "http://193.223.100.81:1080"
		}, {
			"http": "http://217.138.193.62:1080"
		}, {
			"http": "http://20.46.192.92:9300"
		}, {
			"http": "http://178.80.156.227:8080"
		}, {
			"http": "http://5.42.224.18:8080"
		}, {
			"http": "http://2.88.5.196:8080"
		}, {
			"http": "http://37.104.112.202:8080"
		}, {
			"http": "http://37.56.37.130:8080"
		}, {
			"http": "http://118.69.219.185"
		}, {
			"http": "http://127.0.0.1"
		}, {
			"http": "http://50.192.195.69"
		}, {
			"http": "http://89.187.177.91"
		}, {
			"http": "http://192.168.0.179"
		}, {
			"http": "http://139.59.1.14"
		}, {
			"http": "http://103.240.77.98"
		}, {
			"http": "http://58.69.161.161"
		}, {
			"http": "http://103.197.49.165"
		}, {
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

	soup, response = soupParser(f'https://www.amazon.sa/-/en/dp/{productResponse.productID}')
	if soup:
		category, title, valid = titleParser(soup)

		# Writing File
		if valid:
			with io.open(f'static/docs/productPages/EN_{productResponse.productID}.txt', 'w', encoding='UTF-8') as responseFile:

				responseFile.writelines(response.text)

				productPagesScrapper.objects.filter(id=productResponse.id).update(
					category=category,
					description_en=valid,
					title_en=title,
					source='amazon.sa',
				)

def ResponseValidateArabic(productResponse):

	# For Arabic title validation
	soup, response = soupParser(f'https://www.amazon.sa/-/ar/dp/{productResponse.productID}')

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
			)

