from django.urls import path
from . import views
from . import api

urlpatterns = [
    # Existing URLs
    path('', views.product_list, name='product_list'),
    path('create/', views.product_create, name='product_create'),
    path('update/<int:pk>/', views.product_update, name='product_update'),
    path('delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('upload-image/', views.upload_image, name='upload_image'),
    path('pipe-count-history/', views.pipe_count_history, name='pipe_count_history'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # New warehouse dashboard
    path('warehouse-dashboard/', views.warehouse_dashboard, name='warehouse_dashboard'),
    
    # API endpoints
    path('api/detect-pipes/', api.detect_pipes_api, name='detect_pipes_api'),
    path('api/history/', api.history_api, name='history_api'),
    path('api/dashboard-stats/', api.dashboard_stats_api, name='dashboard_stats_api'),
    
    # URLs for LoaiOng
    path('loai-ong/', views.LoaiOngListView.as_view(), name='loai_ong_list'),
    path('loai-ong/create/', views.LoaiOngCreateView.as_view(), name='loai_ong_create'),
    path('loai-ong/update/<int:pk>/', views.LoaiOngUpdateView.as_view(), name='loai_ong_update'),
    
    # URLs for OngNuoc
    path('ong-nuoc/', views.OngNuocListView.as_view(), name='ong_nuoc_list'),
    path('ong-nuoc/create/', views.OngNuocCreateView.as_view(), name='ong_nuoc_create'),
    path('ong-nuoc/update/<int:pk>/', views.OngNuocUpdateView.as_view(), name='ong_nuoc_update'),
    path('ong-nuoc/detail/<int:pk>/', views.OngNuocDetailView.as_view(), name='ong_nuoc_detail'),
    
    # URLs for NhaCungCap
    path('nha-cung-cap/', views.NhaCungCapListView.as_view(), name='nha_cung_cap_list'),
    path('nha-cung-cap/create/', views.NhaCungCapCreateView.as_view(), name='nha_cung_cap_create'),
    path('nha-cung-cap/update/<int:pk>/', views.NhaCungCapUpdateView.as_view(), name='nha_cung_cap_update'),
    
    # URLs for KhachHang
    path('khach-hang/', views.KhachHangListView.as_view(), name='khach_hang_list'),
    path('khach-hang/create/', views.KhachHangCreateView.as_view(), name='khach_hang_create'),
    path('khach-hang/update/<int:pk>/', views.KhachHangUpdateView.as_view(), name='khach_hang_update'),
    
    # URLs for PhieuNhap
    path('phieu-nhap/', views.PhieuNhapListView.as_view(), name='phieu_nhap_list'),
    path('phieu-nhap/create/', views.PhieuNhapCreateView.as_view(), name='phieu_nhap_create'),
    path('phieu-nhap/update/<int:pk>/', views.PhieuNhapUpdateView.as_view(), name='phieu_nhap_update'),
    path('phieu-nhap/detail/<int:pk>/', views.PhieuNhapDetailView.as_view(), name='phieu_nhap_detail'),
    
    # URLs for PhieuXuat
    path('phieu-xuat/', views.PhieuXuatListView.as_view(), name='phieu_xuat_list'),
    path('phieu-xuat/create/', views.PhieuXuatCreateView.as_view(), name='phieu_xuat_create'),
    path('phieu-xuat/update/<int:pk>/', views.PhieuXuatUpdateView.as_view(), name='phieu_xuat_update'),
    path('phieu-xuat/detail/<int:pk>/', views.PhieuXuatDetailView.as_view(), name='phieu_xuat_detail'),
]