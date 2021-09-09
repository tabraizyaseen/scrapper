import django_filters
from .models import *
from django_filters import CharFilter,ChoiceFilter, AllValuesFilter
from django import forms
from django.forms.widgets import TextInput

# Category Dropdown
'''
class CategoryFilter(django_filters.ChoiceFilter):

    def __init__(self, *args, **kwargs):
        workers = kwargs.pop('workers', None)

        kwargs['choices'] = [(a['category'], a['category']) for a in workers]
        super(CategoryFilter, self).__init__(*args, **kwargs)
'''

class ProductFilter(django_filters.FilterSet):

	category = CharFilter(field_name='category', lookup_expr='icontains', label="Category")
	title_en = CharFilter(field_name='title_en', lookup_expr='icontains', label="Title")
	productID = CharFilter(field_name='productID', lookup_expr='startswith', label="Asin")
	category_exact = CharFilter(field_name='category', lookup_expr='exact', label="Match")
	
	# Category Dropdown
	# category_drop = CategoryFilter(field_name='category', workers=productPagesScrapper.objects.values('category').distinct(), label='Category')

	class Meta:
		model = productPagesScrapper
		fields = ['category','productID','title_en']
		
		
class ProductCategoryFilter(django_filters.FilterSet):

	category = CharFilter(field_name='category', lookup_expr='icontains', label="Category")
	category_exact = CharFilter(field_name='category', lookup_expr='exact', label="Category Exact")

	class Meta:
		model = productPagesScrapper
		fields = ['category']


class VariationSettingsFilter(django_filters.FilterSet):

	current_asin = CharFilter(field_name='current_asin', lookup_expr='icontains', label="Current Asin")
	parent_asin = CharFilter(field_name='parent_asin', lookup_expr='icontains', label="Parent Asin")
	title_en = CharFilter(field_name='title_en', lookup_expr='icontains', label="English Title")

	class Meta:
		model = variationSettings
		fields = ['current_asin','parent_asin','title_en']

class TotalVariationsFilter(django_filters.FilterSet):

	productID__productID = CharFilter(field_name='productID__productID', lookup_expr='icontains', label="ProductID")
	parent_asin = CharFilter(field_name='parent_asin', lookup_expr='icontains', label="Parent Asin")
	name_en = CharFilter(field_name='name_en', lookup_expr='icontains', label="Name English")

	class Meta:
		model = totalVariations
		fields = ['productID__productID', 'parent_asin', 'name_en']
