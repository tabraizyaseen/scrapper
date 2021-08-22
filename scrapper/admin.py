from django.contrib import admin
from .models import *

# Register your models here.
# admin.site.register(productPagesScrapper)
# admin.site.register(productDetails)
# admin.site.register(productHighlights)
# admin.site.register(productDescription)
# admin.site.register(productImages)
# admin.site.register(variationSettings)
# admin.site.register(totalVariations)
# admin.site.register(fc_grades)

@admin.register(productPagesScrapper)
class productsAdmin(admin.ModelAdmin):
	fields = ('source','category','title_en','title_ar','price','old_price')
	list_display = ('productID','title_en')
	# list_filter = ('category',)
	empty_value_display = '-empty-'
	search_fields = ('title_en','productID','category')

@admin.register(productDetails)
class productsDetailsAdmin(admin.ModelAdmin):
	fields = ('attributes','values','language')
	list_display = ('productID','attributes')
	empty_value_display = '-empty-'
	search_fields = ('attributes','productID__productID')

@admin.register(productHighlights)
class productHighlightsAdmin(admin.ModelAdmin):
	fields = ('highlight','language')
	list_display = ('productID','highlight')
	empty_value_display = '-empty-'
	search_fields = ('highlight','productID__productID')

@admin.register(productDescription)
class productDescriptionAdmin(admin.ModelAdmin):
	fields = ('long_description','language')
	list_display = ('productID','language')
	empty_value_display = '-empty-'
	search_fields = ('productID__productID',)

@admin.register(productImages)
class productImagesAdmin(admin.ModelAdmin):
	fields = ('image',)
	list_display = ('productID','image')
	empty_value_display = '-empty-'
	search_fields = ('productID__productID',)

@admin.register(variationSettings)
class variationSettingsAdmin(admin.ModelAdmin):
	fields = ('dimension','dimension_val_en','dimension_val_ar','title_en','title_ar','images','price','old_price')
	list_display = ('current_asin','title_en')
	empty_value_display = '-empty-'
	search_fields = ('current_asin', 'title_en')

@admin.register(totalVariations)
class totalVariationsAdmin(admin.ModelAdmin):
	fields = ('name_en','name_ar','value_en','value_ar')
	list_display = ('productID','name_en')
	empty_value_display = '-empty-'
	search_fields = ('name_en','productID__productID')

@admin.register(fc_grades)
class fc_gradesAdmin(admin.ModelAdmin):
	list_display = ('grade_code','grade')
	search_fields = ('grade','grade_code')

# Admin Customization
admin.site.site_header = "Web Scrapper Administration"
admin.site.site_title = "Admin Dashboard"
admin.site.index_title = "Welcome to Admin Dashboard"