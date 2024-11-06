from flask import Flask, render_template, Response, jsonify, request
import cv2
import time
import os
from .utils.vehicle_detection import VehicleDetector
from .utils.constants import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-please-change'

# Global variables
detector = VehicleDetector()
is_camera_active = False
is_video_mode = False
is_paused = False
camera = None
video_path = None

def init_camera():
    """Try different camera indices and return working camera"""
    try:
        if not is_video_mode:
            cap = cv2.VideoCapture(0)
        else:
            cap = cv2.VideoCapture(video_path)
            
        if cap and cap.isOpened():
            if not is_video_mode:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
            return cap
    except Exception as e:
        print(f"Error initializing camera/video: {str(e)}")
    return None

def generate_frames():
    global is_camera_active, camera, is_paused
    
    while is_camera_active and camera and camera.isOpened():
        if is_paused:
            time.sleep(0.1)
            continue
            
        if is_video_mode:
            time.sleep(1/FPS)
            
        success, frame = camera.read()
        if not success:
            if is_video_mode:
                camera.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            break
            
        try:
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
            boxes, speeds, total_count = detector.detect_vehicles(frame)
            
            # Draw counting line
            line_y = int(FRAME_HEIGHT * DETECTION_LINE_POSITION)
            cv2.line(frame, (0, line_y), (FRAME_WIDTH, line_y), (255, 0, 0), 2)
            
            # Draw boxes
            for i, box in enumerate(boxes):
                x, y, w, h = box
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
            if not ret:
                continue
                
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                   
        except Exception as e:
            print(f"Error processing frame: {str(e)}")
            continue

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/video_feed')
def video_feed():
    if not camera or not is_camera_active:
        return Response(status=404)
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_camera')
def start_camera():
    global is_camera_active, camera, is_video_mode
    
    try:
        if not is_camera_active:
            is_video_mode = False
            camera = init_camera()
            if camera is None:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to initialize camera'
                }), 400
                
            is_camera_active = True
            return jsonify({
                'status': 'started',
                'message': 'Camera started successfully'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/stop_camera')
def stop_camera():
    global is_camera_active, camera, is_video_mode, is_paused
    
    try:
        is_camera_active = False
        is_video_mode = False
        is_paused = False
        if camera:
            camera.release()
            camera = None
        return jsonify({
            'status': 'stopped',
            'message': 'Camera/Video stopped successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/upload_video', methods=['POST'])
def upload_video():
    global camera, is_camera_active, is_video_mode, video_path
    
    try:
        if 'video' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No video file uploaded'
            }), 400
            
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No selected file'
            }), 400
            
        upload_folder = 'app/static/uploads'
        os.makedirs(upload_folder, exist_ok=True)
        video_path = os.path.join(upload_folder, 'temp_video.mp4')
        video_file.save(video_path)
        
        if camera:
            camera.release()
        
        is_video_mode = True
        camera = init_camera()
        is_camera_active = True
        
        return jsonify({
            'status': 'success',
            'message': 'Video uploaded and processing started'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/pause_video')
def pause_video():
    global is_paused
    is_paused = request.args.get('paused') == 'true'
    return jsonify({'status': 'success'})

@app.route('/get_stats')
def get_stats():
    try:
        current_count = detector.vehicle_count
        current_speeds = detector.current_speeds
        
        avg_speed = sum(current_speeds) / len(current_speeds) if current_speeds else detector.last_avg_speed
        
        return jsonify({
            'current_count': current_count,
            'average_speed': round(avg_speed, 2),
            'timestamp': time.time(),
            'camera_status': 'active' if is_camera_active and camera else 'inactive'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500