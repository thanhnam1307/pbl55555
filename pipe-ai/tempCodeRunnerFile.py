import cv2
import requests
import numpy as np

ESP32_STREAM_URL = "http://172.20.10.2:81/stream"  # Thay bằng IP ESP32-CAM

def detect_pipes(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=10, maxRadius=50)
    
    count = len(circles[0]) if circles is not None else 0
    return count, frame

cap = cv2.VideoCapture(ESP32_STREAM_URL)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Không thể lấy dữ liệu từ ESP32-CAM")
        break

    count, processed_frame = detect_pipes(frame)
    cv2.putText(processed_frame, f"Ống nước: {count}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow("ESP32-CAM Stream", processed_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
