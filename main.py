from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.core.window import Window
import threading
import os
import time
import yt_dlp

# تعيين لون خلفية النافذة ليطابق التصميم الغامق الأصلي
Window.clearcolor = (0.08, 0.08, 0.08, 1)

APP_NAME = "𝕎𝔸𝔼𝕃 𝔻𝕆𝕎ℕ𝕃𝕆𝔸𝔻𝔼ℝ"
COLOR = [1, 0, 0.2, 1]  # #FF0033

class WaelDownloaderApp(App):
    def build(self):
        self.title = APP_NAME
        
        # الجذر الرئيسي (واجهة عامودية)
        root = BoxLayout(orientation='vertical', padding=10, spacing=5)

        # ==================== Header ====================
        header = Label(
            text=f"{APP_NAME} 📥",
            font_size=24,
            bold=True,
            color=[1, 0, 0.2, 1],
            size_hint_y=None,
            height=50
        )
        root.add_widget(header)

        # ==================== URL Frame ====================
        url_layout = FloatLayout(size_hint_y=None, height=45)
        
        self.url_input = TextInput(
            hint_text="Paste YouTube link here...",
            multiline=False,
            size_hint=(0.85, None),
            height=40,
            pos_hint={'x': 0, 'center_y': 0.5},
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1)
        )
        url_layout.add_widget(self.url_input)

        clear_btn = Button(
            text="✕",
            size_hint=(None, None),
            size=(40, 40),
            pos_hint={'right': 1, 'center_y': 0.5},
            background_color=(0.2, 0.2, 0.2, 1)
        )
        clear_btn.bind(on_press=self.clear_fields)
        url_layout.add_widget(clear_btn)
        
        root.add_widget(url_layout)

        # ==================== Preview / Info Box ====================
        self.info_label = Label(
            text="Paste link to see info",
            font_size=14,
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=80,
            halign='center',
            valign='middle'
        )
        self.info_label.bind(size=self.info_label.setter('text_size'))
        root.add_widget(self.info_label)

        # ==================== Type Selection (Video / MP3) ====================
        type_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=20, padding=[50, 0])
        
        self.type_var = "mp3"
        
        def on_type_active(checkbox, value, t_val):
            if value:
                self.type_var = t_val

        # خيار الفيديو
        v_box = BoxLayout(orientation='horizontal', spacing=5)
        v_chk = CheckBox(group='dl_type', active=False, color=[1, 0, 0.2, 1])
        v_chk.bind(active=lambda cb, val: on_type_active(cb, val, "video"))
        v_box.add_widget(v_chk)
        v_box.add_widget(Label(text="Video MP4 🎬", font_size=13))
        type_layout.add_widget(v_box)

        # خيار الصوت
        m_box = BoxLayout(orientation='horizontal', spacing=5)
        m_chk = CheckBox(group='dl_type', active=True, color=[1, 0, 0.2, 1])
        m_chk.bind(active=lambda cb, val: on_type_active(cb, val, "mp3"))
        m_box.add_widget(m_chk)
        m_box.add_widget(Label(text="Audio MP3 🎵", font_size=13))
        type_layout.add_widget(m_box)

        root.add_widget(type_layout)

        # ==================== Quality ComboBox (Spinner) ====================
        self.quality_spinner = Spinner(
            text='1080p',
            values=('2160p', '1440p', '1080p', '720p', '480p', '360p'),
            size_hint_y=None,
            height=40,
            background_color=(0.2, 0.2, 0.2, 1)
        )
        root.add_widget(self.quality_spinner)

        # ==================== Progress & Status ====================
        self.progress_label = Label(
            text="Waiting for link...",
            font_size=13,
            color=(0.5, 1, 0.5, 1),
            size_hint_y=None,
            height=30
        )
        root.add_widget(self.progress_label)

        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=20)
        root.add_widget(self.progress_bar)

        # ==================== Buttons (Download & Cancel) ====================
        self.download_btn = Button(
            text="Download ⤵️",
            size_hint_y=None,
            height=45,
            background_color=(0.4, 0.8, 0, 1),
            bold=True,
            font_size=16
        )
        self.download_btn.bind(on_press=lambda x: threading.Thread(target=self.start_download, daemon=True).start())
        root.add_widget(self.download_btn)

        self.cancel_btn = Button(
            text="Cancel ❌",
            size_hint_y=None,
            height=45,
            background_color=(0.3, 0.3, 0.3, 1),
            bold=True,
            font_size=16
        )
        self.cancel_btn.bind(on_press=self.cancel_download)
        root.add_widget(self.cancel_btn)

        return root

    def clear_fields(self, instance):
        self.url_input.text = ""
        self.info_label.text = "Paste link to see info"
        self.progress_label.text = "Waiting for link..."
        self.progress_bar.value = 0

    def cancel_download(self, instance):
        self.progress_label.text = "Download cancelled ❌"
        self.progress_bar.value = 0

    def start_download(self):
        url = self.url_input.text.strip()
        if not url:
            Clock.schedule_once(lambda dt: setattr(self.progress_label, 'text', 'Paste a link first!'))
            return

        Clock.schedule_once(lambda dt: setattr(self.progress_label, 'text', 'Connecting to YouTube...'))
        
        # تحديد مسار التخزين الداخلي المناسب للأندرويد أو الديسكتوب
        try:
            from android.storage import primary_external_storage_path
            download_path = os.path.join(primary_external_storage_path(), 'Download')
        except:
            download_path = os.path.expanduser("~")

        dl_type = self.type_var
        q = self.quality_spinner.text
        
        def progress_hook(d):
            if d['status'] == 'downloading':
                percent_str = d.get('_percent_str', '0%').replace('%', '').strip()
                try:
                    p_val = float(percent_str)
                    Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', p_val))
                except:
                    pass
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')
                Clock.schedule_once(lambda dt: setattr(self.progress_label, 'text', f"{p_val}% - {speed} - ETA: {eta}"))

        common_opts = {
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True,
        }

        if dl_type == "mp3":
            opts = {
                **common_opts,
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        else:
            height = q.replace("p", "")
            opts = {
                **common_opts,
                'format': f'bestvideo[height<={height}]+bestaudio/best[height<={height}]',
                'merge_output_format': 'mp4',
            }

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            Clock.schedule_once(lambda dt: setattr(self.progress_label, 'text', 'Download Complete! ✅'))
            Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', 100))
        except Exception as e:
            Clock.schedule_once(lambda dt: setattr(self.progress_label, 'text', f'Error: {str(e)[:30]}'))

if __name__ == '__main__':
    WaelDownloaderApp().run()
