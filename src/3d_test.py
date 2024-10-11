import cv2
import mediapipe as mp

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

with mp_holistic.Holistic(min_detection_confidence=0.8, min_tracking_confidence=0.2) as holistic:
    while cap.isOpened():
        ret, frame = cap.read()

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        results = holistic.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.left_hand_landmarks:
            mp_drawing.draw_landmarks(
                image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        if results.right_hand_landmarks:
            mp_drawing.draw_landmarks(
                image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

        cv2.imshow('Hand Detection with MediaPipe Holistic', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
