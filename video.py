# video.py
import os
import threading
import cv2
from PIL import Image, ImageTk
import tkinter as tk

class SignVideoPlayer:
    def __init__(self, canvas, folder_path):
        self.canvas = canvas
        self.folder_path = folder_path
        self.video_dict = self.load_videos()
        self.stop_event = threading.Event()
        self.current_thread = None

        # Create a single image item on the canvas
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW)
        self.canvas.update()  # Ensure the canvas is updated

    def load_videos(self):
        videos = {}
        for filename in os.listdir(self.folder_path):
            if filename.endswith(('.mp4', '.avi', '.mov')):
                key = os.path.splitext(filename)[0].lower()
                videos[key] = os.path.join(self.folder_path, filename)
        return videos

    def get_video_path(self, word):
        return self.video_dict.get(word.lower(), None)

    def play_video(self, word):
        # Stop any currently playing video
        self.stop_video()

        video_path = self.get_video_path(word)
        if not video_path:
            print(f"No video found for '{word}'")
            return

        self.stop_event.clear()

        def stream_video():
            cap = cv2.VideoCapture(video_path)
            while cap.isOpened() and not self.stop_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    break
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Resize to fit canvas
                frame = cv2.resize(frame, (self.canvas.winfo_width(), self.canvas.winfo_height()))
                # Convert to PhotoImage
                img = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image=img)
                # Update existing image item
                self.canvas.itemconfig(self.image_on_canvas, image=photo)
                self.canvas.image = photo  # keep reference
                self.canvas.update()
                # Delay to control frame rate
                cv2.waitKey(30)
            cap.release()

        self.current_thread = threading.Thread(target=stream_video, daemon=True)
        self.current_thread.start()

    def stop_video(self):
        self.stop_event.set()
        if self.current_thread and self.current_thread.is_alive():
            self.current_thread.join()