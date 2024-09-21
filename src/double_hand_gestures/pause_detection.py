from types import SimpleNamespace
import mediapipe as mp
import pyautogui

from hand_helper.hand_helper import scale_coords, scale

pause_activation_distance = 0.1 * (scale/2)
pause_deactivation_distance = 0.12 * (scale/2)

detecting_pause = False
should_pause = False
mp_hands = mp.solutions.hands

def check_pause_gesture(hand_landmarks, multihandedness):
    global detecting_pause, should_pause

    left_hand, right_hand = None, None

    for idx, hand_landmarks in enumerate(hand_landmarks):
        hand_label = multihandedness[idx].classification[0].label
        if hand_label == 'Left':
            left_hand = hand_landmarks
        else:
            right_hand = hand_landmarks

    if left_hand == None or right_hand == None:
        return False

    l_middle_finger_tip = scale_coords(left_hand.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP])
    r_middle_finger_tip = scale_coords(right_hand.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP])

    middle_fingers_distance = ((l_middle_finger_tip.x - r_middle_finger_tip.x)**2 + (l_middle_finger_tip.y - r_middle_finger_tip.y)**2)**0.5

    if middle_fingers_distance < pause_activation_distance and not detecting_pause:
        detecting_pause = True
        should_pause = not should_pause
        return True
    elif middle_fingers_distance > pause_deactivation_distance and detecting_pause:
        detecting_pause = False
    
    return False

def get_should_pause():
    return should_pause