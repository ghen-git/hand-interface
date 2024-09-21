import cv2
import mediapipe as mp
import pyautogui
import threading
import win32gui
import win32con
from mouse.mouse import mouse_gestures
from mouse.mouse import disable_scroll
from gusts.gusts import gusts_gestures
from double_hand_gestures.pause_detection import check_pause_gesture, get_should_pause

hwnd = win32gui.GetForegroundWindow()
win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

mode = "none"
mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.75, min_tracking_confidence=0.75)

def find_hands(frame):
    height, width, _ = frame.shape
    new_height = height // 2
    new_width = width // 2
    resized_frame = cv2.resize(frame, (new_width, new_height))

    rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
    rgb_frame.flags.writeable = False
    return hands_detector.process(rgb_frame)

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

def main():
    global mode
    cap = cv2.VideoCapture(0)
    pyautogui.PAUSE = 0
    pyautogui.FAILSAFE = False

    stop_event = threading.Event()
    change_mode_thread = threading.Thread(target=change_mode, args=(stop_event,))
    change_mode_thread.start()

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        results = find_hands(frame)
        if results.multi_hand_landmarks:
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

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    stop_event.set()
    change_mode_thread.join()

if __name__ == "__main__":
    main()