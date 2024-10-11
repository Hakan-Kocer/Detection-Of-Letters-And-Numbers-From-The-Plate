import cv2
from glob import glob
import os
import pyautogui
import numpy as np

# Constants
MIN_PIXEL_WIDTH = 5
MIN_PIXEL_HEIGHT = 15
MIN_ASPECT_RATIO = 0.25
MAX_ASPECT_RATIO = 1.0
MIN_PIXEL_AREA = 80

# Variables
s = 0
e = 0

# Get all jpg images
image_files = glob("image/*.jpg")

for image_path in image_files:
    img = cv2.imread(image_path)
    height, width = img.shape[:2]
    
    # Find black pixels
    black_pixels = []
    for x in range(height):
        for y in range(width):
            b, g, r = img[x, y]
            if b < 120 and g < 120 and r < 120:
                black_pixels.append((x, y))
    
    # Create a blank image with black pixels turned white
    img_white_bg = np.zeros((height, width), np.uint8)
    for x, y in black_pixels:
        img_white_bg[x, y] = 255

    # Apply morphological opening
    kernel = np.ones((4, 4), np.uint8)
    processed_img = cv2.morphologyEx(img_white_bg, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(processed_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        aspect_ratio = w / h

        if (area > MIN_PIXEL_AREA and w > MIN_PIXEL_WIDTH and h > MIN_PIXEL_HEIGHT 
                and MIN_ASPECT_RATIO < aspect_ratio < MAX_ASPECT_RATIO):
            sub_img = img[y-2:y+h+4, x:x+w]
            cv2.imshow("Image Section", sub_img)
            
            result = pyautogui.prompt(text=f"What is this? {s}", title="Label Image")
            if result is not None:
                label_dir = result.upper()
                os.makedirs(label_dir, exist_ok=True)
                sub_img_resized = cv2.resize(sub_img, (24, 24))
                cv2.imwrite(f"{label_dir}/{s}.jpg", sub_img_resized)
                s += 1
                
                if result.lower() == "exit":
                    e = 1
                    break
            else:
                continue

    os.remove(image_path)
    if e == 1:
        break

