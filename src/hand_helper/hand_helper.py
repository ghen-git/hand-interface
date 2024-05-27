import mediapipe as mp
mp_hands = mp.solutions.hands
from types import SimpleNamespace

scale = 2

def rotation(hand_landmarks):
    p1, p2, p3 = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST], hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP], hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
    v1, v2 = (p2.x - p1.x, p2.y - p1.y, p2.z - p1.z), (p3.x - p1.x, p3.y - p1.y, p3.z - p1.z)
    normal = (v1[1]*v2[2] - v1[2]*v2[1], v1[2]*v2[0] - v1[0]*v2[2], v1[0]*v2[1] - v1[1]*v2[0])
    normal_mag = ((normal[0])**2 + (normal[1])**2+ (normal[2])**2)**0.5
    return tuple(normal_i/normal_mag for normal_i in normal)

def scale_coords(base_coords):
    return SimpleNamespace(x=(base_coords.x * scale) - (0.5 * (scale-1)), y=(base_coords.y * scale) - (0.5 * (scale-1)))

def scale_coords_by(base_coords, scale):
    return SimpleNamespace(x=(base_coords.x * scale) - (0.5 * (scale-1)), y=(base_coords.y * scale) - (0.5 * (scale-1)))