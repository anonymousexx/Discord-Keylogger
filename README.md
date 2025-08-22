# Discord Keylogger

A sophisticated Python keylogger that captures keystrokes and delivers them to Discord via webhook embeds with comprehensive system information.

![Python](https://img.shields.io/badge/Python-3.6%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
## ⚠️ Legal Disclaimer

**This software is intended for educational purposes and authorized security testing only.**

> **WARNING:** Unauthorized use of this software may violate:
> - Computer Fraud and Abuse Act (CFAA)
> - General Data Protection Regulation (GDPR) 
> - Various state and international privacy laws
> - Terms of service agreements
>
> **Use only on systems you own or have explicit written permission to monitor.**
> The developers assume no liability for misuse of this software.

## 📋 Features

- **Real-time Keystroke Capture**: Logs all keyboard input with special key formatting
- **Discord Webhook Integration**: Sends data via embedded messages
- **System Intelligence**: Collects IP address, hostname, and OS information
- **Stealth Operation**: Runs in background without console visibility
- **Adaptive Transmission**: Sends data at 50-key thresholds or 30-second intervals
- **Session Analytics**: Tracks runtime duration and operational status
- **Error Handling**: Robust network and execution fault tolerance

## 🛠 Installation

### Prerequisites
- Python 3.6+
- pip package manager
- Discord webhook URL

### Install Dependencies
```bash
pip install keyboard requests
pip install pywin32
