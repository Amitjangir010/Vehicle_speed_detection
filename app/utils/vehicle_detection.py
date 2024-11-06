import cv2
import numpy as np
from datetime import datetime
from collections import deque
from .constants import *  # Import constants

class VehicleDetector:
    def __init__(self):
        # Background subtractor with history
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=BG_HISTORY,
            varThreshold=BG_THRESHOLD,
            detectShadows=BG_SHADOW
        )
        
        # Vehicle tracking
        self.vehicles = {}
        self.vehicle_count = 0
        self.current_speeds = []
        self.min_area = MIN_CONTOUR_AREA
        self.ref_iou = IOU_THRESHOLD
        
        # Detection line (middle of frame)
        self.detection_line_y = None
        
        # Store last average speed
        self.last_avg_speed = 0
        
    def detect_vehicles(self, frame):
        height, width = frame.shape[:2]
        if self.detection_line_y is None:
            self.detection_line_y = height // 2
            
        # Process frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(blur)
        
        # Clean up mask
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Reset current frame data
        boxes = []
        self.current_speeds = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area:
                continue
                
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            
            # Filter out non-vehicle shapes
            if not (MIN_ASPECT_RATIO < aspect_ratio < MAX_ASPECT_RATIO):
                continue
                
            # Track vehicle
            vehicle_id = self.track_vehicle(x, y, w, h)
            if vehicle_id:
                boxes.append([x, y, w, h])
                speed = self.calculate_speed(vehicle_id, y)
                self.current_speeds.append(speed)
                
                # Update count if vehicle crosses line
                if not self.vehicles[vehicle_id]['counted']:
                    if (self.vehicles[vehicle_id]['prev_y'] < self.detection_line_y and 
                        y >= self.detection_line_y):
                        self.vehicle_count += 1
                        self.vehicles[vehicle_id]['counted'] = True
        
        # Clean up old vehicles
        self.cleanup_old_vehicles()
        
        # Calculate and store average speed
        if self.current_speeds:
            self.last_avg_speed = sum(self.current_speeds) / len(self.current_speeds)
            
        # Return last known speed if no current vehicles
        current_speeds = self.current_speeds if self.current_speeds else [self.last_avg_speed]
        
        return boxes, current_speeds, self.vehicle_count
        
    def track_vehicle(self, x, y, w, h):
        current_time = datetime.now()
        current_box = [x, y, w, h]
        
        # Check existing vehicles
        for vid, vehicle in self.vehicles.items():
            if 'box' in vehicle:
                iou = self.calculate_iou(current_box, vehicle['box'])
                if iou > self.ref_iou:
                    # Update vehicle data
                    vehicle.update({
                        'box': current_box,
                        'prev_y': vehicle['y'],
                        'y': y,
                        'last_seen': current_time,
                        'positions': vehicle['positions'] + [(x + w//2, y + h//2)]
                    })
                    return vid
        
        # New vehicle
        new_id = f"vehicle_{len(self.vehicles)}"
        self.vehicles[new_id] = {
            'box': current_box,
            'y': y,
            'prev_y': y,
            'first_seen': current_time,
            'last_seen': current_time,
            'counted': False,
            'positions': [(x + w//2, y + h//2)]
        }
        return new_id
        
    def calculate_speed(self, vehicle_id, current_y):
        vehicle = self.vehicles[vehicle_id]
        if len(vehicle['positions']) < POSITIONS_HISTORY:
            return 0
            
        # Use longer time window
        time_diff = (vehicle['last_seen'] - vehicle['first_seen']).total_seconds()
        if time_diff > MIN_SPEED_TIME:
            # Use more positions for average
            positions = vehicle['positions'][-POSITIONS_HISTORY:]  # Last 10 positions
            total_distance = 0
            
            # Calculate average speed over multiple points
            for i in range(len(positions)-1):
                p1 = positions[i]
                p2 = positions[i+1]
                total_distance += np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            
            # Better pixel to meter conversion (calibrated for typical road view)
            meters_per_pixel = METERS_PER_PIXEL  # More realistic value
            speed = (total_distance * meters_per_pixel / time_diff) * 3.6
            
            # Smooth the speed using moving average
            if 'speed_history' not in vehicle:
                vehicle['speed_history'] = []
            vehicle['speed_history'].append(speed)
            if len(vehicle['speed_history']) > SPEED_HISTORY:
                vehicle['speed_history'].pop(0)
                
            avg_speed = sum(vehicle['speed_history']) / len(vehicle['speed_history'])
            return min(avg_speed, MAX_SPEED)
        return 0
        
    def calculate_iou(self, box1, box2):
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        
        xi1 = max(x1, x2)
        yi1 = max(y1, y2)
        xi2 = min(x1 + w1, x2 + w2)
        yi2 = min(y1 + h1, y2 + h2)
        
        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
        box1_area = w1 * h1
        box2_area = w2 * h2
        
        iou = inter_area / float(box1_area + box2_area - inter_area)
        return iou
        
    def cleanup_old_vehicles(self):
        current_time = datetime.now()
        self.vehicles = {
            vid: vehicle for vid, vehicle in self.vehicles.items()
            if (current_time - vehicle['last_seen']).seconds < 1
        }