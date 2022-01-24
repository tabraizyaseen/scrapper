from bs4 import BeautifulSoup
import io
from django.utils import timezone

from .models import productPagesScrapper
from .amazon_response_handler import responseUSA, category_check

def soupParser(link):

	response = responseUSA(link)

	if response:
		
		if response.status_code == 200:
			soup = BeautifulSoup(response.text, 'html.parser')
		else:
			response = None
			soup = None

		return soup, response

	else:
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

	soup, response = soupParser(f'https://www.amazon.com/-/en/dp/{productResponse.productID}')
	if soup:
		category, title, valid = titleParser(soup)

		# Writing File
		if valid:
			with io.open(f'static/docs/productPages/EN_{productResponse.productID}.txt', 'w', encoding='UTF-8') as responseFile:

				responseFile.writelines(response.text)

				productPagesScrapper.objects.filter(id=productResponse.id).update(
					category=category_check(category),
					description_en=valid,
					title_en=title,
					last_checked = timezone.now(),
					source='amazon.com',
				)


