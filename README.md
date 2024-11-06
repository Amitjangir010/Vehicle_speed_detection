# Real-Time Traffic Monitoring System 🚗

A modern web-based traffic monitoring system that detects vehicles, tracks their movement, and provides real-time analytics using computer vision.

## 🌟 Features

- **Real-time Vehicle Detection**: Accurately detects vehicles in video streams
- **Speed Calculation**: Measures vehicle speeds in real-time
- **Traffic Analytics**: 
  - Vehicle counting with line crossing detection
  - Average speed monitoring with rolling average
  - Real-time speed graphs with trend analysis
- **Multiple Input Sources**:
  - Live camera feed
  - Video file processing (supports mp4, avi)
- **Interactive Dashboard**:
  - Clean, modern UI
  - Real-time updates
  - Responsive design
  - Pause/Resume functionality

## 🚀 Quick Start

1. Clone the repository:
```bash
git clone https://github.com/Amitjangir010/Vehicle_speed_detection.git
cd Vehicle_speed_detection
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create required folders:
```bash
mkdir -p app/static/uploads
```

5. Run calibration (important for accurate speed measurement):
```bash
python calibrate_camera.py
```

6. Run the application:
```bash
python run.py
```

7. Open browser and go to:
```
http://localhost:5000
```

## 🛠️ Calibration Guide

For accurate speed measurements, proper calibration is essential:

1. Place a reference object of known length (e.g., 2-meter stick) in camera view
2. Run calibration tool:
```bash
python calibrate_camera.py
```

3. Follow on-screen instructions:
   - Click two points marking known distance
   - Draw rectangle around typical vehicle size
   - Values automatically update in constants.py

4. Tips for better calibration:
   - Use clear reference markers
   - Keep camera stable
   - Ensure good lighting
   - Calibrate during daylight
   - Recalibrate if camera position changes

## 📊 Usage Guide

1. **Live Camera Mode**:
   - Click "Start Camera"
   - System automatically:
     - Detects vehicles
     - Calculates speeds
     - Updates statistics
   - Real-time display shows:
     - Vehicle boxes
     - Counting line
     - Current count
     - Average speed

2. **Video Processing**:
   - Click "Upload Video"
   - Select video file
   - System processes with same features as live mode
   - Supports video pause/resume

3. **Controls & Features**:
   - Start/Stop: Toggle camera/video
   - Pause/Resume: Freeze processing
   - Speed Graph: Shows trends over time
   - Vehicle Counter: Tracks total vehicles
   - Average Speed: Rolling average calculation

## 🔧 Configuration

Key parameters in `constants.py`:
```python
# Video processing
FRAME_WIDTH = 800
FRAME_HEIGHT = 600
FPS = 30

# Vehicle detection
MIN_CONTOUR_AREA = 2000
MIN_ASPECT_RATIO = 0.4
MAX_ASPECT_RATIO = 2.5

# Speed calculation
METERS_PER_PIXEL = 0.05  # Set by calibration
MAX_SPEED = 120
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Night vision support
- Multiple camera support
- Vehicle type classification
- Speed zone alerts
- Data export features

## 🔍 Troubleshooting

Common issues and solutions:
1. Camera not detected: Check device permissions
2. Slow performance: Adjust FRAME_WIDTH/HEIGHT
3. Inaccurate speeds: Recalibrate system
4. Video upload fails: Check file format/size
---
Made with ❤️ for traffic monitoring