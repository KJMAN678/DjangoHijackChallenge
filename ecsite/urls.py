from django.urls import path
from . import views

app_name = 'ecsite'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('purchase/<int:product_id>/', views.purchase_product, name='purchase_product'),
    path('purchase-history/', views.purchase_history, name='purchase_history'),
]
