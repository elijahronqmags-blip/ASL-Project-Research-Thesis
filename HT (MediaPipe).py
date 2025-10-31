import cv2
import mediapipe as mp
import numpy as np
import json
import tkinter as tk
from tkinter import ttk
from textblob import TextBlob
import threading
import time
import queue
from PIL import Image, ImageTk

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Load gesture definitions from JSON (if you want to keep gesture matching)
with open('gestures.json', 'r') as f:
    gestures = json.load(f)  # e.g., {"hello": [x1, y1, z1, ...], ...}

# Mapping from recognized speech to sign videos
speech_to_sign_video_map = {
    "hello": "videos/hello.mp4",
    "goodbye": "videos/goodbye.mp4",
    "thank you": "videos/thank_you.mp4"
    # Add more mappings as needed
}

class SignToTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sign-to-Text Translator (150 Signs)")
        self.root.geometry("600x600")
        
        # Queue for thread-safe GUI updates
        self.gui_queue = queue.Queue()

        # GUI Elements
        self.control_frame = ttk.Frame(root)
        self.control_frame.pack(pady=10)

        self.start_btn = ttk.Button(self.control_frame, text="Start Sign Input", command=self.start_sign_input)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(self.control_frame, text="Stop Sign Input", command=self.stop_sign_input, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.text_display = tk.Text(root, height=10, width=60)
        self.text_display.pack(pady=10)

        # Video display label
        self.video_label = ttk.Label(root)
        self.video_label.pack()

        # Threading and state
        self.sign_thread = None
        self.running = False
        self.last_match_time = 0

        # Start processing GUI queue
        self.root.after(100, self.process_gui_queue)

    def process_gui_queue(self):
        while not self.gui_queue.empty():
            msg = self.gui_queue.get()
            if msg['type'] == 'update_text':
                self.text_display.insert(tk.END, msg['text'])
                self.text_display.see(tk.END)
            elif msg['type'] == 'video_frame':
                imgtk = msg['image']
                self.video_label.config(image=imgtk)
                self.video_label.image = imgtk  # Keep reference
        self.root.after(100, self.process_gui_queue)

    def start_sign_input(self):
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.sign_thread = threading.Thread(target=self.sign_input_loop, daemon=True)
        self.sign_thread.start()

    def stop_sign_input(self):
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def sign_input_loop(self):
        cap = None
        try:
            cap = cv2.VideoCapture(0)
            while self.running and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)
                display_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(display_frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                        landmarks = []
                        for lm in hand_landmarks.landmark:
                            landmarks.extend([lm.x, lm.y, lm.z])
                        current_time = time.time()
                        if current_time - self.last_match_time > 1.0:
                            # You can enable gesture matching here if needed
                            # matched_gesture = self.match_gesture(np.array(landmarks))
                            # if matched_gesture and matched_gesture != "Unknown Gesture":
                            #     corrected = str(TextBlob(matched_gesture).correct())
                            #     self.gui_queue.put({'type': 'update_text', 'text': f"Recognized: {corrected}\n"})
                            #     self.last_match_time = current_time
                            pass

                # Convert frame for Tkinter display
                im = Image.fromarray(cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB))
                imgtk = ImageTk.PhotoImage(image=im)
                self.gui_queue.put({'type': 'video_frame', 'image': imgtk})

                time.sleep(0.03)  # ~30 fps
        except Exception as e:
            print(f"Error in sign_input_loop: {e}")
        finally:
            if cap:
                cap.release()

    def handle_recognized_speech(self, recognized_text):
        # Call this method with the recognized speech text
        text = recognized_text.lower().strip()
        if text in speech_to_sign_video_map:
            video_path = speech_to_sign_video_map[text]
            threading.Thread(target=self.play_sign_video, args=(video_path,), daemon=True).start()
        else:
            self.gui_queue.put({'type': 'update_text', 'text': f"No sign video for: {text}\n"})

    def play_sign_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            im = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=im)
            self.gui_queue.put({'type': 'video_frame', 'image': imgtk})
            time.sleep(0.03)
        cap.release()

    # Optional: gesture matching method (disabled here)
    # def match_gesture(self, detected_landmarks):
    #     min_distance = float('inf')
    #     best_match = None
    #     for gesture, ref_landmarks in gestures.items():
    #         ref_array = np.array(ref_landmarks)
    #         if len(ref_array) == len(detected_landmarks):
    #             distance = np.linalg.norm(detected_landmarks - ref_array)
    #             if distance < min_distance:
    #                 min_distance = distance
    #                 best_match = gesture
    #     if min_distance < 0.5:
    #         return best_match
    #     return "Unknown Gesture"

if __name__ == "__main__":
    root = tk.Tk()
    app = SignToTextApp(root)
    root.mainloop()