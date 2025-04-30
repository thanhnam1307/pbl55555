from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Count
from django.utils import timezone
from .models import (
    Product, WaterPipeCountHistory, 
    LoaiOng, OngNuoc, NhaCungCap, KhachHang, 
    PhieuNhap, PhieuXuat, PhieuNhapChiTiet, PhieuXuatChiTiet
)
from .forms import (
    ProductForm, ImageUploadForm,
    LoaiOngForm, OngNuocForm, NhaCungCapForm, KhachHangForm,
    PhieuNhapForm, PhieuXuatForm, PhieuNhapChiTietForm, PhieuXuatChiTietForm,
    LoaiOngSearchForm, OngNuocSearchForm, NhaCungCapSearchForm, KhachHangSearchForm,
    PhieuNhapSearchForm, PhieuXuatSearchForm
)

# Basic Product CRUD functions
def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sản phẩm đã được tạo thành công.')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form})

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sản phẩm đã được cập nhật thành công.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Sản phẩm đã được xóa thành công.')
        return redirect('product_list')
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})

def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        source = request.POST.get('source', 'upload')
        
        # Xử lý tải ảnh từ form
        if form.is_valid() and source == 'upload':
            # Lấy dữ liệu từ form
            product = form.cleaned_data['product']
            image = form.cleaned_data['image']
            
            # Lưu ảnh tạm thời
            product.image = image
            product.save()
            
            try:
                # Lấy đường dẫn tương đối của ảnh để gửi đến API
                image_path = product.image.name
                
                # Gọi API để phân tích ảnh
                import json
                import requests
                from django.urls import reverse
                from urllib.parse import urljoin
                
                # Tạo đường dẫn đầy đủ đến API endpoint
                api_url = request.build_absolute_uri(reverse('detect_pipes_api'))
                
                # Chuẩn bị dữ liệu để gửi đến API
                api_data = {
                    'image_path': image_path,
                    'product_id': product.id,
                    'note': f'Phân tích từ trang tải ảnh lên'
                }
                
                # Gọi API bằng requests
                headers = {'Content-Type': 'application/json'}
                response = requests.post(api_url, data=json.dumps(api_data), headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result['status'] == 'success':
                        # Lấy kết quả từ API
                        pipe_count = result['count']
                        processed_image_path = result['processed_image']
                        
                        # Cập nhật số lượng sản phẩm
                        product.quantity = pipe_count
                        product.save()
                        
                        # Hiển thị kết quả
                        return render(request, 'inventory/image_upload.html', {
                            'image_processed': True,
                            'product': product,
                            'pipe_count': pipe_count,
                            'original_image': product.image.url,
                            'processed_image': '/media/' + processed_image_path
                        })
                    else:
                        messages.error(request, f'Lỗi khi phân tích hình ảnh: {result["message"]}')
                else:
                    messages.error(request, f'Không thể kết nối đến API phân tích hình ảnh. Mã lỗi: {response.status_code}')
            
            except Exception as e:
                messages.error(request, f'Đã xảy ra lỗi: {str(e)}')
        
        # Xử lý ảnh từ ESP32-CAM
        elif source == 'camera' and 'camera_image' in request.POST:
            try:
                product_id = request.POST.get('product_id')
                product = Product.objects.get(pk=product_id)
                
                # Xử lý dữ liệu hình ảnh base64 từ ESP32-CAM
                import base64
                import uuid
                from django.core.files.base import ContentFile
                
                # Tách header và dữ liệu base64
                image_data = request.POST['camera_image']
                if ',' in image_data:
                    header, image_data = image_data.split(',', 1)
                
                # Giải mã base64 thành dữ liệu nhị phân
                binary_data = base64.b64decode(image_data)
                
                # Tạo tên file duy nhất
                filename = f'camera_{int(timezone.now().timestamp())}.jpg'
                
                # Lưu hình ảnh và cập nhật sản phẩm
                from django.core.files.storage import default_storage
                from django.core.files.base import ContentFile
                
                image_path = f'warehouse_images/{filename}'
                path = default_storage.save(image_path, ContentFile(binary_data))
                
                # Cập nhật hình ảnh cho sản phẩm
                product.image = path
                product.save()
                
                # Gọi API để phân tích ảnh
                import json
                import requests
                from django.urls import reverse
                
                api_url = request.build_absolute_uri(reverse('detect_pipes_api'))
                
                api_data = {
                    'image_path': image_path,
                    'product_id': product.id,
                    'note': f'Chụp từ ESP32-CAM'
                }
                
                headers = {'Content-Type': 'application/json'}
                response = requests.post(api_url, data=json.dumps(api_data), headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result['status'] == 'success':
                        pipe_count = result['count']
                        processed_image_path = result['processed_image']
                        
                        # Cập nhật số lượng sản phẩm
                        product.quantity = pipe_count
                        product.save()
                        
                        # Hiển thị kết quả
                        return render(request, 'inventory/image_upload.html', {
                            'image_processed': True,
                            'product': product,
                            'pipe_count': pipe_count,
                            'original_image': f'/media/{image_path}',
                            'processed_image': f'/media/{processed_image_path}'
                        })
                    else:
                        messages.error(request, f'Lỗi khi phân tích hình ảnh: {result["message"]}')
                else:
                    messages.error(request, f'Không thể kết nối đến API phân tích hình ảnh. Mã lỗi: {response.status_code}')
                
            except Exception as e:
                messages.error(request, f'Đã xảy ra lỗi: {str(e)}')
    else:
        form = ImageUploadForm()
    
    # Truyền tất cả các sản phẩm vào context để sử dụng trong tab ESP32-CAM
    all_products = Product.objects.all()
    return render(request, 'inventory/image_upload.html', {'form': form, 'all_products': all_products})

def pipe_count_history(request):
    history = WaterPipeCountHistory.objects.all().order_by('-timestamp')
    return render(request, 'inventory/pipe_count_history.html', {'history': history})

def dashboard(request):
    # This is the original dashboard, not the new warehouse dashboard
    total_products = Product.objects.count()
    recent_history = WaterPipeCountHistory.objects.order_by('-timestamp')[:5]
    
    context = {
        'total_products': total_products,
        'recent_history': recent_history
    }
    return render(request, 'inventory/dashboard.html', context)

# Enhanced class-based views for LoaiOng with search functionality
class LoaiOngListView(FormMixin, ListView):
    model = LoaiOng
    template_name = 'inventory/loai_ong_list.html'
    context_object_name = 'loai_ong_list'
    form_class = LoaiOngSearchForm
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        form = self.get_form()
        
        if form.is_valid():
            search_term = form.cleaned_data.get('search_term')
            if search_term:
                queryset = queryset.filter(
                    Q(ten_loai__icontains=search_term) | 
                    Q(mo_ta__icontains=search_term)
                )
        
        return queryset
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data'] = self.request.GET or None
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.get_form()
        return context

class LoaiOngCreateView(CreateView):
    model = LoaiOng
    form_class = LoaiOngForm
    template_name = 'inventory/loai_ong_form.html'
    success_url = reverse_lazy('loai_ong_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Loại ống đã được thêm thành công.')
        return super().form_valid(form)

class LoaiOngUpdateView(UpdateView):
    model = LoaiOng
    form_class = LoaiOngForm
    template_name = 'inventory/loai_ong_form.html'
    success_url = reverse_lazy('loai_ong_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Loại ống đã được cập nhật thành công.')
        return super().form_valid(form)

# Enhanced class-based views for OngNuoc with search and filter
class OngNuocListView(FormMixin, ListView):
    model = OngNuoc
    template_name = 'inventory/ong_nuoc_list.html'
    context_object_name = 'ong_nuoc_list'
    form_class = OngNuocSearchForm
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        form = self.get_form()
        
        if form.is_valid():
            search_term = form.cleaned_data.get('search_term')
            loai_ong = form.cleaned_data.get('loai_ong')
            
            if search_term:
                queryset = queryset.filter(
                    Q(ten_ong__icontains=search_term) | 
                    Q(kich_thuoc__icontains=search_term) |
                    Q(chat_lieu__icontains=search_term)
                )
            
            if loai_ong:
                queryset = queryset.filter(ma_loai=loai_ong)
        
        return queryset
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data'] = self.request.GET or None
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.get_form()
        return context

class OngNuocCreateView(CreateView):
    model = OngNuoc
    form_class = OngNuocForm
    template_name = 'inventory/ong_nuoc_form.html'
    success_url = reverse_lazy('ong_nuoc_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Ống nước đã được thêm thành công.')
        return super().form_valid(form)

class OngNuocUpdateView(UpdateView):
    model = OngNuoc
    form_class = OngNuocForm
    template_name = 'inventory/ong_nuoc_form.html'
    success_url = reverse_lazy('ong_nuoc_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Ống nước đã được cập nhật thành công.')
        return super().form_valid(form)

class OngNuocDetailView(DetailView):
    model = OngNuoc
    template_name = 'inventory/ong_nuoc_detail.html'
    context_object_name = 'ong_nuoc'

# Enhanced class-based views for NhaCungCap
class NhaCungCapListView(FormMixin, ListView):
    model = NhaCungCap
    template_name = 'inventory/nha_cung_cap_list.html'
    context_object_name = 'nha_cung_cap_list'
    form_class = NhaCungCapSearchForm
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        form = self.get_form()
        
        if form.is_valid():
            search_term = form.cleaned_data.get('search_term')
            if search_term:
                queryset = queryset.filter(
                    Q(ten_ncc__icontains=search_term) | 
                    Q(sdt__icontains=search_term) |
                    Q(email__icontains=search_term)
                )
        
        return queryset
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data'] = self.request.GET or None
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.get_form()
        return context

class NhaCungCapCreateView(CreateView):
    model = NhaCungCap
    form_class = NhaCungCapForm
    template_name = 'inventory/nha_cung_cap_form.html'
    success_url = reverse_lazy('nha_cung_cap_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Nhà cung cấp đã được thêm thành công.')
        return super().form_valid(form)

class NhaCungCapUpdateView(UpdateView):
    model = NhaCungCap
    form_class = NhaCungCapForm
    template_name = 'inventory/nha_cung_cap_form.html'
    success_url = reverse_lazy('nha_cung_cap_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Nhà cung cấp đã được cập nhật thành công.')
        return super().form_valid(form)

# Enhanced class-based views for KhachHang
class KhachHangListView(FormMixin, ListView):
    model = KhachHang
    template_name = 'inventory/khach_hang_list.html'
    context_object_name = 'khach_hang_list'
    form_class = KhachHangSearchForm
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        form = self.get_form()
        
        if form.is_valid():
            search_term = form.cleaned_data.get('search_term')
            if search_term:
                queryset = queryset.filter(
                    Q(ten_kh__icontains=search_term) | 
                    Q(sdt__icontains=search_term) |
                    Q(ma_so_thue__icontains=search_term)
                )
        
        return queryset
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data'] = self.request.GET or None
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.get_form()
        return context

class KhachHangCreateView(CreateView):
    model = KhachHang
    form_class = KhachHangForm
    template_name = 'inventory/khach_hang_form.html'
    success_url = reverse_lazy('khach_hang_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Khách hàng đã được thêm thành công.')
        return super().form_valid(form)

class KhachHangUpdateView(UpdateView):
    model = KhachHang
    form_class = KhachHangForm
    template_name = 'inventory/khach_hang_form.html'
    success_url = reverse_lazy('khach_hang_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Khách hàng đã được cập nhật thành công.')
        return super().form_valid(form)

# Enhanced class-based views for PhieuNhap
class PhieuNhapListView(FormMixin, ListView):
    model = PhieuNhap
    template_name = 'inventory/phieu_nhap_list.html'
    context_object_name = 'phieu_nhap_list'
    form_class = PhieuNhapSearchForm
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        form = self.get_form()
        
        if form.is_valid():
            search_term = form.cleaned_data.get('search_term')
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')
            nha_cung_cap = form.cleaned_data.get('nha_cung_cap')
            
            if search_term:
                queryset = queryset.filter(
                    Q(nguoi_tao__icontains=search_term) | 
                    Q(ghi_chu__icontains=search_term)
                )
            
            if from_date:
                queryset = queryset.filter(ngay_nhap__gte=from_date)
            
            if to_date:
                queryset = queryset.filter(ngay_nhap__lte=to_date)
            
            if nha_cung_cap:
                queryset = queryset.filter(ma_ncc=nha_cung_cap)
        
        return queryset.order_by('-ngay_nhap')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data'] = self.request.GET or None
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.get_form()
        return context

class PhieuNhapCreateView(CreateView):
    model = PhieuNhap
    form_class = PhieuNhapForm
    template_name = 'inventory/phieu_nhap_form.html'
    success_url = reverse_lazy('phieu_nhap_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Phiếu nhập đã được tạo thành công.')
        return super().form_valid(form)

class PhieuNhapUpdateView(UpdateView):
    model = PhieuNhap
    form_class = PhieuNhapForm
    template_name = 'inventory/phieu_nhap_form.html'
    success_url = reverse_lazy('phieu_nhap_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Phiếu nhập đã được cập nhật thành công.')
        return super().form_valid(form)

class PhieuNhapDetailView(DetailView):
    model = PhieuNhap
    template_name = 'inventory/phieu_nhap_detail.html'
    context_object_name = 'phieu_nhap'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chi_tiet_list'] = PhieuNhapChiTiet.objects.filter(ma_phieu_nhap=self.object)
        return context

# Enhanced class-based views for PhieuXuat
class PhieuXuatListView(FormMixin, ListView):
    model = PhieuXuat
    template_name = 'inventory/phieu_xuat_list.html'
    context_object_name = 'phieu_xuat_list'
    form_class = PhieuXuatSearchForm
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        form = self.get_form()
        
        if form.is_valid():
            search_term = form.cleaned_data.get('search_term')
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')
            khach_hang = form.cleaned_data.get('khach_hang')
            
            if search_term:
                queryset = queryset.filter(
                    Q(nguoi_tao__icontains=search_term) | 
                    Q(ghi_chu__icontains=search_term)
                )
            
            if from_date:
                queryset = queryset.filter(ngay_xuat__gte=from_date)
            
            if to_date:
                queryset = queryset.filter(ngay_xuat__lte=to_date)
            
            if khach_hang:
                queryset = queryset.filter(ma_kh=khach_hang)
        
        return queryset.order_by('-ngay_xuat')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data'] = self.request.GET or None
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.get_form()
        return context

class PhieuXuatCreateView(CreateView):
    model = PhieuXuat
    form_class = PhieuXuatForm
    template_name = 'inventory/phieu_xuat_form.html'
    success_url = reverse_lazy('phieu_xuat_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Phiếu xuất đã được tạo thành công.')
        return super().form_valid(form)

class PhieuXuatUpdateView(UpdateView):
    model = PhieuXuat
    form_class = PhieuXuatForm
    template_name = 'inventory/phieu_xuat_form.html'
    success_url = reverse_lazy('phieu_xuat_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Phiếu xuất đã được cập nhật thành công.')
        return super().form_valid(form)

class PhieuXuatDetailView(DetailView):
    model = PhieuXuat
    template_name = 'inventory/phieu_xuat_detail.html'
    context_object_name = 'phieu_xuat'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chi_tiet_list'] = PhieuXuatChiTiet.objects.filter(ma_phieu_xuat=self.object)
        return context

# New enhanced dashboard
def warehouse_dashboard(request):
    # Get overall statistics
    total_ong_nuoc = OngNuoc.objects.count()
    total_loai_ong = LoaiOng.objects.count()
    total_nha_cung_cap = NhaCungCap.objects.count()
    total_khach_hang = KhachHang.objects.count()
    
    # Get recent activity
    recent_phieu_nhap = PhieuNhap.objects.order_by('-ngay_nhap')[:5]
    recent_phieu_xuat = PhieuXuat.objects.order_by('-ngay_xuat')[:5]
    
    # Calculate inventory stats
    ong_nuoc_inventory = OngNuoc.objects.aggregate(
        total_inventory=Sum('so_met_ton')
    )
    
    # Get low stock items (less than 10m)
    low_stock_items = OngNuoc.objects.filter(so_met_ton__lt=10).order_by('so_met_ton')
    
    # Get inventory by type
    inventory_by_type = OngNuoc.objects.values('ma_loai__ten_loai').annotate(
        total=Sum('so_met_ton')
    ).order_by('-total')
    
    context = {
        'total_ong_nuoc': total_ong_nuoc,
        'total_loai_ong': total_loai_ong,
        'total_nha_cung_cap': total_nha_cung_cap,
        'total_khach_hang': total_khach_hang,
        'recent_phieu_nhap': recent_phieu_nhap,
        'recent_phieu_xuat': recent_phieu_xuat,
        'total_inventory': ong_nuoc_inventory.get('total_inventory', 0),
        'low_stock_items': low_stock_items,
        'inventory_by_type': inventory_by_type,
    }
    
    return render(request, 'inventory/warehouse_dashboard.html', context)

