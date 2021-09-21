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
	    session.mount('https://www.amazon.co.uk', HTTPAdapter(max_retries=10))

	    HEADERS =[{
	        'authority': 'www.amazon.co.uk',
	        'pragma': 'no-cache',
	        'cache-control': 'no-cache',
	        'dnt': '1',
	        'upgrade-insecure-requests': '1',
	        'accept': '*/*',
	        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
	        'sec-fetch-site': 'none',
	        'sec-fetch-mode': 'navigate',
	        'sec-fetch-dest': 'document',
	        'referer' : 'https://www.amazon.co.uk/'
	    },{
	        'authority': 'www.amazon.co.uk',
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
	        'authority': 'www.amazon.co.uk',
	        'pragma': 'no-cache',
	        'cache-control': 'no-cache',
	        'dnt': '1',
	        'upgrade-insecure-requests': '1',
	        'accept': '*/*',
	        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
	        'sec-fetch-site': 'none',
	        'sec-fetch-mode': 'navigate',
	        'sec-fetch-dest': 'document',
	        'referer' : 'https://www.amazon.co.uk/'
	    },{
	        'authority': 'www.amazon.co.uk',
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
	        "http": "http://43.224.10.31:6666"
	    },{
	        "http": "http://103.251.214.167:6666"
	    },{
	        "http": "http://125.99.120.166:40390"
	    },{
	        "http": "http://115.243.184.76:23500"
	    },{
	        "http": "http://103.241.227.106:6666"
	    },{
	        "http": "http://139.99.105.185"
	    },{
	        "http": "http://150.129.148.99:35101"
	    },{
	        "http": "http://150.129.151.83:6666"
	    },{
	        "http": "http://150.129.148.88:35101"
	    },{
	        "http": "http://103.241.227.107:6666"
	    },{
	        "http": "http://122.183.244.51:3128"
	    },{
	        "http": "http://101.53.158.48:9300"
	    },{
	        "http": "http://103.21.163.76:6666"
	    },{
	        "http": "http://165.22.216.241:80"
	    },{
	        "http": "http://27.116.51.181:6666"
	    },{
	        "http": "http://103.216.82.153:6666"
	    },{
	        "http": "http://103.21.163.81:6666"
	    },{
	        "http": "http://103.197.49.165"
	    },{
	        "http": "http://103.15.140.140"
	    }]

		session.proxies.update(random.choice(proxies))
		session.headers.update(random.choice(HEADERS))

		response = session.get(link, stream=True)
		
		if response.status_code == 200:
			soup = BeautifulSoup(response.text, 'html.parser')
		else:
	        response = None
	        soup = None

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

	soup, response = soupParser(f'https://www.amazon.co.uk/-/en/dp/{productResponse.productID}')
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
					source='amazon.co.uk',
				)


