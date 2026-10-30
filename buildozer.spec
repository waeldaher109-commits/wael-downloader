[app]
title = Wael Downloader
package.name = waeldownloader
package.domain = org.wael.downloader
source.dir = .
source.include_exts = py,png,jpg,kv
version = 1.0
requirements = python3,kivy==2.3.0,yt_dlp,pillow
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.accept_sdk_license_agreements = True
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
