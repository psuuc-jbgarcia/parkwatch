import cv2
import numpy as np
import json
import pickle
from ultralytics import YOLO  # Import the YOLO class from ultralytics

# File path for parking positions
parking_file = 'CarParkPos2'
camera_file = 'camera_urls.json'

# Load YOLOv8 model
model = YOLO('yolov8n.pt')  # Load YOLOv8 model weights directly

# Function to load parking positions
def load_pos_list():
    try:
        with open(parking_file, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        print(f"Warning: {parking_file} not found.")
        return []

# Initialize or load parking positions
posList = load_pos_list()

# Function to load camera URLs
def load_camera_urls():
    try:
        with open(camera_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {camera_file} not found.")
        return []

video_path = 'vid.mp4'  # Replace with your video file path

# Counter for the number of parking spaces
space_counter = len(posList)
def checkSpaces(img):
    global space_counter
    results = model(img)  # Perform detection
    detections = results[0].boxes  # Get the boxes

    spaces = 0

    for det in detections:
        # Check if there are bounding boxes detected
        if det.xyxy is not None and len(det.xyxy) > 0:
            for box in det.xyxy:
                # Ensure the box contains at least 6 values before unpacking
                if len(box) >= 6:
                    # Unpack bounding box data safely
                    x1, y1, x2, y2, conf, cls = box.tolist()  # Convert tensor to list
                    class_id = int(cls)

                    # Check for car, motorcycle, or tricycle (YOLO classes)
                    if class_id in [0, 1, 2]:  # Assuming 0 = car, 1 = motorcycle, 2 = tricycle
                        # Draw bounding box
                        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
                        label = f'{model.names[class_id]}: {conf:.2f}'
                        cv2.putText(img, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        spaces += 1  # Count detected vehicles

    # Update display with detection counts
    cv2.putText(img, f'Detected: {spaces}', (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


    # Update display with detection counts
    cv2.putText(img, f'Detected: {spaces}', (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

def mouseClick(events, x, y, flags, params):
    # Your existing mouse click handling logic
    pass

def save_pos_list():
    # Your existing save position logic
    pass

# Open video capture for video file
cap = cv2.VideoCapture(video_path)

# Main loop
while True:
    success, img = cap.read()
    if not success:
        print("End of video or failed to grab frame.")
        break

    # Check for spaces and draw rectangles using YOLO
    checkSpaces(img)

    # Display output
    cv2.imshow("Image", img)

    key = cv2.waitKey(10)
    if key == ord('s'):
        break

# Release video capture and close all windows
cap.release()
cv2.destroyAllWindows()
