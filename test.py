import cv2

# RTSP URL from IP webcam app
rtsp_url = 'rtsp://192.168.100.112:8080/h264_aac.sdp'

# Create a VideoCapture object
cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("Error: Could not open RTSP stream.")
    exit()

# Define scaling factor
scale_factor = 0.5  # Adjust this value to zoom out or in (e.g., 0.5 for 50% of original size)

while True:
    ret, frame = cap.read()
    
    if ret:
        # Resize the frame
        width = int(frame.shape[1] * scale_factor)
        height = int(frame.shape[0] * scale_factor)
        dim = (width, height)
        
        resized_frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
        
        cv2.imshow('RTSP Stream', resized_frame)
        
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        print("Error: Could not read frame.")
        break

cap.release()
cv2.destroyAllWindows()
