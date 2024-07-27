import cv2
import numpy as np
import math
import time

def get_centroid(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx, cy

def process_frame(frame1, frame2, line_height=None):
    d = cv2.absdiff(frame1, frame2)
    grey = cv2.cvtColor(d, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(grey, (5, 5), 0)
    _, th = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(th, np.ones((3, 3)))
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    return contours, d
