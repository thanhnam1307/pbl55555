from django.db import models
from django.utils import timezone

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100)
    diameter = models.FloatField(help_text='Diameter in inches')
    length = models.FloatField(help_text='Length in feet')
    quantity = models.IntegerField(default=0)
    import_date = models.DateField(default=timezone.now)
    image = models.ImageField(upload_to='warehouse_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.diameter}\" x {self.length}'"

class WaterPipeCountHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='count_history')
    count = models.IntegerField()
    timestamp = models.DateTimeField(default=timezone.now)
    original_image = models.ImageField(upload_to='history/original/', null=True, blank=True)
    processed_image = models.ImageField(upload_to='history/processed/', null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Water Pipe Count History"
        verbose_name_plural = "Water Pipe Count History Records"

    def __str__(self):
        return f"{self.product.name} - {self.count} pipes at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

# New models for pipe warehouse management
class LoaiOng(models.Model):
    ma_loai = models.AutoField(primary_key=True)
    ten_loai = models.CharField(max_length=100)
    mo_ta = models.TextField(blank=True, null=True)
    don_vi_tinh = models.CharField(max_length=20)

    def __str__(self):
        return self.ten_loai
    
    class Meta:
        verbose_name = "Loại Ống"
        verbose_name_plural = "Loại Ống"

class OngNuoc(models.Model):
    ma_ong = models.AutoField(primary_key=True)
    ma_loai = models.ForeignKey(LoaiOng, on_delete=models.CASCADE, related_name='ong_nuoc')
    ten_ong = models.CharField(max_length=100)
    kich_thuoc = models.CharField(max_length=50)
    chat_lieu = models.CharField(max_length=100)
    ap_luc_toi_da = models.DecimalField(max_digits=10, decimal_places=2, help_text='Đơn vị: bar')
    so_met_ton = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    anh_minh_hoa = models.ImageField(upload_to='warehouse_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.ten_ong} - {self.kich_thuoc}"
    
    class Meta:
        verbose_name = "Ống Nước"
        verbose_name_plural = "Ống Nước"

class NhaCungCap(models.Model):
    ma_ncc = models.AutoField(primary_key=True)
    ten_ncc = models.CharField(max_length=200)
    sdt = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    dia_chi = models.TextField()

    def __str__(self):
        return self.ten_ncc
    
    class Meta:
        verbose_name = "Nhà Cung Cấp"
        verbose_name_plural = "Nhà Cung Cấp"

class KhachHang(models.Model):
    ma_kh = models.AutoField(primary_key=True)
    ten_kh = models.CharField(max_length=200)
    sdt = models.CharField(max_length=15)
    dia_chi = models.TextField()
    ma_so_thue = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.ten_kh
    
    class Meta:
        verbose_name = "Khách Hàng"
        verbose_name_plural = "Khách Hàng"

class PhieuNhap(models.Model):
    ma_phieu_nhap = models.AutoField(primary_key=True)
    ma_ncc = models.ForeignKey(NhaCungCap, on_delete=models.CASCADE, related_name='phieu_nhap')
    ngay_nhap = models.DateField(default=timezone.now)
    tong_tien = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    nguoi_tao = models.CharField(max_length=100)
    ghi_chu = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"PN-{self.ma_phieu_nhap} - {self.ngay_nhap}"
    
    class Meta:
        verbose_name = "Phiếu Nhập"
        verbose_name_plural = "Phiếu Nhập"

class PhieuNhapChiTiet(models.Model):
    ma_ct_phieu_nhap = models.AutoField(primary_key=True)
    ma_phieu_nhap = models.ForeignKey(PhieuNhap, on_delete=models.CASCADE, related_name='chi_tiet')
    ma_ong = models.ForeignKey(OngNuoc, on_delete=models.CASCADE, related_name='phieu_nhap_chi_tiet')
    so_luong = models.DecimalField(max_digits=10, decimal_places=2)
    don_gia = models.DecimalField(max_digits=15, decimal_places=2)

    @property
    def thanh_tien(self):
        return self.so_luong * self.don_gia

    def __str__(self):
        return f"CTPN-{self.ma_ct_phieu_nhap} - {self.ma_ong.ten_ong}"
    
    class Meta:
        verbose_name = "Chi Tiết Phiếu Nhập"
        verbose_name_plural = "Chi Tiết Phiếu Nhập"

class PhieuXuat(models.Model):
    ma_phieu_xuat = models.AutoField(primary_key=True)
    ma_kh = models.ForeignKey(KhachHang, on_delete=models.CASCADE, related_name='phieu_xuat')
    ngay_xuat = models.DateField(default=timezone.now)
    tong_tien = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    nguoi_tao = models.CharField(max_length=100)
    ghi_chu = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"PX-{self.ma_phieu_xuat} - {self.ngay_xuat}"
    
    class Meta:
        verbose_name = "Phiếu Xuất"
        verbose_name_plural = "Phiếu Xuất"

class PhieuXuatChiTiet(models.Model):
    ma_ct_phieu_xuat = models.AutoField(primary_key=True)
    ma_phieu_xuat = models.ForeignKey(PhieuXuat, on_delete=models.CASCADE, related_name='chi_tiet')
    ma_ong = models.ForeignKey(OngNuoc, on_delete=models.CASCADE, related_name='phieu_xuat_chi_tiet')
    so_luong = models.DecimalField(max_digits=10, decimal_places=2)
    don_gia = models.DecimalField(max_digits=15, decimal_places=2)

    @property
    def thanh_tien(self):
        return self.so_luong * self.don_gia

    def __str__(self):
        return f"CTPX-{self.ma_ct_phieu_xuat} - {self.ma_ong.ten_ong}"
    
    class Meta:
        verbose_name = "Chi Tiết Phiếu Xuất"
        verbose_name_plural = "Chi Tiết Phiếu Xuất"
