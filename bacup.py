import json
import cv2
from flask import Response, jsonify, request

CAMERA_FILE_PATH = 'camera_urls.json'

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

def generate_frames(video_source):
    cap = cv2.VideoCapture(video_source)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Encode as JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # Yield the frame as bytes
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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

        # Determine the next ID
        next_id = max((camera['id'] for camera in camera_urls), default=1) + 1

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
