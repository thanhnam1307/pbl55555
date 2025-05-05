from django.contrib import admin
from .models import OngNuoc, LoaiOng, NhaCungCap, KhachHang, PhieuNhap, PhieuNhapChiTiet, PhieuXuat, PhieuXuatChiTiet

@admin.register(OngNuoc)
class OngNuocAdmin(admin.ModelAdmin):
    list_display = ('ten_ong', 'kich_thuoc', 'chat_lieu', 'so_met_ton')
    search_fields = ('ten_ong',)
    list_filter = ('ma_loai',)

@admin.register(LoaiOng)
class LoaiOngAdmin(admin.ModelAdmin):
    list_display = ('ten_loai',)
    search_fields = ('ten_loai',)

@admin.register(NhaCungCap)
class NhaCungCapAdmin(admin.ModelAdmin):
    list_display = ('ten_ncc', 'sdt', 'email', 'dia_chi')
    search_fields = ('ten_ncc',)

@admin.register(KhachHang)
class KhachHangAdmin(admin.ModelAdmin):
    list_display = ('ten_kh', 'sdt', 'dia_chi', 'ma_so_thue')
    search_fields = ('ten_kh',)

@admin.register(PhieuNhap)
class PhieuNhapAdmin(admin.ModelAdmin):
    list_display = ('ma_phieu_nhap', 'ma_ncc', 'ngay_nhap', 'tong_tien', 'nguoi_tao')
    search_fields = ('ma_phieu_nhap',)
    list_filter = ('ngay_nhap',)

@admin.register(PhieuNhapChiTiet)
class PhieuNhapChiTietAdmin(admin.ModelAdmin):
    list_display = ('ma_ct_phieu_nhap', 'ma_phieu_nhap', 'ma_ong', 'so_luong', 'don_gia')
    search_fields = ('ma_ct_phieu_nhap',)

@admin.register(PhieuXuat)
class PhieuXuatAdmin(admin.ModelAdmin):
    list_display = ('ma_phieu_xuat', 'ma_kh', 'ngay_xuat', 'tong_tien', 'nguoi_tao')
    search_fields = ('ma_phieu_xuat',)
    list_filter = ('ngay_xuat',)

@admin.register(PhieuXuatChiTiet)
class PhieuXuatChiTietAdmin(admin.ModelAdmin):
    list_display = ('ma_ct_phieu_xuat', 'ma_phieu_xuat', 'ma_ong', 'so_luong', 'don_gia')
    search_fields = ('ma_ct_phieu_xuat',)
