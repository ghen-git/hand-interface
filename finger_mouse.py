import cv2
import mediapipe as mp
import pyautogui
import time
import pygetwindow as gw
import speech_recognition as sr

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
move_window = False
mouse_down = False
alttab_down = False
minimize_window = False
gesture = False
scrolling = False
double_clicked = False

# OpenCV setup
cap = cv2.VideoCapture(0)
last_update_time = time.time()
screen_width, screen_height = pyautogui.size()
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

alpha = 0.05  # Smoothing factor (adjust as needed)
smoothed_x = 0
smoothed_y = 0
mouse_window_offset_x = 0
mouse_window_offset_y = 0
scroll_base_y = 0

frames_without_hands = 0
window = []

def speech_to_text():
    recognizer = sr.Recognizer()
     


    with sr.Microphone() as source:
        audio = recognizer.listen(source, timeout=5)

        try:
            text = recognizer.recognize_google(audio)
            if text == "remove":
                pyautogui.typewrite("")
            if text == "space":
                pyautogui.typewrite(" ")
            if text == "dash":
                pyautogui.typewrite("-")
            else:
                pyautogui.typewrite(text.replace("enter", "\n").replace("colon", ":").replace("Dash", "- ").replace("newpoint", "\n- ").replace("new point", "\n- ").replace("nupoint", "\n- "))
        except sr.UnknownValueError:
            print("Google Web Speech API could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Web Speech API; {0}".format(e))


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe Hands
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        frames_without_hands = 0
        hand_landmarks = results.multi_hand_landmarks[0]

        if len(results.multi_hand_landmarks) == 2:
            hand_landmarks = results.multi_hand_landmarks[1]

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

        target_x = int((1 - (index_finger_tip.x + thumb_tip.x)/2) * screen_width)
        target_y = int((index_finger_tip.y + thumb_tip.y)/2 * screen_height)

        smoothed_x = alpha * target_x + (1 - alpha) * smoothed_x
        smoothed_y = alpha * target_y + (1 - alpha) * smoothed_y

        if move_window:
            if window[0].isMaximized:
                pyautogui.moveTo(int(smoothed_x) - mouse_window_offset_x, int(smoothed_y) - mouse_window_offset_y + 4, 0)
            elif "Visual Studio Code" in window[0].title:
                pyautogui.moveTo(int(smoothed_x) - mouse_window_offset_x - (window[0].width / 2) + 12, int(smoothed_y) - mouse_window_offset_y + 12, 0)
            else:
                pyautogui.moveTo(int(smoothed_x) - mouse_window_offset_x, int(smoothed_y) - mouse_window_offset_y + 12, 0)
        elif not scrolling and not double_clicked:
            pyautogui.moveTo(smoothed_x, smoothed_y, 0)

        if distance < 0.04 and index_finger_tip.y > thumb_tip.y and not minimize_window and not mouse_down:
            window = gw.getWindowsAt(smoothed_x, smoothed_y)
            if window:
                window[0].minimize()
                minimize_window = True
        elif distance > 0.1 and minimize_window:
            minimize_window = False

        # if distance < 0.04 and not move_window and not minimize_window and not mouse_down:
        #     window = gw.getWindowsAt(smoothed_x, smoothed_y)
        #     if window:
        #         mouse_window_offset_x = int(smoothed_x) - max(window[0].left + window[0].width / 2, 0)
        #         mouse_window_offset_y = int(smoothed_y) - max(window[0].top, 0)
        #         if not window[0].title == "Program Manager":
        #             move_window = True
        #             if window[0].isMaximized:
        #                 pyautogui.moveTo(int(smoothed_x) - mouse_window_offset_x, int(smoothed_y) - mouse_window_offset_y + 4, 0)
        #             elif "Visual Studio Code" in window[0].title:
        #                 pyautogui.moveTo(int(smoothed_x) - mouse_window_offset_x - (window[0].width / 2) + 12, int(smoothed_y) - mouse_window_offset_y + 12, 0)
        #             else:
        #                 pyautogui.moveTo(int(smoothed_x) - mouse_window_offset_x, int(smoothed_y) - mouse_window_offset_y + 12, 0)

        #             window[0].activate()
        #         pyautogui.mouseDown()
        # elif distance > 0.1 and move_window:
        #     move_window = False
        #     pyautogui.mouseUp()

        if click_distance < 0.04 and middle_finger_tip.y > thumb_tip.y and not double_clicked and not mouse_down:
            double_clicked = True
            pyautogui.doubleClick()
        elif click_distance > 0.1 and double_clicked:
            double_clicked = False

        if (click_distance < 0.04 or distance < 0.04) and not mouse_down and not move_window and not minimize_window and not double_clicked:
            mouse_down = True
            pyautogui.mouseDown()
        elif (click_distance > 0.1 and distance > 0.1) and mouse_down:
            mouse_down = False
            pyautogui.mouseUp()

        if tab_distance < 0.04 and not alttab_down and not move_window:
            alttab_down = True
            pyautogui.keyDown("alt")
            pyautogui.press("tab")
        elif tab_distance > 0.1 and alttab_down:
            alttab_down = False
            pyautogui.keyUp("alt")

        if scrolling:
            y_difference = index_finger_tip.y - scroll_base_y
            y_difference *= 100
            pyautogui.scroll(int(y_difference))

        if scroll_distance < 0.06 and not scrolling:
            scroll_base_y = index_finger_tip.y
            scrolling = True
        elif scroll_distance > 0.08 and scrolling:
            scrolling = False

        if listen_distance < 0.04:
            print("here")
            speech_to_text()
    
    # Break the loop when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture
cap.release()
