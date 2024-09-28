import easyocr
import cv2
import os
import re
import numpy as np
import json
from datetime import datetime
from ultralytics import YOLO

def preprocess_image(img):
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding or other preprocessing methods
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return thresh

def enhance_image(img):
    # Ensure the image is in color before applying enhancement
    if len(img.shape) == 2:  # Grayscale image
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    
    # Increase contrast and sharpen the image
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
    l, a, b = cv2.split(lab)
    l = cv2.equalizeHist(l)
    lab = cv2.merge((l, a, b))
    img = cv2.cvtColor(lab, cv2.COLOR_Lab2BGR)
    
    # Sharpen the image
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    img = cv2.filter2D(img, -1, kernel)
    
    return img

def resize_for_ocr(img, scale_factor=2):
    # Resize image for better OCR accuracy
    width = int(img.shape[1] * scale_factor)
    height = int(img.shape[0] * scale_factor)
    dim = (width, height)
    resized_img = cv2.resize(img, dim, interpolation=cv2.INTER_LINEAR)
    return resized_img

def normalize_text(text):
    # Normalize text by removing extra spaces and converting to uppercase
    return re.sub(r'\s+', ' ', text).strip().upper()

def is_valid_plate(text):
    # Check if the text matches the typical format of a license plate
    pattern = r'^[A-Z0-9\- ]+$'
    return re.match(pattern, text)

# Initialize YOLO model and EasyOCR reader
model = YOLO('license_plate_detector.pt')  # Replace with your YOLO model path
reader = easyocr.Reader(['en'])

# Define paths
video_path = 'a.mp4'
output_json_path = 'detected_plates.json'
output_images_dir = 'detected_images'

# Create directory for saving images if it doesn't exist
if not os.path.exists(output_images_dir):
    os.makedirs(output_images_dir)

# Load and process the video
cap = cv2.VideoCapture(0)

# Set to track processed license plates and their variations
processed_plates = {}
plate_states = {}
detected_plates_data = []

frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Process every 5th frame to improve performance
    if frame_count % 5 == 0:
        # Apply YOLO detection on the current frame
        results = model(frame, conf=0.5)

        current_detected_plates = set()

        # Process each detected license plate
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                license_plate_crop = frame[y1:y2, x1:x2]

                if license_plate_crop.size == 0:
                    print(f"Empty crop for coordinates: ({x1}, {y1}, {x2}, {y2})")
                    continue

                # Preprocess and enhance image
                preprocessed_crop = preprocess_image(license_plate_crop)
                enhanced_crop = enhance_image(preprocessed_crop)
                resized_crop = resize_for_ocr(enhanced_crop)

                # Use EasyOCR to extract text
                ocr_results = reader.readtext(resized_crop)

                if not ocr_results:
                    print(f"No text detected in crop from coordinates: ({x1}, {y1}, {x2}, {y2})")
                    continue

                # Extract and normalize text from OCR results
                detected_text = ' '.join(result[1] for result in ocr_results).strip()
                normalized_text = normalize_text(detected_text)

                # Check if the normalized text is a valid plate
                if not is_valid_plate(normalized_text):
                    print(f"Invalid plate format: {normalized_text}. Skipping.")
                    continue

                # Debug print to check actual text and normalization
                print(f"Detected text: {detected_text}")
                print(f"Normalized text: {normalized_text}")

                current_detected_plates.add(normalized_text)

                # If the normalized text has stabilized
                if normalized_text not in plate_states:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    plate_states[normalized_text] = {
                        'arrival_time': timestamp,
                        'departure_time': None
                    }
                    detected_plates_data.append({
                        'plate_number': normalized_text,
                        'arrival_time': timestamp,
                        'departure_time': None
                    })

                    # Save the cropped image with the detected plate
                    image_path = os.path.join(output_images_dir, f"{normalized_text}.jpg")
                    cv2.imwrite(image_path, license_plate_crop)
                    print(f"Saved image: {image_path}")

                    # Save detected plates data to JSON immediately after detection
                    with open(output_json_path, 'w') as json_file:
                        json.dump(detected_plates_data, json_file, indent=4)
                    print(f"Detected plates saved to {output_json_path}.")

                # Draw a rectangle around the detected license plate
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Overlay text on the frame with a background rectangle
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.7
                font_color = (0, 255, 0)  # Green color
                font_thickness = 2
                text_size, _ = cv2.getTextSize(normalized_text, font, font_scale, font_thickness)
                text_x = x1
                text_y = y1 - 10  # Position text above the detected plate
                background_top_left = (text_x, text_y - text_size[1] - 10)
                background_bottom_right = (text_x + text_size[0], text_y + 5)

                # Draw the background rectangle for text
                cv2.rectangle(frame, background_top_left, background_bottom_right, (0, 0, 0), cv2.FILLED)

                # Draw the text on the frame
                cv2.putText(frame, normalized_text, (text_x, text_y), font, font_scale, font_color, font_thickness, cv2.LINE_AA)

        # Update departure time for plates not detected in the current frame
        for plate in list(plate_states.keys()):
            if plate not in current_detected_plates:
                # If not detected, set the departure time
                if plate_states[plate]['departure_time'] is None:
                    plate_states[plate]['departure_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    # Update detected_plates_data to reflect the departure time
                    for entry in detected_plates_data:
                        if entry['plate_number'] == plate:
                            entry['departure_time'] = plate_states[plate]['departure_time']
                            break
                    print(f"Plate {plate} has departed at {plate_states[plate]['departure_time']}")
                    del plate_states[plate]  # Optionally remove it from tracking

        # Show the video frame with overlayed text
        cv2.imshow('Video', frame)

    frame_count += 1

    # Exit the video display if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Final save in case there are plates that were not saved previously
with open(output_json_path, 'w') as json_file:
    json.dump(detected_plates_data, json_file, indent=4)
print(f"Final detected plates saved to {output_json_path}.")
