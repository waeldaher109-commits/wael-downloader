import customtkinter as ctk
import yt_dlp
import os
import threading
import tkinter as tk
import time
import sys
import webbrowser
from PIL import Image, ImageTk
import urllib.request
from io import BytesIO
import subprocess
import platform
from tkinter import filedialog
import socket
from tkinter import messagebox
def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        # لما يكون exe
        base = sys._MEIPASS
    else:
        # لما يكون ب VS Code
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "ffmpeg.exe")

FFMPEG_PATH = get_ffmpeg_path()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    jpg_path = os.path.join(BASE_DIR, "icon.jpg")
    ico_path = os.path.join(BASE_DIR, "icon.ico")
    if os.path.exists(jpg_path):
        Image.open(jpg_path).save(ico_path, sizes=[(256,256),(40,40),(50,50)])
except:
    pass

APP_NAME = "𝕎𝔸𝔼𝕃 𝔻𝕆𝕎ℕ𝕃𝕆𝔸𝔻𝔼ℝ"
# تم تصغير حجم النافذة لتناسب الشاشات الصغيرة بشكل مريح
APP_WIDTH = 550
APP_HEIGHT = 590
COLOR = "#FF0033"

ctk.set_appearance_mode("dark")
app = ctk.CTk()
try:
    app.iconbitmap(os.path.join(BASE_DIR, "icon.ico"))
except:
    pass

app.title(APP_NAME)
app.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
# جعل النافذة تتكيف مع الشاشة ولا تتجاوز حدودها
app.maxsize(APP_WIDTH, APP_HEIGHT)
app.resizable(False, False)

# ==================== Header Frame ====================
header_frame = ctk.CTkFrame(app, fg_color="transparent")
header_frame.pack(pady=5, fill="x", padx=10)
header_frame.configure(height=75)
header_frame.pack_propagate(False)

try:
    logo_path = os.path.join(BASE_DIR, "logo.png")
    if os.path.exists(logo_path):
        logo_pil = Image.open(logo_path)
        logo_img = ctk.CTkImage(light_image=logo_pil, dark_image=logo_pil, size=(140, 120))
        logo_label = ctk.CTkLabel(header_frame, image=logo_img, text="")
        logo_label.place(x=-30, y=-30)
    else:
        print("logo.png not found")
except Exception as e:
    print(f"Logo error: {e}")

title = ctk.CTkLabel(header_frame, text=f" {APP_NAME}📥", font=("Arial", 32, "bold"), text_color=COLOR)
title.place(x=100, y=5)

def open_youtube():
    url = "https://www.youtube.com"
    try:
        chrome = webbrowser.get("chrome")
        chrome.open(url)
    except:
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if os.path.exists(chrome_path):
            subprocess.Popen([chrome_path, url])
        else:
            webbrowser.open(url)

# ==================== URL Frame & Clear Button ====================
url_frame = ctk.CTkFrame(app, width=520, height=40, fg_color="transparent")
url_frame.pack(pady=3)
url_frame.pack_propagate(False)

url_entry = ctk.CTkEntry(url_frame, width=435, height=30, placeholder_text="Paste YouTube link here...")
url_entry.place(x=45, y=5)

try:
    yt_pil = Image.open(os.path.join(BASE_DIR, "youtube.png"))
    yt_img = ctk.CTkImage(light_image=yt_pil, dark_image=yt_pil, size=(24, 24))
    yt_btn = ctk.CTkButton(url_frame, image=yt_img, text="", width=0, height=30, fg_color="transparent", command=open_youtube)
    yt_btn.place(x=10, y=5)
except:
    yt_btn = ctk.CTkButton(url_frame, text="▶", width=30, height=30, fg_color="transparent", command=open_youtube)
    yt_btn.place(x=10, y=5)

menu = tk.Menu(app, tearoff=0, bg="#1a1a1a", fg="white")
menu.add_command(label="Cut", command=lambda: app.focus_get().event_generate("<<Cut>>"))
menu.add_command(label="Copy", command=lambda: app.focus_get().event_generate("<<Copy>>"))
menu.add_command(label="Paste", command=lambda: app.focus_get().event_generate("<<Paste>>"))
def show_menu(e):
    menu.tk_popup(e.x_root, e.y_root)
url_entry.bind("<Button-3>", show_menu)
url_entry.bind("<Button-2>", show_menu)

# ==================== Preview Frame ====================
preview_frame = ctk.CTkFrame(app, width=520, height=105, fg_color="#151515", corner_radius=10)
preview_frame.pack(pady=3)
preview_frame.pack_propagate(False)

thumb_label = tk.Label(preview_frame, bg="#222", bd=0)
thumb_label.pack(side="left", padx=2, pady=3)
info_label = ctk.CTkLabel(preview_frame, text="Paste link to see info", font=("Arial", 12), wraplength=750, justify="left")
info_label.pack(side="left", padx=20)

thumb_image_ref = None
last_fetched_url = ""
is_fetching = False
is_downloading = False
download_path = os.path.join(os.path.expanduser("~"), "Downloads")

def clear_url_action():
    global last_fetched_url, is_fetching, thumb_image_ref
    is_fetching = False
    last_fetched_url = ""
    url_entry.delete(0, "end")
    thumb_image_ref = None
    thumb_label.configure(image="", text="")
    thumb_label.image = None
    url_entry.focus()
    try:
        thumb_label.configure(image=None, text="No Preview")
    except:
        thumb_label.configure(text="No Preview")
    thumb_image_ref = None
    info_label.configure(text="Paste link to see info")
    progress_label.configure(text="Waiting for link...")
    quality_combo.configure(values=["2160p", "1440p", "1080p", "720p", "480p", "360p"])
    quality_var.set("1080p")
    bar.set(0)
    log("Cleared - Ready for new link")

clear_btn = ctk.CTkButton(app, text="✕", width=30, height=28, fg_color="#2a2a2a", command=clear_url_action)
clear_btn.place(x=490, y=92)

def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except:
        return False

def show_no_internet_popup():
    messagebox.showerror("No Internet Connection", "No internet connection detected.\nPlease check your network connection and try again.")

def load_thumbnail(url):
    def do_download():
        try:
            if url_entry.get().strip() == "" or last_fetched_url == "":
                return
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as u:
                data = u.read()
            pil_im = Image.open(BytesIO(data)).convert("RGB").resize((280, 160), Image.LANCZOS)
            def apply_in_main():
                global thumb_image_ref
                tk_im = ImageTk.PhotoImage(pil_im)
                thumb_image_ref = tk_im
                thumb_label.configure(image=tk_im, text="")
                thumb_label.image = tk_im
            app.after(0, apply_in_main)
        except Exception as e:
            print(f"Thumb error: {e}")
    threading.Thread(target=do_download, daemon=True).start()

def fetch_preview():
    global last_fetched_url, is_fetching
    url = url_entry.get().strip()
    if not url.startswith("http"):
        return
    if last_fetched_url == url:
        return
    if not is_connected():
        info_label.configure(text="No internet connection", text_color="#FF6A00")
        progress_label.configure(text="No internet connection ❌🌐")
        log("No internet connection", text_color="#FF6200")
        show_no_internet_popup()
        return

    info_label.configure(text="Fetching info...", text_color="#00FFF2")
    progress_label.configure(text="Checking link...", text_color="#00FFF2")
    last_fetched_url = url
    is_fetching = True
    try:
        info = None
        ydl_opts = {
            'quiet': True, 
            'no_warnings': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0',
            'ffmpeg_location': FFMPEG_PATH,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        if not info:
            raise Exception("No info")
        title_text = info.get('title', 'No title')
        duration = info.get('duration', 0)
        filesize = info.get('filesize_approx') or info.get('filesize') or 0
        size_str = f"{filesize/1024/1024:.1f} MB" if filesize else "Unknown size"
        info_label.configure(text=f"{title_text[:45]}...\n{duration // 60}m {duration % 60}s | {size_str}")
        formats = info.get('formats', [])
        heights = []
        for f in formats:
            h = f.get('height')
            vcodec = f.get('vcodec')
            if h and vcodec != 'none' and h >= 144:
                heights.append(h)
        heights = sorted(set(heights), reverse=True)
        if heights:
            real_qualities = [f"{h}p" for h in heights]
            quality_combo.configure(values=real_qualities)
            quality_var.set(real_qualities[0])
            log(f"Available qualities: {real_qualities}", text_color="#FF00A6")
        else:
            quality_combo.configure(values=["1080p", "720p", "480p", "360p"])
            quality_var.set("1080p")
        thumbs = info.get('thumbnails', [])
        thumb_url = thumbs[-1]['url'] if thumbs else info.get('thumbnail')
        if thumb_url:
            threading.Thread(target=lambda: load_thumbnail(thumb_url), daemon=True).start()
        progress_label.configure(text="Link Ready ✓✅", text_color="#4400FF")
    except Exception as e:
        print(e)
        info_label.configure(text="Failed to fetch info⚠️❗️🛑", text_color="#FF0000")
        progress_label.configure(text="Link not supported or invalid ❌⁉️", text_color="#FF0000")
    finally:
        is_fetching = False

def on_url_change(event=None):
    threading.Thread(target=fetch_preview, daemon=True).start()

url_entry.bind("<KeyRelease>", lambda e: app.after(800, on_url_change) if len(url_entry.get()) > 10 else None)
url_entry.bind("<<Paste>>", lambda e: app.after(500, on_url_change))

# ==================== Type & Quality Controls ====================
type_var = ctk.StringVar(value="mp3")
f1 = ctk.CTkFrame(app, fg_color="transparent")
f1.pack(pady=3)
ctk.CTkRadioButton(f1, text="Video MP4🎬", variable=type_var, value="video", border_color=COLOR, fg_color=COLOR, font=("Arial", 11, "bold")).pack(side="left", padx=15)
ctk.CTkRadioButton(f1, text="Audio MP3🎵", variable=type_var, value="mp3", border_color=COLOR, fg_color=COLOR, font=("Arial", 11, "bold")).pack(side="left", padx=15)

quality_var = ctk.StringVar(value="1080p")
quality_combo = ctk.CTkComboBox(app, variable=quality_var, values=["2160p", "1440p", "1080p", "720p", "480p", "360p"], width=180, button_color=COLOR, border_color=COLOR)
quality_combo.pack(pady=5)

# ==================== Path Selection Frame ====================
path_frame = ctk.CTkFrame(app, fg_color="transparent")
path_frame.pack(pady=3, fill="x")
path_frame.configure(height=35)
path_frame.pack_propagate(False)

path_label = ctk.CTkLabel(path_frame, text=f" Save to: {download_path[:38]}...", font=("Arial", 10), width=300)
path_label.place(x=115, y=3)

def choose_folder():
    global download_path
    folder = filedialog.askdirectory(initialdir=download_path)
    if folder:
        download_path = folder
        path_label.configure(text=f" Save to: {download_path[:38]}...")
        log(f"Save folder changed to✅: {download_path}", text_color="#00FF00")

choose_btn = ctk.CTkButton(path_frame, text="📁 Choose Folder", width=100, height=10, fg_color="#97932C", command=choose_folder, font=("Arial", 10))
choose_btn.place(x=350, y=5)

# ==================== Progress & Log Box ====================
progress_label = ctk.CTkLabel(app, text="Waiting for link🔄...", font=("Arial", 11, "bold"))
progress_label.pack()
bar = ctk.CTkProgressBar(app, width=520, height=10, progress_color=COLOR)
bar.pack(pady=5)
bar.set(0)

log_box = ctk.CTkTextbox(app, width=520, height=110, font=("Consolas", 11), fg_color="#0a0a0a", text_color="#00FF00")
log_box.pack(pady=5)
log_box.tag_config("red", foreground="#FF3B3B")
log_box.tag_config("green", foreground="#00FF00")
log_box.tag_config("blue", foreground="#3498DB")
log_box.tag_config("orange", foreground="#F39C12")
log_box.configure(state="disabled")

cancel_flag = False
last_log_time = 0

def log(msg, color="green", text_color=None, **kwargs):
    log_box.configure(state="normal")
    log_box.insert("end", msg + "\n", color)
    log_box.see("end")
    log_box.configure(state="disabled")

log("Ready - Paste link and start🌐")

def animate_button():
    if is_downloading:
        current = download_btn.cget("fg_color")
        new_color = "#ff3366" if current == COLOR else COLOR
        download_btn.configure(fg_color=new_color)
        app.after(400, animate_button)
    else:
        download_btn.configure(fg_color=COLOR)

def hook(d):
    global last_log_time
    if cancel_flag:
        raise Exception("Cancelled")
    if d['status'] == 'downloading':
        s = d.get('_percent_str', '0%').strip()
        speed = d.get('_speed_str', '').strip()
        eta = d.get('_eta_str', '').strip()
        total = d.get('_total_bytes_str', 'N/A').strip()
        try:
            p = float(s.replace('%', '')) / 100
            bar.set(p)
        except:
            pass
        progress_label.configure(text=f"{s} - {speed} - {eta}")
        if time.time() - last_log_time > 0.5:
            log(f"[download] {s} of {total} at {speed} ETA {eta}")
            last_log_time = time.time()
    elif d['status'] == 'finished':
        progress_label.configure(text="Finishing...")
        log("Finished - merging...")

def open_folder():
    folder_to_open = download_path if os.path.exists(download_path) else BASE_DIR
    if platform.system() == "Windows":
        os.startfile(folder_to_open)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", folder_to_open])
    else:
        subprocess.Popen(["xdg-open", folder_to_open])

def download():
    global cancel_flag, is_downloading
    cancel_flag = False
    is_downloading = True
    animate_button()
    if not is_connected():
        log("No internet connection - download cancelled")
        progress_label.configure(text="No internet connection ❌")
        is_downloading = False
        show_no_internet_popup()
        return
    url = url_entry.get().strip()
    if not url:
        log("Paste a link first")
        is_downloading = False
        return
    bar.set(0)
    progress_label.configure(text="Preparing link...")
    log("Connecting to YouTube...")
    q = quality_var.get()
    h = q.replace("p", "")
    dl_type = type_var.get()
    log(f"Requested {dl_type} quality {q} | Saving to: {download_path}")
    common = {
        'ffmpeg_location': BASE_DIR,
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'progress_hooks': [hook],
        'quiet': True,
        'no_warnings': True,
    }
    if dl_type == "mp3":
        opts = {
            **common,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:
        selected = quality_var.get()
        height = ''.join(filter(str.isdigit, selected)) or "720"
        opts = {
            **common,
            'format': f'bestvideo[vcodec^=avc][ext=mp4][height<={height}]+bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/best',
            'merge_output_format': 'mp4',
        }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        log(f"Downloaded successfully✅ {dl_type} with quality {q}")
        progress_label.configure(text=f"Done {q} ✅✓")
        bar.set(1)
    except Exception as e:
        if "Cancelled" in str(e) or cancel_flag:
            log("Download cancelled")
            progress_label.configure(text="Download cancelled🚫❌")
            bar.set(0)
        else:
            log(f"Error: {e}")
            progress_label.configure(text="Error occurred💢")
    finally:
        is_downloading = False

def cancel_download():
    global cancel_flag, is_downloading
    cancel_flag = True
    is_downloading = False
    log("Cancelling - will stop in a second")

# ==================== Bottom Frame (Download & Cancel Buttons) ====================
bottom_frame = ctk.CTkFrame(app, fg_color="transparent")
bottom_frame.pack(pady=3, fill="x")
bottom_frame.configure(height=100)
bottom_frame.pack_propagate(False)

download_btn = ctk.CTkButton(bottom_frame, text="Download ⤵️", command=lambda: threading.Thread(target=download, daemon=True).start(), width=520, height=28, fg_color="#67CC01", hover_color="#cc0029", font=("Arial", 16, "bold"))
download_btn.place(x=15, y=0)

cancel_btn = ctk.CTkButton(bottom_frame, text="Cancel ❌", command=cancel_download, width=520, height=28, fg_color="#555555", hover_color="#333333", font=("Arial", 16, "bold"))
cancel_btn.place(x=15, y=32)

app.mainloop()