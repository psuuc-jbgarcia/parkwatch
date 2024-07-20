import cv2
import pickle
import numpy as np

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

# Counter for the number of parking spaces
space_counter = len(posList)

# Flag for delete mode
delete_mode = False

def empty(a):
    pass

# Create trackbars for adjusting threshold values
cv2.namedWindow("Vals")
cv2.resizeWindow("Vals", 640, 240)
cv2.createTrackbar("Val1", "Vals", 25, 50, empty)
cv2.createTrackbar("Val2", "Vals", 16, 50, empty)
cv2.createTrackbar("Val3", "Vals", 5, 50, empty)

def draw_text_with_background(img, text, position, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1, font_thickness=2, text_color=(255, 255, 255), background_color=(0, 0, 0)):
    """
    Draws text on an image with a background rectangle for better visibility.
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
        x, y, reserved, shape, points = pos

        if shape == 'rect':
            w, h = 107, 48
            imgCrop = imgThres[y:y + h, x:x + w]
            count = cv2.countNonZero(imgCrop)
        elif shape == 'portrait':
            w, h = 48, 107
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

        # Draw polygon with space number
        if shape == 'rect':
            cv2.rectangle(img, (x, y), (x + 107, y + 48), color, thickness)
            draw_text_with_background(img, f'Space {i+1}', (x + 10, y + 25), text_color=color)
        elif shape == 'portrait':
            cv2.rectangle(img, (x, y), (x + 48, y + 107), color, thickness)
            draw_text_with_background(img, f'Space {i+1}', (x + 10, y + 25), text_color=color)
        else:  # 'poly'
            if points:  # Ensure points are not empty
                points_np = np.array(points, dtype=np.int32)
                cv2.polylines(img, [points_np], isClosed=True, color=color, thickness=thickness)
                if points[0]:  # Ensure at least one point exists
                    draw_text_with_background(img, f'Space {i+1}', (points[0][0] + 10, points[0][1] + 25), text_color=color)
                    draw_text_with_background(img, str(count), (points[0][0], points[0][1] - 6), text_color=color)

    draw_text_with_background(img, f'Free: {spaces}/{len(posList)}', (50, 60), text_color=(0, 200, 0), background_color=(0, 0, 0))
    draw_text_with_background(img, f'Reserved: {reserved_spaces}', (50, 110), text_color=(0, 255, 255), background_color=(0, 0, 0))

    # Display mode status
    mode_text = "Delete Mode" if delete_mode else "Normal Mode"
    draw_text_with_background(img, mode_text, (50, 150), text_color=(0, 255, 0) if delete_mode else (0, 0, 255), background_color=(0, 0, 0))

def mouseClick(events, x, y, flags, params):
    global posList, space_counter, delete_mode
    if events == cv2.EVENT_LBUTTONDOWN:
        if delete_mode:
            # Delete parking space in delete mode
            for i, pos in enumerate(posList):
                px, py, reserved, shape, points = pos
                if shape == 'rect' and px < x < px + 107 and py < y < py + 48:
                    posList.pop(i)
                    space_counter -= 1
                    save_pos_list()
                    break
                elif shape == 'portrait' and px < x < px + 48 and py < y < py + 107:
                    posList.pop(i)
                    space_counter -= 1
                    save_pos_list()
                    break
                elif shape == 'poly' and cv2.pointPolygonTest(np.array(points, dtype=np.int32), (x, y), False) >= 0:
                    posList.pop(i)
                    space_counter -= 1
                    save_pos_list()
                    break
        else:
            # Add new parking space
            posList.append((x, y, False, 'rect', []))
            space_counter += 1
            save_pos_list()
    elif events == cv2.EVENT_RBUTTONDOWN:
        # Toggle shape between 'rect' and 'portrait'
        for i, pos in enumerate(posList):
            px, py, reserved, shape, points = pos
            if shape == 'rect' and px < x < px + 107 and py < y < py + 48:
                posList[i] = (px, py, reserved, 'portrait', points)
                save_pos_list()
                break
            elif shape == 'portrait' and px < x < px + 48 and py < y < py + 107:
                posList[i] = (px, py, reserved, 'rect', points)
                save_pos_list()
                break
            elif shape == 'poly' and cv2.pointPolygonTest(np.array(points, dtype=np.int32), (x, y), False) >= 0:
                posList.pop(i)
                space_counter -= 1
                save_pos_list()
                break
    elif events == cv2.EVENT_MBUTTONDOWN:
        # Toggle reserved status for the clicked parking space
        for i, pos in enumerate(posList):
            px, py, reserved, shape, points = pos
            if shape == 'rect' and px < x < px + 107 and py < y < py + 48:
                posList[i] = (px, py, not reserved, shape, points)
                save_pos_list()
                break
            elif shape == 'portrait' and px < x < px + 48 and py < y < py + 107:
                posList[i] = (px, py, not reserved, shape, points)
                save_pos_list()
                break
            elif shape == 'poly' and cv2.pointPolygonTest(np.array(points, dtype=np.int32), (x, y), False) >= 0:
                posList[i] = (px, py, not reserved, shape, points)
                save_pos_list()
                break
    elif events == cv2.EVENT_LBUTTONDBLCLK:
        # Start drawing a new polygon
        posList.append((x, y, False, 'poly', [(x, y)]))
    elif events == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
        # Continue drawing a polygon
        if posList and posList[-1][3] == 'poly':
            posList[-1][4].append((x, y))
            save_pos_list()

def save_pos_list():
    with open(parking_file, 'wb') as f:
        pickle.dump(posList, f)

# Open video capture
cap = cv2.VideoCapture('carPark.mp4')  # Change to your video source

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

    # Display output
    cv2.imshow("Image", img_resized)

    key = cv2.waitKey(1)
    if key == ord('s'):
        break
    elif key == ord('d'):
        # Toggle delete mode
        delete_mode = not delete_mode
        mode = "Delete Mode" if delete_mode else "Normal Mode"
        print(f"Mode switched to {mode}")

# Release video capture and close all windows
cap.release()
cv2.destroyAllWindows()
