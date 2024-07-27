from flask import Flask, render_template, Response, request, redirect
from camera import Camera
from video_processing import estimate_vehicle_speed

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_video', methods=['POST'])
def process_video():
    if 'video' not in request.files:
        return "No video file found.", 400

    video = request.files['video']
    if video.filename == '':
        return "No selected video file.", 400

    video_path = "uploads/" + video.filename
    video.save(video_path)

    speed_text = estimate_vehicle_speed(video_path)

    return redirect("/")

@app.route('/video_feed')
def video_feed():
    return Response(Camera().generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_camera', methods=['POST'])
def start_camera():
    Camera().start_camera()
    return 'Camera started'

@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    Camera().stop_camera()
    return 'Camera stopped'

if __name__ == '__main__':
    app.run(debug=True)
