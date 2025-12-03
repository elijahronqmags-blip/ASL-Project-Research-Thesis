import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QTextEdit, 
    QFrame, QSizePolicy, QFileDialog
)
from PyQt5.QtCore import Qt, QUrl, QTime
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget


class HandGestureCameraApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hand Gesture Camera & Transcript Recorder")
        self.setGeometry(100, 100, 1400, 900)

        # State
        self.is_recording = False
        self.is_dark_theme = True
        self.camera_running = False

        # Set dark theme
        self.set_dark_theme()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Top section with camera and video player
        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)

        # Camera section (left)
        self.camera_frame = self.create_camera_section()
        top_layout.addWidget(self.camera_frame, 1)

        # Video player section (right)
        self.video_frame = self.create_video_section()
        top_layout.addWidget(self.video_frame, 1)

        main_layout.addLayout(top_layout, 2)

        # Transcript section
        self.transcript_section = self.create_transcript_section()
        main_layout.addWidget(self.transcript_section, 3)

        # Bottom buttons and controls
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        # Start Recording button
        self.record_btn = QPushButton("🎤 Start Recording")
        self.record_btn.setStyleSheet(self._record_button_style("#3b82f6"))
        self.record_btn.clicked.connect(self.toggle_recording)

        bottom_layout.addWidget(self.record_btn)
        bottom_layout.addStretch()

        # Settings button
        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedSize(50, 50)
        settings_btn.setStyleSheet(self._circle_button_style())

        # Theme toggle button
        self.theme_btn = QPushButton("☀️")
        self.theme_btn.setFixedSize(50, 50)
        self.theme_btn.setStyleSheet(self._circle_button_style())
        self.theme_btn.clicked.connect(self.toggle_theme)

        # Help button
        help_btn = QPushButton("?")
        help_btn.setFixedSize(50, 50)
        help_btn.setStyleSheet(self._circle_button_style())

        bottom_layout.addWidget(settings_btn)
        bottom_layout.addWidget(self.theme_btn)
        bottom_layout.addWidget(help_btn)

        main_layout.addLayout(bottom_layout)

        # Ensure initial styling for frames/textareas matches theme
        self.apply_theme_to_frames()

    # ----------------- UI pieces -----------------
    def create_camera_section(self):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame { background-color: #374151; border-radius: 12px; }
        """)

        layout = QVBoxLayout(frame)
        layout.setAlignment(Qt.AlignCenter)

        # Camera icon
        icon_label = QLabel("📷")
        icon_label.setStyleSheet("font-size: 64px; background: transparent;")
        icon_label.setAlignment(Qt.AlignCenter)

        # Title
        title = QLabel("Hand Gesture Camera")
        title.setStyleSheet("""
            color: #9ca3af;
            font-size: 18px;
            background: transparent;
        """)
        title.setAlignment(Qt.AlignCenter)

        # Start Camera button
        self.start_camera_btn = QPushButton("Start Camera")
        self.start_camera_btn.setStyleSheet(self._primary_button_style())
        self.start_camera_btn.clicked.connect(self.toggle_camera)

        layout.addWidget(icon_label)
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(self.start_camera_btn, alignment=Qt.AlignCenter)

        return frame

    def create_video_section(self):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame { background-color: #000000; border-radius: 12px; }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)

        # Video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background-color: #000000; border-radius: 12px;")
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Media player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)

        # Connect signals for time updates
        self.media_player.durationChanged.connect(self.on_duration_changed)
        self.media_player.positionChanged.connect(self.on_position_changed)
        self.media_player.stateChanged.connect(self.on_state_changed)

        # Video controls
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(10, 10, 10, 10)

        # Open file / load video
        open_btn = QPushButton("Open")
        open_btn.setFixedSize(60, 36)
        open_btn.setStyleSheet(self._control_button_style())
        open_btn.clicked.connect(self.open_video_file)

        # Play/Pause button
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(40, 40)
        self.play_btn.setStyleSheet(self._round_control_style())
        self.play_btn.clicked.connect(self.play_pause_video)

        # Time label
        self.time_label = QLabel("0:00 / 0:00")
        self.time_label.setStyleSheet("""
            color: white;
            background: transparent;
            font-size: 12px;
        """)

        # Volume (mute) button
        self.volume_btn = QPushButton("🔊")
        self.volume_btn.setFixedSize(40, 40)
        self.volume_btn.setStyleSheet(self._round_control_style())
        self.volume_btn.clicked.connect(self.toggle_mute)

        controls_layout.addWidget(open_btn)
        controls_layout.addWidget(self.play_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(self.time_label)
        controls_layout.addStretch()
        controls_layout.addWidget(self.volume_btn)

        layout.addWidget(self.video_widget)
        layout.addLayout(controls_layout)

        return frame

    def create_transcript_section(self):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame { background-color: #374151; border-radius: 12px; }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Hand Gesture Transcript")
        title.setStyleSheet("""
            color: #e5e7eb;
            font-size: 20px;
            font-weight: bold;
            background: transparent;
        """)

        # Transcript text area
        self.transcript_text = QTextEdit()
        self.transcript_text.setPlaceholderText("Transcript text will appear here ...")
        self.transcript_text.setStyleSheet("""
            QTextEdit {
                background-color: #1f2937;
                color: #9ca3af;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)

        layout.addWidget(title)
        layout.addWidget(self.transcript_text)

        return frame

    # ----------------- Theme -----------------
    def set_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(31, 41, 55))
        palette.setColor(QPalette.WindowText, QColor(229, 231, 235))
        self.setPalette(palette)
        self.setStyleSheet("QMainWindow { background-color: #1f2937; }")
        self.is_dark_theme = True

    def set_light_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(243, 244, 246))
        palette.setColor(QPalette.WindowText, QColor(17, 24, 39))
        self.setPalette(palette)
        self.setStyleSheet("QMainWindow { background-color: #f3f4f6; }")
        self.is_dark_theme = False

    def toggle_theme(self):
        if self.is_dark_theme:
            # switch to light
            self.theme_btn.setText("🌙")
            self.set_light_theme()
        else:
            # switch to dark
            self.theme_btn.setText("☀️")
            self.set_dark_theme()

        # apply consistent colors to internal frames/widgets
        self.apply_theme_to_frames()

    def apply_theme_to_frames(self):
        if self.is_dark_theme:
            self.camera_frame.setStyleSheet("QFrame { background-color: #374151; border-radius: 12px; }")
            self.transcript_section.setStyleSheet("QFrame { background-color: #374151; border-radius: 12px; }")
            self.transcript_text.setStyleSheet("""
                QTextEdit {
                    background-color: #1f2937;
                    color: #9ca3af;
                    border: none;
                    border-radius: 8px;
                    padding: 15px;
                    font-size: 14px;
                    font-family: 'Consolas', 'Monaco', monospace;
                }
            """)
            self.video_frame.setStyleSheet("QFrame { background-color: #000000; border-radius: 12px; }")
        else:
            self.camera_frame.setStyleSheet("QFrame { background-color: #e5e7eb; border-radius: 12px; }")
            self.transcript_section.setStyleSheet("QFrame { background-color: #ffffff; border-radius: 12px; }")
            self.transcript_text.setStyleSheet("""
                QTextEdit {
                    background-color: #f9fafb;
                    color: #4b5563;
                    border: 1px solid #d1d5db;
                    border-radius: 8px;
                    padding: 15px;
                    font-size: 14px;
                    font-family: 'Consolas', 'Monaco', monospace;
                }
            """)
            self.video_frame.setStyleSheet("QFrame { background-color: #f3f4f6; border-radius: 12px; }")

    # ----------------- Actions -----------------
    def toggle_camera(self):
        # simple toggle placeholder (replace with real camera logic later)
        self.camera_running = not self.camera_running
        if self.camera_running:
            self.start_camera_btn.setText("Stop Camera")
            self.transcript_text.append("Camera started...")
        else:
            self.start_camera_btn.setText("Start Camera")
            self.transcript_text.append("Camera stopped.")

    def toggle_recording(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.record_btn.setText("⏹️ Stop Recording")
            self.record_btn.setStyleSheet(self._record_button_style("#ef4444"))
            self.transcript_text.append("Recording started...")
        else:
            self.record_btn.setText("🎤 Start Recording")
            self.record_btn.setStyleSheet(self._record_button_style("#3b82f6"))
            self.transcript_text.append("Recording stopped.")

    def open_video_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4 *.mov *.mkv *.avi);;All Files (*)")
        if path:
            url = QUrl.fromLocalFile(path)
            self.media_player.setMedia(QMediaContent(url))
            self.play_btn.setText("▶")
            self.time_label.setText("0:00 / 0:00")
            self.transcript_text.append(f"Loaded video: {path}")

    def play_pause_video(self):
        if self.media_player.mediaStatus() in (QMediaPlayer.NoMedia,):
            self.transcript_text.append("No video loaded.")
            return

        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            # play button text will be updated in on_state_changed
        else:
            self.media_player.play()

    def toggle_mute(self):
        is_muted = self.media_player.isMuted()
        self.media_player.setMuted(not is_muted)
        self.volume_btn.setText("🔈" if not is_muted else "🔊")

    # ----------------- Media callbacks -----------------
    def on_duration_changed(self, duration_ms):
        # duration in ms
        total = self._format_ms(duration_ms)
        current = self._format_ms(self.media_player.position())
        self.time_label.setText(f"{current} / {total}")

    def on_position_changed(self, position_ms):
        total_ms = self.media_player.duration()
        current = self._format_ms(position_ms)
        total = self._format_ms(total_ms) if total_ms > 0 else "0:00"
        self.time_label.setText(f"{current} / {total}")

    def on_state_changed(self, state):
        if state == QMediaPlayer.PlayingState:
            self.play_btn.setText("⏸")
        else:
            self.play_btn.setText("▶")

    # ----------------- Utilities -----------------
    @staticmethod
    def _format_ms(ms):
        if ms is None or ms <= 0:
            return "0:00"
        secs = int(ms / 1000)
        m, s = divmod(secs, 60)
        return f"{m}:{s:02d}"

    # Styles helpers
    @staticmethod
    def _primary_button_style():
        return """
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """

    @staticmethod
    def _record_button_style(color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                filter: brightness(0.95);
            }}
        """

    @staticmethod
    def _circle_button_style():
        return """
            QPushButton {
                background-color: #374151;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """

    @staticmethod
    def _control_button_style():
        return """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.12);
            }
        """

    @staticmethod
    def _round_control_style():
        return """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.12);
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.18);
            }
        """


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = HandGestureCameraApp()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
