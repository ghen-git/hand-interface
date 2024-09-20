import mediapipe as mp
import pyautogui
from types import SimpleNamespace

from hand_helper.hand_helper import rotation, scale_coords

# gesture parameters
gust_min_speed = 0.6
flick_min_speed = 0.6

# states
prev_wrist = SimpleNamespace(x=0, y=0)
prev_middle_finger = SimpleNamespace(x=0, y=0)
gust_speed = 0
flick_speed = 0
screen_width, screen_height = pyautogui.size()

mp_hands = mp.solutions.hands

def flick(hand_landmarks):
    global gust_speed, prev_wrist, flick_speed, prev_middle_finger
    middle_finger = scale_coords(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP])

    direction_v = SimpleNamespace(x=prev_middle_finger.x - middle_finger.x, y=prev_middle_finger.y - middle_finger.y)
    direction = None

    if abs(direction_v.x) > abs(direction_v.y):
        direction = 'right' if direction_v.x > 0 else 'left'
    else:
        direction = 'up' if direction_v.y > 0 else 'down'

    if direction == 'left' or direction == 'right':
        pyautogui.hotkey('alt', direction)
    elif direction == 'down':
        pyautogui.hotkey('ctrl', 'z')
    else:
        pyautogui.hotkey('shift', 'ctrl', 'z')
        pyautogui.hotkey('ctrl', 'y')

    print("flick: ",flick_speed, direction)

def gust(hand_landmarks):
    global gust_speed, prev_wrist, flick_speed, prev_middle_finger
    wrist = scale_coords(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP])

    direction_v = SimpleNamespace(x=prev_wrist.x - wrist.x, y=prev_wrist.y - wrist.y)
    direction = None

    if abs(direction_v.x) > abs(direction_v.y):
        direction = 'right' if direction_v.x > 0 else 'left'
    else:
        direction = 'up' if direction_v.y > 0 else 'down'

    pyautogui.keyDown('win')
    pyautogui.press(direction)
    pyautogui.keyUp('win')

    print("gust: ",gust_speed, direction)

def gusts(hand_landmarks):
    global gust_speed, prev_wrist
    wrist = scale_coords(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP])

    gust_speed = ((prev_wrist.x - wrist.x)**2 + (prev_wrist.y - wrist.y)**2)**0.5

    if gust_speed > gust_min_speed:
        gust(hand_landmarks)

    prev_wrist = wrist

def flicks(hand_landmarks):
    global flick_speed, prev_middle_finger
    middle_finger = scale_coords(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP])

    flick_speed = ((prev_middle_finger.x - middle_finger.x)**2 + (prev_middle_finger.y - middle_finger.y)**2)**0.5

    if flick_speed > flick_min_speed:
        flick(hand_landmarks)

    prev_middle_finger = middle_finger

def gusts_gestures(hand_landmarks):
    global gust_speed, prev_wrist, flick_speed, prev_middle_finger
    wrist = scale_coords(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST])
    middle_finger = scale_coords(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP])

    gust_speed = ((prev_wrist.x - wrist.x)**2 + (prev_wrist.y - wrist.y)**2)**0.5
    flick_speed = ((prev_middle_finger.x - middle_finger.x)**2 + (prev_middle_finger.y - middle_finger.y)**2)**0.5

    if gust_speed > gust_min_speed:
        gust(hand_landmarks)
    elif flick_speed > flick_min_speed:
        flick(hand_landmarks)

    prev_wrist = wrist
    prev_middle_finger = middle_finger