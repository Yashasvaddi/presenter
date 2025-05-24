import cv2
import mediapipe as mp
import screeninfo as sc
from screeninfo import get_monitors
import math as m
import threading as th
import keyboard as kb


number_of_images=3


i=1
Disp=None
flag=True
option_flag=False
monitor = get_monitors()[0]
screen_width, screen_height = monitor.width, monitor.height
cap=cv2.VideoCapture(0)
mp_hands=mp.solutions.hands
mp_drawing=mp.solutions.drawing_utils
hands=mp_hands.Hands()
(butx1,buty1)=(550,50)
(butx2,buty2)=(600,100)
(windoww,windowh)=(screen_width//2,screen_height)
while True:
    ret,frame=cap.read()
    frame=cv2.flip(frame,1)
    processed_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    results=hands.process(processed_frame)
    h,w,_=frame.shape
    if results.multi_hand_landmarks:
        for multi_hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame,multi_hand_landmarks,mp_hands.HAND_CONNECTIONS)
            cv2.rectangle(frame,(butx1,buty1),(butx2,buty2),(0,0,0),-1)
            cv2.circle(frame,(int((butx1+butx2)/2),int((buty1+buty2)/2)),15,(255,255,255),1)
            cv2.line(frame,(int((butx1+butx2)/2),int((buty1+buty2)/2)-5),(int((butx1+butx2)/2),int((buty1+buty2)/2)-20),(255,255,255),1 )
            index_tip=multi_hand_landmarks.landmark[8]
            index_x=int(index_tip.x*w)
            index_y=int(index_tip.y*h)
            if butx1<index_x<butx2 and buty1<index_y<buty2:
                cv2.destroyWindow("Frame")
                while True:
                    add=f"presenter\\pics\\meme{i}.jpg"
                    Disp=cv2.imread(add)
                    temp,window=cap.read()
                    window=cv2.flip(window,1)
                    proc_window=cv2.cvtColor(window,cv2.COLOR_BGR2RGB)
                    results=hands.process(proc_window)
                    #cv2.putText(window,"Hello",(300,300),cv2.FONT_HERSHEY_TRIPLEX,1,(0,0,0),1)
                    if results.multi_hand_landmarks:
                        for multi_hand_landmarks in results.multi_hand_landmarks:
                            thumb=multi_hand_landmarks.landmark[4] 
                            thumb_x=int(thumb.x*w)
                            thumb_y=int(thumb.y*h)
                            index_tip=multi_hand_landmarks.landmark[8]
                            index_x=int(index_tip.x*w)
                            index_y=int(index_tip.y*h)
                            #mp_drawing.draw_landmarks(window,multi_hand_landmarks,mp_hands.HAND_CONNECTIONS)
                    if cv2.waitKey(1)==ord('m') or option_flag:
                        add=f"presenter\\pics\\meme{i}.jpg"
                        Disp=cv2.imread(add)
                        dist=m.sqrt((index_x-thumb_x)**2+(index_y-thumb_y)**2)
                        if dist<30:
                            if index_x>=550:
                                if flag:
                                    if i>=number_of_images:
                                        i=1
                                    else:
                                        i=i+1
                                    flag=False
                            if index_x<=150:
                                if flag:
                                    if i<=1:
                                        i=number_of_images
                                    else:
                                        i=i-1
                                    flag=False
                            cv2.line(window,(thumb_x,thumb_y),(index_x,index_y),(0,0,255),1)
                        else:
                            flag=True
                            cv2.line(window,(thumb_x,thumb_y),(index_x,index_y),(255,0,0),1)
                        cv2.namedWindow("Window",cv2.WINDOW_NORMAL)
                        cv2.imshow("Window",window)
                        cv2.resizeWindow("Window",windoww//3,windowh//3)
                        cv2.moveWindow("Window",0,0)
                        cv2.namedWindow("Disp",cv2.WINDOW_NORMAL)
                        cv2.imshow("Disp",Disp)
                        cv2.resizeWindow("Disp",screen_width,screen_height)
                        cv2.moveWindow("Disp",0,0)
                        option_flag=True
                        if cv2.waitKey(1)==ord('n'):
                            option_flag=False
                    else:
                        dist=m.sqrt((index_x-thumb_x)**2+(index_y-thumb_y)**2)
                        if dist<30:
                            if index_x>=550:
                                if flag:
                                    if i>=number_of_images:
                                        i=1
                                    else:
                                        i=i+1
                                    flag=False
                            if index_x<=150:
                                if flag:
                                    if i<=1:
                                        i=number_of_images
                                    else:
                                        i=i-1
                                    flag=False
                            cv2.line(window,(thumb_x,thumb_y),(index_x,index_y),(0,0,255),1)
                        else:
                            flag=True
                            cv2.line(window,(thumb_x,thumb_y),(index_x,index_y),(255,0,0),1)
                        add=f"presenter\\pics\\meme{i}.jpg"
                        Disp=cv2.imread(add)
                        cv2.namedWindow("Window",cv2.WINDOW_NORMAL)
                        cv2.imshow("Window",window)
                        cv2.resizeWindow("Window",windoww,windowh)
                        cv2.moveWindow("Window",0,0)
                        cv2.namedWindow("Disp",cv2.WINDOW_NORMAL)
                        cv2.imshow("Disp",Disp)
                        cv2.resizeWindow("Disp",windoww,windowh)
                        cv2.moveWindow("Disp",windoww,0)
                        
                    if cv2.waitKey(1)==ord('q'): 
                        break
    cv2.namedWindow("Frame",cv2.WINDOW_NORMAL)
    cv2.imshow("Frame",frame)
    if cv2.waitKey(1)==ord('x'):
        break