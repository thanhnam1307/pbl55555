from django.urls import path
from . import views
from . import api

urlpatterns = [
    # Dashboard and home page
    path('', views.OngNuocListView.as_view(), name='product_list'),  # Renamed but keeping URL pattern
    path('dashboard/', views.dashboard, name='dashboard'),
    path('warehouse-dashboard/', views.warehouse_dashboard, name='warehouse_dashboard'),
    
    # Image upload and history
    path('upload-image/', views.upload_image, name='upload_image'),
    path('pipe-count-history/', views.pipe_count_history, name='pipe_count_history'),
    path('pipe-detection-report/', views.pipe_detection_report, name='pipe_detection_report'),
    path('pipe-detection-analytics/', views.pipe_detection_analytics, name='pipe_detection_analytics'),
    path('batch-process-images/', views.batch_process_images, name='batch_process_images'),
    path('batch-process/', views.batch_process_images, name='batch_process_images'),
    path('pipe-analytics/', views.pipe_analytics, name='pipe_analytics'),
    
    # API endpoints
    path('api/detect-pipes/', api.detect_pipes_api, name='detect_pipes_api'),
    path('api/history/', api.history_api, name='history_api'),
    path('api/dashboard-stats/', api.dashboard_stats_api, name='dashboard_stats_api'),
    
    # Báo cáo
    path('bao-cao/tong-quan/', views.bao_cao_tong_quan, name='bao_cao_tong_quan'),
    path('bao-cao/nhap-xuat/', views.bao_cao_nhap_xuat, name='bao_cao_nhap_xuat'),
    path('bao-cao/ton-kho/', views.bao_cao_ton_kho, name='bao_cao_ton_kho'),
    path('bao-cao/doi-tac/', views.bao_cao_doi_tac, name='bao_cao_doi_tac'),
    
    # Export reports
    path('export/bao-cao-ton-kho/', views.export_bao_cao_ton_kho, name='export_bao_cao_ton_kho'),
    path('export/bao-cao-nhap-xuat/', views.export_bao_cao_nhap_xuat, name='export_bao_cao_nhap_xuat'),
    path('export/bao-cao-doi-tac/', views.export_bao_cao_doi_tac, name='export_bao_cao_doi_tac'),
    
    # Inventory adjustments
    path('dieu-chinh-ton-kho/', views.dieu_chinh_ton_kho, name='dieu_chinh_ton_kho'),
    path('dieu-chinh-ton-kho/<int:pk>/', views.dieu_chinh_ton_kho_detail, name='dieu_chinh_ton_kho_detail'),
    
    # URLs for LoaiOng
    path('loai-ong/', views.LoaiOngListView.as_view(), name='loai_ong_list'),
    path('loai-ong/create/', views.LoaiOngCreateView.as_view(), name='loai_ong_create'),
    path('loai-ong/update/<int:pk>/', views.LoaiOngUpdateView.as_view(), name='loai_ong_update'),
    path('loai-ong/delete/<int:pk>/', views.LoaiOngDeleteView.as_view(), name='loai_ong_delete'),
    
    # URLs for OngNuoc
    path('ong-nuoc/', views.OngNuocListView.as_view(), name='ong_nuoc_list'),
    path('ong-nuoc/create/', views.OngNuocCreateView.as_view(), name='ong_nuoc_create'),
    path('ong-nuoc/update/<int:pk>/', views.OngNuocUpdateView.as_view(), name='ong_nuoc_update'),
    path('ong-nuoc/detail/<int:pk>/', views.OngNuocDetailView.as_view(), name='ong_nuoc_detail'),
    path('ong-nuoc/delete/<int:pk>/', views.OngNuocDeleteView.as_view(), name='ong_nuoc_delete'),
    
    # URLs for NhaCungCap
    path('nha-cung-cap/', views.NhaCungCapListView.as_view(), name='nha_cung_cap_list'),
    path('nha-cung-cap/create/', views.NhaCungCapCreateView.as_view(), name='nha_cung_cap_create'),
    path('nha-cung-cap/update/<int:pk>/', views.NhaCungCapUpdateView.as_view(), name='nha_cung_cap_update'),
    path('nha-cung-cap/delete/<int:pk>/', views.NhaCungCapDeleteView.as_view(), name='nha_cung_cap_delete'),
    
    # URLs for KhachHang
    path('khach-hang/', views.KhachHangListView.as_view(), name='khach_hang_list'),
    path('khach-hang/create/', views.KhachHangCreateView.as_view(), name='khach_hang_create'),
    path('khach-hang/update/<int:pk>/', views.KhachHangUpdateView.as_view(), name='khach_hang_update'),
    path('khach-hang/delete/<int:pk>/', views.KhachHangDeleteView.as_view(), name='khach_hang_delete'),
    
    # URLs for PhieuNhap
    path('phieu-nhap/', views.PhieuNhapListView.as_view(), name='phieu_nhap_list'),
    path('phieu-nhap/create/', views.PhieuNhapCreateView.as_view(), name='phieu_nhap_create'),
    path('phieu-nhap/update/<int:pk>/', views.PhieuNhapUpdateView.as_view(), name='phieu_nhap_update'),
    path('phieu-nhap/detail/<int:pk>/', views.PhieuNhapDetailView.as_view(), name='phieu_nhap_detail'),
    path('phieu-nhap/delete/<int:pk>/', views.PhieuNhapDeleteView.as_view(), name='phieu_nhap_delete'),
    
    # URLs for PhieuXuat
    path('phieu-xuat/', views.PhieuXuatListView.as_view(), name='phieu_xuat_list'),
    path('phieu-xuat/create/', views.PhieuXuatCreateView.as_view(), name='phieu_xuat_create'),
    path('phieu-xuat/update/<int:pk>/', views.PhieuXuatUpdateView.as_view(), name='phieu_xuat_update'),
    path('phieu-xuat/detail/<int:pk>/', views.PhieuXuatDetailView.as_view(), name='phieu_xuat_detail'),
    path('phieu-xuat/delete/<int:pk>/', views.PhieuXuatDeleteView.as_view(), name='phieu_xuat_delete'),
    
    # URLs for PhieuNhapChiTiet
    path('phieu-nhap-chi-tiet/create/<int:phieu_nhap_id>/', views.PhieuNhapChiTietCreateView.as_view(), name='phieu_nhap_chi_tiet_create'),
    path('phieu-nhap-chi-tiet/update/<int:pk>/', views.PhieuNhapChiTietUpdateView.as_view(), name='phieu_nhap_chi_tiet_update'),
    path('phieu-nhap-chi-tiet/delete/<int:pk>/', views.PhieuNhapChiTietDeleteView.as_view(), name='phieu_nhap_chi_tiet_delete'),
    
    # URLs for PhieuXuatChiTiet
    path('phieu-xuat-chi-tiet/create/<int:phieu_xuat_id>/', views.PhieuXuatChiTietCreateView.as_view(), name='phieu_xuat_chi_tiet_create'),
    path('phieu-xuat-chi-tiet/update/<int:pk>/', views.PhieuXuatChiTietUpdateView.as_view(), name='phieu_xuat_chi_tiet_update'),
    path('phieu-xuat-chi-tiet/delete/<int:pk>/', views.PhieuXuatChiTietDeleteView.as_view(), name='phieu_xuat_chi_tiet_delete'),
]