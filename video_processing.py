import cv2
import numpy as np
import math
import time
from utils import get_centroid, process_frame

def estimate_vehicle_speed(video_path):
    line_height = 450
    car_counter = 0
    total_speed = 0
    num_cars = 0
    prev_position = None
    prev_frame_time = None

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video file")
        return

    ret, frame1 = cap.read()
    ret, frame2 = cap.read()

    while ret:
        contours, _ = process_frame(frame1, frame2, line_height)
        
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w < 40 or h < 40:
                continue

            centroid = get_centroid(x, y, w, h)
            cy = centroid[1]

            if (cy < line_height + 10) and (cy > line_height - 10):
                car_counter += 0.27

                current_position = centroid

                if prev_position is not None and prev_frame_time is not None:
                    distance = math.sqrt((current_position[0] - prev_position[0]) ** 2 +
                                         (current_position[1] - prev_position[1]) ** 2)
                    time_elapsed = time.time() - prev_frame_time

                    if time_elapsed != 0:
                        speed = distance / time_elapsed
                        total_speed += speed
                        num_cars += 1

                prev_position = current_position
                prev_frame_time = time.time()

        cv2.putText(frame1, f"Vehicle Count: {math.floor(car_counter)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 4)
        
        if num_cars != 0:
            average_speed = total_speed / num_cars
            speed_text = f"Average Speed: {average_speed:.2f} kmph"
            cv2.putText(frame1, speed_text, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 4)

        cv2.imshow("Vehicle Detection", cv2.resize(frame1, (700, 480)))

        if cv2.waitKey(40) == ord('q'):
            break

        frame1 = frame2
        ret, frame2 = cap.read()

    cv2.destroyAllWindows()
    cap.release()

    return speed_text
