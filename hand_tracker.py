import cv2
import mediapipe as mp
import time
import socket

# max shared mem length: 1400 chars

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

video_capture = cv2.VideoCapture(0)

# Variables for FPS calculation
prev_time = 0
curr_time = 0

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('localhost', 5050))
    while video_capture.isOpened():
        success, frame = video_capture.read()
        if not success:
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
            mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            s.sendall(repr(hand_landmarks).encode())

        # Calculate FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time

        # Display FPS on the image
        cv2.putText(frame, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.imshow('MediaPipe Hands', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

video_capture.release()
