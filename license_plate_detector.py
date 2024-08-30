import easyocr
import cv2
import os
import numpy as np
import re
from ultralytics import YOLO

class LicensePlateDetector:
    def __init__(self, model_path: str, output_dir: str = "detected_plates"):
        self.model = YOLO(model_path)
        self.reader = easyocr.Reader(['en'])
        self.processed_plates = {}
        self.final_plates = set()
        self.output_dir = output_dir

        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        self.txt_file_path = os.path.join(self.output_dir, 'extracted_plates.txt')

    def preprocess_image(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def enhance_image(self, img):
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
        l, a, b = cv2.split(lab)
        l = cv2.equalizeHist(l)
        lab = cv2.merge((l, a, b))
        img = cv2.cvtColor(lab, cv2.COLOR_Lab2BGR)
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        img = cv2.filter2D(img, -1, kernel)
        return img

    def resize_for_ocr(self, img, scale_factor=2):
        width = int(img.shape[1] * scale_factor)
        height = int(img.shape[0] * scale_factor)
        dim = (width, height)
        return cv2.resize(img, dim, interpolation=cv2.INTER_LINEAR)

    def normalize_text(self, text):
        return re.sub(r'\s+', ' ', text).strip().upper()

    def is_valid_plate(self, text):
        pattern = r'^[A-Z0-9\- ]+$'
        return re.match(pattern, text)

    def save_detected_plate(self, cropped_image, plate_text):
        # Normalize and validate plate text
        normalized_plate = re.sub(r'\s+', ' ', plate_text).strip().upper()

        # Check if the plate text is already in the text file
        if os.path.exists(self.txt_file_path):
            with open(self.txt_file_path, 'r') as f:
                existing_plates = {line.strip() for line in f.readlines()}
        else:
            existing_plates = set()

        if normalized_plate not in existing_plates:
            # Save the cropped image as a PNG file
            image_file_name = f"{normalized_plate}.png"
            image_file_path = os.path.join(self.output_dir, image_file_name)
            cv2.imwrite(image_file_path, cropped_image)

            # Append the new plate text to the text file
            with open(self.txt_file_path, 'a') as f:
                f.write(normalized_plate + '\n')
            print(f"Saved new plate: {normalized_plate}")
        else:
            print(f"Duplicate plate {normalized_plate} not saved.")

    def detect_license_plates(self, frame):
        results = self.model(frame, conf=0.5)
        plates_info = []

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                license_plate_crop = frame[y1:y2, x1:x2]
                if license_plate_crop.size == 0:
                    continue
                preprocessed_crop = self.preprocess_image(license_plate_crop)
                enhanced_crop = self.enhance_image(preprocessed_crop)
                resized_crop = self.resize_for_ocr(enhanced_crop)
                ocr_results = self.reader.readtext(resized_crop)
                if not ocr_results:
                    continue
                detected_text = ' '.join(result[1] for result in ocr_results).strip()
                normalized_text = self.normalize_text(detected_text)
                if not self.is_valid_plate(normalized_text):
                    continue
                if normalized_text not in self.processed_plates:
                    self.processed_plates[normalized_text] = 0
                self.processed_plates[normalized_text] += 1
                if self.processed_plates[normalized_text] >= 5:
                    if normalized_text not in self.final_plates:
                        self.final_plates.add(normalized_text)
                        plates_info.append((x1, y1, x2, y2, normalized_text))
                        self.save_detected_plate(license_plate_crop, normalized_text)

        return plates_info
