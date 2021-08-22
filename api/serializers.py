from rest_framework import serializers

from scrapper.models import *

class productPagesScrapperSerializer(serializers.ModelSerializer):
	class Meta:
		model = productPagesScrapper
		fields = ['productID','category','title_en','title_ar']