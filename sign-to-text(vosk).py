import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import queue
import json
import numpy as np
import cv2
import mediapipe as mp
from vosk import Model, KaldiRecognizer
import pyaudio
from textblob import TextBlob
import pyttsx3
import os

# Initialize mediapipe and models
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

model = Model("models/vosk-model-en-us-0.22")
recognizer = KaldiRecognizer(model, 16000)

voice_queue = queue.Queue()
sign_queue = queue.Queue()

with open('gestures.json', 'r') as f:
    gestures = json.load(f)

with open('videos.json', 'r') as f:
    video_map = json.load(f)

tts_engine = pyttsx3.init()

class SignTranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sign-to-Text Translator")
        self.root.geometry("800x600")

        # GUI Elements
        self.control_frame = ttk.Frame(root)
        self.control_frame.pack(pady=10)

        self.start_voice_btn = ttk.Button(self.control_frame, text="Start Voice Input", command=self.start_voice_input)
        self.start_voice_btn.pack(side=tk.LEFT, padx=5)

        self.stop_voice_btn = ttk.Button(self.control_frame, text="Stop Voice Input", command=self.stop_voice_input, state=tk.DISABLED)
        self.stop_voice_btn.pack(side=tk.LEFT, padx=5)

        self.start_sign_btn = ttk.Button(self.control_frame, text="Start Sign Input", command=self.start_sign_input)
        self.start_sign_btn.pack(side=tk.LEFT, padx=5)

        self.stop_sign_btn = ttk.Button(self.control_frame, text="Stop Sign Input", command=self.stop_sign_input, state=tk.DISABLED)
        self.stop_sign_btn.pack(side=tk.LEFT, padx=5)

        self.translate_btn = ttk.Button(self.control_frame, text="Translate to Sign/Speech", command=self.translate_output)
        self.translate_btn.pack(side=tk.LEFT, padx=5)

        # Display areas
        self.text_display = tk.Text(root, height=10, width=80)
        self.text_display.pack(pady=10)

        self.video_label = ttk.Label(root, text="Sign Video Output")
        self.video_label.pack()
        self.video_canvas = tk.Canvas(root, width=400, height=300, bg="black")
        self.video_canvas.pack()

        # Thread control flags
        self.voice_thread = None
        self.sign_thread = None
        self.voice_running = False
        self.sign_running = False
        self.current_text = ""

        # Store reference for video image to prevent garbage collection
        self.video_img = None

    def start_voice_input(self):
        self.voice_running = True
        self.start_voice_btn.config(state=tk.DISABLED)
        self.stop_voice_btn.config(state=tk.NORMAL)
        self.voice_thread = threading.Thread(target=self.voice_input_loop, daemon=True)
        self.voice_thread.start()

    def stop_voice_input(self):
        self.voice_running = False
        self.start_voice_btn.config(state=tk.NORMAL)
        self.stop_voice_btn.config(state=tk.DISABLED)

    def voice_input_loop(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        stream.start_stream()
        while self.voice_running:
            data = stream.read(4000, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text:
                    corrected = str(TextBlob(text).correct())
                    self.update_text(f"Voice: {corrected}\n")
                    self.current_text = corrected
        stream.stop_stream()
        stream.close()
        p.terminate()

    def start_sign_input(self):
        self.sign_running = True
        self.start_sign_btn.config(state=tk.DISABLED)
        self.stop_sign_btn.config(state=tk.NORMAL)
        self.sign_thread = threading.Thread(target=self.sign_input_loop, daemon=True)
        self.sign_thread.start()

    def stop_sign_input(self):
        self.sign_running = False
        self.start_sign_btn.config(state=tk.NORMAL)
        self.stop_sign_btn.config(state=tk.DISABLED)

    def sign_input_loop(self):
        cap = cv2.VideoCapture(0)
        while self.sign_running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            # Convert frame for mediapipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    landmarks = []
                    for lm in hand_landmarks.landmark:
                        landmarks.extend([lm.x, lm.y, lm.z])
                    matched_gesture = self.match_gesture(np.array(landmarks))
                    if matched_gesture:
                        self.update_text(f"Sign: {matched_gesture}\n")
                        self.current_text = matched_gesture
            # Show frame (for debugging)
            cv2.imshow("Sign Input", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    def match_gesture(self, detected_landmarks):
        for gesture, ref_landmarks in gestures.items():
            ref_array = np.array(ref_landmarks)
            distance = np.linalg.norm(detected_landmarks - ref_array)
            if distance < 0.5:
                return gesture
        return None

    def translate_output(self):
        if not self.current_text:
            return
        # Text-to-Speech
        threading.Thread(target=self.speak_text, args=(self.current_text,), daemon=True).start()
        # Text-to-Video
        words = self.current_text.split()
        for word in words:
            video_path = video_map.get(word.lower())
            if video_path and os.path.exists(video_path):
                self.play_video(video_path)
            else:
                self.update_canvas_text(word)

    def speak_text(self, text):
        tts_engine.say(text)
        tts_engine.runAndWait()

    def update_text(self, message):
        self.root.after(0, lambda: self.text_display.insert(tk.END, message))
        self.root.after(0, lambda: self.text_display.see(tk.END))

    def update_canvas_text(self, text):
        self.video_canvas.delete("all")
        self.video_canvas.create_text(200, 150, text=text, font=("Arial", 24), fill="white")

    def play_video(self, path):
        cap = cv2.VideoCapture(path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.resize(frame, (400, 300))
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img)
            self.video_img = ImageTk.PhotoImage(image=pil_img)
            # Update canvas image
            self.video_canvas.delete("all")
            self.video_canvas.create_image(0, 0, anchor=tk.NW, image=self.video_img)
            self.root.update()
            cv2.waitKey(30)
        cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = SignTranslatorApp(root)
    root.mainloop()