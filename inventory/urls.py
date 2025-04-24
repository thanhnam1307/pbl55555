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
    path('dashboard/', views.dashboard, name='dashboard'),
    # API endpoints
    path('api/detect-pipes/', api.detect_pipes_api, name='detect_pipes_api'),
    path('api/history/', api.history_api, name='history_api'),
    path('api/dashboard-stats/', api.dashboard_stats_api, name='dashboard_stats_api'),
]