import cv2

# First camera with DirectShow backend
cap1 = cv2.VideoCapture(1)




while True:
    ret1, frame1 = cap1.read()

    if ret1:
        cv2.imshow('Camera 1', frame1)
    

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap1.release()
cv2.destroyAllWindows()
