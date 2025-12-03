from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.properties import BooleanProperty, StringProperty, ObjectProperty
from kivy.core.window import Window
from math import cos, sin, radians

class ToggleSwitch(Widget):
    dark_mode = BooleanProperty(True)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Toggle dark/light mode
            self.dark_mode = not self.dark_mode
            if hasattr(self.parent.parent, 'toggle_theme'):
                self.parent.parent.toggle_theme()
        return super().on_touch_down(touch)

    def on_dark_mode(self, instance, value):
        self.canvas.ask_update()

    def on_size(self, *args):
        self.canvas.ask_update()

    def on_pos(self, *args):
        self.canvas.ask_update()

    def on_draw(self):
        self.canvas.clear()
        with self.canvas:
            if self.dark_mode:
                # Dark mode background
                Color(0.1, 0.1, 0.1, 1)
                Rectangle(pos=self.pos, size=self.size)
                Color(1, 1, 1, 1)
                Ellipse(pos=(self.right - 40, self.y + 5), size=(35, 35))
            else:
                # Light mode background
                Color(0.9, 0.9, 0.9, 1)
                Rectangle(pos=self.pos, size=self.size)
                Color(0.3, 0.3, 0.3, 1)
                Ellipse(pos=(self.x + 5, self.y + 5), size=(35, 35))

    def on_canvas(self, *args):
        self.on_draw()


class CameraIcon(Widget):
    icon_color = StringProperty("#64748b")

    def on_draw(self):
        self.canvas.clear()
        with self.canvas:
            c = self.hex_to_rgb(self.icon_color)
            Color(*c)
            # Camera body
            Line(rectangle=(self.x + 10, self.y + 15, 60, 35), width=2)
            # Lens
            Line(circle=(self.x + 40, self.y + 35, 10), width=2)
            # Top rectangle
            Color(*c)
            Rectangle(pos=(self.x + 35, self.y + 48), size=(10, 5))

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        lv = len(hex_color)
        return tuple(int(hex_color[i:i + lv // 3], 16) / 255 for i in range(0, lv, lv // 3))

    def on_size(self, *args):
        self.on_draw()

    def on_pos(self, *args):
        self.on_draw()


class SigntraLayout(BoxLayout):
    dark_mode = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        self.update_theme_colors()

        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)
        self.title = Label(text="Signtra", font_size=28, bold=True, color=self.text_color)
        header.add_widget(self.title)
        header.add_widget(Widget())  # spacer
        self.add_widget(header)

        # Top section
        top = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=0.5)

        # Left: Camera section
        left = BoxLayout(orientation='vertical', padding=10, spacing=10, background_color=self.panel_bg)
        self.camera_icon = CameraIcon()
        left.add_widget(self.camera_icon)
        self.camera_label = Label(text="Hand Gesture Camera", color=self.text_color, font_size=16)
        left.add_widget(self.camera_label)
        self.start_cam_btn = Button(text="Start Camera", background_color=self.button_blue, color=(1, 1, 1, 1))
        left.add_widget(self.start_cam_btn)
        top.add_widget(left)

        # Right: Video panel
        right = BoxLayout(orientation='vertical', padding=0, spacing=5)
        self.video_bar = Widget(size_hint_y=None, height=40)
        with self.video_bar.canvas:
            Color(0, 0, 0, 1)
            Rectangle(pos=self.video_bar.pos, size=self.video_bar.size)
        self.video_area = Widget()
        with self.video_area.canvas:
            Color(*self.hex_to_rgb(self.panel_bg))
            Rectangle(pos=self.video_area.pos, size=self.video_area.size)
        right.add_widget(self.video_bar)
        right.add_widget(self.video_area)
        top.add_widget(right)

        self.add_widget(top)

        # Transcript Area
        self.transcript_label = Label(text="Hand Gesture Transcript", color=self.text_color, font_size=14)
        self.add_widget(self.transcript_label)
        self.transcript_box = TextInput(
            hint_text="Transcript text will appear here...",
            background_color=self.hex_to_rgb(self.text_bg),
            foreground_color=self.hex_to_rgb(self.text_placeholder),
            size_hint_y=None, height=120
        )
        self.add_widget(self.transcript_box)

        # Bottom controls
        bottom = BoxLayout(orientation='horizontal', size_hint_y=None, height=80, spacing=10)

        self.record_btn = Button(text="🎤 Start Recording", background_color=self.button_blue, color=(1, 1, 1, 1))
        bottom.add_widget(self.record_btn)
        bottom.add_widget(Widget())

        self.settings_btn = Button(text="⚙", size_hint_x=None, width=70, background_color=self.hex_to_rgb(self.icon_bg))
        bottom.add_widget(self.settings_btn)

        self.toggle_switch = ToggleSwitch(size_hint_x=None, width=80)
        bottom.add_widget(self.toggle_switch)

        self.help_btn = Button(text="?", size_hint_x=None, width=70, background_color=self.hex_to_rgb(self.icon_bg))
        bottom.add_widget(self.help_btn)

        self.add_widget(bottom)

        self.bind(size=self.redraw, pos=self.redraw)

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        lv = len(hex_color)
        return tuple(int(hex_color[i:i + lv // 3], 16) / 255 for i in range(0, lv, lv // 3))

    def redraw(self, *args):
        if hasattr(self.video_area, 'canvas'):
            self.video_area.canvas.clear()
            with self.video_area.canvas:
                Color(*self.hex_to_rgb(self.panel_bg))
                Rectangle(pos=self.video_area.pos, size=self.video_area.size)

    def update_theme_colors(self):
        if self.dark_mode:
            self.bg_dark = "#0f172a"
            self.panel_bg = "#1e293b"
            self.text_bg = "#334155"
            self.text_placeholder = "#64748b"
            self.text_color = (0.89, 0.91, 0.94, 1)
            self.button_blue = (0.23, 0.51, 0.96, 1)
            self.icon_bg = "#334155"
        else:
            self.bg_dark = "#f1f5f9"
            self.panel_bg = "#ffffff"
            self.text_bg = "#e2e8f0"
            self.text_placeholder = "#64748b"
            self.text_color = (0.06, 0.09, 0.16, 1)
            self.button_blue = (0.23, 0.51, 0.96, 1)
            self.icon_bg = "#e2e8f0"

        Window.clearcolor = self.hex_to_rgb(self.bg_dark)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.update_theme_colors()
        # Update text/icon color
        self.transcript_label.color = self.text_color
        self.camera_label.color = self.text_color
        self.title.color = self.text_color
        self.camera_icon.icon_color = self.text_placeholder
        self.toggle_switch.dark_mode = self.dark_mode


class SigntraApp(App):
    def build(self):
        Window.size = (400, 700)  # mobile aspect
        return SigntraLayout()


if __name__ == '__main__':
    SigntraApp().run()