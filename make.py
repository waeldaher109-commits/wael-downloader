from PIL import Image
import pyzipper
im = Image.open("icon.ico").convert("RGBA")
im.save("icon.ico", sizes=[(16,16),(20,20),(24,24),(32,32),(40,40),(48,48),(60,60),(64,64),(72,72),(96,96),(120,120),(128,128),(256,256),(384,384)])
print("Done")
import pyzipper
import os
exe_path = "WAEL_DOWNLOADER_Setup.exe"

if not os.path.exists(exe_path):
    print("EXE not found! Run pyinstaller first.")
else:
    with pyzipper.AESZipFile('WAEL_DOWNLOADER_Setup.zip', 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(b"wael1234567890")
        zf.write(exe_path, 'WAEL_DOWNLOADER_Setup.exe')
    print("Done! Created WAEL_DOWNLOADER.zip")

