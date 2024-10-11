import multiprocessing.reduction
import cv2
import threading
import queue
import mediapipe as mp
import joblib
import multiprocessing
import cloudpickle as dill
from io import BytesIO

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

hand_data_queues = None
frame_queues = None
frame_number = multiprocessing.Value("i", 0)
n_of_queues = 0

class HandDataFrame:
    def __init__(self, data, frame):
        self.data = data
        self.frame = frame

def start_processing_thread(pool_size):
    global hand_data_queues, frame_queues, n_of_queues
    processes = []
    hand_data_queues = []
    frame_queues = []
    n_of_queues = pool_size
    
    manager = multiprocessing.Manager()

    for i in range(pool_size):
        frame_queue = manager.Queue()
        hand_data_queue = manager.Queue()
        process = multiprocessing.Process(target=hand_data_processing, args=(i, frame_queue, hand_data_queue))
        processes.append(process)
        hand_data_queues.append(hand_data_queue)
        frame_queues.append(frame_queue)

    for process in processes:
        process.start()

        
last_queue_index = -1
def init_frame_queue(frame):
    global last_queue_index

    last_queue_index = (last_queue_index + 1) % n_of_queues
    curr_frame_queue = frame_queues[last_queue_index]
    curr_frame_queue.put(dill.dumps(frame))

def get_first_frame_hands(next_frame):
    global last_queue_index
    curr_hand_data_queue = hand_data_queues[last_queue_index]
    curr_frame_queue = frame_queues[last_queue_index]

    last_queue_index = (last_queue_index + 1) % n_of_queues
    # print("before", last_queue_index)
    hand_data_frame = dill.loads(curr_hand_data_queue.get())
    curr_frame_queue.put(dill.dumps(next_frame))
    return hand_data_frame.data

def hand_data_processing(i, in_queue, out_queue):
    # print("started", i)

    while True:
        frame = dill.loads(in_queue.get())

        # print("captured", i)

        results = find_hands(frame)

        out_queue.put(dill.dumps(HandDataFrame(results, frame)))

