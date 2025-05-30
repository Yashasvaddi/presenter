from screeninfo import get_monitors
import cv2
import mediapipe as mp
import math
import os
import time
from collections import deque

# Configuration
number_of_images = 3
drawing_lifetime = 4  # seconds before drawings disappear

monitor = get_monitors()[0]
screen_width, screen_height = monitor.width, monitor.height

# Global variables
i = 1
Disp = None
flag = True
option_flag = False

# Drawing points with timestamps
bpoints = [deque(maxlen=512)]
bpoints_timestamps = [deque(maxlen=512)]
blue_index = 0
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]

# Screen and UI settings
screen_width, screen_height = 1920, 1080  # Default values
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands()

# Button coordinates
(butx1, buty1) = (550, 50)
(butx2, buty2) = (600, 100)
(windoww, windowh) = (screen_width // 2, screen_height)

def remove_old_drawings():
    """Remove drawing points older than drawing_lifetime seconds"""
    current_time = time.time()
    global bpoints, bpoints_timestamps, blue_index
    
    for stroke_idx in range(len(bpoints)):
        if stroke_idx < len(bpoints_timestamps):
            # Remove old points from this stroke
            while (bpoints_timestamps[stroke_idx] and 
                   current_time - bpoints_timestamps[stroke_idx][-1] > drawing_lifetime):
                bpoints_timestamps[stroke_idx].pop()
                if bpoints[stroke_idx]:
                    bpoints[stroke_idx].pop()

def create_placeholder_image(slide_num):
    """Create a placeholder image for demonstration"""
    placeholder = cv2.zeros((600, 800, 3), dtype=cv2.uint8)
    cv2.rectangle(placeholder, (0, 0), (800, 600), (50, 50, 50), -1)
    cv2.putText(placeholder, f"Slide {slide_num}", 
               (250, 300), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    cv2.putText(placeholder, "Use hand gestures to navigate", 
               (150, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)
    return placeholder

print("Hand Gesture Presenter")
print("Point at the button to start presentation mode")
print("Press 'x' to exit")

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(processed_frame)
    h, w, _ = frame.shape
    
    if results.multi_hand_landmarks:
        landmarks = []
        for multi_hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, multi_hand_landmarks, mp_hands.HAND_CONNECTIONS)
            cv2.rectangle(frame, (butx1, buty1), (butx2, buty2), (0, 0, 0), -1)
            cv2.circle(frame, (int((butx1 + butx2) / 2), int((buty1 + buty2) / 2)), 15, (255, 255, 255), 1)
            cv2.line(frame, (int((butx1 + butx2) / 2), int((buty1 + buty2) / 2) - 5), 
                    (int((butx1 + butx2) / 2), int((buty1 + buty2) / 2) - 20), (255, 255, 255), 1)
            
            index_tip = multi_hand_landmarks.landmark[8]
            index_x = int(index_tip.x * w)
            index_y = int(index_tip.y * h)
            
            if butx1 < index_x < butx2 and buty1 < index_y < buty2:
                cv2.destroyWindow("Frame")
                print("Entering presentation mode...")
                print("Gestures:")
                print("- Pinch on right side: Next slide")
                print("- Pinch on left side: Previous slide")
                print("- Point with index finger: Draw (disappears after 4 seconds)")
                print("- Press 'm' for option mode")
                print("- Press 'q' to quit")
                
                while True:
                    # Try to load image, create placeholder if not found
                    add = f"presenter\\pics\\img{i}.jpg"
                    if os.path.exists(add):
                        Disp = cv2.imread(add)
                    else:
                        Disp = create_placeholder_image(i)
                    
                    temp, window = cap.read()
                    window = cv2.flip(window, 1)
                    proc_window = cv2.cvtColor(window, cv2.COLOR_BGR2RGB)
                    results = hands.process(proc_window)
                    
                    # Get actual dimensions
                    disp_h, disp_w = Disp.shape[:2]
                    window_h, window_w = window.shape[:2]
                    
                    # Remove old drawings
                    remove_old_drawings()
                    
                    if results.multi_hand_landmarks:
                        for multi_hand_landmarks in results.multi_hand_landmarks:
                            for lm in multi_hand_landmarks.landmark:
                                lmx = int(lm.x * window_w)
                                lmy = int(lm.y * window_h)
                                landmarks.append([lmx, lmy])
                            
                            thumb = multi_hand_landmarks.landmark[4]
                            thumb_x = int(thumb.x * window_w)
                            thumb_y = int(thumb.y * window_h)
                            index_tip = multi_hand_landmarks.landmark[8]
                            index_x = int(index_tip.x * window_w)
                            index_y = int(index_tip.y * window_h)
                            # FIXED: Direct mapping of index finger to display coordinates
                            # Use the normalized coordinates directly for accurate mapping
                            draw_x = int(index_tip.x * disp_w)
                            draw_y = int(index_tip.y * disp_h)
                            cv2.circle(Disp,(draw_x,draw_y),13,(255,255,255),-1)
                            cv2.circle(Disp,(draw_x,draw_y),10,(0,0,0),-1)
                            
                            # Check if thumb and index are far apart (drawing mode)
                            dist_thumb_index = math.sqrt((thumb_x - index_x)**2 + (thumb_y - index_y)**2)
                            
                            if dist_thumb_index < 30:  # Close together - new stroke
                                bpoints.append(deque(maxlen=512))
                                bpoints_timestamps.append(deque(maxlen=512))
                                blue_index += 1
                            else:  # Far apart - drawing mode
                                # Add drawing point with timestamp
                                current_time = time.time()
                                bpoints[blue_index].appendleft((draw_x, draw_y))
                                bpoints_timestamps[blue_index].appendleft(current_time)
                            
                            # Draw all current strokes
                            # for stroke_idx in range(len(bpoints)):
                            #     if len(bpoints[stroke_idx]) >= 1:
                            #         stroke_points = list(bpoints[stroke_idx])
                            #         for k in range(1, len(stroke_points)):
                            #             if stroke_points[k - 1] and stroke_points[k]:
                            #                 cv2.line(Disp, stroke_points[k - 1], stroke_points[k], (0, 0, 255), 3)
                    if cv2.waitKey(1) == ord('m') or option_flag:
                        if os.path.exists(add):
                            Disp = cv2.imread(add)
                        else:
                            Disp = create_placeholder_image(i)
                        
                        if results.multi_hand_landmarks:
                            for multi_hand_landmarks in results.multi_hand_landmarks:
                                thumb = multi_hand_landmarks.landmark[4]
                                thumb_x = int(thumb.x * window_w)
                                thumb_y = int(thumb.y * window_h)
                                index_tip = multi_hand_landmarks.landmark[8]
                                index_x = int(index_tip.x * window_w)
                                index_y = int(index_tip.y * window_h)
                                draw_x = int(index_tip.x * disp_w)
                                draw_y = int(index_tip.y * disp_h)
                                cv2.circle(Disp,(draw_x,draw_y),13,(255,255,255),-1)
                                cv2.circle(Disp,(draw_x,draw_y),10,(0,0,0),-1)
                                dist = math.sqrt((index_x - thumb_x)**2 + (index_y - thumb_y)**2)
                                if dist < 30:
                                    if index_x >= 550:
                                        if flag:
                                            if i >= number_of_images:
                                                i = 1
                                            else:
                                                i = i + 1
                                            flag = False
                                    if index_x <= 150:
                                        if flag:
                                            if i <= 1:
                                                i = number_of_images
                                            else:
                                                i = i - 1
                                            flag = False
                                    cv2.line(window, (thumb_x, thumb_y), (index_x, index_y), (0, 0, 255), 1)
                                else:
                                    flag = True
                                    cv2.line(window, (thumb_x, thumb_y), (index_x, index_y), (255, 0, 0), 1)
                        
                        cv2.namedWindow("Window", cv2.WINDOW_NORMAL)
                        cv2.imshow("Window", window)
                        cv2.resizeWindow("Window", windoww // 3, windowh // 3)
                        cv2.moveWindow("Window", 0, 0)
                        cv2.namedWindow("Disp", cv2.WINDOW_NORMAL)
                        cv2.imshow("Disp", Disp)
                        cv2.resizeWindow("Disp", screen_width, screen_height)
                        cv2.moveWindow("Disp", 0, 0)
                        option_flag = True
                        if cv2.waitKey(1) == ord('n'):
                            option_flag = False
                    else:
                        if results.multi_hand_landmarks:
                            for multi_hand_landmarks in results.multi_hand_landmarks:
                                thumb = multi_hand_landmarks.landmark[4]
                                thumb_x = int(thumb.x * window_w)
                                thumb_y = int(thumb.y * window_h)
                                index_tip = multi_hand_landmarks.landmark[8]
                                index_x = int(index_tip.x * window_w)
                                index_y = int(index_tip.y * window_h)
                                draw_x = int(index_tip.x * disp_w)
                                draw_y = int(index_tip.y * disp_h)
                                cv2.circle(Disp,(draw_x,draw_y),13,(255,255,255),-1)
                                cv2.circle(Disp,(draw_x,draw_y),10,(0,0,0),-1)
                                dist = math.sqrt((index_x - thumb_x)**2 + (index_y - thumb_y)**2)
                                if dist < 30:
                                    if index_x >= 550:
                                        if flag:
                                            if i >= number_of_images:
                                                i = 1
                                            else:
                                                i = i + 1
                                            flag = False
                                    if index_x <= 150:
                                        if flag:
                                            if i <= 1:
                                                i = number_of_images
                                            else:
                                                i = i - 1
                                            flag = False
                                    cv2.line(window, (thumb_x, thumb_y), (index_x, index_y), (0, 0, 255), 1)
                                else:
                                    flag = True
                                    cv2.line(window, (thumb_x, thumb_y), (index_x, index_y), (255, 0, 0), 1)
                        
                        if os.path.exists(add):
                            Disp = cv2.imread(add)
                        else:
                            Disp = create_placeholder_image(i)
                        
                        # Redraw all current strokes on the display
                        # for stroke_idx in range(len(bpoints)):
                        #     if len(bpoints[stroke_idx]) >= 1:
                        #         stroke_points = list(bpoints[stroke_idx])
                        #         for k in range(1, len(stroke_points)):
                        #             if stroke_points[k - 1] and stroke_points[k]:
                        #                 cv2.line(Disp, stroke_points[k - 1], stroke_points[k], (0, 0, 255), 3)
                        cv2.namedWindow("Window", cv2.WINDOW_NORMAL)
                        cv2.imshow("Window", window)
                        cv2.resizeWindow("Window", windoww, windowh)
                        cv2.moveWindow("Window", 0, 0)
                        cv2.namedWindow("Disp", cv2.WINDOW_NORMAL)
                        cv2.imshow("Disp", Disp)
                        cv2.resizeWindow("Disp", windoww, windowh)
                        cv2.moveWindow("Disp", windoww, 0)
                    
                    if cv2.waitKey(1) == ord('q'):
                        break
    
    cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) == ord('x'):
        break

cap.release()
cv2.destroyAllWindows()
print("Hand Gesture Presenter closed.")