import cv2
import mediapipe as mp
import os
import threading
import tkinter as tk
from video import SignVideoPlayer  # Assuming this is in 'video.py'
import speech_recognition as sr  # For speech recognition

# Setup Tkinter window and canvas
root = tk.Tk()
root.title("Sign Language Detection & Video Player")
canvas_width, canvas_height = 640, 480
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
canvas.pack()

# Initialize the video player with the canvas and folder path
video_folder = os.path.join("Research", "Sign library")
player = SignVideoPlayer(canvas, video_folder)

# Initialize MediaPipe Hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# Open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open webcam")
    exit()

# Function for detecting signs and triggering videos
def detect_and_play():
    success, image = cap.read()
    if not success:
        print("Failed to capture frame.")
        root.after(10, detect_and_play)
        return

    # Hand detection
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as hands:
        results = hands.process(image_rgb)

        # Draw hand landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )
            # Placeholder for sign recognition logic
            recognized_word = "hello"  # Replace with actual recognition logic
            print(f"Recognized sign: {recognized_word}")
            # Play video for recognized sign
            player.play_video(recognized_word)

    # Show webcam feed in OpenCV window
    cv2.imshow('Webcam', image)
    # Schedule next detection
    root.after(10, detect_and_play)

# Function to handle recognized speech input
def handle_recognized_speech(recognized_text):
    # Convert to lowercase and strip
    text = recognized_text.lower().strip()
    print(f"Recognized speech: {text}")
    # Trigger sign video playback
    player.play_video(text)

# Thread function for continuous speech recognition
def speech_recognition_thread():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
    while True:
        try:
            with microphone as source:
                print("Listening for speech...")
                audio = recognizer.listen(source, phrase_time_limit=3)
            recognized_text = recognizer.recognize_google(audio)
            # Call the handler in the main thread
            root.after(0, handle_recognized_speech, recognized_text)
        except sr.UnknownValueError:
            pass  # Could not understand audio
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

# Start the speech recognition in a separate thread
threading.Thread(target=speech_recognition_thread, daemon=True).start()

# Start detection loop
root.after(0, detect_and_play)

# Run Tkinter event loop
root.mainloop()

# Cleanup after closing window
cap.release()
cv2.destroyAllWindows()