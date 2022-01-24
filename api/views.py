from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import productPagesScrapperSerializer
from .formats import productClass, categoryClass
from . import tasks
from django_celery_results.models import TaskResult
from . import amazon_api

from scrapper.models import *

# Create your views here.
@api_view(['GET'])
def overview(request):

	api_urls = {
		'Product': '/<str:asin>/',
		'Product Details': 'details/<str:asin>/',
		'Product Variation Details': 'variation/<str:asin>/',
		'Category Details': 'category/<str:category>/',
	}

	return Response(api_urls)

@api_view(['GET'])
def product(request, asin):

	item = get_object_or_404(productPagesScrapper,productID=asin)

	serializer = productPagesScrapperSerializer(item)

	return Response(serializer.data)

@api_view(['GET'])
def singleProductDetails(request, asin):

	db_item = productPagesScrapper.objects.filter(productID=asin)
	variation_item = variationSettings.objects.filter(current_asin=asin)
	productClassIns = productClass(asin)

	if db_item:

		items = productClassIns.productAttributes(db_item[0], data_dict={}, category=61003, weight_class='light')

		return Response(items)
	elif variation_item:
		variation_item = variation_item[0]
		if variation_item.description_en and variation_item.description_ar:
			items = productClassIns.childProduct(variation_item)
			return Response(items)
		else:

			items = amazon_api.child_item(variation_item.current_asin)
			return Response(items)
			
			# Asynic : task queue code
			'''
			tasks.child_item.delay(variation_item.current_asin)
			return Response(f"job created for {asin}", status=status.HTTP_202_ACCEPTED)
			'''
	else:

		items = amazon_api.single_item(asin)
		return Response(items)


		# Asynic : task queue code
		'''
		if not TaskResult.objects.filter(task_args=f'"(\'{asin}\',)"', status__in=('PROGRESS','PENDING'), task_name="api.tasks.single_item").exists():
			tasks.single_item.delay(asin)
			return Response(f"job created for {asin}", status=status.HTTP_202_ACCEPTED)
		else:
			task = TaskResult.objects.filter(task_args=f'"(\'{asin}\',)"', task_name="api.tasks.single_item")

			return Response(f"Status of {asin} : {task.status}")
		'''


@api_view(['GET'])
def productVaraitions(request, asin):

	productClassIns = productClass(asin)

	item = productClassIns.mainProductData()

	'''
	if not TaskResult.objects.filter(task_args=f'"(\'{asin}\',)"', status__in=('PROGRESS','PENDING'), task_name="api.tasks.item_variations").exists():

		tasks.item_variations.delay(asin)
		return Response(f"job created for {asin}", status=status.HTTP_202_ACCEPTED)
	'''
	
	# item = productInformation(asin)
	
	return Response(item)


@api_view(['GET'])
def categoryDetails(request, category):

	categoryClassIns = categoryClass(category)

	items = categoryClassIns.categoryAttributes()

	return Response(items)

