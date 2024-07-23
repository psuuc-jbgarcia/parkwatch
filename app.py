from flask import Flask, render_template, Response, request, jsonify
import cv2
import pickle
import numpy as np
import subprocess
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

app = Flask(__name__)

# File path for parking positions
parking_file = 'CarParkPos'

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

# Ensure all positions are in the correct format
for i in range(len(posList)):
    if len(posList[i]) == 2:
        posList[i] = (*posList[i], False, 'poly', [])
    elif len(posList[i]) == 3:
        posList[i] = (*posList[i], 'poly', [])
    elif len(posList[i]) == 4:
        posList[i] = (*posList[i], posList[i][3])  # Correct format for existing entries

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
    spaces = 0
    reserved_spaces = 0
    for i, pos in enumerate(posList):
        x, y, reserved, shape, points, size = pos
        w, h = size

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

        if reserved:
            color = (0, 255, 255)  # Yellow for reserved
            thickness = 5
            reserved_spaces += 1
        elif count < 900:
            color = (0, 200, 0)
            thickness = 5
            spaces += 1
        else:
            color = (0, 0, 200)
            thickness = 2

        # Draw shapes and text with background
        if shape == 'rect':
            cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)
            cv2.putText(img, f'Space {i+1}', (x + 10, y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
        elif shape == 'portrait':
            cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)
            cv2.putText(img, f'Space {i+1}', (x + 10, y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
        else:  # 'poly'
            if points:  # Ensure points are not empty
                points_np = np.array(points, dtype=np.int32)
                cv2.polylines(img, [points_np], isClosed=True, color=color, thickness=thickness)
                if points[0]:  # Ensure at least one point exists
                    cv2.putText(img, f'Space {i+1}', (points[0][0] + 10, points[0][1] + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
                    cv2.putText(img, str(count), (points[0][0], points[0][1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)

    free_spaces = spaces
    cv2.putText(img, f'Free: {spaces}/{len(posList)}', (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 0), 1, lineType=cv2.LINE_AA)
    cv2.putText(img, f'Reserved: {reserved_spaces}', (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, lineType=cv2.LINE_AA)


# Monitor changes to the parking file using watchdog
class ParkingFileEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == os.path.abspath(parking_file):
            global posList
            posList = load_pos_list()

event_handler = ParkingFileEventHandler()
observer = Observer()
observer.schedule(event_handler, path=os.path.dirname(os.path.abspath(parking_file)), recursive=False)
observer.start()

# Initialize video captures for multiple feeds
cap1 = cv2.VideoCapture('vid.mp4')
cap2 = cv2.VideoCapture('vid.mp4')  # Additional video source

def gen_frames(video_source):
    prev_frame_time = 0
    while True:
        success, frame = video_source.read()
        if not success:
            break

        # Preprocess the frame
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

        # Check for free spaces and draw rectangles
        checkSpaces(frame, imgThres)

        # Encode image as jpg format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Calculate delay to match the video frame rate
        curr_frame_time = cv2.getTickCount()
        time_diff = (curr_frame_time - prev_frame_time) / cv2.getTickFrequency()
        prev_frame_time = curr_frame_time
        delay = max(int(1000 / 30 - time_diff * 1000), 1)  # Assuming 30 FPS, adjust if needed

        # Yielding current state of posList along with frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n' + pickle.dumps(posList) + b'\r\n')

        # Adding delay to simulate frame rate
        cv2.waitKey(delay)

# Flask routes
@app.route('/')
def index():
    return render_template('index.php')  # Ensure this file exists in templates folder

@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    if camera_id == 1:
        return Response(gen_frames(cap1), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif camera_id == 2:
        return Response(gen_frames(cap2), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "Invalid camera ID", 404

@app.route('/get_parking_info')
def get_parking_info():
    global posList, free_spaces, reserved_spaces
    total_vehicles = len(posList) - free_spaces  # Total vehicles parked is the total number of parking positions minus free spaces

    return jsonify({
        'totalVehicles': total_vehicles,
        'parkingAvailable': free_spaces,
        'slotsReserved': reserved_spaces
    })

@app.route('/run_management', methods=['GET'])
def run_management():
    try:
        # Replace 'python manage.py' with the command to run your management script
        result = subprocess.run(['python', 'manage.py'], capture_output=True, text=True)
        print(result.stdout)
        return result.stdout, 200
    except Exception as e:
        print(f"Error running management script: {e}")
        return str(e), 500

@app.route('/update_positions', methods=['POST'])
def update_positions():
    global posList
    data = request.get_data()
    posList = pickle.loads(data)
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True)
