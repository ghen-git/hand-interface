from types import SimpleNamespace
import mediapipe as mp
import pyautogui

from hand_helper.hand_helper import scale_coords, scale
from gusts.gusts import flicks, gusts, gusts_gestures

# gesture parameters
click_activation_distance = 0.07 * (scale/2)
click_deactivation_distance = 0.075 * (scale/2)
scroll_activation_distance = 0.07 * (scale/2)
scroll_activation_distance_from_thumb = 0.1 * (scale/2)
scroll_deactivation_distance = 0.08 * (scale/2)
click_deactivation_frames = 4
scroll_deactivation_frames = 10
smoothing_factor = 0.9 * (1/(scale/2))
precise_smoothing_factor = 0.0125 * (1/(scale/2))
min_cursor_speed = 1
max_cursor_speed = 100
click_delay_frames = 5
click_position_lookbehind = 5
cursor_distance_lookbehind = 5
precise_scale = 1.5

# states
mouse_down = False
mouse_down_right = False
alttab_down = False
minimize_window = False
scrolling = False
double_clicked = False
toggled_gusts = False
gusts_mode = 0
mouse_up_frames = 0
not_scrolling_frames = 0
click_delay_counter = 0
rclick_delay_counter = 0
smoothed_x = 0
smoothed_y = 0
scroll_base_x = 0
scroll_base_y = 0
previous_positions_buffer = [(0,0)] * click_position_lookbehind
cursor_distance_buffer = [0] * cursor_distance_lookbehind
pp_buffer_index = 0
cd_buffer_index = 0
prev_position = (0,0)
disable_scroll = False
screen_width, screen_height = pyautogui.size()

mp_hands = mp.solutions.hands

def easingFunction(x):
    # return x * x # (ease in quad)
    return x

def mouse_gestures(hand_landmarks):
    global mouse_down, alttab_down, minimize_window, scrolling, double_clicked, mouse_up_frames
    global not_scrolling_frames, click_delay_counter, smoothed_x, smoothed_y, scroll_base_x, scroll_base_y, previous_positions_buffer
    global pp_buffer_index, screen_width, screen_height, disable_scroll, mouse_down_right, rclick_delay_counter
    global toggled_gusts, gusts_mode
    global cd_buffer_index, cursor_distance_buffer, prev_position

    thumb_tip = scale_coords(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP])
    index_finger_tip = scale_coords(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP])
    middle_finger_tip = scale_coords(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP])
    ring_finger_tip = scale_coords(hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP])
    pinky_tip = scale_coords(hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP])
    wrist = scale_coords(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST])

    pointer_distance = ((thumb_tip.x - index_finger_tip.x)**2 + (thumb_tip.y - index_finger_tip.y)**2)**0.5
    middle_distance = ((thumb_tip.x - middle_finger_tip.x)**2 + (thumb_tip.y - middle_finger_tip.y)**2)**0.5
    ring_distance = ((thumb_tip.x - ring_finger_tip.x)**2 + (thumb_tip.y - ring_finger_tip.y)**2)**0.5
    pinky_distance = ((thumb_tip.x - pinky_tip.x)**2 + (thumb_tip.y - pinky_tip.y)**2)**0.5
    pointermid_distance = ((index_finger_tip.x - middle_finger_tip.x)**2 + (index_finger_tip.y - middle_finger_tip.y)**2)**0.5

    target_x = int((1 - (middle_finger_tip.x + thumb_tip.x)/2) * screen_width)
    target_y = int((middle_finger_tip.y + thumb_tip.y)/2 * screen_height)

    if pinky_distance < click_activation_distance and not toggled_gusts and not mouse_down:
        toggled_gusts = True
        gusts_mode = (gusts_mode + 1) % 3
        print("gusts: ", gusts_mode)
    elif pinky_distance > click_deactivation_distance and toggled_gusts:
        toggled_gusts = False
    
    if gusts_mode > 0:
        if gusts_mode == 1:
            gusts(hand_landmarks)
        else:
            flicks(hand_landmarks)
        return

    # mean_cursor_distance = min(max(sum(cursor_distance_buffer) / cursor_distance_lookbehind, min_cursor_speed), max_cursor_speed)
    prev_x, prev_y = prev_position
    mean_cursor_distance = min(max(((prev_x - target_x)**2 + (prev_y - target_y)**2)**0.5, min_cursor_speed), max_cursor_speed)
    calculated_smoothing_factor = (easingFunction((mean_cursor_distance - min_cursor_speed) / (max_cursor_speed - min_cursor_speed)) * (smoothing_factor - precise_smoothing_factor)) + precise_smoothing_factor

    print(mean_cursor_distance, calculated_smoothing_factor)
    smoothed_x = calculated_smoothing_factor * target_x + (1 - calculated_smoothing_factor) * smoothed_x
    smoothed_y = calculated_smoothing_factor * target_y + (1 - calculated_smoothing_factor) * smoothed_y

    # if middle_finger_tip.y <= thumb_tip.y:
    #     smoothed_x = calculated_smoothing_factor * target_x + (1 - calculated_smoothing_factor) * smoothed_x
    #     smoothed_y = calculated_smoothing_factor * target_y + (1 - calculated_smoothing_factor) * smoothed_y
    # else:
    #     smoothed_x = precise_smoothing_factor * target_x + (1 - precise_smoothing_factor) * smoothed_x
    #     smoothed_y = precise_smoothing_factor * target_y + (1 - precise_smoothing_factor) * smoothed_y

    if not scrolling and click_delay_counter == 0:
        pyautogui.moveTo(smoothed_x, smoothed_y, 0)
        previous_positions_buffer[pp_buffer_index] = (smoothed_x, smoothed_y)
        pp_buffer_index = (pp_buffer_index + 1) % click_position_lookbehind
        prev_x, prev_y = prev_position
        # cursor_distance_buffer[cd_buffer_index] = ((prev_x - smoothed_x)**2 + (prev_y - smoothed_y)**2)**0.5
        # cd_buffer_index = (cd_buffer_index + 1) % cursor_distance_lookbehind
        prev_position = (target_x, target_y)

    if pointer_distance < click_activation_distance and not mouse_down and not minimize_window and not double_clicked:
        click_delay_counter += 1
        if click_delay_counter > click_delay_frames:
            pp_buffer_x, pp_buffer_y = previous_positions_buffer[(pp_buffer_index - (click_position_lookbehind - 1)) % click_position_lookbehind]
            pyautogui.moveTo(pp_buffer_x, pp_buffer_y, 0.05)
            mouse_down = True
            pyautogui.mouseDown()
            click_delay_counter = 0
    elif mouse_down and pointer_distance <= click_deactivation_distance and mouse_up_frames > 0:
        mouse_up_frames = 0
    elif  pointer_distance > click_deactivation_distance and click_delay_counter > 0:
        pyautogui.click()
        click_delay_counter = 0
    elif  pointer_distance > click_deactivation_distance and mouse_down:
        mouse_up_frames += 1
        if mouse_up_frames > click_deactivation_frames:
            pp_buffer_x, pp_buffer_y = previous_positions_buffer[(pp_buffer_index - (click_deactivation_frames - 1)) % click_position_lookbehind]
            pyautogui.moveTo(pp_buffer_x, pp_buffer_y, 0)
            mouse_down = False
            pyautogui.mouseUp()

    if ring_distance < click_activation_distance and not mouse_down_right and not minimize_window and not double_clicked:
        rclick_delay_counter += 1
        if rclick_delay_counter > click_delay_frames:
            pp_buffer_x, pp_buffer_y = previous_positions_buffer[(pp_buffer_index - (click_position_lookbehind - 1)) % click_position_lookbehind]
            pyautogui.moveTo(pp_buffer_x, pp_buffer_y, 0.05)
            mouse_down_right = True
            pyautogui.mouseDown(button="right")
            rclick_delay_counter = 0
    elif mouse_down_right and ring_distance <= click_deactivation_distance and mouse_up_frames > 0:
        mouse_up_frames = 0
    elif  ring_distance > click_deactivation_distance and rclick_delay_counter > 0:
        pyautogui.rightClick()
        rclick_delay_counter = 0
    elif  ring_distance > click_deactivation_distance and mouse_down_right:
        mouse_up_frames += 1
        if mouse_up_frames > click_deactivation_frames:
            pp_buffer_x, pp_buffer_y = previous_positions_buffer[(pp_buffer_index - (click_position_lookbehind - 1)) % click_position_lookbehind]
            pyautogui.moveTo(pp_buffer_x, pp_buffer_y, 0)
            mouse_down_right = False
            pyautogui.mouseDown(button="right")

    if middle_distance < click_activation_distance and not double_clicked and not mouse_down:
        pp_buffer_x, pp_buffer_y = previous_positions_buffer[(pp_buffer_index - (click_position_lookbehind - 1)) % click_position_lookbehind]
        pyautogui.moveTo(pp_buffer_x, pp_buffer_y, 0)
        double_clicked = True
        pyautogui.doubleClick()
    elif middle_distance > click_deactivation_distance and double_clicked:
        double_clicked = False

    if scrolling:
        x_difference = index_finger_tip.x - scroll_base_x
        x_difference *= 100
        y_difference = index_finger_tip.y - scroll_base_y
        y_difference *= 100

        pyautogui.keyDown('shift')
        pyautogui.scroll(-int(x_difference))
        pyautogui.keyUp('shift')
        pyautogui.scroll(int(y_difference))

    if pointermid_distance < scroll_activation_distance and middle_distance >= scroll_activation_distance_from_thumb and not scrolling and not mouse_down and not alttab_down and not disable_scroll:
        scroll_base_x = index_finger_tip.x
        scroll_base_y = index_finger_tip.y
        scrolling = True
    elif scrolling and pointermid_distance <= scroll_deactivation_distance and not_scrolling_frames > 0:
        not_scrolling_frames = 0
    elif pointermid_distance > scroll_deactivation_distance and scrolling:
        not_scrolling_frames += 1
        if not_scrolling_frames > scroll_deactivation_frames:
            scrolling = False