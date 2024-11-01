import cv2
import mediapipe as mp
import pyautogui
import threading
import win32gui
import win32con
import time
import numpy as np

from mouse.mouse import mouse_gestures
from mouse.mouse import disable_scroll
from gusts.gusts import gusts_gestures
from double_hand_gestures.pause_detection import check_pause_gesture, get_should_pause
from multithreaded_hand_processing import get_first_frame_hands, start_processing_thread, find_hands, init_frame_queue

hwnd = win32gui.GetForegroundWindow()
win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

mode = "none"

def change_mode(stop):
    global mode, disable_scroll
    while not stop.is_set():
        new_mode = input()
        if new_mode == 'disable scroll':
            disable_scroll = True
        elif new_mode == 'enable scroll':
            disable_scroll = False
        else:
            mode = new_mode
            print(f"Mode changed to: {mode}")

mean_process_time = 0

def main():
    global mode, prev_time, curr_time, mean_process_time
    cap = cv2.VideoCapture(0)
    
    pyautogui.PAUSE = 0
    pyautogui.FAILSAFE = False

    stop_event = threading.Event()
    change_mode_thread = threading.Thread(target=change_mode, args=(stop_event,))
    change_mode_thread.start()

    pool_size = 4
    start_processing_thread(pool_size)

    for i in range(0, pool_size):
        success, frame = cap.read()
        init_frame_queue(frame)

    while mode != "stop":
        success, frame = cap.read()
        before_process_time = time.time()
        results = get_first_frame_hands(frame)
        # results = find_hands(frame)

        if results.multi_hand_landmarks and len(results.multi_hand_landmarks) > 0:
            hand_landmarks = results.multi_hand_landmarks[0]
            hand_count = len(results.multi_hand_landmarks) 

            if hand_count == 2 and check_pause_gesture(results.multi_hand_landmarks, results.multi_handedness):
                if get_should_pause():
                    mode = "pause"
                else:
                    mode = "mouse"

            if mode == "mouse":
                mouse_gestures(hand_landmarks)
            elif mode == "gusts":
                gusts_gestures(hand_landmarks)
            elif mode == "combine":
                mouse_gestures(hand_landmarks)
                gusts_gestures(hand_landmarks)
                
        # Calculate the frame rate (FPS)
        curr_time = time.time()
        process_time = curr_time - before_process_time
        mean_process_time = (mean_process_time + process_time) / 2 

        # print(" " * 50, end="\r")
        # print(mean_process_time, end="\r")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stop_event.set()
    change_mode_thread.join()

if __name__ == "__main__":
    main()