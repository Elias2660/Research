"""
? Can we render these videos correctly though?
"""
import os
import cv2

path = os.path.join("2021-10-13 04:32:22.416976.h264")
cap = cv2.VideoCapture(path)
count = 0
while cap.isOpened():
    ret, frame = cap.read()
    
    if frame is None or not ret:
        break
    elif ret and frame is not None:
        count += 1
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
cap.release()
cv2.destroyAllWindows()