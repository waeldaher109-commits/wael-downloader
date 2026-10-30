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
import yt_dlp

Window.clearcolor = (0.08, 0.08, 0.08, 1)

APP_NAME = "WAEL DOWNLOADER"
COLOR_RED = [1, 0, 0.2, 1]

class WaelDownloaderApp(App):
    def build(self):
        self.title = APP_NAME
        self.is_downloading = False
        self.stop_flag = threading.Event()
        
        root = BoxLayout(orientation='vertical', padding=10, spacing=8)

        # Header
        header = Label(
            text=f"{APP_NAME}  📥",
            font_size=22,
            bold=True,
            color=COLOR_RED,
            size_hint_y=None,
            height=50
        )
        root.add_widget(header)

        # URL Frame
        url_layout = FloatLayout(size_hint_y=None, height=45)
        self.url_input = TextInput(
            hint_text="Paste YouTube link here...",
            multiline=False,
            size_hint=(0.85, None),
            height=40,
            pos_hint={'x': 0, 'center_y': 0.5},
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 0, 0.2, 1)
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

        # Info Box
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

        # Type Selection
        type_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=20, padding=[50, 0])
        self.type_var = "mp3"
        
        def on_type_active(checkbox, value, t_val):
            if value:
                self.type_var = t_val

        v_box = BoxLayout(orientation='horizontal', spacing=5)
        v_chk = CheckBox(group='dl_type', active=False, color=COLOR_RED)
        v_chk.bind(active=lambda cb, val: on_type_active(cb, val, "video"))
        v_box.add_widget(v_chk)
        v_box.add_widget(Label(text="Video MP4 🎬", font_size=13))
        type_layout.add_widget(v_box)

        m_box = BoxLayout(orientation='horizontal', spacing=5)
        m_chk = CheckBox(group='dl_type', active=True, color=COLOR_RED)
        m_chk.bind(active=lambda cb, val: on_type_active(cb, val, "mp3"))
        m_box.add_widget(m_chk)
        m_box.add_widget(Label(text="Audio MP3 🎵", font_size=13))
        type_layout.add_widget(m_box)
        root.add_widget(type_layout)

        # Quality Spinner
        self.quality_spinner = Spinner(
            text='1080p',
            values=('2160p', '1440p', '1080p', '720p', '480p', '360p'),
            size_hint_y=None,
            height=40,
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1,1,1,1)
        )
        root.add_widget(self.quality_spinner)

        # Progress
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

        # Buttons
        self.download_btn = Button(
            text="Download ⤵️",
            size_hint_y=None,
            height=50,
            background_color=(0.15, 0.6, 0.15, 1),
            bold=True,
            font_size=16
        )
        self.download_btn.bind(on_press=self.on_download_press)
        root.add_widget(self.download_btn)

        self.cancel_btn = Button(
            text="Cancel ❌",
            size_hint_y=None,
            height=50,
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
        self.stop_flag.set()

    def cancel_download(self, instance):
        if self.is_downloading:
            self.stop_flag.set()
            self.progress_label.text = "Cancelling... ❌"
        else:
            self.progress_label.text = "Nothing to cancel"
            self.progress_bar.value = 0

    def on_download_press(self, instance):
        if self.is_downloading:
            return
        self.stop_flag.clear()
        threading.Thread(target=self.start_download, daemon=True).start()

    def start_download(self):
        url = self.url_input.text.strip()
        if not url:
            Clock.schedule_once(lambda dt: setattr(self.progress_label, 'text', 'Paste a link first! ⚠️'))
            return

        self.is_downloading = True
        Clock.schedule_once(lambda dt: setattr(self.progress_label, 'text', 'Connecting to YouTube...'))
        Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', 0))
        
        try:
            from android.storage import primary_external_storage_path
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
            download_path = os.path.join(primary_external_storage_path(), 'Download')
        except:
            download_path = os.path.expanduser("~/Downloads")
            os.makedirs(download_path, exist_ok=True)

        dl_type = self.type_var
        q = self.quality_spinner.text
        
        def progress_hook(d):
            if self.stop_flag.is_set():
                raise Exception("Cancelled by user")
            if d['status'] == 'downloading':
                try:
                    # yt-dlp يعطي downloaded_bytes و total_bytes
                    total = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
                    downloaded = d.get('downloaded_bytes', 0)
                    p_val = (downloaded / total) * 100
                    Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', p_val))
                    speed = d.get('_speed_str', '')
                    eta = d.get('_eta_str', '')
                    Clock.schedule_once(lambda dt: setattr(self.progress_label, 'text', f"{p_val:.1f}% - {speed} - ETA: {eta}"))
                except:
                    pass
            elif d['status'] == 'finished':
                Clock.schedule_once(lambda dt: setattr(self.progress_label, 'text', 'Merging files...'))

        common_opts = {
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
        }

        if dl_type == "mp3":
            opts = {
                **common_opts,
                'format': 'bestaudio/best',
                # اذا في ffmpeg بيحول لـ mp3، اذا لا بينزل m4a الأصلي
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'postprocessor_args': [],
            }
        else:
            height = q.replace("p", "")
            opts = {
                **common_opts,
                'format': f'bestvideo[height<={height}]+bestaudio/best[height<={height}]/best',
                'merge_output_format': 'mp4',
            }

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                # جيب معلومات الفيديو للعرض
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Video')[:40]
                Clock.schedule_once(lambda dt: setattr(self.info_label, 'text', f"Title: {title}\nDownloading to: {download_path}"))
                
                if not self.stop_flag.is_set():
                    ydl.download([url])
            
            if not self.stop_flag.is_set():
                Clock.schedule_once(lambda dt: setattr(self.progress_label, 'text', 'Download Complete! ✅'))
                Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', 100))
        except Exception as e:
            err_msg = str(e)
            if "Cancelled" in err_msg:
                Clock.schedule_once(lambda dt: setattr(self.progress_label, 'text', 'Download cancelled ❌'))
                Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', 0))
            elif "ffmpeg" in err_msg.lower() or "ffprobe" in err_msg.lower():
                # Fallback بدون ffmpeg: حمل الصوت الأصلي
                try:
                    fallback_opts = {**common_opts, 'format': 'bestaudio/best'}
                    fallback_opts.pop('postprocessors', None)
                    with yt_dlp.YoutubeDL(fallback_opts) as ydl2:
                        ydl2.download([url])
                    Clock.schedule_once(lambda dt: setattr(self.progress_label, 'text', 'Downloaded as M4A (no ffmpeg) ✅'))
                    Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', 100))
                except Exception as e2:
                    Clock.schedule_once(lambda dt: setattr(self.progress_label, 'text', f'Error: {str(e2)[:40]}'))
            else:
                Clock.schedule_once(lambda dt: setattr(self.progress_label, 'text', f'Error: {err_msg[:40]}'))
        finally:
            self.is_downloading = False

if __name__ == '__main__':
    WaelDownloaderApp().run()
