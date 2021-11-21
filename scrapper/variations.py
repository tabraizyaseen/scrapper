from bs4 import BeautifulSoup, SoupStrainer
import io
import json
import re

from django.utils import timezone

from .models import *
from .amazon_response_handler import *


class VariationsSoup():

	def __init__(self,item):

		print("I'm the one : ",item)

		self.item = item

	def soupParserEN(self):

		item = self.item

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

		return soup_en

	def soupParserAR(self):

		item = self.item

		# Tag to parse
		only_tags = SoupStrainer('script',{'type':'text/javascript'})

		# Reading Arabic File
		with io.open(f'static/docs/productPages/AR_{item}.txt', 'r', encoding='UTF-8') as html_file:
			soup = BeautifulSoup(html_file.read(), 'lxml', parse_only=only_tags)
			try:
				pattern = re.compile(r"P\.register\('twister-js-init-dpx-data', function\(\) \{")
				soup_ar = soup.find('script',string=pattern).contents[0]
			except AttributeError:
				soup_ar = ''

		return soup_ar

	
	# "currentAsin" : "B08L5NLF53"
	def CurrentAsin(self):
		javascript_tag = self.soupParserEN()

		if javascript_tag:
			crnt_st = javascript_tag.find('"currentAsin"')+16
			crnt_end = javascript_tag.find(',\n"parentAsin"')
			crnt_asin = json.loads(javascript_tag[crnt_st:crnt_end])

			return crnt_asin


	# 'Parent Asin': 'B08SDP1RJR'
	def ParentAsin(self):
		javascript_tag = self.soupParserEN()

		if javascript_tag:

			prt_st = javascript_tag.find('"parentAsin"')+15
			prt_end = javascript_tag.find(',\n"dimensionToAsinMap"')
			prt_asin = json.loads(javascript_tag[prt_st:prt_end])

			return prt_asin

	# 'configuration': ['64 GB', '128 GB', '256 GB']
	def TotalVariation(self):
		javascript_tag = self.soupParserEN()

		if javascript_tag:
			val_start = javascript_tag.find('"variationValues"')+20
			variationValues = javascript_tag[val_start:].split('\n')[0][:-1]
			variations = json.loads(variationValues)

			return variations

	# 'configuration': ['64 GB', '128 GB', '256 GB']
	def TotalVariationAR(self):
		javascript_tag = self.soupParserAR()

		if javascript_tag:
			val_start = javascript_tag.find('"variationValues"')+20
			variationValues = javascript_tag[val_start:].split('\n')[0][:-1]
			variations = json.loads(variationValues)

			return variations

	# 'B08L5RJ392': ['International Version', '(PRODUCT)RED', '128 GB']
	def DimensionsDetails(self):
		javascript_tag = self.soupParserEN()

		if javascript_tag:
			dimstr_str = javascript_tag.find('"dimensionValuesDisplayData"')+31
			dimstr_end = javascript_tag.find(',\n"pwASINs"')
			dimstr = json.loads(javascript_tag[dimstr_str:dimstr_end])
			print(len(dimstr))

			return dimstr

	# 'B08L5RJ392': ['International Version', '(PRODUCT)RED', '128 GB']
	def DimensionsDetailsAR(self):
		javascript_tag = self.soupParserAR()

		if javascript_tag:
			dimstr_str = javascript_tag.find('"dimensionValuesDisplayData"')+31
			dimstr_end = javascript_tag.find(',\n"pwASINs"')
			dimstr = json.loads(javascript_tag[dimstr_str:dimstr_end])
			print(len(dimstr))

			return dimstr

	# '0_0_0': 'B08L5RJ392'
	def Dimensions(self):

		javascript_tag = self.soupParserEN()

		if javascript_tag:
			dim_st = javascript_tag.find('"dimensionToAsinMap"')+23
			dim_end =javascript_tag.find(',\n"variationValues"')
			dimenstions = json.loads(javascript_tag[dim_st:dim_end])

			return dimenstions

	# '0_0_0': 'B08L5RJ392'
	def DimensionsAR(self):

		javascript_tag = self.soupParserAR()

		if javascript_tag:
			dim_st = javascript_tag.find('"dimensionToAsinMap"')+23
			dim_end =javascript_tag.find(',\n"variationValues"')
			dimenstions = json.loads(javascript_tag[dim_st:dim_end])

			return dimenstions


class varienceDetail():

	def __init__(self,item):

		self.item = item


	def html_fileEN(self):
		item = self.item

		# Reading English File
		with io.open(f'static/docs/productPages/EN_{item.current_asin}.txt', 'r', encoding='UTF-8') as html_file:
			html_file = html_file.read()

		return html_file

	def html_fileAR(self):
		item = self.item

		# Reading Arabic File
		with io.open(f'static/docs/productPages/AR_{item.current_asin}.txt', 'r', encoding='UTF-8') as html_file:
			html_file_ar = html_file.read()

		return html_file_ar

	def price(self):

		html_file = self.html_fileEN()
		price_only = SoupStrainer('div' , {'id':'price'})
		soup = BeautifulSoup(html_file, 'lxml', parse_only=price_only)

		try:
			price = float(soup.find('span',{'id':'priceblock_ourprice'}).text.split('\xa0')[-1].split('.')[0].replace(',','').replace('₹',''))
		except Exception:
			try:
				price = float(soup.find('span',{'id':'priceblock_dealprice'}).text.split('\xa0')[-1].split('.')[0].replace(',','').replace('₹',''))
			except Exception:
				price = 0.0

		return price

	def old_price(self):

		html_file = self.html_fileEN()
		price_only = SoupStrainer('div' , {'id':'price'})
		soup = BeautifulSoup(html_file, 'lxml', parse_only=price_only)
		
		try:
			old_price = float(soup.find('span','priceBlockStrikePriceString').text.strip().split('\xa0')[-1].split('.')[0].replace(',','').replace('₹',''))
		except Exception:
			old_price = 0.0

		return old_price

	def titleParser(self):

		html_file = self.html_fileEN()
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

		html_file = self.html_fileAR()
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

		html_file = self.html_fileEN()
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

		
	def saveResponse(self):

		def checkResponse(response, title_only, item):
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

		item = self.item
		if not item.description_en:

			title_only = SoupStrainer(['script',{'type':'text/javascript'}, 'span' , {'id':'productTitle'}])
			print("From Save Response Current Asin : ",item.current_asin)

			# For UAE
			if item.productID.source == "amazon.ae":
				response = responseUAE(f'https://www.amazon.ae/-/en/dp/{item.current_asin}')
				if response:
					checkResponse(response, title_only, item)

			# For KSA
			elif item.productID.source == "amazon.sa":
				response = responseKSA(f'https://www.amazon.sa/-/en/dp/{item.current_asin}')
				if response:
					checkResponse(response, title_only, item)

			# For India
			elif item.productID.source == "amazon.in":
				response = responseIND(f'https://www.amazon.in/-/en/dp/{item.current_asin}')
				if response:
					checkResponse(response, title_only, item)

			# For AU
			elif item.productID.source == "amazon.com.au":
				response = responseAU(f'https://www.amazon.com.au/-/en/dp/{item.current_asin}')
				if response:
					checkResponse(response, title_only, item)

			# For UK
			elif item.productID.source == "amazon.co.uk":
				response = responseUK(f'https://www.amazon.co.uk/-/en/dp/{item.current_asin}')
				if response:
					checkResponse(response, title_only, item)

			# For USA
			elif item.productID.source == "amazon.com":
				response = responseUSA(f'https://www.amazon.com/-/en/dp/{item.current_asin}')
				if response:
					checkResponse(response, title_only, item)

	def saveResponseAR(self):

		def checkArResponse(response_ar, title_only, item):
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

		item = self.item
		if not item.description_ar:
			title_only = SoupStrainer('span' , {'id':'productTitle'})

			# For UAE
			if item.productID.source == "amazon.ae":
				response_ar = responseUAE(f'https://www.amazon.ae/-/ar/dp/{item.current_asin}')
				if response_ar:
					checkArResponse(response_ar, title_only, item)

			# For KSA
			elif item.productID.source == "amazon.sa":
				response_ar = responseKSA(f'https://www.amazon.sa/-/ar/dp/{item.current_asin}')
				if response_ar:
					checkArResponse(response_ar, title_only, item)