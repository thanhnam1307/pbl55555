from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
import cv2
import numpy as np
import sys
import json
import base64
from .models import Product

# Thêm đường dẫn đến thư mục pipe-ai để có thể import các module từ đó
sys.path.append(os.path.join(settings.BASE_DIR, 'pipe-ai'))

# Import mô hình YOLO từ thư viện ultralytics
try:
    from ultralytics import YOLO
    model_path = os.path.join(settings.BASE_DIR, 'pipe-ai', 'runs', 'detect', 'train', 'weights', 'best.pt')
    
    # Nếu không tìm thấy mô hình đã huấn luyện, sử dụng mô hình mặc định
    if not os.path.exists(model_path):
        model_path = os.path.join(settings.BASE_DIR, 'pipe-ai', 'yolov8n.pt')
    
    # Tải mô hình YOLO
    model = YOLO(model_path)
except ImportError:
    print("Không thể import YOLO, vui lòng cài đặt ultralytics")
    model = None

@csrf_exempt
def detect_pipes_api(request):
    """
    API endpoint để phát hiện và đếm ống nước trong hình ảnh.
    
    POST param:
        - image_path: Đường dẫn đến hình ảnh (tương đối với MEDIA_ROOT)
        - product_id: ID của sản phẩm cần cập nhật số lượng (tùy chọn)
    
    Trả về:
        - count: Số lượng ống nước được phát hiện
        - processed_image: Đường dẫn đến hình ảnh đã xử lý
        - status: Trạng thái của yêu cầu (success/error)
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Chỉ hỗ trợ phương thức POST'})
    
    try:
        data = json.loads(request.body)
        image_path = data.get('image_path', '')
        product_id = data.get('product_id', None)
        
        # Kiểm tra đường dẫn hình ảnh
        full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)
        if not os.path.exists(full_image_path):
            return JsonResponse({
                'status': 'error', 
                'message': f'Không tìm thấy hình ảnh tại {full_image_path}'
            })
        
        # Đọc hình ảnh
        image = cv2.imread(full_image_path)
        if image is None:
            return JsonResponse({
                'status': 'error',
                'message': f'Không thể đọc hình ảnh từ {full_image_path}'
            })
            
        # Phát hiện ống nước
        results = model(image)
        
        # Đếm số lượng ống nước
        pipe_count = 0
        for r in results:
            pipe_count += len(r.boxes)
            
            # Vẽ hình chữ nhật bao quanh các ống nước được phát hiện
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Thêm số lượng ống nước vào hình ảnh
        cv2.putText(image, f"Ống nước: {pipe_count}", (10, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Lưu hình ảnh đã xử lý
        output_dir = os.path.join(settings.MEDIA_ROOT, 'processed_images')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        output_image_name = f"processed_{os.path.basename(full_image_path)}"
        output_image_path = os.path.join(output_dir, output_image_name)
        cv2.imwrite(output_image_path, image)
        
        # Nếu có product_id, cập nhật số lượng
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                product.quantity = pipe_count
                product.save()
            except Product.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Không tìm thấy sản phẩm với ID {product_id}'
                })
        
        # Trả về kết quả
        return JsonResponse({
            'status': 'success',
            'count': pipe_count,
            'processed_image': f'processed_images/{output_image_name}'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Lỗi khi xử lý hình ảnh: {str(e)}'
        })