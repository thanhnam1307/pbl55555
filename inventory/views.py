import os
import json
import requests
import csv
import xlwt
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from .models import (
    WaterPipeCountHistory, 
    LoaiOng, OngNuoc, NhaCungCap, KhachHang, 
    PhieuNhap, PhieuXuat, PhieuNhapChiTiet, PhieuXuatChiTiet,
    DieuChinhTonKho
)
from .forms import (
    ImageUploadForm,
    LoaiOngForm, OngNuocForm, NhaCungCapForm, KhachHangForm,
    PhieuNhapForm, PhieuXuatForm, PhieuNhapChiTietForm, PhieuXuatChiTietForm,
    LoaiOngSearchForm, OngNuocSearchForm, NhaCungCapSearchForm, KhachHangSearchForm,
    PhieuNhapSearchForm, PhieuXuatSearchForm, DieuChinhTonKhoForm
)

# Basic Product CRUD functions đã bị xóa

# New Delete Views
class LoaiOngDeleteView(DeleteView):
    model = LoaiOng
    template_name = 'inventory/loai_ong_confirm_delete.html'
    success_url = reverse_lazy('loai_ong_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Loại ống đã được xóa thành công.')
        return super().delete(request, *args, **kwargs)

class OngNuocDeleteView(DeleteView):
    model = OngNuoc
    template_name = 'inventory/ong_nuoc_confirm_delete.html'
    success_url = reverse_lazy('ong_nuoc_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Ống nước đã được xóa thành công.')
        return super().delete(request, *args, **kwargs)

class NhaCungCapDeleteView(DeleteView):
    model = NhaCungCap
    template_name = 'inventory/nha_cung_cap_confirm_delete.html'
    success_url = reverse_lazy('nha_cung_cap_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Nhà cung cấp đã được xóa thành công.')
        return super().delete(request, *args, **kwargs)

class PhieuNhapDeleteView(DeleteView):
    model = PhieuNhap
    template_name = 'inventory/phieu_nhap_confirm_delete.html'
    success_url = reverse_lazy('phieu_nhap_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Phiếu nhập đã được xóa thành công.')
        return super().delete(request, *args, **kwargs)

class PhieuXuatDeleteView(DeleteView):
    model = PhieuXuat
    template_name = 'inventory/phieu_xuat_confirm_delete.html'
    success_url = reverse_lazy('phieu_xuat_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Phiếu xuất đã được xóa thành công.')
        return super().delete(request, *args, **kwargs)

# Phieu Nhap Chi Tiet views
class PhieuNhapChiTietCreateView(CreateView):
    model = PhieuNhapChiTiet
    form_class = PhieuNhapChiTietForm
    template_name = 'inventory/phieu_nhap_chi_tiet_form.html'
    
    def get_success_url(self):
        return reverse_lazy('phieu_nhap_detail', kwargs={'pk': self.kwargs['phieu_nhap_id']})
    
    def get_initial(self):
        initial = super().get_initial()
        initial['ma_phieu_nhap'] = self.kwargs['phieu_nhap_id']
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['phieu_nhap'] = get_object_or_404(PhieuNhap, pk=self.kwargs['phieu_nhap_id'])
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Cập nhật số lượng tồn kho
        chi_tiet = self.object
        ong_nuoc = chi_tiet.ma_ong
        ong_nuoc.so_met_ton += chi_tiet.so_met
        ong_nuoc.save()
        
        messages.success(self.request, 'Chi tiết phiếu nhập đã được thêm thành công.')
        return response

class PhieuNhapChiTietUpdateView(UpdateView):
    model = PhieuNhapChiTiet
    form_class = PhieuNhapChiTietForm
    template_name = 'inventory/phieu_nhap_chi_tiet_form.html'
    
    def get_success_url(self):
        return reverse_lazy('phieu_nhap_detail', kwargs={'pk': self.object.ma_phieu_nhap.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['phieu_nhap'] = self.object.ma_phieu_nhap
        return context
    
    def form_valid(self, form):
        # Lấy số lượng cũ trước khi cập nhật
        chi_tiet_cu = PhieuNhapChiTiet.objects.get(pk=self.object.pk)
        so_met_cu = chi_tiet_cu.so_met
        
        response = super().form_valid(form)
        
        # Cập nhật số lượng tồn kho
        chi_tiet = self.object
        ong_nuoc = chi_tiet.ma_ong
        
        # Tính chênh lệch để cập nhật tồn kho
        so_met_moi = chi_tiet.so_met
        chenh_lech = so_met_moi - so_met_cu
        
        ong_nuoc.so_met_ton += chenh_lech
        ong_nuoc.save()
        
        messages.success(self.request, 'Chi tiết phiếu nhập đã được cập nhật thành công.')
        return response

class PhieuNhapChiTietDeleteView(DeleteView):
    model = PhieuNhapChiTiet
    template_name = 'inventory/phieu_nhap_chi_tiet_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('phieu_nhap_detail', kwargs={'pk': self.object.ma_phieu_nhap.pk})
    
    def delete(self, request, *args, **kwargs):
        chi_tiet = self.get_object()
        ong_nuoc = chi_tiet.ma_ong
        
        # Trừ số lượng khỏi tồn kho
        ong_nuoc.so_met_ton -= chi_tiet.so_met
        ong_nuoc.save()
        
        messages.success(request, 'Chi tiết phiếu nhập đã được xóa thành công.')
        return super().delete(request, *args, **kwargs)

# Phieu Xuat Chi Tiet views
class PhieuXuatChiTietCreateView(CreateView):
    model = PhieuXuatChiTiet
    form_class = PhieuXuatChiTietForm
    template_name = 'inventory/phieu_xuat_chi_tiet_form.html'
    
    def get_success_url(self):
        return reverse_lazy('phieu_xuat_detail', kwargs={'pk': self.kwargs['phieu_xuat_id']})
    
    def get_initial(self):
        initial = super().get_initial()
        initial['ma_phieu_xuat'] = self.kwargs['phieu_xuat_id']
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['phieu_xuat'] = get_object_or_404(PhieuXuat, pk=self.kwargs['phieu_xuat_id'])
        context['ong_nuoc_list'] = OngNuoc.objects.filter(so_met_ton__gt=0)
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Cập nhật số lượng tồn kho
        chi_tiet = self.object
        ong_nuoc = chi_tiet.ma_ong
        
        # Kiểm tra nếu số lượng xuất lớn hơn tồn kho
        if chi_tiet.so_met > ong_nuoc.so_met_ton:
            self.object.delete()  # Xóa chi tiết vừa tạo
            messages.error(self.request, f'Số lượng xuất ({chi_tiet.so_met} mét) lớn hơn số lượng tồn kho ({ong_nuoc.so_met_ton} mét).')
            return redirect('phieu_xuat_chi_tiet_create', phieu_xuat_id=self.kwargs['phieu_xuat_id'])
        
        ong_nuoc.so_met_ton -= chi_tiet.so_met
        ong_nuoc.save()
        
        messages.success(self.request, 'Chi tiết phiếu xuất đã được thêm thành công.')
        return response

class PhieuXuatChiTietUpdateView(UpdateView):
    model = PhieuXuatChiTiet
    form_class = PhieuXuatChiTietForm
    template_name = 'inventory/phieu_xuat_chi_tiet_form.html'
    
    def get_success_url(self):
        return reverse_lazy('phieu_xuat_detail', kwargs={'pk': self.object.ma_phieu_xuat.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['phieu_xuat'] = self.object.ma_phieu_xuat
        return context
    
    def form_valid(self, form):
        # Lấy số lượng cũ trước khi cập nhật
        chi_tiet_cu = PhieuXuatChiTiet.objects.get(pk=self.object.pk)
        so_met_cu = chi_tiet_cu.so_met
        ong_nuoc = chi_tiet_cu.ma_ong
        
        # Hoàn trả số lượng cũ về tồn kho
        ong_nuoc.so_met_ton += so_met_cu
        
        response = super().form_valid(form)
        
        # Trừ số lượng mới
        chi_tiet = self.object
        ong_nuoc = chi_tiet.ma_ong
        
        # Kiểm tra nếu số lượng xuất lớn hơn tồn kho
        if chi_tiet.so_met > ong_nuoc.so_met_ton:
            # Hoàn trả về trạng thái ban đầu
            chi_tiet.so_met = so_met_cu
            chi_tiet.save()
            ong_nuoc.so_met_ton -= so_met_cu
            ong_nuoc.save()
            
            messages.error(self.request, f'Số lượng xuất ({chi_tiet.so_met} mét) lớn hơn số lượng tồn kho ({ong_nuoc.so_met_ton + so_met_cu} mét).')
            return redirect('phieu_xuat_chi_tiet_update', pk=self.object.pk)
        
        ong_nuoc.so_met_ton -= chi_tiet.so_met
        ong_nuoc.save()
        
        messages.success(self.request, 'Chi tiết phiếu xuất đã được cập nhật thành công.')
        return response

class PhieuXuatChiTietDeleteView(DeleteView):
    model = PhieuXuatChiTiet
    template_name = 'inventory/phieu_xuat_chi_tiet_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('phieu_xuat_detail', kwargs={'pk': self.object.ma_phieu_xuat.pk})
    
    def delete(self, request, *args, **kwargs):
        chi_tiet = self.get_object()
        ong_nuoc = chi_tiet.ma_ong
        
        # Hoàn trả số lượng vào tồn kho
        ong_nuoc.so_met_ton += chi_tiet.so_met
        ong_nuoc.save()
        
        messages.success(request, 'Chi tiết phiếu xuất đã được xóa thành công.')
        return super().delete(request, *args, **kwargs)

# Inventory adjustment functionality
@login_required
def dieu_chinh_ton_kho(request):
    """
    Hiển thị danh sách các lần điều chỉnh tồn kho và form tạo mới
    """
    if request.method == 'POST':
        form = DieuChinhTonKhoForm(request.POST)
        if form.is_valid():
            dieu_chinh = form.save(commit=False)
            ong_nuoc = dieu_chinh.ma_ong
            
            # Lưu số lượng tồn kho trước khi điều chỉnh
            dieu_chinh.so_met_truoc = ong_nuoc.so_met_ton
            
            # Xác định loại điều chỉnh và cập nhật tồn kho
            if dieu_chinh.loai_dieu_chinh == 'tang':
                ong_nuoc.so_met_ton += dieu_chinh.so_met
                dieu_chinh.so_met_sau = ong_nuoc.so_met_ton
            else:  # 'giam'
                if ong_nuoc.so_met_ton < dieu_chinh.so_met:
                    messages.error(request, f'Số lượng giảm ({dieu_chinh.so_met} mét) lớn hơn số lượng tồn kho ({ong_nuoc.so_met_ton} mét).')
                    return redirect('dieu_chinh_ton_kho')
                
                ong_nuoc.so_met_ton -= dieu_chinh.so_met
                dieu_chinh.so_met_sau = ong_nuoc.so_met_ton
            
            # Lưu thay đổi
            ong_nuoc.save()
            dieu_chinh.nguoi_tao = request.user.username if request.user.is_authenticated else 'Unknown'
            dieu_chinh.save()
            
            messages.success(request, f'Đã điều chỉnh tồn kho thành công. Số lượng tồn kho mới: {ong_nuoc.so_met_ton} mét.')
            return redirect('dieu_chinh_ton_kho')
    else:
        form = DieuChinhTonKhoForm()
    
    # Lấy danh sách các lần điều chỉnh
    dieu_chinh_list = DieuChinhTonKho.objects.all().order_by('-ngay_dieu_chinh')
    
    return render(request, 'inventory/dieu_chinh_ton_kho.html', {
        'form': form,
        'dieu_chinh_list': dieu_chinh_list
    })

@login_required
def dieu_chinh_ton_kho_detail(request, pk):
    """
    Hiển thị chi tiết một lần điều chỉnh tồn kho
    """
    dieu_chinh = get_object_or_404(DieuChinhTonKho, pk=pk)
    
    return render(request, 'inventory/dieu_chinh_ton_kho_detail.html', {
        'dieu_chinh': dieu_chinh
    })

# Export functionality
@login_required
def export_bao_cao_ton_kho(request):
    """
    Xuất báo cáo tồn kho ra file Excel
    """
    # Lấy filter từ URL nếu có
    loai_ong_id = request.GET.get('loai_ong')
    search_term = request.GET.get('search_term')
    
    # Query danh sách ống nước
    ong_nuoc_query = OngNuoc.objects
    
    if loai_ong_id and loai_ong_id != '':
        ong_nuoc_query = ong_nuoc_query.filter(ma_loai=loai_ong_id)
    
    if search_term:
        ong_nuoc_query = ong_nuoc_query.filter(
            Q(ten_ong__icontains=search_term) | 
            Q(kich_thuoc__icontains=search_term) |
            Q(chat_lieu__icontains=search_term)
        )
    
    ong_nuoc_list = ong_nuoc_query.order_by('ma_loai', 'ten_ong')
    
    # Tạo workbook Excel
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Báo cáo tồn kho')
    
    # Sheet header, first row
    row_num = 0
    
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    
    columns = ['Mã ống', 'Tên ống', 'Loại ống', 'Kích thước', 'Chất liệu', 'Số mét tồn', 'Đơn giá', 'Thành tiền']
    
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    
    for ong in ong_nuoc_list:
        row_num += 1
        
        # Tìm đơn giá mới nhất từ phiếu nhập
        phieu_nhap_gan_nhat = PhieuNhapChiTiet.objects.filter(
            ma_ong=ong
        ).order_by('-ma_phieu_nhap__ngay_nhap').first()
        
        don_gia = 0
        if phieu_nhap_gan_nhat:
            don_gia = phieu_nhap_gan_nhat.don_gia
        
        thanh_tien = ong.so_met_ton * don_gia
        
        row = [
            ong.ma_ong,
            ong.ten_ong,
            ong.ma_loai.ten_loai if ong.ma_loai else '',
            ong.kich_thuoc,
            ong.chat_lieu,
            ong.so_met_ton,
            don_gia,
            thanh_tien
        ]
        
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    
    # Tổng cộng
    row_num += 2
    ws.write(row_num, 0, 'Tổng cộng', font_style)
    ws.write(row_num, 5, sum(ong.so_met_ton for ong in ong_nuoc_list), font_style)
    ws.write(row_num, 7, sum(ong.so_met_ton * (PhieuNhapChiTiet.objects.filter(ma_ong=ong).order_by('-ma_phieu_nhap__ngay_nhap').first().don_gia if PhieuNhapChiTiet.objects.filter(ma_ong=ong).exists() else 0) for ong in ong_nuoc_list), font_style)
    
    # Tạo response với file Excel
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="bao_cao_ton_kho.xls"'
    
    wb.save(response)
    return response

@login_required
def export_bao_cao_nhap_xuat(request):
    """
    Xuất báo cáo nhập xuất ra file Excel
    """
    # Lấy filter từ URL nếu có
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    loai_ong_id = request.GET.get('loai_ong')
    
    # Xử lý các tham số
    from_date = None
    to_date = None
    loai_ong = None
    
    if from_date_str:
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
    
    if to_date_str:
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
    
    if loai_ong_id and loai_ong_id != '':
        loai_ong = LoaiOng.objects.get(pk=loai_ong_id)
    
    # Tạo workbook Excel
    wb = xlwt.Workbook(encoding='utf-8')
    
    # Sheet 1: Phiếu nhập
    ws1 = wb.add_sheet('Phiếu nhập')
    
    # Sheet header
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    
    columns = ['Mã phiếu', 'Ngày nhập', 'Nhà cung cấp', 'Người tạo', 'Ghi chú', 'Tổng giá trị']
    
    for col_num in range(len(columns)):
        ws1.write(row_num, col_num, columns[col_num], font_style)
    
    # Query phiếu nhập
    phieu_nhap_query = PhieuNhap.objects
    if from_date:
        phieu_nhap_query = phieu_nhap_query.filter(ngay_nhap__gte=from_date)
    if to_date:
        phieu_nhap_query = phieu_nhap_query.filter(ngay_nhap__lte=to_date)
    
    phieu_nhap_list = phieu_nhap_query.order_by('-ngay_nhap')
    
    # Sheet body
    font_style = xlwt.XFStyle()
    
    for phieu in phieu_nhap_list:
        row_num += 1
        
        # Tính tổng giá trị phiếu nhập
        chi_tiet_list = PhieuNhapChiTiet.objects.filter(ma_phieu_nhap=phieu)
        if loai_ong:
            chi_tiet_list = chi_tiet_list.filter(ma_ong__ma_loai=loai_ong)
        
        tong_gia_tri = sum(chi_tiet.so_met * chi_tiet.don_gia for chi_tiet in chi_tiet_list)
        
        row = [
            phieu.ma_phieu_nhap,
            phieu.ngay_nhap.strftime('%d/%m/%Y'),
            phieu.ma_ncc.ten_ncc if phieu.ma_ncc else '',
            phieu.nguoi_tao,
            phieu.ghi_chu,
            tong_gia_tri
        ]
        
        for col_num in range(len(row)):
            ws1.write(row_num, col_num, row[col_num], font_style)
    
    # Sheet 2: Phiếu xuất
    ws2 = wb.add_sheet('Phiếu xuất')
    
    # Sheet header
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    
    columns = ['Mã phiếu', 'Ngày xuất', 'Khách hàng', 'Người tạo', 'Ghi chú', 'Tổng giá trị']
    
    for col_num in range(len(columns)):
        ws2.write(row_num, col_num, columns[col_num], font_style)
    
    # Query phiếu xuất
    phieu_xuat_query = PhieuXuat.objects
    if from_date:
        phieu_xuat_query = phieu_xuat_query.filter(ngay_xuat__gte=from_date)
    if to_date:
        phieu_xuat_query = phieu_xuat_query.filter(ngay_xuat__lte=to_date)
    
    phieu_xuat_list = phieu_xuat_query.order_by('-ngay_xuat')
    
    # Sheet body
    font_style = xlwt.XFStyle()
    
    for phieu in phieu_xuat_list:
        row_num += 1
        
        # Tính tổng giá trị phiếu xuất
        chi_tiet_list = PhieuXuatChiTiet.objects.filter(ma_phieu_xuat=phieu)
        if loai_ong:
            chi_tiet_list = chi_tiet_list.filter(ma_ong__ma_loai=loai_ong)
        
        tong_gia_tri = sum(chi_tiet.so_met * chi_tiet.don_gia for chi_tiet in chi_tiet_list)
        
        row = [
            phieu.ma_phieu_xuat,
            phieu.ngay_xuat.strftime('%d/%m/%Y'),
            phieu.ma_kh.ten_kh if phieu.ma_kh else '',
            phieu.nguoi_tao,
            phieu.ghi_chu,
            tong_gia_tri
        ]
        
        for col_num in range(len(row)):
            ws2.write(row_num, col_num, row[col_num], font_style)
    
    # Tạo response với file Excel
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="bao_cao_nhap_xuat.xls"'
    
    wb.save(response)
    return response

@login_required
def export_bao_cao_doi_tac(request):
    """
    Xuất báo cáo đối tác ra file Excel
    """
    # Lấy filter từ URL nếu có
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    
    # Xử lý các tham số
    from_date = None
    to_date = None
    
    if from_date_str:
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
    
    if to_date_str:
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
    
    # Tạo workbook Excel
    wb = xlwt.Workbook(encoding='utf-8')
    
    # Sheet 1: Nhà cung cấp
    ws1 = wb.add_sheet('Nhà cung cấp')
    
    # Sheet header
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    
    columns = ['Mã NCC', 'Tên nhà cung cấp', 'Địa chỉ', 'SĐT', 'Email', 'Số phiếu nhập', 'Tổng giá trị nhập']
    
    for col_num in range(len(columns)):
        ws1.write(row_num, col_num, columns[col_num], font_style)
    
    # Thống kê nhà cung cấp
    nha_cung_cap_list = NhaCungCap.objects.all()
    
    # Sheet body
    font_style = xlwt.XFStyle()
    
    for ncc in nha_cung_cap_list:
        row_num += 1
        
        # Query phiếu nhập
        phieu_nhap_query = PhieuNhap.objects.filter(ma_ncc=ncc)
        
        if from_date:
            phieu_nhap_query = phieu_nhap_query.filter(ngay_nhap__gte=from_date)
        if to_date:
            phieu_nhap_query = phieu_nhap_query.filter(ngay_nhap__lte=to_date)
        
        so_phieu_nhap = phieu_nhap_query.count()
        
        # Tính tổng giá trị nhập
        tong_gia_tri_nhap = 0
        for phieu in phieu_nhap_query:
            chi_tiet_list = PhieuNhapChiTiet.objects.filter(ma_phieu_nhap=phieu)
            for chi_tiet in chi_tiet_list:
                tong_gia_tri_nhap += chi_tiet.so_met * chi_tiet.don_gia
        
        row = [
            ncc.ma_ncc,
            ncc.ten_ncc,
            ncc.dia_chi,
            ncc.sdt,
            ncc.email,
            so_phieu_nhap,
            tong_gia_tri_nhap
        ]
        
        for col_num in range(len(row)):
            ws1.write(row_num, col_num, row[col_num], font_style)
    
    # Sheet 2: Khách hàng
    ws2 = wb.add_sheet('Khách hàng')
    
    # Sheet header
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    
    columns = ['Mã KH', 'Tên khách hàng', 'Địa chỉ', 'SĐT', 'Mã số thuế', 'Số phiếu xuất', 'Tổng giá trị xuất']
    
    for col_num in range(len(columns)):
        ws2.write(row_num, col_num, columns[col_num], font_style)
    
    # Thống kê khách hàng
    khach_hang_list = KhachHang.objects.all()
    
    # Sheet body
    font_style = xlwt.XFStyle()
    
    for kh in khach_hang_list:
        row_num += 1
        
        # Query phiếu xuất
        phieu_xuat_query = PhieuXuat.objects.filter(ma_kh=kh)
        
        if from_date:
            phieu_xuat_query = phieu_xuat_query.filter(ngay_xuat__gte=from_date)
        if to_date:
            phieu_xuat_query = phieu_xuat_query.filter(ngay_xuat__lte=to_date)
        
        so_phieu_xuat = phieu_xuat_query.count()
        
        # Tính tổng giá trị xuất
        tong_gia_tri_xuat = 0
        for phieu in phieu_xuat_query:
            chi_tiet_list = PhieuXuatChiTiet.objects.filter(ma_phieu_xuat=phieu)
            for chi_tiet in chi_tiet_list:
                tong_gia_tri_xuat += chi_tiet.so_met * chi_tiet.don_gia
        
        row = [
            kh.ma_kh,
            kh.ten_kh,
            kh.dia_chi,
            kh.sdt,
            kh.ma_so_thue,
            so_phieu_xuat,
            tong_gia_tri_xuat
        ]
        
        for col_num in range(len(row)):
            ws2.write(row_num, col_num, row[col_num], font_style)
    
    # Tạo response với file Excel
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="bao_cao_doi_tac.xls"'
    
    wb.save(response)
    return response

