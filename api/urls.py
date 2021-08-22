from django.urls import path
from . import views

urlpatterns = [
	path('', views.overview),
	path('<str:asin>/', views.product),
	path('details/<str:asin>/', views.singleProductDetails),
	path('variation/<str:asin>/', views.productVaraitions),
	path('category/<str:category>/', views.categoryDetails),
]