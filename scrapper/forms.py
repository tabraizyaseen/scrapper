from django.forms import ModelForm
from .models import *

class DetailsForm(ModelForm):
    class Meta:
        model = productDetails
        fields = '__all__'
