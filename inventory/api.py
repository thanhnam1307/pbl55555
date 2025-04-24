from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
import os
import cv2
import numpy as np
import sys
import json
import base64
from datetime import datetime, timedelta
from .models import Product, WaterPipeCountHistory

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
        - note: Ghi chú về lần phát hiện này (tùy chọn)
    
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
        note = data.get('note', None)
        
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
        results = model(image, verbose=False)
        
        # Đếm số lượng ống nước
        pipe_count = 0
        for r in results:
            pipe_count += len(r.boxes)
            
            # Vẽ hình chữ nhật bao quanh các ống nước được phát hiện
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Không thêm text vào hình ảnh theo yêu cầu mới
        
        # Lưu hình ảnh đã xử lý
        output_dir = os.path.join(settings.MEDIA_ROOT, 'processed_images')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        output_image_name = f"processed_{os.path.basename(full_image_path)}"
        output_image_path = os.path.join(output_dir, output_image_name)
        cv2.imwrite(output_image_path, image)
        
        # Nếu có product_id, cập nhật số lượng
        product = None
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
        
        # Lưu kết quả phát hiện vào lịch sử
        history_record = WaterPipeCountHistory(
            count=pipe_count,
            notes=note
        )
        
        if product:
            history_record.product = product
        
        # Lưu hình ảnh gốc và hình ảnh đã xử lý
        from django.core.files.base import ContentFile
        
        # Lưu hình ảnh gốc vào bản ghi lịch sử
        with open(full_image_path, 'rb') as f:
            original_image_content = f.read()
            image_filename = os.path.basename(full_image_path)
            history_record.original_image.save(
                f'history_original_{image_filename}', 
                ContentFile(original_image_content)
            )
        
        # Lưu hình ảnh đã xử lý vào bản ghi lịch sử
        with open(output_image_path, 'rb') as f:
            processed_image_content = f.read()
            history_record.processed_image.save(
                f'history_processed_{image_filename}', 
                ContentFile(processed_image_content)
            )
        
        history_record.save()
        
        # Trả về kết quả
        return JsonResponse({
            'status': 'success',
            'count': pipe_count,
            'processed_image': f'processed_images/{output_image_name}',
            'history_id': history_record.id
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Lỗi khi xử lý hình ảnh: {str(e)}'
        })

@csrf_exempt
def history_api(request):
    """
    API endpoint để lấy lịch sử phát hiện ống nước.
    
    GET params:
        - product_id: Lọc theo ID sản phẩm (tùy chọn)
        - start_date: Lọc từ ngày (định dạng YYYY-MM-DD, tùy chọn)
        - end_date: Lọc đến ngày (định dạng YYYY-MM-DD, tùy chọn)
    
    Trả về:
        - danh sách các bản ghi lịch sử phát hiện
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Chỉ hỗ trợ phương thức GET'})
    
    try:
        # Lấy tham số từ query
        product_id = request.GET.get('product_id', None)
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)
        
        # Khởi tạo QuerySet
        history_records = WaterPipeCountHistory.objects.all().order_by('-timestamp')
        
        # Lọc theo product_id nếu có
        if product_id:
            history_records = history_records.filter(product_id=product_id)
        
        # Lọc theo ngày bắt đầu nếu có
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                history_records = history_records.filter(timestamp__date__gte=start_date)
            except ValueError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Định dạng start_date không hợp lệ. Sử dụng YYYY-MM-DD'
                })
        
        # Lọc theo ngày kết thúc nếu có
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                # Cộng thêm 1 ngày để bao gồm cả ngày end_date
                end_date_inclusive = end_date + timedelta(days=1)
                history_records = history_records.filter(timestamp__date__lt=end_date_inclusive)
            except ValueError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Định dạng end_date không hợp lệ. Sử dụng YYYY-MM-DD'
                })
        
        # Chuẩn bị dữ liệu để trả về
        history_data = []
        for record in history_records:
            history_item = {
                'id': record.id,
                'count': record.count,
                'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'notes': record.notes,
                'original_image': record.original_image.url if record.original_image else None,
                'processed_image': record.processed_image.url if record.processed_image else None,
                'product': {
                    'id': record.product.id,
                    'name': record.product.name,
                    'diameter': record.product.diameter,
                    'length': record.product.length
                } if record.product else None
            }
            history_data.append(history_item)
        
        return JsonResponse({
            'status': 'success',
            'data': history_data
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Lỗi khi lấy dữ liệu lịch sử: {str(e)}'
        })

@csrf_exempt
def dashboard_stats_api(request):
    """
    API endpoint để lấy thống kê cho dashboard.
    
    GET params:
        - period: Khoảng thời gian (day, week, month, year, all) - mặc định là all
    
    Trả về:
        - total_pipes: Tổng số ống đã phát hiện
        - total_detections: Tổng số lần phát hiện
        - pipes_by_type: Số lượng ống theo loại sản phẩm
        - daily_counts: Thống kê số lượng ống theo ngày
        - low_stock_warnings: Cảnh báo hàng tồn kho thấp
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Chỉ hỗ trợ phương thức GET'})
    
    try:
        # Lấy tham số từ query
        period = request.GET.get('period', 'all')
        
        # Lọc theo khoảng thời gian
        now = timezone.now()
        history_records = WaterPipeCountHistory.objects.all()
        
        if period == 'day':
            history_records = history_records.filter(timestamp__date=now.date())
        elif period == 'week':
            start_of_week = now - timedelta(days=now.weekday())
            history_records = history_records.filter(timestamp__gte=start_of_week)
        elif period == 'month':
            history_records = history_records.filter(timestamp__year=now.year, timestamp__month=now.month)
        elif period == 'year':
            history_records = history_records.filter(timestamp__year=now.year)
        
        # Tổng số ống đã phát hiện
        total_pipes = sum(record.count for record in history_records)
        
        # Tổng số lần phát hiện
        total_detections = history_records.count()
        
        # Số lượng loại ống khác nhau
        pipe_types_count = Product.objects.count()
        
        # Số lượng ống theo loại sản phẩm
        pipes_by_type = {}
        for record in history_records:
            if record.product:
                product_name = record.product.name
                if product_name not in pipes_by_type:
                    pipes_by_type[product_name] = 0
                pipes_by_type[product_name] += record.count
        
        # Số lượng ống theo ngày
        from django.db.models import Sum
        from django.db.models.functions import TruncDate
        
        daily_records = (
            history_records
            .annotate(date=TruncDate('timestamp'))
            .values('date')
            .annotate(total=Sum('count'))
            .order_by('date')
        )
        
        daily_counts = [
            {
                'date': record['date'].strftime('%Y-%m-%d') if record['date'] else '',
                'count': record['total']
            }
            for record in daily_records
        ]
        
        # Cảnh báo hàng tồn kho thấp
        # Ngưỡng cảnh báo: Nếu số lượng < 10
        threshold = 10
        low_stock_warnings = []
        
        for product in Product.objects.all():
            if product.quantity < threshold:
                low_stock_warnings.append({
                    'id': product.id,
                    'name': product.name,
                    'quantity': product.quantity,
                    'threshold': threshold
                })
        
        # Lấy 5 lần phát hiện gần đây nhất
        recent_detections = []
        for record in history_records.order_by('-timestamp')[:5]:
            detection_data = {
                'id': record.id,
                'count': record.count,
                'timestamp': record.timestamp.strftime('%d/%m/%Y %H:%M'),
                'product_name': record.product.name if record.product else 'Không xác định',
                'product_id': record.product.id if record.product else None
            }
            recent_detections.append(detection_data)
        
        return JsonResponse({
            'status': 'success',
            'total_pipes': total_pipes,
            'total_detections': total_detections,
            'pipe_types': pipe_types_count,
            'pipes_by_type': pipes_by_type,
            'daily_counts': daily_counts,
            'low_stock_warnings': low_stock_warnings,
            'recent_detections': recent_detections
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Lỗi khi lấy dữ liệu thống kê: {str(e)}'
        })