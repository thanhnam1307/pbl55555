from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
import requests
import os
import shutil
from datetime import datetime
from ultralytics import YOLO
from typing import Optional
import io

app = FastAPI()

# CORS cho phép truy cập từ frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả các origin, có thể hạn chế trong môi trường production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tạo thư mục uploads nếu chưa tồn tại
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Tạo thư mục results nếu chưa tồn tại
RESULT_FOLDER = "results"
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Cấu hình phục vụ file tĩnh
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")
app.mount("/results", StaticFiles(directory=RESULT_FOLDER), name="results")

# URL stream từ ESP32-CAM (giữ lại cho tính năng stream)
ESP32_STREAM_URL = "http://172.20.10.2:81/stream"

# Load mô hình YOLOv8 đã train
try:
    model = YOLO("runs/detect/train/weights/best.pt")
    print("✅ Đã tải mô hình YOLOv8 thành công")
except Exception as e:
    print(f"❌ Lỗi khi tải mô hình: {e}")
    # Fallback sang mô hình mặc định nếu không tìm thấy mô hình đã train
    try:
        model = YOLO("yolov8n.pt")
        print("⚠️ Sử dụng mô hình dự phòng YOLOv8n")
    except Exception as e:
        print(f"❌ Lỗi khi tải mô hình dự phòng: {e}")
        model = None

def detect_pipes(frame):
    """Phát hiện và đếm ống nước trong khung hình
    
    Args:
        frame: Hình ảnh OpenCV (numpy array)
        
    Returns:
        tuple: (frame đã xử lý, số lượng ống nước)
    """
    if model is None:
        return frame, 0
        
    results = model(frame)
    pipe_count = 0

    for r in results:
        pipe_count += len(r.boxes)
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.putText(frame, f"Ống nước: {pipe_count}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    return frame, pipe_count

# Giữ tính năng stream video cho ESP32-CAM
def generate_frames():
    cap = cv2.VideoCapture(ESP32_STREAM_URL)
    if not cap.isOpened():
        print("❌ Không thể kết nối ESP32-CAM")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Không đọc được frame từ ESP32-CAM")
            break

        processed_frame, _ = detect_pipes(frame)

        _, buffer = cv2.imencode(".jpg", processed_frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/detect_pipes")
async def detect_pipes_endpoint(file: UploadFile = File(...), product_id: Optional[str] = Form(None)):
    """Nhận ảnh từ client, phát hiện ống nước, và trả về kết quả
    
    Args:
        file: File hình ảnh được tải lên
        product_id: ID sản phẩm (tùy chọn)
        
    Returns:
        JSONResponse: Kết quả phân tích với số lượng ống nước và đường dẫn đến hình ảnh đã xử lý
    """
    try:
        # Tạo tên file duy nhất để tránh xung đột
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        
        # Lưu file đã tải lên
        upload_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Đọc hình ảnh bằng OpenCV
        img = cv2.imread(upload_path)
        if img is None:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Không thể đọc file hình ảnh"}
            )
            
        # Phát hiện ống nước trong hình ảnh
        processed_img, pipe_count = detect_pipes(img)
        
        # Lưu hình ảnh đã xử lý
        result_path = os.path.join(RESULT_FOLDER, f"processed_{filename}")
        cv2.imwrite(result_path, processed_img)
        
        # Trả về kết quả
        return JSONResponse(content={
            "success": True,
            "count": pipe_count,
            "product_id": product_id,
            "original_image": f"/uploads/{filename}",
            "processed_image": f"/results/processed_{filename}"
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/health")
def health_check():
    """Kiểm tra trạng thái hoạt động của API"""
    return {"status": "ok", "model_loaded": model is not None}

if __name__ == "__main__":
    import uvicorn
    # Chạy server trên cổng 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
