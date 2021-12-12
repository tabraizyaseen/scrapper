import requests
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
import random

def priceNormalizing(price):
		price = float(price.text.strip().split('\xa0')[-1].split('.')[0].replace(',','').replace('SAR','').replace('AED','').replace('₹','').replace('$','').replace('£',''))
		return price

def responseUAE(link):

	try:

		session = requests.Session()
		session.mount('https://www.amazon.ae', HTTPAdapter(max_retries=10))

		HEADERS = [{
			'authority': 'www.amazon.ae',
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
			'referer': 'https://www.amazon.ae/'
		}, {
			'authority': 'www.amazon.ae',
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
			'authority': 'www.amazon.ae',
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
			'referer': 'https://www.amazon.ae/'
		}, {
			'authority': 'www.amazon.ae',
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
			'authority': 'www.amazon.ae',
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
			{'http': 'http://185.117.75.148:1080'},
			{'http': 'http://94.56.27.42:3128'},
			{'http': 'http://47.91.104.13:3128'},
			{'http': 'http://47.91.125.143:43256'},
			{'http': 'http://47.91.110.23:43256'},
			{'http': 'http://47.91.111.135:43256'},
			{'http': 'http://47.91.106.119:43256'},
			{'http': 'http://47.91.108.78:43256'},
			{'http': 'http://87.247.185.94:1080'},
			{'http': 'http://94.56.172.201:3128'},
			{'http': 'http://80.227.141.50:8118'},
			{'http': 'http://185.140.248.45:8080'},
			{'http': 'http://94.204.189.249:8080'},
			{'http': 'http://2.50.152.79:53281'},
			{'http': 'http://40.123.207.53:8080'},
			{'http': 'http://2.50.154.149:53281'},
			{'http': 'http://217.138.193.126:3128'},
			{'http': 'http://217.165.93.198:53281'},
			{'http': 'http://217.165.93.18:53281'},
			{'http': 'http://217.165.93.149:53281'},
			{'http': 'http://5.32.86.34:8080'},
			{'http': 'http://5.32.81.181:1080'},
			{'http': 'http://47.91.105.34:80'},
			{'http': 'http://94.205.140.158:34561'},
			{'http': 'http://91.201.5.167:3128'},
		]

		session.proxies.update(random.choice(proxies))
		session.headers.update(random.choice(HEADERS))

		response = session.get(link, stream=True)

		return response

	except RequestException:
		response = None

		return response


def responseKSA(link):

	try:

		session = requests.Session()
		session.mount('https://www.amazon.sa', HTTPAdapter(max_retries=10))

		HEADERS =[{
			'authority': 'www.amazon.sa',
			'method': 'GET',
			'scheme': 'https',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'Connection': 'keep-alive',
			'Accept-Encoding': 'gzip, deflate, br',
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer' : 'https://www.amazon.sa/'
		},{
			'authority': 'www.amazon.sa',
			'method': 'GET',
			'scheme': 'https',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'Connection': 'keep-alive',
			'Accept-Encoding': 'gzip, deflate, br',
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (iPad; CPU OS 15_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer' : 'https://www.google.com/'
		},{
			'authority': 'www.amazon.sa',
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
			'referer' : 'https://www.amazon.sa/'
		},{
			'authority': 'www.amazon.sa',
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
			'referer' : 'https://www.google.com/'
		},{
			'authority': 'www.amazon.sa',
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
			{'http': 'http://142.154.47.154:8080'},
			{'http': 'http://145.82.206.237:8080'},
			{'http': 'http://93.112.203.154:8080'},
			{'http': 'http://51.223.247.70:8080'},
			{'http': 'http://88.84.105.68:1080'},
			{'http': 'http://175.110.204.167:8080'},
			{'http': 'http://51.223.254.208:8080'},
			{'http': 'http://188.50.166.251:1981'},
			{'http': 'http://93.112.168.84:8080'},
			{'http': 'http://142.154.124.228:8080'},
			{'http': 'http://37.106.76.27:8080'},
			{'http': 'http://51.223.246.99:8080'},
			{'http': 'http://86.60.62.29:8080'},
			{'http': 'http://93.112.210.235:8080'},
			{'http': 'http://175.110.197.49:8080'},
			{'http': 'http://51.223.90.95:8080'},
			{'http': 'http://51.223.247.165:8080'},
			{'http': 'http://51.223.248.121:8080'},
			{'http': 'http://51.223.245.26:8080'},
			{'http': 'http://86.60.62.40:8080'},
			{'http': 'http://51.223.244.181:8080'},
			{'http': 'http://51.223.251.74:8080'},
			{'http': 'http://51.223.250.58:8080'},
			{'http': 'http://95.177.160.166:1080'},
			{'http': 'http://51.211.2.157:8080'},
			{'http': 'http://51.223.248.225:8080'},
			{'http': 'http://86.60.62.32:8080'},
			{'http': 'http://141.164.215.44:8080'},
			{'http': 'http://31.166.33.7:9090'},
			{'http': 'http://31.166.194.120:9090'},
		]

		session.proxies.update(random.choice(proxies))
		session.headers.update(random.choice(HEADERS))

		response = session.get(link, stream=True)

		return response

	except RequestException:
		response = None

		return response


def responseIND(link):

	try:

		session = requests.Session()
		session.mount('https://www.amazon.in', HTTPAdapter(max_retries=10))

		HEADERS =[{
			'authority': 'www.amazon.in',
			'method': 'GET',
			'scheme': 'https',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'Connection': 'keep-alive',
			'Accept-Encoding': 'gzip, deflate, br',
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer' : 'https://www.amazon.in/'
		},{
			'authority': 'www.amazon.in',
			'method': 'GET',
			'scheme': 'https',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'Connection': 'keep-alive',
			'Accept-Encoding': 'gzip, deflate, br',
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (iPad; CPU OS 15_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer' : 'https://www.google.com/'
		},{
			'authority': 'www.amazon.in',
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
			'referer' : 'https://www.amazon.in/'
		},{
			'authority': 'www.amazon.in',
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
			'referer' : 'https://www.google.com/'
		},{
			'authority': 'www.amazon.in',
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

		return response

	except RequestException:
		response = None

		return response


def responseUK(link):
	
	try:

		session = requests.Session()
		session.mount('https://www.amazon.co.uk', HTTPAdapter(max_retries=10))

		HEADERS =[{
			'authority': 'www.amazon.co.uk',
			'method': 'GET',
			'scheme': 'https',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'Connection': 'keep-alive',
			'Accept-Encoding': 'gzip, deflate, br',
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer' : 'https://www.amazon.co.uk/'
		},{
			'authority': 'www.amazon.co.uk',
			'method': 'GET',
			'scheme': 'https',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'Connection': 'keep-alive',
			'Accept-Encoding': 'gzip, deflate, br',
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (iPad; CPU OS 15_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer' : 'https://www.google.com/'
		},{
			'authority': 'www.amazon.co.uk',
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
			'referer' : 'https://www.amazon.co.uk/'
		},{
			'authority': 'www.amazon.co.uk',
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
			'referer' : 'https://www.google.com/'
		},{
			'authority': 'www.amazon.co.uk',
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

		return response

	except RequestException:
		response = None

		return response

def responseAU(link):

	try:

		session = requests.Session()
		session.mount('https://www.amazon.com.au', HTTPAdapter(max_retries=10))

		HEADERS =[{
			'authority': 'www.amazon.com.au',
			'method': 'GET',
			'scheme': 'https',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'Connection': 'keep-alive',
			'Accept-Encoding': 'gzip, deflate, br',
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer' : 'https://www.amazon.com.au/'
		},{
			'authority': 'www.amazon.com.au',
			'method': 'GET',
			'scheme': 'https',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'Connection': 'keep-alive',
			'Accept-Encoding': 'gzip, deflate, br',
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (iPad; CPU OS 15_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer' : 'https://www.google.com/'
		},{
			'authority': 'www.amazon.com.au',
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
			'referer' : 'https://www.amazon.com.au/'
		},{
			'authority': 'www.amazon.com.au',
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
			'referer' : 'https://www.google.com/'
		},{
			'authority': 'www.amazon.com.au',
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

		return response

	except RequestException:
		response = None

		return response

def responseUSA(link):

	try:

		session = requests.Session()
		session.mount('https://www.amazon.com', HTTPAdapter(max_retries=10))

		HEADERS =[{
			'authority': 'www.amazon.com',
			'method': 'GET',
			'scheme': 'https',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'Connection': 'keep-alive',
			'Accept-Encoding': 'gzip, deflate, br',
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer' : 'https://www.amazon.com/'
		},{
			'authority': 'www.amazon.com',
			'method': 'GET',
			'scheme': 'https',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'dnt': '1',
			'upgrade-insecure-requests': '1',
			'Connection': 'keep-alive',
			'Accept-Encoding': 'gzip, deflate, br',
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (iPad; CPU OS 15_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
			'sec-fetch-site': 'none',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-dest': 'document',
			'referer' : 'https://www.google.com/'
		},{
			'authority': 'www.amazon.com',
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
			'referer' : 'https://www.amazon.com/'
		},{
			'authority': 'www.amazon.com',
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
			'referer' : 'https://www.google.com/'
		},{
			'authority': 'www.amazon.com',
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

		return response

	except RequestException:
		response = None

		return response