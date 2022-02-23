from django.urls import path
from client.views import *


urlpatterns = [
    path('countries', get_countries),
    path('cities', get_cities),
    path('patch_user_profile', patch_user_profile),
    path('get_profile', get_profile),
    path('upload_sales_file', upload_sales_file),
    path('sale_statistics/', sale_statistics),
]
