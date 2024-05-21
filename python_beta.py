import cv2
import mediapipe as mp
import pyautogui
import time
import pygetwindow as gw
import speech_recognition as sr
import os

# gesture confidence parameters
tab_activation_distance = 0.05
tab_deactivation_distance = 0.06
click_activation_distance = 0.06
click_deactivation_distance = 0.07
scroll_activation_distance = 0.04
scroll_deactivation_distance = 0.07
click_deactivation_frames = 2
tab_deactivation_frames = 5
scroll_deactivation_frames = 5
smoothing_factor = 0.25
precise_smoothing_factor = 0.025

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mouse_down = False
alttab_down = False
minimize_window = False
gesture = False
scrolling = False
double_clicked = False
mouse_up_frames = 0
alttab_up_frames = 0
not_scrolling_frames = 0

# OpenCV setup
cap = cv2.VideoCapture(0)
last_update_time = time.time()
screen_width, screen_height = pyautogui.size()
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

# Variables for FPS calculation
prev_time = 0
curr_time = 0

smoothed_x = 0
smoothed_y = 0
scroll_base_x = 0
scroll_base_y = 0

frames_without_hands = 0
window = []


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    height, width, _ = frame.shape
    new_height = height // 2
    new_width = width // 2
    resized_frame = cv2.resize(frame, (new_width, new_height))

    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

    rgb_frame.flags.writeable = False

    # Process the frame with MediaPipe Hands
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        frames_without_hands = 0
        hand_landmarks = results.multi_hand_landmarks[0]

        thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
        index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
        pinky_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

        thumb_tip.x = (thumb_tip.x * 2) - 0.5
        thumb_tip.y = (thumb_tip.y * 2) - 0.5
        index_finger_tip.x = (index_finger_tip.x * 2) - 0.5
        index_finger_tip.y = (index_finger_tip.y * 2) - 0.5
        middle_finger_tip.x = (middle_finger_tip.x * 2) - 0.5
        middle_finger_tip.y = (middle_finger_tip.y * 2) - 0.5
        ring_finger_tip.x = (ring_finger_tip.x * 2) - 0.5
        ring_finger_tip.y = (ring_finger_tip.y * 2) - 0.5
        pinky_finger_tip.x = (pinky_finger_tip.x * 2) - 0.5
        pinky_finger_tip.y = (pinky_finger_tip.y * 2) - 0.5

        distance = ((thumb_tip.x - index_finger_tip.x)**2 + (thumb_tip.y - index_finger_tip.y)**2)**0.5
        click_distance = ((thumb_tip.x - middle_finger_tip.x)**2 + (thumb_tip.y - middle_finger_tip.y)**2)**0.5
        tab_distance = ((thumb_tip.x - ring_finger_tip.x)**2 + (thumb_tip.y - ring_finger_tip.y)**2)**0.5
        scroll_distance = ((index_finger_tip.x - middle_finger_tip.x)**2 + (index_finger_tip.y - middle_finger_tip.y)**2)**0.5
        listen_distance = ((pinky_finger_tip.x - thumb_tip.x)**2 + (pinky_finger_tip.y - thumb_tip.y)**2)**0.5

        target_x = int((1 - (middle_finger_tip.x + thumb_tip.x)/2) * screen_width)
        target_y = int((middle_finger_tip.y + thumb_tip.y)/2 * screen_height)

        if middle_finger_tip.y <= thumb_tip.y:
            smoothed_x = smoothing_factor * target_x + (1 - smoothing_factor) * smoothed_x
            smoothed_y = smoothing_factor * target_y + (1 - smoothing_factor) * smoothed_y
        else:
            smoothed_x = precise_smoothing_factor * target_x + (1 - precise_smoothing_factor) * smoothed_x
            smoothed_y = precise_smoothing_factor * target_y + (1 - precise_smoothing_factor) * smoothed_y

        if not scrolling and not double_clicked:
            pyautogui.moveTo(smoothed_x, smoothed_y, 0)

        if tab_distance < tab_activation_distance and ring_finger_tip.y > thumb_tip.y and not minimize_window and not mouse_down:
            window = gw.getWindowsAt(smoothed_x, smoothed_y)
            if window:
                window[0].minimize()
                minimize_window = True
        elif tab_distance > tab_deactivation_distance and minimize_window:
            minimize_window = False

        if click_distance < click_activation_distance and not double_clicked and not mouse_down:
            double_clicked = True
            pyautogui.doubleClick()
        elif click_distance > click_deactivation_distance and double_clicked:
            double_clicked = False

        if (click_distance < click_activation_distance or distance < click_activation_distance) and not mouse_down and not minimize_window and not double_clicked:
            mouse_down = True
            pyautogui.mouseDown()
        elif mouse_down and (click_distance <= click_deactivation_distance or distance <= click_deactivation_distance) and mouse_up_frames > 0:
            mouse_up_frames = 0
        elif (click_distance > click_deactivation_distance and distance > click_deactivation_distance) and mouse_down:
            mouse_up_frames += 1
            if mouse_up_frames > click_deactivation_frames:
                mouse_down = False
                pyautogui.mouseUp()

        if tab_distance < tab_activation_distance and ring_finger_tip.y <= thumb_tip.y and not alttab_down:
            alttab_down = True
            pyautogui.keyDown("alt")
            pyautogui.press("tab")
        elif tab_distance <= tab_deactivation_distance and alttab_down and alttab_up_frames > 0:
            alttab_up_frames = 0
        elif tab_distance > tab_deactivation_distance and alttab_down:
            alttab_up_frames += 1
            if alttab_up_frames > tab_deactivation_frames:
                alttab_down = False
                pyautogui.keyUp("alt")

        if scrolling:
            x_difference = index_finger_tip.x - scroll_base_x
            x_difference *= 100
            y_difference = index_finger_tip.y - scroll_base_y
            y_difference *= 100

            pyautogui.keyDown('shift')
            pyautogui.scroll(-int(x_difference))
            pyautogui.keyUp('shift')
            pyautogui.scroll(int(y_difference))

        if scroll_distance < scroll_activation_distance and not scrolling and not mouse_down:
            scroll_base_x = index_finger_tip.x
            scroll_base_y = index_finger_tip.y
            scrolling = True
        elif scrolling and scroll_distance <= scroll_deactivation_distance and not_scrolling_frames > 0:
            not_scrolling_frames = 0
        elif scroll_distance > scroll_deactivation_distance and scrolling:
            not_scrolling_frames += 1
            if not_scrolling_frames > scroll_deactivation_frames:
                scrolling = False

    # Break the loop when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture
cap.release()
