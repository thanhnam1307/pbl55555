from django.urls import path
from . import views
from . import api

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('create/', views.product_create, name='product_create'),
    path('update/<int:pk>/', views.product_update, name='product_update'),
    path('delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('upload-image/', views.upload_image, name='upload_image'),
    path('pipe-count-history/', views.pipe_count_history, name='pipe_count_history'),
    # API endpoint
    path('api/detect-pipes/', api.detect_pipes_api, name='detect_pipes_api'),
]