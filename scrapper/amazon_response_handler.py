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
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
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
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4',
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
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
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
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
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
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
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
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4',
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
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
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
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
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
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
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
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4',
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
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
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
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
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
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
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
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4',
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
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
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
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
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
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
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
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4',
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
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
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
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
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
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
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
			'accept': '*/*',
			'User-Agent' : 'Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4',
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
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
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
			'accept': '*/*',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-user': '?1',
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

		return response

	except RequestException:
		response = None

		return response