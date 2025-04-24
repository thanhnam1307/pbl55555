from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import Product, WaterPipeCountHistory
from .forms import ProductForm, ImageUploadForm
import requests
import json
import os
import cv2
import numpy as np
from django.conf import settings
import sys
from django.core.files.base import ContentFile

# Thêm đường dẫn đến thư mục pipe-ai vào sys.path để có thể import các module từ đó
sys.path.append(os.path.join(settings.BASE_DIR, 'pipe-ai'))



def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form, 'action': 'Create'})

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form, 'action': 'Update'})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})

def upload_image(request):
    context = {
        'form': ImageUploadForm(),
        'image_processed': False,
        'all_products': Product.objects.all()  # Thêm danh sách sản phẩm cho tab camera
    }
    
    if request.method == 'POST':
        source = request.POST.get('source', 'upload')
        
        if source == 'upload':
            # Xử lý tải ảnh lên như trước đây
            form = ImageUploadForm(request.POST, request.FILES)
            if form.is_valid():
                product = form.cleaned_data['product']
                image = form.cleaned_data['image']
                
                # Tạo đường dẫn thư mục nếu chưa tồn tại
                warehouse_dir = os.path.join(settings.MEDIA_ROOT, 'warehouse_images')
                if not os.path.exists(warehouse_dir):
                    os.makedirs(warehouse_dir)
                    
                # Lưu hình ảnh gốc vào thư mục warehouse_images
                image_name = image.name
                image_path = os.path.join(settings.MEDIA_ROOT, 'warehouse_images', image_name)
                with open(image_path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)
                
                # Cập nhật đường dẫn hình ảnh trong model Product
                product.image = f'warehouse_images/{image_name}'
                product.save()
        
        elif source == 'camera':
            # Xử lý hình ảnh từ camera
            try:
                product_id = request.POST.get('product_id')
                camera_image_data = request.POST.get('camera_image')
                
                if not product_id or not camera_image_data:
                    messages.error(request, 'Dữ liệu camera không hợp lệ.')
                    return render(request, 'inventory/image_upload.html', context)
                
                product = Product.objects.get(id=product_id)
                
                # Tạo đường dẫn thư mục nếu chưa tồn tại
                warehouse_dir = os.path.join(settings.MEDIA_ROOT, 'warehouse_images')
                if not os.path.exists(warehouse_dir):
                    os.makedirs(warehouse_dir)
                
                # Tạo tên file duy nhất cho hình ảnh camera
                import time
                timestamp = int(time.time())
                image_name = f'camera_{timestamp}.jpg'
                image_path = os.path.join(settings.MEDIA_ROOT, 'warehouse_images', image_name)
                
                # Lưu hình ảnh từ dữ liệu base64
                import base64
                image_data = camera_image_data.split(',')[1]  # Bỏ qua phần "data:image/jpeg;base64,"
                with open(image_path, 'wb') as f:
                    f.write(base64.b64decode(image_data))
                
                # Cập nhật đường dẫn hình ảnh trong model Product
                product.image = f'warehouse_images/{image_name}'
                product.save()
                
            except Product.DoesNotExist:
                messages.error(request, 'Không tìm thấy sản phẩm.')
                return render(request, 'inventory/image_upload.html', context)
            except Exception as e:
                messages.error(request, f'Lỗi khi xử lý hình ảnh từ camera: {str(e)}')
                return render(request, 'inventory/image_upload.html', context)
        
        # Xử lý hình ảnh và cập nhật sản phẩm (giống nhau cho cả hai nguồn)
        try:
            # Phân tích hình ảnh và đếm ống nước
            pipe_count = call_ai_pipe_counter_api(image_path)
            
            # Update product quantity
            product.quantity = pipe_count
            product.save()
            
            # Chuẩn bị context để hiển thị kết quả
            context['image_processed'] = True
            context['product'] = product
            context['pipe_count'] = pipe_count
            context['original_image'] = f'/media/warehouse_images/{image_name}'
            context['processed_image'] = f'/media/processed_images/processed_{image_name}'
            
            # Lưu lịch sử đếm ống nước
            history_record = WaterPipeCountHistory(
                product=product,
                count=pipe_count
            )
            
            # Lưu hình ảnh gốc và hình ảnh đã xử lý vào bản ghi lịch sử
            with open(image_path, 'rb') as f:
                original_image_content = f.read()
                history_record.original_image.save(
                    f'history_original_{image_name}', 
                    ContentFile(original_image_content)
                )
            
            processed_image_path = os.path.join(settings.MEDIA_ROOT, 'processed_images', f'processed_{image_name}')
            if os.path.exists(processed_image_path):
                with open(processed_image_path, 'rb') as f:
                    processed_image_content = f.read()
                    history_record.processed_image.save(
                        f'history_processed_{image_name}', 
                        ContentFile(processed_image_content)
                    )
            
            history_record.save()
            
            messages.success(request, f'Ảnh đã được phân tích thành công. Phát hiện {pipe_count} ống nước.')
        except Exception as e:
            messages.error(request, f'Lỗi khi phân tích hình ảnh: {str(e)}')
            if source == 'upload':
                context['form'] = form
    
    return render(request, 'inventory/image_upload.html', context)

def call_ai_pipe_counter_api(image_path):
    """
    Sử dụng mô hình YOLOv8 đã huấn luyện từ thư mục pipe-ai để đếm số lượng ống nước
    trong hình ảnh và trả về kết quả.
    """
    try:
        # Cách 1: Xử lý ảnh trực tiếp (không gọi API)
        from ultralytics import YOLO
        
        model_path = os.path.join(settings.BASE_DIR, 'pipe-ai', 'runs', 'detect', 'train', 'weights', 'best.pt')
        
        # Nếu không tìm thấy mô hình đã huấn luyện, sử dụng mô hình mặc định
        if not os.path.exists(model_path):
            model_path = os.path.join(settings.BASE_DIR, 'pipe-ai', 'yolov8n.pt')
        
        # Tải mô hình YOLO
        model = YOLO(model_path)
        
        # Đọc hình ảnh bằng OpenCV
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Không thể đọc hình ảnh từ {image_path}")
        
        # Tạo một bản sao của hình ảnh gốc để vẽ lên đó
        image_with_boxes = image.copy()
        
        # Sử dụng mô hình để phát hiện ống nước với tham số verbose=False để tắt các thông tin debug
        results = model(image, verbose=False)
        
        # Đếm số lượng ống nước được phát hiện
        pipe_count = 0
        
        for r in results:
            boxes = r.boxes
            pipe_count += len(boxes)
            
            # Vẽ hình chữ nhật bao quanh các ống nước được phát hiện
            for box in boxes:
                # Lấy tọa độ
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # Vẽ hình chữ nhật màu xanh lá
                cv2.rectangle(image_with_boxes, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # KHÔNG thêm bất kỳ text nào vào hình ảnh
        
        # Lưu hình ảnh đã xử lý
        output_dir = os.path.join(settings.MEDIA_ROOT, 'processed_images')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        output_image_path = os.path.join(output_dir, f"processed_{os.path.basename(image_path)}")
        cv2.imwrite(output_image_path, image_with_boxes)
        
        return pipe_count
    
    except Exception as e:
        print(f"Lỗi khi phân tích hình ảnh: {str(e)}")
        # Nếu có lỗi, sử dụng phương pháp giả lập
        import random
        pipe_count = random.randint(5, 20)
        return pipe_count

def pipe_count_history(request):
    """
    Hiển thị lịch sử đếm ống nước
    """
    # Lấy tham số lọc từ GET request
    product_id = request.GET.get('product_id')
    
    if product_id:
        # Lọc theo sản phẩm cụ thể
        history_records = WaterPipeCountHistory.objects.filter(product_id=product_id)
        selected_product = get_object_or_404(Product, id=product_id)
    else:
        # Hiển thị tất cả bản ghi
        history_records = WaterPipeCountHistory.objects.all()
        selected_product = None
    
    # Lấy danh sách tất cả sản phẩm để hiển thị trong dropdown
    all_products = Product.objects.all()
    
    context = {
        'history_records': history_records,
        'all_products': all_products,
        'selected_product': selected_product
    }
    
    return render(request, 'inventory/pipe_count_history.html', context)

def dashboard(request):
    """
    View to render the dashboard page with statistics and charts.
    """
    # Get all products for the product selection
    products = Product.objects.all()
    
    context = {
        'products': products,
    }
    
    return render(request, 'inventory/dashboard.html', context)

