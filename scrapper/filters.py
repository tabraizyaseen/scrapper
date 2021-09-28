import django_filters
from .models import *
from django_filters import CharFilter,ChoiceFilter, AllValuesFilter
from django import forms
from django.forms.widgets import TextInput
from django.db.models import Q

# Category Dropdown
'''
class CategoryFilter(django_filters.ChoiceFilter):

	def __init__(self, *args, **kwargs):
		workers = kwargs.pop('workers', None)

		kwargs['choices'] = [(a['category'], a['category']) for a in workers]
		super(CategoryFilter, self).__init__(*args, **kwargs)
'''

class ProductFilter(django_filters.FilterSet):

	'''
	# Category Dropdown
	# category_drop = CategoryFilter(field_name='category', workers=productPagesScrapper.objects.values('category').distinct(), label='Category')

	class Meta:
		model = productPagesScrapper
		fields = ['category']
	'''


	q = django_filters.CharFilter(method='my_custom_filter',label="Search")
	category_exact = CharFilter(field_name='category', lookup_expr='exact', label="Category Search")

	class Meta:
		model = productPagesScrapper
		fields = ['q']

	def my_custom_filter(self, queryset, name, value):
		return productPagesScrapper.objects.filter(
			Q(category__icontains=value) | Q(title_en__icontains=value) | Q(productID__startswith=value) | Q(source=value) | Q(description_en=value) | Q(description_ar=value)
		)
		
		
class ProductCategoryFilter(django_filters.FilterSet):

	category = CharFilter(field_name='category', lookup_expr='icontains', label="Category")
	category_exact = CharFilter(field_name='category', lookup_expr='exact', label="Category Exact")

	class Meta:
		model = productPagesScrapper
		fields = ['category']


class VariationSettingsFilter(django_filters.FilterSet):

	q = django_filters.CharFilter(method='my_custom_filter',label="Search")

	class Meta:
		model = variationSettings
		fields = ['q']

	def my_custom_filter(self, queryset, name, value):
		return variationSettings.objects.filter(
			Q(current_asin__icontains=value) | Q(parent_asin__icontains=value) | Q(title_en__icontains=value) | Q(description_en=value) | Q(description_ar=value)
		)

class TotalVariationsFilter(django_filters.FilterSet):

	q = django_filters.CharFilter(method='my_custom_filter',label="Search")

	class Meta:
		model = totalVariations
		fields = ['q']

	def my_custom_filter(self, queryset, name, value):
		return totalVariations.objects.filter(
			Q(productID__productID=value) | Q(parent_asin__icontains=value) | Q(name_en__icontains=value)
		)
