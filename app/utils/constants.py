# Video processing
FPS = 30  # Default video FPS
FRAME_WIDTH = 800
FRAME_HEIGHT = 600
JPEG_QUALITY = 70

# Vehicle detection
MIN_CONTOUR_AREA = 4305.0  # Calibrated value
MIN_ASPECT_RATIO = 0.4   # Width/Height ratio minimum
MAX_ASPECT_RATIO = 2.5   # Width/Height ratio maximum
IOU_THRESHOLD = 0.45

# Background subtractor
BG_HISTORY = 100
BG_THRESHOLD = 40
BG_SHADOW = False

# Speed calculation
METERS_PER_PIXEL = 0.01801144089860997  # Calibrated value
MIN_SPEED_TIME = 0.5     # Minimum time between measurements
MAX_SPEED = 120          # Maximum expected speed in km/h
POSITIONS_HISTORY = 10  # Number of positions to keep for speed calculation
SPEED_HISTORY = 5  # Number of speed readings to average

# Vehicle tracking
TRACKING_MEMORY = 1  # How many seconds to keep tracking a vehicle
DETECTION_LINE_POSITION = 0.5  # Line position (0-1)

# Stats
MAX_STATS_HISTORY = 50  # Maximum number of readings to keep for stats 