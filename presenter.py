import cv2
import mediapipe as mp

cap=cv2.VideoCapture(0)
mp_hands=mp.solutions.hands
mp_drawing=mp.solutions.drawing_utils
hands=mp_hands.Hands()

while True:
    ret,frame=cap.read()
    frame=cv2.flip(frame,1)
    processed_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    results=hands.process(processed_frame)
    if results.multi_hand_landmarks:
        for multi_hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame,multi_hand_landmarks,mp_hands.HAND_CONNECTIONS)
    cv2.imshow("Frame",frame)
    if cv2.waitKey(1)==ord('x'):
        break