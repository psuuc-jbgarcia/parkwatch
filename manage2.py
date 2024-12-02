import cv2
import pickle
import numpy as np
import json
# File path for parking positions
parking_file = 'CarParkPos2'
camera_file = 'json_file/camera_urls.json'
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
# Function to get the camera URL by ID
def get_camera_url(camera_id):
    camera_urls = load_camera_urls()
    for camera in camera_urls:
        if camera['id'] == camera_id:
            return camera['url']
    return 'carPark.mp4'  # Default URL if ID not found
# Ensure all positions are in the correct format
for i in range(len(posList)):
    if len(posList[i]) == 2:
        posList[i] = (*posList[i], False, 'rect', [], (107, 107))  # Default size (107, 48)
    elif len(posList[i]) == 3:
        posList[i] = (*posList[i], 'rect', [], (107, 107))
    elif len(posList[i]) == 4:
        posList[i] = (*posList[i], [],(107, 107))
    elif len(posList[i]) == 5:
        posList[i] = (*posList[i],(107, 107))
cctv_url = get_camera_url(2)
# Counter for the number of parking spaces
space_counter = len(posList)

# Flags for modes
delete_mode = False
resize_mode = False
resize_index = -1
trapezoid_mode = False
trapezoid_points = []
def empty(a):
    pass

# Create trackbars for adjusting threshold values
cv2.namedWindow("Vals")
cv2.resizeWindow("Vals", 640, 240)
cv2.createTrackbar("Val1", "Vals", 25, 50, empty)
cv2.createTrackbar("Val2", "Vals", 16, 50, empty)
cv2.createTrackbar("Val3", "Vals", 5, 50, empty)
cap = cv2.VideoCapture(cctv_url)

def draw_text_with_background(img, text, position, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.5, font_thickness=1, text_color=(255, 255, 255), background_color=(0, 0, 0)):
    """
    Draws text on an image with a background rectangle for better visibility.
    
    Args:
        img: The image to draw on.
        text: The text to be drawn.
        position: The position (x, y) to place the text.
        font: The font type.
        font_scale: The scale factor that is multiplied by the font-specific base size.
        font_thickness: The thickness of the text stroke.
        text_color: The color of the text.
        background_color: The color of the text background rectangle.
    """
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size

    # Calculate the bottom left corner of the rectangle
    rect_x, rect_y = position[0] - 5, position[1] + 5
    rect_w, rect_h = text_w + 10, text_h + 10

    # Draw the rectangle background
    cv2.rectangle(img, (rect_x, rect_y - rect_h), (rect_x + rect_w, rect_y), background_color, -1)

    # Draw the text
    cv2.putText(img, text, position, font, font_scale, text_color, font_thickness)


def checkSpaces(img, imgThres):
    global space_counter
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
        # elif shape == 'trapezoid':  # Add trapezoid handling here
        #     mask = np.zeros(imgThres.shape, dtype=np.uint8)
        #     points_np = np.array(points, dtype=np.int32)
        #     cv2.fillPoly(mask, [points_np], 255)
        #     imgCrop = cv2.bitwise_and(imgThres, mask)
        #     count = cv2.countNonZero(imgCrop)
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
        elif count < 15000:
            color = (0, 200, 0)
            thickness = 5
            spaces += 1
        else:
            color = (0, 0, 200)
            thickness = 2

        # Draw polygon with space number
        if shape == 'rect':
            cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)
            draw_text_with_background(img, f'Space {i+1}', (x + 10, y + 25), text_color=color)
        elif shape == 'portrait':
            cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)
            draw_text_with_background(img, f'Space {i+1}', (x + 10, y + 25), text_color=color)
        else:  # 'poly'
            if points:  # Ensure points are not empty
                points_np = np.array(points, dtype=np.int32)
                cv2.polylines(img, [points_np], isClosed=True, color=color, thickness=thickness)
                if points[0]:  # Ensure at least one point exists
                    draw_text_with_background(img, f'Space {i+1}', (points[0][0] + 10, points[0][1] + 25), text_color=color)
                    # draw_text_with_background(img, str(count), (points[0][0], points[0][1] - 6), text_color=color)

    draw_text_with_background(img, f'Free: {spaces}/{len(posList)}', (50, 60), text_color=(0, 200, 0), background_color=(0, 0, 0))
    draw_text_with_background(img, f'Reserved: {reserved_spaces}', (50, 110), text_color=(0, 255, 255), background_color=(0, 0, 0))

    # Display mode status
    if delete_mode:
        draw_text_with_background(img, "Delete Mode", (50, 150), text_color=(0, 0, 255), background_color=(0, 0, 0))
    if resize_mode:
        draw_text_with_background(img, "Resize Mode", (50, 200), text_color=(0, 255, 0), background_color=(0, 0, 0))
    if trapezoid_mode:
        draw_text_with_background(img, "Custom Shape Mode", (50, 200), text_color=(0, 255, 0), background_color=(0, 0, 0))

def mouseClick(events, x, y, flags, params):
    global posList, space_counter, delete_mode, resize_mode, resize_index, trapezoid_points

    if events == cv2.EVENT_LBUTTONDOWN:
        if delete_mode:
            for i, pos in enumerate(posList):
                px, py, reserved, shape, points, size = pos
                if shape == 'rect' and px < x < px + size[0] and py < y < py + size[1]:
                    posList.pop(i)
                    space_counter -= 1
                    save_pos_list()
                    break
                elif shape == 'portrait' and px < x < px + size[0] and py < y < py + size[1]:
                    posList.pop(i)
                    space_counter -= 1
                    save_pos_list()
                    break
                elif shape == 'poly' and cv2.pointPolygonTest(np.array(points, dtype=np.int32), (x, y), False) >= 0:
                    posList.pop(i)
                    space_counter -= 1
                    save_pos_list()
                    break
                elif shape == 'trapezoid':  # Handling trapezoid deletion
                    if cv2.pointPolygonTest(np.array(points, dtype=np.int32), (x, y), False) >= 0:
                        posList.pop(i)
                        space_counter -= 1
                        save_pos_list()
                        break
        elif resize_mode:
            for i, pos in enumerate(posList):
                px, py, reserved, shape, points, size = pos
                if shape in ['rect', 'portrait'] and px < x < px + size[0] and py < y < py + size[1]:
                    resize_index = i
                    break
        elif trapezoid_mode:
            trapezoid_points.append((x, y))  # Add point to trapezoid
            if len(trapezoid_points) == 4:  # If 4 points are collected
                posList.append((0, 0, False, 'trapezoid', trapezoid_points, (0, 0)))
                trapezoid_points = []  # Reset points for the next trapezoid
                save_pos_list()
        else:
            posList.append((x, y, False, 'rect', [], (107, 48)))  # Default size (107, 48)
            space_counter += 1
            save_pos_list()

    elif events == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate(posList):
            px, py, reserved, shape, points, size = pos
            if shape == 'rect' and px < x < px + size[0] and py < y < py + size[1]:
                posList[i] = (px, py, reserved, 'portrait', points, (48, 107))
                save_pos_list()
                break
            elif shape == 'portrait' and px < x < px + size[0] and py < y < py + size[1]:
                posList[i] = (px, py, reserved, 'rect', points, (107, 48))
                save_pos_list()
                break
            elif shape == 'poly' and cv2.pointPolygonTest(np.array(points, dtype=np.int32), (x, y), False) >= 0:
                posList.pop(i)
                space_counter -= 1
                save_pos_list()
                break
            elif shape == 'trapezoid':  # Handle trapezoid reservation toggle
                if cv2.pointPolygonTest(np.array(points, dtype=np.int32), (x, y), False) >= 0:
                    posList[i] = (px, py, not reserved, shape, points, size)
                    save_pos_list()
                    break

    elif events == cv2.EVENT_MBUTTONDOWN:
        for i, pos in enumerate(posList):
            px, py, reserved, shape, points, size = pos
            if shape == 'rect' and px < x < px + size[0] and py < y < py + size[1]:
                posList[i] = (px, py, not reserved, shape, points, size)
                save_pos_list()
                break
            elif shape == 'portrait' and px < x < x + size[0] and py < y < py + size[1]:
                posList[i] = (px, py, not reserved, shape, points, size)
                save_pos_list()
                break
            elif shape == 'poly' and cv2.pointPolygonTest(np.array(points, dtype=np.int32), (x, y), False) >= 0:
                posList[i] = (px, py, not reserved, shape, points, size)
                save_pos_list()
                break
            elif shape == 'trapezoid':  # Handle trapezoid reservation toggle
                if cv2.pointPolygonTest(np.array(points, dtype=np.int32), (x, y), False) >= 0:
                    posList[i] = (px, py, not reserved, shape, points, size)
                    save_pos_list()
                    break

    elif events == cv2.EVENT_LBUTTONDBLCLK:
        posList.append((x, y, False, 'poly', [(x, y)], (0, 0)))  # Polygon size is managed by points

    elif events == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
        if resize_mode and resize_index != -1:
            # Resize the rectangle
            px, py, reserved, shape, points, _ = posList[resize_index]
            new_size = (max(20, x - px), max(20, y - py))  # Ensure minimum size of 20x20
            posList[resize_index] = (px, py, reserved, shape, points, new_size)
            save_pos_list()
        elif posList and posList[-1][3] == 'poly':
            posList[-1][4].append((x, y))
            save_pos_list()

def save_pos_list():
    with open(parking_file, 'wb') as f:
        pickle.dump(posList, f)

# Open video capture for CCTV stream
# cctv_url = 'rtsp://admin:jerico12@192.168.100.159:5454/stream1'  # Replace with your CCTV stream URL
cap = cv2.VideoCapture(cctv_url)

# Get original video dimensions
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
screen_res = (frame_width, frame_height)

# Set window properties
cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.setMouseCallback("Image", mouseClick)

# Main loop
while True:
    success, img = cap.read()
    if not success:
        print("Failed to grab frame from CCTV feed.")
        break

    # No resizing of the image
    img_resized = img

    # Restart video if it reaches the end
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # Preprocess the image
    imgGray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
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
    checkSpaces(img_resized, imgThres)
    if trapezoid_mode and len(trapezoid_points) > 0:
        for point in trapezoid_points:
            cv2.circle(img, point, 5, (0, 255, 0), -1)  # Draw green circles for points

    # Display output
    cv2.imshow("Image", img_resized)

    key = cv2.waitKey(10)
    if key == ord('s'):
        break
    elif key == ord('d'):
        # Toggle delete mode
        delete_mode = not delete_mode
        resize_mode = False  # Ensure resize mode is turned off
        print("Mode switched to Delete Mode" if delete_mode else "Mode switched to Normal Mode")
    elif key == ord('r'):
        # Toggle resize mode
        resize_mode = not resize_mode
        delete_mode = False  # Ensure delete mode is turned off
        resize_index = -1  # Reset resize index
        print("Mode switched to Resize Mode" if resize_mode else "Mode switched to Normal Mode")
    elif key == ord('t'):  # Toggle trapezoid mode
        trapezoid_mode = not trapezoid_mode
        print("Mode switched to Custom Shape Mode" if trapezoid_mode else "Mode switched to Normal Mode")


# Release video capture and close all windows
cap.release()
cv2.destroyAllWindows()




