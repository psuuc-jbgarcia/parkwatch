import cv2
import numpy as np
import pickle
import os
from flask import Flask, render_template, Response, request, jsonify,send_from_directory
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import subprocess
from license_plate_detector import LicensePlateDetector
from firebase.firebase_config import db
import json,time
import pytz
import datetime
import threading
from camera_manager import load_camera_urls, save_camera_urls, get_video_source, generate_frames, add_camera, get_cameras,get_parking_info2
from incident_manager import report_incident, save_full_parking_timestamp, fetch_comments, save_full_parking_timestamp2
from flask import send_file,abort
from report import generate_report,process_parking_data  # Import the generate_report function
from fpdf import FPDF
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
# Path to your trained YOLO model
# model_path = 'license_plate_detector.pt'
daily_total_parked_vehicles = 0
daily_reserved_vehicles = 0
FULL_PARKING_TIMESTAMPS_FILE = 'full_parking_timestamps.json'
DAILY_REPORT_FILE = 'daily_report.json'
CAMERA_FILE_PATH = 'camera_urls.json'
cameraIdCounter = 2  # Start camera ID from 2
camera_urls_path = os.path.join(app.root_path, 'camera_urls.json')

scheduler = BackgroundScheduler(timezone='Asia/Manila')

# Initialize License Plate Detector
# plate_detector = LicensePlateDetector(model_path)
# Adjust Code for Network Latency
# If the camera is on a different network with high latency, increase the timeout value for cv2.VideoCapture.
# Example:

# python
# Copy code
# cap1_web.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)  # Set a longer timeout
# File path for parking positions
parking_file = 'CarParkPos'
timeout_ms = 60000  # Adjust as needed rtsp://admin:jerico12@192.168.100.159:5454/stream1
vid1 = 'car.mp4'
cap1_web = cv2.VideoCapture(vid1, cv2.CAP_FFMPEG)
cap2_web = cv2.VideoCapture(vid1,cv2.CAP_FFMPEG)
cap1_flutter = cv2.VideoCapture(vid1,cv2.CAP_FFMPEG)
cap2_flutter = cv2.VideoCapture(vid1,cv2.CAP_FFMPEG)

cap1_web.set(cv2.CAP_PROP_BUFFERSIZE, 3)
cap2_web.set(cv2.CAP_PROP_BUFFERSIZE, 3)
cap1_flutter.set(cv2.CAP_PROP_BUFFERSIZE, 3)
cap2_flutter.set(cv2.CAP_PROP_BUFFERSIZE, 3)

def run_plate_script():
    try:
        # Make sure to provide the correct path to plate.py
        subprocess.Popen(['python', 'license.py'])
        print("plate.py script is running...")
    except Exception as e:
        print(f"Error running plate.py: {e}")

def save_daily_report():
    global daily_total_parked_vehicles, daily_reserved_vehicles

    tz = pytz.timezone('Asia/Manila')
    now = datetime.datetime.now(tz)
    today = now.strftime('%Y-%m-%d')

    report_data = {
        'date': today,
        'total_parked_vehicles': daily_total_parked_vehicles,
        'reserved_vehicles': daily_reserved_vehicles
    }

    print("Attempting to save daily report...")

    try:
        if os.path.exists(DAILY_REPORT_FILE):
            try:
                with open(DAILY_REPORT_FILE, 'r') as file:
                    reports = json.load(file)
            except json.JSONDecodeError:
                print("JSON decoding error. Initializing empty list.")
                reports = []
        else:
            reports = []

        reports.append(report_data)
        print("Writing to JSON file...")

        with open(DAILY_REPORT_FILE, 'w') as file:
            json.dump(reports, file)

        print(f"Report saved at {now.strftime('%Y-%m-%d %H:%M:%S')}")

        daily_total_parked_vehicles = 0
        daily_reserved_vehicles = 0

    except Exception as e:
        print(f"Error saving daily report: {e}")


def schedule_daily_report():
    global scheduler
    if not scheduler.get_job('daily_report_job'):
        trigger = CronTrigger(hour='23', minute='59')

        # trigger = CronTrigger(minute='*/1')  # For testing purposes, every minute
        scheduler.add_job(save_daily_report, trigger, id='daily_report_job')
        print("Scheduled daily report job.")
    else:
        print("Daily report job already scheduled.")


# Schedule the daily report job
schedule_daily_report()

# Start the scheduler
scheduler.start()
def load_pos_list():
    if not os.path.exists(parking_file):
        print(f"Error: File not found: {parking_file}")
        return []
    try:
        with open(parking_file, 'rb') as f:
            return pickle.load(f)
    except (pickle.PickleError, EOFError, IOError) as e:
        print(f"Error loading pickle file: {e}")
        return []

# Initialize or load parking positions
posList = load_pos_list()

# Ensure all positions are in the correct format
for i in range(len(posList)):
    if len(posList[i]) == 2:
        posList[i] = (*posList[i], False, 'poly', [])
    elif len(posList[i]) == 3:
        posList[i] = (*posList[i], 'poly', [])
    elif len(posList[i]) == 4:
        posList[i] = (*posList[i], posList[i][3])

# Counter for the number of parking spaces
space_counter = len(posList)

# Global variables to store parking information
free_spaces = 0
reserved_spaces = 0

def empty(a):
    pass

# Create trackbars for adjusting threshold values
cv2.namedWindow("Vals")
cv2.resizeWindow("Vals", 640, 240)
cv2.createTrackbar("Val1", "Vals", 25, 50, empty)
cv2.createTrackbar("Val2", "Vals", 16, 50, empty)
cv2.createTrackbar("Val3", "Vals", 5, 50, empty)

def checkSpaces(img, imgThres):
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
        if shape == 'rect':
            imgCrop = imgThres[y:y + h, x:x + w]
            count = cv2.countNonZero(imgCrop)
        elif shape == 'portrait':
            imgCrop = imgThres[y:y + h, x:x + w]
            count = cv2.countNonZero(imgCrop)
        else:  # 'poly'
            mask = np.zeros(imgThres.shape, dtype=np.uint8)
            points_np = np.array(points, dtype=np.int32)
            cv2.fillPoly(mask, [points_np], 255)
            imgCrop = cv2.bitwise_and(imgThres, mask)
            count = cv2.countNonZero(imgCrop)

        # Check if space is reserved or parked
        if reserved:
            color = (0, 255, 255)  # Yellow for reserved
            thickness = 5
            if not was_reserved:  # Increment only when transitioning from non-reserved to reserved
                daily_reserved_vehicles += 1
                posList[i] = (*pos[:6], True, was_occupied)  # Update state in posList
            reserved_spaces += 1  # Count for displaying purposes
        elif count < 1200:
            color = (0, 200, 0)  # Green for free space
            thickness = 5
            if not was_occupied:  # Increment only when transitioning from not occupied to occupied
                daily_total_parked_vehicles += 1
                posList[i] = (*pos[:6], was_reserved, True)  # Update state in posList
            spaces += 1  # Count for displaying purposes
        else:
            color = (0, 0, 200)  # Red for occupied
            thickness = 2
            # Reset if previously reserved or occupied
            if was_reserved or was_occupied:
                posList[i] = (*pos[:6], False, False)  # Reset states to False

        # Draw shapes and text with background
        if shape == 'rect':
            cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)
            cv2.putText(img, f'Space {i+1}', (x + 10, y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
        elif shape == 'portrait':
            cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)
            cv2.putText(img, f'Space {i+1}', (x + 10, y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
        else:  # 'poly'
            if points:
                points_np = np.array(points, dtype=np.int32)
                cv2.polylines(img, [points_np], isClosed=True, color=color, thickness=thickness)
                if points[0]:
                    cv2.putText(img, f'Space {i+1}', (points[0][0] + 10, points[0][1] + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
                    cv2.putText(img, str(count), (points[0][0], points[0][1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)

    # Update global counters
    free_spaces = spaces
    reserved_spaces = reserved_spaces

    # Display counters
    cv2.putText(img, f'Free: {spaces}/{len(posList)}', (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 0), 1, lineType=cv2.LINE_AA)
    cv2.putText(img, f'Reserved: {reserved_spaces}', (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, lineType=cv2.LINE_AA)

class ParkingFileEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == os.path.abspath(parking_file):
            global posList
            posList = load_pos_list()

event_handler = ParkingFileEventHandler()
observer = Observer()
observer.schedule(event_handler, path=os.path.dirname(os.path.abspath(parking_file)), recursive=False)
observer.start()

def gen_frames(video_source):
    while True:
        success, frame = video_source.read()
        if not success:
            print("Failed to grab frame, retrying...")
            video_source.release()
            video_source = cv2.VideoCapture(vid1, cv2.CAP_FFMPEG)
            continue

        # Preprocess the frame as before
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

        
        checkSpaces(frame, imgThres)

        # Encode image as jpg format
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("Failed to encode frame")
            break
        frame = buffer.tobytes()

        # Yielding current state of posList along with frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



def gen_frames_for_flutter(video_source):
    last_time = time.time()
    frame_rate = 30  # Desired frame rate
    while True:
        # Calculate time between frames
        current_time = time.time()
        elapsed_time = current_time - last_time
        if elapsed_time < 1.0 / frame_rate:
            continue  # Skip frame to maintain frame rate

        last_time = current_time  # Update the last frame time
        
        # Read and process frames as usual
        success, frame = video_source.read()
        if not success:
            print("Failed to grab frame, retrying...")
            video_source.release()
            video_source = cv2.VideoCapture(vid1, cv2.CAP_FFMPEG)
            continue

        # Preprocess and apply threshold as in your code
        imgGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)

        # Get threshold values
        val1 = cv2.getTrackbarPos("Val1", "Vals")
        val2 = cv2.getTrackbarPos("Val2", "Vals")
        val3 = cv2.getTrackbarPos("Val3", "Vals")

        if val1 % 2 == 0: val1 += 1
        if val3 % 2 == 0: val3 += 1

        imgThres = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, val1, val2)
        imgThres = cv2.medianBlur(imgThres, val3)
        kernel = np.ones((3, 3), np.uint8)
        imgThres = cv2.dilate(imgThres, kernel, iterations=1)

        checkSpaces(frame, imgThres)

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("Failed to encode frame")
            break
        frame_bytes = buffer.tobytes()

        pos_list_serialized = pickle.dumps(posList)

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n' + pos_list_serialized + b'\r\n')



@app.route('/')
def index():
    return render_template ('index.html')  # Ensure this file exists in templates folder

@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    try:
        if camera_id == 1:
            return Response(gen_frames(cap1_web), mimetype='multipart/x-mixed-replace; boundary=frame')
        elif camera_id == 2:
            return Response(gen_frames(cap2_web), mimetype='multipart/x-mixed-replace; boundary=frame')
        else:
            return "Invalid camera ID", 404
    except Exception as e:
        print(f"Error in video_feed: {e}")
        return "Error occurred", 500

@app.route('/video_feed_flutter/<int:camera_id>')
def video_feed_flutter(camera_id):
    try:
        if camera_id == 1:
            return Response(gen_frames_for_flutter(cap1_flutter), mimetype='multipart/x-mixed-replace; boundary=frame')
        elif camera_id == 2:
            return Response(gen_frames_for_flutter(cap2_flutter), mimetype='multipart/x-mixed-replace; boundary=frame')
        else:
            return "Invalid camera ID", 404
    except Exception as e:
        print(f"Error in video_feed_flutter: {e}")
        return "Error occurred", 500



@app.route('/get_parking_info')
def get_parking_info():
    global posList, free_spaces, reserved_spaces
    total_vehicles = len(posList) - free_spaces

    return jsonify({
        'totalVehicles': total_vehicles,
        'parkingAvailable': free_spaces,
        'slotsReserved': reserved_spaces
    })

@app.route('/run_management', methods=['GET'])
def run_management():
    try:
        result = subprocess.run(['python', 'manage.py'], capture_output=True, text=True)
        print(result.stdout)
        return result.stdout, 200
    except Exception as e:
        print(f"Error running management script: {e}")
        return str(e), 500
@app.route('/run_management2', methods=['GET'])
def run_management2():
    try:
        result = subprocess.run(['python', 'manage2.py'], capture_output=True, text=True)
        print(result.stdout)
        return result.stdout, 200
    except Exception as e:
        print(f"Error running management script: {e}")
        return str(e), 500
    
@app.route('/report_incident', methods=['POST'])
def report_incident_route():
    return report_incident()

@app.route('/save_full_parking_timestamp', methods=['POST'])
def save_full_parking_timestamp_route():
    return save_full_parking_timestamp()
@app.route('/save_full_parking_timestamp2', methods=['POST'])
def save_full_parking_timestamp_route2():
    return save_full_parking_timestamp2()  # Call the function to handle the request


# @app.route('/fetch_comments', methods=['GET'])
# def fetch_comments_route():
#     return fetch_comments()

@app.route('/add_camera', methods=['POST'])
def add_camera_route():
    return add_camera()

@app.route('/video_feed_parking_space_2', methods=['GET'])
def get_cameras_route():
    return get_cameras()

@app.route('/video_feed/2')
def video_feed_parking_space_2():
    """Video streaming route for parking space 2."""
    video_source = get_video_source(2)  # Camera ID 2 for parking space 2
    if video_source:
        return Response(generate_frames(video_source),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "Video source not found.", 404
@app.route('/get_parking_info2', methods=['GET'])
def parking_info_route():
    return get_parking_info2()



@app.route('/camera_urls.json')
def get_camera_urls():
    return send_from_directory(os.getcwd(), 'camera_urls.json')
@app.route('/edit_camera/<int:camera_id>', methods=['POST'])
def edit_camera(camera_id):
    data = request.get_json()
    new_url = data.get('url')

    # Load your camera URLs from the JSON file
    with open('camera_urls.json', 'r') as f:
        cameras = json.load(f)

    # Update the camera URL
    for camera in cameras:
        if camera['id'] == camera_id:
            camera['url'] = new_url
            break

    # Save back to the JSON file
    with open('camera_urls.json', 'w') as f:
        json.dump(cameras, f)

    return jsonify({"message": "Camera updated successfully"}), 200


@app.route('/delete_camera/<int:camera_id>', methods=['DELETE'])
def delete_camera(camera_id):
    # Load your camera URLs from the JSON file
    with open('camera_urls.json', 'r') as f:
        cameras = json.load(f)

    # Remove the camera from the list
    cameras = [camera for camera in cameras if camera['id'] != camera_id]

    # Save back to the JSON file
    with open('camera_urls.json', 'w') as f:
        json.dump(cameras, f)

    return jsonify({"message": "Camera deleted successfully"}), 200
@app.route('/generate_report')
def generate_report_route():
    parking_file_path = 'full_parking_timestamps.json'
    detected_plates_file_path = 'detected_plates.json'
    daily_report_file_path = 'daily_report.json'
    
    # Get the 'date' parameter from the request
    date_str = request.args.get('date')
    
    if not date_str:
        return jsonify({'error': 'Date parameter is missing'}), 400
    
    report = None  # Initialize report variable
    
    try:
        # Generate the report using the provided date and all necessary file paths
        report = generate_report(parking_file_path, detected_plates_file_path, daily_report_file_path, date_str)
        
        # Check if the report was generated successfully
        if report:
            return jsonify({'report': report})  # Return JSON response with the report
        else:
            return jsonify({'error': 'Report generation failed. No data available for the given date.'}), 404

    except Exception as e:
        # Log the error and return a detailed error response
        print(f"Error generating report: {e}")
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    ####################################################
@app.route('/fetch_user_reports')
def fetch_user_reports():
    db = firestore.client()
    reports_ref = db.collection('userreports')  # Assuming reports are in the 'admin' collection
    reports = reports_ref.stream()

    report_list = []
    for report in reports:
        report_data = report.to_dict()
        report_list.append({
            'description': report_data.get('description', 'No description'),
            'name': report_data.get('name', 'Unknown'),
            'timestamp': report_data.get('timestamp', 'Unknown')
        })

    return jsonify(report_list)


if __name__ == '__main__':
    # run_plate_script()
    app.run(debug=True, host='0.0.0.0', port=5000)
    # use_reloader=False
