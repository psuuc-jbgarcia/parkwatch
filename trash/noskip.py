import easyocr
import cv2
import os
import re
import numpy as np
import json
from datetime import datetime
import time
from ultralytics import YOLO

def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def enhance_image(img):
    if len(img.shape) == 2:  # Grayscale image
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
    l, a, b = cv2.split(lab)
    l = cv2.equalizeHist(l)
    lab = cv2.merge((l, a, b))
    img = cv2.cvtColor(lab, cv2.COLOR_Lab2BGR)
    
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    img = cv2.filter2D(img, -1, kernel)
    
    return img

def resize_for_ocr(img, scale_factor=2):
    width = int(img.shape[1] * scale_factor)
    height = int(img.shape[0] * scale_factor)
    dim = (width, height)
    return cv2.resize(img, dim, interpolation=cv2.INTER_LINEAR)

def normalize_text(text):
    return re.sub(r'\s+', ' ', text).strip().upper().replace("-", " ")

def is_valid_plate(text):
    pattern = r'^[A-Z0-9\s]+$'
    return re.match(pattern, text)

# Initialize YOLO model and EasyOCR reader
model = YOLO('license_plate_detector.pt')
reader = easyocr.Reader(['en'])

# Define paths
video_path = 'test1.mp4'
output_json_path = 'json_file/detected_plates.json'
output_images_dir = 'detected_plates'

if not os.path.exists(output_images_dir):
    os.makedirs(output_images_dir)

# Load existing plate records if they exist
detected_plates_data = []
if os.path.exists(output_json_path):
    # Check if the file is not empty before loading
    if os.path.getsize(output_json_path) > 0:
        try:
            with open(output_json_path, 'r') as json_file:
                detected_plates_data = json.load(json_file)
        except json.JSONDecodeError as e:
            print(f"Error loading JSON data: {e}. The file may be malformed.")
            detected_plates_data = []  # Reset to an empty list in case of an error
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            detected_plates_data = []  # Reset to an empty list in case of an unexpected error
    else:
        print(f"{output_json_path} is empty. No plate records to load.")


# Create a dictionary for easy access to plate data
plate_states = {entry['plate_number']: entry for entry in detected_plates_data}

STABILITY_THRESHOLD = 3  # number of frames for stability
MIN_PLATE_LENGTH = 5  # Minimum length for a valid plate

frame_count = 0
stable_plate = None
stable_count = 0

cap = cv2.VideoCapture(0)

while cap.isOpened():

    ret, frame = cap.read()
    if not ret:
        break

    # if frame_count % 5 == 0:
    results = model(frame, conf=0.5)
    current_detected_plates = {}

    for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                license_plate_crop = frame[y1:y2, x1:x2]

                if license_plate_crop.size == 0:
                    continue

                preprocessed_crop = preprocess_image(license_plate_crop)
                enhanced_crop = enhance_image(preprocessed_crop)
                resized_crop = resize_for_ocr(enhanced_crop)

                ocr_results = reader.readtext(resized_crop)

                if not ocr_results:
                    continue

                detected_text = ' '.join(result[1] for result in ocr_results).strip()
                normalized_text = normalize_text(detected_text)

                if not is_valid_plate(normalized_text) or len(normalized_text) < MIN_PLATE_LENGTH:
                    continue

                # Remove any duplicate entries in the same frame
                current_detected_plates[normalized_text] = time.time()

                # Check stability
                if stable_plate == normalized_text:
                    stable_count += 1
                else:
                    stable_plate = normalized_text
                    stable_count = 1  # reset counter on change

                # Only finalize if stable
                if stable_count >= STABILITY_THRESHOLD:
                    current_time = time.time()

                    # Check if the plate is already recorded
                    if stable_plate in plate_states:
                        # If plate exists, add a new entry for departure
                        departure_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        detected_plates_data.append({
                            'plate_number': stable_plate,
                            'arrival_time': plate_states[stable_plate]['arrival_time'],
                            'departure_time': departure_time
                        })
                    else:
                        # If not recorded, add a new entry for arrival
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        plate_states[stable_plate] = {
                            'plate_number': stable_plate,
                            'arrival_time': timestamp
                        }
                        detected_plates_data.append({
                            'plate_number': stable_plate,
                            'arrival_time': timestamp,
                            'departure_time': None  # No departure time yet
                        })

                        # Save the cropped image
                        image_path = os.path.join(output_images_dir, f"{stable_plate}.jpg")
                        cv2.imwrite(image_path, license_plate_crop)

                    # Save detected plates data to JSON
                    with open(output_json_path, 'w') as json_file:
                        json.dump(detected_plates_data, json_file, indent=4)

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.7
                font_color = (0, 255, 0)
                font_thickness = 2
                text_size, _ = cv2.getTextSize(normalized_text, font, font_scale, font_thickness)
                text_x = x1
                text_y = y1 - 10
                background_top_left = (text_x, text_y - text_size[1] - 10)
                background_bottom_right = (text_x + text_size[0], text_y + 5)

                cv2.rectangle(frame, background_top_left, background_bottom_right, (0, 0, 0), cv2.FILLED)
                cv2.putText(frame, normalized_text, (text_x, text_y), font, font_scale, font_color, font_thickness, cv2.LINE_AA)

        # Show the video frame with overlayed text
    cv2.imshow('Plate Number Recognition', frame)

    frame_count += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Final save in case there are plates that were not saved previously
with open(output_json_path, 'w') as json_file:
    json.dump(detected_plates_data, json_file, indent=4)
