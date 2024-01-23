"""
? Convert / Download the Video using CV2
"""

import os
import cv2
IN_PATH = os.path.join("2021-10-13 04:32:22.416976.h264")
OUT_PATH = os.path.join("converted.mp4")

cap = cv2.VideoCapture(IN_PATH)

# OUTPUT VARIABLES
fourcc = cv2.VideoWriter_fourcc(*'avc1')
fps = cap.get(cv2.CAP_PROP_FPS)
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
print(f"FPS: {fps}, Height: {height}, Width: {width}")

video_writer = cv2.VideoWriter(OUT_PATH, fourcc, fps, (width, height))

print("Writing...")
count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if ret and frame is not None:
        print(f"Converting Frame {count}", end="\r")
        cv2.imshow(f"{IN_PATH}", frame)
        video_writer.write(frame)
        count += 1
        
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break  
        
    else:
        print("FINISHED CONVERTING", end= "\r")
        print()
        break

cap.release()
video_writer.release()
cv2.destroyAllWindows()





