import json
import cv2
from flask import Response, jsonify, request
import numpy as np
import pickle
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time,datetime
from firebase_admin import storage

daily_total_parked_vehicles = 0
daily_reserved_vehicles = 0
CAMERA_FILE_PATH = 'json_file/camera_urls.json'
PARKING_FILE_PATH = 'CarParkPos2'
class ParkingFileEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == os.path.abspath(PARKING_FILE_PATH):
            global posList
            posList = load_pos_list()

event_handler = ParkingFileEventHandler()
observer = Observer()
observer.schedule(event_handler, path=os.path.dirname(os.path.abspath(PARKING_FILE_PATH)), recursive=False)
observer.start()
# Initialize or load parking positions
def load_pos_list():
    if not os.path.exists(PARKING_FILE_PATH):
        print(f"Error: File not found: {PARKING_FILE_PATH}")
        return []
    try:
        with open(PARKING_FILE_PATH, 'rb') as f:
            return pickle.load(f)
    except (pickle.PickleError, EOFError, IOError) as e:
        print(f"Error loading pickle file: {e}")
        return []

posList = load_pos_list()
for i in range(len(posList)):
    if len(posList[i]) == 2:
        posList[i] = (*posList[i], False, 'poly', [])
    elif len(posList[i]) == 3:
        posList[i] = (*posList[i], 'poly', [])
    elif len(posList[i]) == 4:
        posList[i] = (*posList[i], posList[i][3])

space_counter = len(posList)
free_spaces = 0
reserved_spaces = 0

def empty(a):
    pass

cv2.namedWindow("Vals")
cv2.resizeWindow("Vals", 640, 240)
cv2.createTrackbar("Val1", "Vals", 25, 50, empty)
cv2.createTrackbar("Val2", "Vals", 16, 50, empty)
cv2.createTrackbar("Val3", "Vals", 5, 50, empty)

def check_spaces(img, imgThres):
    global space_counter, free_spaces, reserved_spaces
    global daily_total_parked_vehicles, daily_reserved_vehicles
    
    spaces = 0
    reserved_spaces = 0
    
    for i, pos in enumerate(posList):
        # Ensure default values if not enough elements in pos
        if len(pos) < 6:
            print(f"Warning: Unexpected format for position {i}: {pos}")
            continue  # Skip this entry as it's not in the expected format

        x, y, reserved, shape, points, size = pos[:6]  # Unpack the first 6 elements safely

        # Ensure the additional fields have default values if missing
        was_reserved = pos[6] if len(pos) > 6 else False
        was_occupied = pos[7] if len(pos) > 7 else False

        w, h = size

        # Determine the number of non-zero pixels in the defined shape
        if shape in ['rect', 'portrait']:
            imgCrop = imgThres[y:y + h, x:x + w]
            count = cv2.countNonZero(imgCrop)
        elif shape == 'trapezoid':
            mask = np.zeros(imgThres.shape, dtype=np.uint8)
            points_np = np.array(points, dtype=np.int32)
            cv2.fillPoly(mask, [points_np], 255)
            imgCrop = cv2.bitwise_and(imgThres, mask)
            count = cv2.countNonZero(imgCrop)
        else:  # 'poly' shape
            mask = np.zeros(imgThres.shape, dtype=np.uint8)
            points_np = np.array(points, dtype=np.int32)
            cv2.fillPoly(mask, [points_np], 255)
            imgCrop = cv2.bitwise_and(imgThres, mask)
            count = cv2.countNonZero(imgCrop)

        # Check if space is reserved or parked
        if reserved:
            color = (0, 255, 255)  # Yellow for reserved
            thickness = 5
            reserved_spaces += 1  # Increment reserved spaces for display
            
            # Only increment daily_reserved_vehicles if transitioning from not reserved
            if not was_reserved:
                daily_reserved_vehicles += 1
                posList[i] = (*pos[:6], True, was_occupied)  # Update state in posList
        elif count < 15000:  # Free space
            color = (0, 200, 0)  # Green for free space
            thickness = 5
            
            # Only increment daily_total_parked_vehicles if transitioning to parked
            if not was_occupied:  
                daily_total_parked_vehicles += 1
                posList[i] = (*pos[:6], reserved, True)  # Update state in posList
            spaces += 1  # Count for displaying purposes
        else:  # Occupied space
            color = (0, 0, 200)  # Red for occupied
            thickness = 2
            
            # Reset only if previously reserved or occupied
            if was_reserved or was_occupied:
                posList[i] = (*pos[:6], False, False)  # Reset states to False

        # Draw shapes and text with background
        if shape in ['rect', 'portrait']:
            cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)
            cv2.putText(img, f'Space {i + 1}', (x + 10, y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
        else:  # 'poly' shape
            if points:
                points_np = np.array(points, dtype=np.int32)
                cv2.polylines(img, [points_np], isClosed=True, color=color, thickness=thickness)
                if points[0]:
                    cv2.putText(img, f'Space {i + 1}', (points[0][0] + 10, points[0][1] + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
                    # cv2.putText(img, str(count), (points[0][0] + 10, points[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    # Update global counters
    free_spaces = spaces

    # Display counters
    # cv2.putText(img, f'Free: {spaces}/{len(posList)}', (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 0), 1, lineType=cv2.LINE_AA)
    # cv2.putText(img, f'Reserved: {reserved_spaces}', (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, lineType=cv2.LINE_AA)


def generate_frames(video_source):
    cap = cv2.VideoCapture(video_source)
    
    while True:
        success, frame = cap.read()
        
        if not success:
            print("Failed to grab frame, retrying...")
            cap.release()  # Release the current capture
            cap = cv2.VideoCapture(video_source, cv2.CAP_FFMPEG)  # Reinitialize the capture
            continue
        
        # Preprocess the frame
        imgGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)

        # Get threshold values
        val1 = cv2.getTrackbarPos("Val1", "Vals")
        val2 = cv2.getTrackbarPos("Val2", "Vals")
        val3 = cv2.getTrackbarPos("Val3", "Vals")

        # Ensure odd values for threshold parameters
        if val1 % 2 == 0: val1 += 1
        if val3 % 2 == 0: val3 += 1

        # Apply adaptive threshold and blur
        imgThres = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, val1, val2)
        imgThres = cv2.medianBlur(imgThres, val3)
        kernel = np.ones((3, 3), np.uint8)
        imgThres = cv2.dilate(imgThres, kernel, iterations=1)

        # Check for free spaces and draw rectangles
        check_spaces(frame, imgThres)

        # Encode image as jpg format
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("Failed to encode frame")
            continue
        
        frame_bytes = buffer.tobytes()

        # Serialize posList only if necessary
        pos_list_serialized = pickle.dumps(posList)

        # Yielding the current state of posList along with frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n' + pos_list_serialized + b'\r\n')

def upload_frame_to_firebase2(frame_bytes, file_name):
    # Define the folder name
    folder_name = 'parkingmodel'
    
    # Combine the folder name with the file name
    full_file_name = f"{folder_name}/parkingmodel2"
    
    # Get the bucket
    bucket = storage.bucket()
    
    # Create a blob (i.e., a reference to the file in Firebase Storage)
    blob = bucket.blob(full_file_name)
    time.sleep(5)  # Wait for 1 second between uploads

    # Upload the frame as binary data (frame_bytes)
    blob.upload_from_string(frame_bytes, content_type='image/jpeg')
    print(f"Uploaded {file_name} to Firebase Storage in folder '{folder_name}'")
    
    # Optionally, you can retrieve the file's public URL
    download_url = blob.public_url
    # print(f"Image uploaded and accessible at: {download_url}")

def parking_model2(video_source):
    last_time = time.time()
    frame_rate = 30  # Desired frame rate
    
    top_color = np.array([245, 245, 245], dtype=np.uint8)
    bottom_color = np.array([230, 230, 230], dtype=np.uint8)
    
    retries = 3  # Number of retry attempts
    retry_delay = 2  # Delay in seconds between retries

    while True:
        current_time = time.time()
        elapsed_time = current_time - last_time
        if elapsed_time < 1.0 / frame_rate:
            continue

        last_time = current_time
        
        success, frame = video_source.read()
        
        # Retry logic if frame is not successfully grabbed
        if not success:
            print("Failed to grab frame, retrying...")
            for attempt in range(retries):
                print(f"Retrying... Attempt {attempt + 1}/{retries}")
                time.sleep(retry_delay)  # Wait before retrying
                success, frame = video_source.read()
                if success:
                    print("Frame grabbed successfully")
                    break
            if not success:
                print("Failed to grab frame after retries, exiting...")
                break

        height, width, _ = frame.shape
        gradient = np.zeros_like(frame, dtype=np.uint8)

        # Create smooth gradient background
        for y in range(height):
            alpha = y / height
            color = (1 - alpha) * top_color + alpha * bottom_color
            gradient[y, :] = color

        # Convert to grayscale and apply processing
        imgGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)

        val1 = cv2.getTrackbarPos("Val1", "Vals")
        val2 = cv2.getTrackbarPos("Val2", "Vals")
        val3 = cv2.getTrackbarPos("Val3", "Vals")
        
        if val1 % 2 == 0: val1 += 1
        if val3 % 2 == 0: val3 += 1

        imgThres = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, val1, val2)
        imgThres = cv2.medianBlur(imgThres, val3)
        kernel = np.ones((3, 3), np.uint8)
        imgThres = cv2.dilate(imgThres, kernel, iterations=1)

        check_spaces(gradient, imgThres)  # Assuming this is a function to overlay detected spaces

        cv2.putText(gradient, "Parking Model", (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.rectangle(gradient, (0, 0), (width-1, height-1), (255, 255, 255), 3)

        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', gradient)
        if not ret:
            print("Failed to encode frame")
            break
        frame_bytes = buffer.tobytes()

        # Upload the frame to Firebase
        upload_frame_to_firebase2(frame_bytes, 'parking_model2.jpg')  # Save as 'parking_frame.jpg' or use a dynamic name
        pos_list_serialized = pickle.dumps(posList)

        # Yield the frame and serialized data for streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n' +
               b'Content-Type: application/octet-stream\r\n\r\n' + pos_list_serialized + b'\r\n')

def load_camera_urls():
    """Load camera URLs from the JSON file."""
    try:
        with open(CAMERA_FILE_PATH, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_camera_urls(camera_urls):
    """Save camera URLs to the JSON file."""
    with open(CAMERA_FILE_PATH, 'w') as file:
        json.dump(camera_urls, file, indent=4)

def get_video_source(camera_id):
    try:
        with open(CAMERA_FILE_PATH) as f:
            cameras = json.load(f)
        for camera in cameras:
            if camera['id'] == camera_id:
                return camera['url']
        return None
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None

def add_camera():
    """Add a new camera from a JSON POST request."""
    if request.content_type != 'application/json':
        return jsonify({'error': 'Content-type must be application/json'}), 400

    try:
        data = request.json
        if not data:
            raise ValueError("No JSON data received")

        camera_url = data.get('url')
        if not camera_url:
            raise ValueError("Invalid data: 'url' is required")

        # Load existing camera URLs
        camera_urls = load_camera_urls()

        # Check if there is already 1 camera (new limit)
        if len(camera_urls) >= 1:
            return jsonify({'error': 'Only 2 camera is supported for now.'}), 400

        # Determine the next ID, starting from 2
        current_ids = [camera['id'] for camera in camera_urls]
        next_id = max(current_ids, default=1) + 1
        if next_id < 2:
            next_id = 2

        # Add the new camera with the next ID
        camera_urls.append({
            'id': next_id,
            'url': camera_url
        })

        # Save updated list back to the JSON file
        save_camera_urls(camera_urls)

        return jsonify({'message': 'Camera added successfully', 'camera': {'id': next_id, 'url': camera_url}}), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500


def get_cameras():
    """Fetch all camera URLs from the JSON file."""
    try:
        cameras = load_camera_urls()
        
        if not cameras:
            return jsonify({"error": "No cameras available"}), 404

        return jsonify(cameras), 200
    except Exception as e:
        return jsonify({"error": "Failed to load cameras"}), 500
def get_parking_info2():
    global posList, free_spaces, reserved_spaces
    total_vehicles = len(posList) - free_spaces

    return jsonify({
        'totalVehicles': total_vehicles,
        'parkingAvailable': free_spaces,
        'slotsReserved': reserved_spaces
    })