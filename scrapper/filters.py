import django_filters
from .models import *
from django_filters import CharFilter,ChoiceFilter
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
	category_exact = CharFilter(field_name='category__name', lookup_expr='exact', label="Category Search")

	class Meta:
		model = productPagesScrapper
		fields = ['q']

	def my_custom_filter(self, queryset, name, value):
		return productPagesScrapper.objects.filter(
			Q(category__name__icontains=value) | Q(title_en__icontains=value) | Q(productID__startswith=value) | Q(source=value) | Q(id=value if value.isdigit() else 0) | Q(batchname__icontains=value)
		)
		
		
class ProductCategoryFilter(django_filters.FilterSet):

	name = CharFilter(field_name='name', lookup_expr='icontains', label="Category")
	category_exact = CharFilter(field_name='name', lookup_expr='exact', label="Category Exact")

	class Meta:
		model = Categories
		fields = ['name']


class VariationSettingsFilter(django_filters.FilterSet):

	q = django_filters.CharFilter(method='my_custom_filter',label="Search")

	class Meta:
		model = variationSettings
		fields = ['q']

	def my_custom_filter(self, queryset, name, value):
		return variationSettings.objects.filter(
			Q(productID__productID=value) | Q(current_asin__icontains=value) | Q(parent_asin__icontains=value) | Q(title_en__icontains=value)
		)

class TotalVariationsFilter(django_filters.FilterSet):

	q = django_filters.CharFilter(method='my_custom_filter',label="Search")

	class Meta:
		model = totalVariations
		fields = ['q']

	def my_custom_filter(self, queryset, name, value):
		return totalVariations.objects.filter(
			Q(productID__productID=value) | Q(parent_asin__icontains=value) | Q(name_en__icontains=value) | Q(value_en__icontains=value)
		)
