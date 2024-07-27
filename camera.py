import cv2
import numpy as np
import math
import time
from utils import get_centroid, process_frame

class Camera:
    def __init__(self):
        self.cap = None
        self.prev_position = None
        self.prev_frame_time = None
        self.car_counter = 0
        self.total_speed = 0
        self.num_cars = 0

    def process_frame(self, frame1, frame2):
        contours, _ = process_frame(frame1, frame2)
        
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w < 40 or h < 40:
                continue

            centroid = get_centroid(x, y, w, h)
            cy = centroid[1]

            if (cy < 460) and (cy > 440):
                self.car_counter += 0.27

                current_position = centroid

                if self.prev_position is not None and self.prev_frame_time is not None:
                    distance = math.sqrt((current_position[0] - self.prev_position[0]) ** 2 +
                                         (current_position[1] - self.prev_position[1]) ** 2)
                    time_elapsed = time.time() - self.prev_frame_time

                    if time_elapsed != 0:
                        speed = distance / time_elapsed
                        self.total_speed += speed
                        self.num_cars += 1

                self.prev_position = current_position
                self.prev_frame_time = time.time()

        cv2.putText(frame1, f"Vehicle Count: {math.floor(self.car_counter)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if self.num_cars != 0:
            average_speed = self.total_speed / self.num_cars
            speed_text = f"Average Speed: {average_speed:.2f} kmph"
            cv2.putText(frame1, speed_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        return frame1

    def generate_frames(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            print("Error: Camera not opened.")
            return

        ret, frame1 = self.cap.read()
        ret, frame2 = self.cap.read()

        if not ret:
            print("Error: Failed to capture frame.")
            return

        while ret:
            frame = self.process_frame(frame1, frame2)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            frame1 = frame2
            ret, frame2 = self.cap.read()

            if not ret:
                print("Error: Failed to capture frame.")
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def start_camera(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            print("Error: Camera not opened.")
            return
        
        self.prev_position = None
        self.prev_frame_time = None
        self.car_counter = 0
        self.total_speed = 0
        self.num_cars = 0

    def stop_camera(self):
        if self.cap is not None:
            self.cap.release()
        self.cap = None
