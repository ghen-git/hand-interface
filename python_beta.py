import cv2
import mediapipe as mp
import pyautogui
import time

# gesture parameters
tab_activation_distance = 0.05
tab_deactivation_distance = 0.06
click_activation_distance = 0.07
click_deactivation_distance = 0.08
scroll_activation_distance = 0.07
scroll_activation_distance_from_thumb = 0.1
scroll_deactivation_distance = 0.08
click_deactivation_frames = 5
tab_deactivation_frames = 5
scroll_deactivation_frames = 10
smoothing_factor = 0.25
precise_smoothing_factor = 0.025
click_delay_frames = 7
click_position_lookbehind = 2

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
click_delay_counter = 0

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
previous_positions_buffer = [(0,0)] * click_position_lookbehind
pp_buffer_index = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
        
    height, width, _ = frame.shape
    new_height = height // 2
    new_width = width // 2
    resized_frame = cv2.resize(frame, (new_width, new_height))

    rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
    rgb_frame.flags.writeable = False
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
        middlefinger_distance = ((thumb_tip.x - middle_finger_tip.x)**2 + (thumb_tip.y - middle_finger_tip.y)**2)**0.5
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

        if not scrolling and click_delay_counter == 0:
            pyautogui.moveTo(smoothed_x, smoothed_y, 0)
            previous_positions_buffer[pp_buffer_index] = (smoothed_x, smoothed_y)
            pp_buffer_index = (pp_buffer_index + 1) % click_position_lookbehind

        if distance < click_activation_distance and not mouse_down and not minimize_window and not double_clicked:
            click_delay_counter += 1
            if click_delay_counter > click_delay_frames:
                pp_buffer_x, pp_buffer_y = previous_positions_buffer[(pp_buffer_index - (click_position_lookbehind - 1)) % click_position_lookbehind]
                pyautogui.moveTo(pp_buffer_x, pp_buffer_y, 0)
                mouse_down = True
                pyautogui.mouseDown()
                click_delay_counter = 0
        elif mouse_down and distance <= click_deactivation_distance and mouse_up_frames > 0:
            mouse_up_frames = 0
        elif  distance > click_deactivation_distance and click_delay_counter > 0:
            pyautogui.click()
            click_delay_counter = 0
        elif  distance > click_deactivation_distance and mouse_down:
            mouse_up_frames += 1
            if mouse_up_frames > click_deactivation_frames:
                pp_buffer_x, pp_buffer_y = previous_positions_buffer[(pp_buffer_index - (click_position_lookbehind - 1)) % click_position_lookbehind]
                pyautogui.moveTo(pp_buffer_x, pp_buffer_y, 0)
                mouse_down = False
                pyautogui.mouseUp()

        # if tab_distance < tab_activation_distance and ring_finger_tip.y > thumb_tip.y and not minimize_window and not mouse_down:
        #     window = gw.getWindowsAt(smoothed_x, smoothed_y)
        #     if window:
        #         window[0].minimize()
        #         minimize_window = True
        # elif tab_distance > tab_deactivation_distance and minimize_window:
        #     minimize_window = False

        if middlefinger_distance < click_activation_distance and not double_clicked and not mouse_down:
            pp_buffer_x, pp_buffer_y = previous_positions_buffer[(pp_buffer_index - (click_position_lookbehind - 1)) % click_position_lookbehind]
            pyautogui.moveTo(pp_buffer_x, pp_buffer_y, 0)
            double_clicked = True
            pyautogui.doubleClick()
        elif middlefinger_distance > click_deactivation_distance and double_clicked:
            double_clicked = False

        # if tab_distance < tab_activation_distance and ring_finger_tip.y <= thumb_tip.y and not alttab_down and not scrolling and not mouse_down:
        #     alttab_down = True
        #     pyautogui.keyDown("alt")
        #     pyautogui.press("tab")
        # elif tab_distance <= tab_deactivation_distance and alttab_down and alttab_up_frames > 0:
        #     alttab_up_frames = 0
        # elif tab_distance > tab_deactivation_distance and alttab_down:
        #     alttab_up_frames += 1
        #     if alttab_up_frames > tab_deactivation_frames:
        #         alttab_down = False
        #         pyautogui.keyUp("alt")

        if scrolling:
            x_difference = index_finger_tip.x - scroll_base_x
            x_difference *= 100
            y_difference = index_finger_tip.y - scroll_base_y
            y_difference *= 100

            pyautogui.keyDown('shift')
            pyautogui.scroll(-int(x_difference))
            pyautogui.keyUp('shift')
            pyautogui.scroll(int(y_difference))

        if scroll_distance < scroll_activation_distance and middlefinger_distance >= scroll_activation_distance_from_thumb and not scrolling and not mouse_down and not alttab_down:
            scroll_base_x = index_finger_tip.x
            scroll_base_y = index_finger_tip.y
            scrolling = True
        elif scrolling and scroll_distance <= scroll_deactivation_distance and not_scrolling_frames > 0:
            not_scrolling_frames = 0
        elif scroll_distance > scroll_deactivation_distance and scrolling:
            not_scrolling_frames += 1
            if not_scrolling_frames > scroll_deactivation_frames:
                scrolling = False

        # p1, p2, p3 = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST], hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP], hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
        # v1, v2 = (p2.x - p1.x, p2.y - p1.y, p2.z - p1.z), (p3.x - p1.x, p3.y - p1.y, p3.z - p1.z)
        # normal = (v1[1]*v2[2] - v1[2]*v2[1], v1[2]*v2[0] - v1[0]*v2[2], v1[0]*v2[1] - v1[1]*v2[0])
        # normal_mag = ((normal[0])**2 + (normal[1])**2+ (normal[2])**2)**0.5
        # normalized_normal = tuple(normal_i/normal_mag for normal_i in normal)

        # print(f"Position: {hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]}\nRotation: {normalized_normal}\033[A\033[A\033[A\033[A\033[A")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
