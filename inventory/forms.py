from django import forms
from .models import (
    LoaiOng, OngNuoc, NhaCungCap, 
    KhachHang, PhieuNhap, PhieuXuat, 
    PhieuNhapChiTiet, PhieuXuatChiTiet
)

# Cập nhật ImageUploadForm để chỉ sử dụng OngNuoc mới
class ImageUploadForm(forms.Form):
    ong_nuoc = forms.ModelChoiceField(
        queryset=OngNuoc.objects.all(),
        label='Chọn ống nước',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    image = forms.ImageField(
        label='Tải lên hình ảnh',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        ong_nuoc = cleaned_data.get('ong_nuoc')
        
        if not ong_nuoc:
            self.add_error('ong_nuoc', 'Vui lòng chọn ống nước.')
        
        return cleaned_data

# New forms for warehouse pipe management models
class LoaiOngForm(forms.ModelForm):
    class Meta:
        model = LoaiOng
        fields = ['ten_loai', 'mo_ta', 'don_vi_tinh']
        widgets = {
            'mo_ta': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'ten_loai': 'Tên loại ống',
            'mo_ta': 'Mô tả',
            'don_vi_tinh': 'Đơn vị tính',
        }
        
class OngNuocForm(forms.ModelForm):
    class Meta:
        model = OngNuoc
        fields = ['ma_loai', 'ten_ong', 'kich_thuoc', 'chat_lieu', 'ap_luc_toi_da', 'so_met_ton', 'anh_minh_hoa']
        widgets = {
            'ap_luc_toi_da': forms.NumberInput(attrs={'step': '0.01'}),
            'so_met_ton': forms.NumberInput(attrs={'step': '0.01'}),
        }
        labels = {
            'ma_loai': 'Loại ống',
            'ten_ong': 'Tên ống',
            'kich_thuoc': 'Kích thước',
            'chat_lieu': 'Chất liệu',
            'ap_luc_toi_da': 'Áp lực tối đa (bar)',
            'so_met_ton': 'Số mét tồn kho',
            'anh_minh_hoa': 'Ảnh minh họa',
        }

class NhaCungCapForm(forms.ModelForm):
    class Meta:
        model = NhaCungCap
        fields = ['ten_ncc', 'sdt', 'email', 'dia_chi']
        widgets = {
            'dia_chi': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'ten_ncc': 'Tên nhà cung cấp',
            'sdt': 'Số điện thoại',
            'email': 'Email',
            'dia_chi': 'Địa chỉ',
        }

class KhachHangForm(forms.ModelForm):
    class Meta:
        model = KhachHang
        fields = ['ten_kh', 'sdt', 'dia_chi', 'ma_so_thue']
        widgets = {
            'dia_chi': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'ten_kh': 'Tên khách hàng',
            'sdt': 'Số điện thoại',
            'dia_chi': 'Địa chỉ',
            'ma_so_thue': 'Mã số thuế',
        }

class PhieuNhapForm(forms.ModelForm):
    class Meta:
        model = PhieuNhap
        fields = ['ma_ncc', 'ngay_nhap', 'tong_tien', 'nguoi_tao', 'ghi_chu']
        widgets = {
            'ngay_nhap': forms.DateInput(attrs={'type': 'date'}),
            'tong_tien': forms.NumberInput(attrs={'step': '0.01'}),
            'ghi_chu': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'ma_ncc': 'Nhà cung cấp',
            'ngay_nhap': 'Ngày nhập',
            'tong_tien': 'Tổng tiền',
            'nguoi_tao': 'Người tạo',
            'ghi_chu': 'Ghi chú',
        }

class PhieuXuatForm(forms.ModelForm):
    class Meta:
        model = PhieuXuat
        fields = ['ma_kh', 'ngay_xuat', 'tong_tien', 'nguoi_tao', 'ghi_chu']
        widgets = {
            'ngay_xuat': forms.DateInput(attrs={'type': 'date'}),
            'tong_tien': forms.NumberInput(attrs={'step': '0.01'}),
            'ghi_chu': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'ma_kh': 'Khách hàng',
            'ngay_xuat': 'Ngày xuất',
            'tong_tien': 'Tổng tiền',
            'nguoi_tao': 'Người tạo',
            'ghi_chu': 'Ghi chú',
        }

class PhieuNhapChiTietForm(forms.ModelForm):
    class Meta:
        model = PhieuNhapChiTiet
        fields = ['ma_phieu_nhap', 'ma_ong', 'so_luong', 'don_gia']
        widgets = {
            'so_luong': forms.NumberInput(attrs={'step': '0.01'}),
            'don_gia': forms.NumberInput(attrs={'step': '0.01'}),
        }
        labels = {
            'ma_phieu_nhap': 'Phiếu nhập',
            'ma_ong': 'Ống nước',
            'so_luong': 'Số lượng',
            'don_gia': 'Đơn giá',
        }

class PhieuXuatChiTietForm(forms.ModelForm):
    class Meta:
        model = PhieuXuatChiTiet
        fields = ['ma_phieu_xuat', 'ma_ong', 'so_luong', 'don_gia']
        widgets = {
            'so_luong': forms.NumberInput(attrs={'step': '0.01'}),
            'don_gia': forms.NumberInput(attrs={'step': '0.01'}),
        }
        labels = {
            'ma_phieu_xuat': 'Phiếu xuất',
            'ma_ong': 'Ống nước',
            'so_luong': 'Số lượng',
            'don_gia': 'Đơn giá',
        }

# Search forms
class LoaiOngSearchForm(forms.Form):
    search_term = forms.CharField(
        required=False, 
        label='Tìm kiếm',
        widget=forms.TextInput(attrs={'placeholder': 'Tìm theo tên loại ống...'})
    )

class OngNuocSearchForm(forms.Form):
    search_term = forms.CharField(
        required=False, 
        label='Tìm kiếm',
        widget=forms.TextInput(attrs={'placeholder': 'Tìm theo tên ống...'})
    )
    loai_ong = forms.ModelChoiceField(
        queryset=LoaiOng.objects.all(),
        required=False,
        label='Lọc theo loại',
        empty_label="Tất cả các loại"
    )

class NhaCungCapSearchForm(forms.Form):
    search_term = forms.CharField(
        required=False, 
        label='Tìm kiếm',
        widget=forms.TextInput(attrs={'placeholder': 'Tìm theo tên hoặc số điện thoại...'})
    )

class KhachHangSearchForm(forms.Form):
    search_term = forms.CharField(
        required=False, 
        label='Tìm kiếm',
        widget=forms.TextInput(attrs={'placeholder': 'Tìm theo tên hoặc số điện thoại...'})
    )

class PhieuNhapSearchForm(forms.Form):
    search_term = forms.CharField(
        required=False, 
        label='Tìm kiếm',
        widget=forms.TextInput(attrs={'placeholder': 'Tìm kiếm...'})
    )
    from_date = forms.DateField(
        required=False, 
        label='Từ ngày',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    to_date = forms.DateField(
        required=False, 
        label='Đến ngày',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    nha_cung_cap = forms.ModelChoiceField(
        queryset=NhaCungCap.objects.all(),
        required=False,
        label='Nhà cung cấp',
        empty_label="Tất cả nhà cung cấp"
    )

class PhieuXuatSearchForm(forms.Form):
    search_term = forms.CharField(
        required=False, 
        label='Tìm kiếm',
        widget=forms.TextInput(attrs={'placeholder': 'Tìm kiếm...'})
    )
    from_date = forms.DateField(
        required=False, 
        label='Từ ngày',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    to_date = forms.DateField(
        required=False, 
        label='Đến ngày',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    khach_hang = forms.ModelChoiceField(
        queryset=KhachHang.objects.all(),
        required=False,
        label='Khách hàng',
        empty_label="Tất cả khách hàng"
    )