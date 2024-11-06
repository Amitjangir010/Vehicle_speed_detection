import cv2
import numpy as np
import argparse
import json

class CameraCalibrator:
    def __init__(self):
        self.points = []
        self.reference_distance = 2.0  # meters
        self.calibration_results = {
            'meters_per_pixel': 0,
            'vehicle_width': 0,
            'vehicle_height': 0,
            'min_area': 0
        }
        
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.points.append((x, y))
            cv2.circle(self.frame, (x, y), 3, (0, 255, 0), -1)
            
            if len(self.points) == 2:
                cv2.line(self.frame, self.points[0], self.points[1], (0, 255, 0), 2)
                pixel_distance = np.sqrt(
                    (self.points[1][0] - self.points[0][0])**2 + 
                    (self.points[1][1] - self.points[0][1])**2
                )
                self.calibration_results['meters_per_pixel'] = self.reference_distance / pixel_distance
                print(f"\nDistance Calibration:")
                print(f"Reference distance: {self.reference_distance} meters")
                print(f"Pixel distance: {pixel_distance:.2f} pixels")
                print(f"Meters per pixel: {self.calibration_results['meters_per_pixel']:.6f}")
    
    def measure_vehicle(self):
        print("\nDraw rectangle around a typical vehicle (click and drag)")
        print("Press SPACE or ENTER to confirm selection")
        print("Press 'c' to cancel and retry")
        
        while True:
            rect = cv2.selectROI('Vehicle Measurement', self.frame, False)
            x, y, w, h = rect
            
            # Check if selection is valid
            if w > 0 and h > 0:
                self.calibration_results.update({
                    'vehicle_width': w,
                    'vehicle_height': h,
                    'min_area': w * h * 0.7  # 30% margin for minimum area
                })
                
                print(f"\nVehicle Measurements:")
                print(f"Width: {w} pixels")
                print(f"Height: {h} pixels")
                print(f"Area: {w * h} pixels²")
                print(f"Minimum area: {self.calibration_results['min_area']} pixels²")
                print(f"Aspect ratio: {w/h:.2f}")
                
                cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.imshow('Calibration Result', self.frame)
                cv2.waitKey(0)
                break
            else:
                print("\nInvalid selection! Please try again.")
                continue
    
    def calibrate(self, source=0):
        print("\nCamera Calibration Tool")
        print("=======================")
        print("1. Mark two points of known distance (e.g., 2 meters)")
        print("2. Draw rectangle around a typical vehicle")
        print("3. Press 'q' to save and quit")
        print("\nStarting camera...")
        
        try:
            cap = cv2.VideoCapture(source)
            if not cap.isOpened():
                print("Error: Could not open camera/video")
                return False
                
            # Get first frame
            ret, self.frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                return False
                
            # Set up window for distance calibration
            cv2.namedWindow('Calibration')
            cv2.setMouseCallback('Calibration', self.mouse_callback)
            
            print("\nStep 1: Click two points of known distance")
            while True:
                cv2.imshow('Calibration', self.frame)
                if cv2.waitKey(1) & 0xFF == ord('q') or len(self.points) == 2:
                    break
            
            # Measure vehicle only if distance calibration was successful
            if len(self.points) == 2:
                self.measure_vehicle()
            
            # Clean up
            cap.release()
            cv2.destroyAllWindows()
            
            # Save calibration results
            if self.calibration_results['meters_per_pixel'] > 0 and self.calibration_results['min_area'] > 0:
                self.save_calibration()
                return True
            else:
                print("\nCalibration incomplete! Please try again.")
                return False
                
        except Exception as e:
            print(f"\nError during calibration: {str(e)}")
            return False
            
    def save_calibration(self):
        try:
            # Save to constants.py
            with open('app/utils/constants.py', 'r') as f:
                lines = f.readlines()
            
            with open('app/utils/constants.py', 'w') as f:
                for line in lines:
                    if 'METERS_PER_PIXEL =' in line:
                        f.write(f"METERS_PER_PIXEL = {self.calibration_results['meters_per_pixel']}  # Calibrated value\n")
                    elif 'MIN_CONTOUR_AREA =' in line:
                        f.write(f"MIN_CONTOUR_AREA = {self.calibration_results['min_area']}  # Calibrated value\n")
                    elif 'vehicle_width =' in line:
                        f.write(f"vehicle_width = {self.calibration_results['vehicle_width']}  # Calibrated value\n")
                    elif 'vehicle_height =' in line:
                        f.write(f"vehicle_height = {self.calibration_results['vehicle_height']}  # Calibrated value\n")
                    else:
                        f.write(line)
                        
            print("\nCalibration values saved successfully!")
            print("You can now run the main application.")
            
        except Exception as e:
            print(f"\nError saving calibration: {str(e)}")
            # Save to backup file
            with open('calibration_results.json', 'w') as f:
                json.dump(self.calibration_results, f, indent=4)
            print("Calibration results saved to calibration_results.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Camera Calibration Tool')
    parser.add_argument('--source', type=str, default='0',
                        help='Camera index or video file (default: 0)')
    parser.add_argument('--distance', type=float, default=2.0,
                        help='Reference distance in meters (default: 2.0)')
    
    args = parser.parse_args()
    
    calibrator = CameraCalibrator()
    calibrator.reference_distance = args.distance
    
    # Handle both camera index and video file
    source = int(args.source) if args.source.isdigit() else args.source
    
    if calibrator.calibrate(source):
        print("\nCalibration completed successfully!")
    else:
        print("\nCalibration failed. Please try again.")