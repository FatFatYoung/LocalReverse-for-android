# LocalReverse for Android

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Platform: Android](https://img.shields.io/badge/Platform-Android-green.svg)
![Build: No Gradle](https://img.shields.io/badge/Build-Shell%20%2B%20SDK-blue.svg)

**LocalReverse** is a lightweight, zero-dependency **HTTP Reverse Proxy** application designed for Android.

Unlike standard proxy tools, LocalReverse turns your Android phone into a dedicated proxy node. By configuring a target URL, it allows other devices on the same network (PCs, tablets, other phones) to access that target site through your phone's IP and port.

## 🌟 Why Use This?

-   **Mobile VPN Access**: Connect your phone to a VPN, then let your PC access intranet resources via the phone.
-   **Bypass IP Restrictions**: Some sites restrict access by IP. Access them via a phone on a different network.
-   **Zero-Config Proxy**: No need to install Termux or configure complex tools. Just install the APK and Start.
-   **Educational Value**: A perfect example of how to build a functional Android app using **pure Android SDK** (No Gradle, No Android Studio).

## ✨ Key Features

-   **🔀 Reverse Proxy Logic**: Seamlessly stitches client request paths to the target URL.
-   **🚀 Header Forwarding**: Automatically relays client headers (User-Agent, Cookies, etc.) to bypass modern bot detection and CAPTCHAs.
-   **🔄 Auto Redirect**: Natively handles 301/302 redirects so you don't get stuck.
-   **📱 Pure Java + WebView**: Built with raw Java and Android SDK. No third-party libraries.
-   **⚡ Zero Dependencies**: No Gradle, No Maven, No Android Studio required.
-   **💾 Persistence**: Remembers your settings (Port, Target URL) across reboots.
-   **🔗 One-Click Browser**: Instantly opens the proxy address in your system browser.
-   **📶 Network Optimized**: Forced IPv4 stack ensures stable connections from various devices.

## ⚠️ Security Notice

> **Use on Trusted Networks Only.**
>
> 1.  **No Authentication**: The proxy does not require a password. Anyone on your LAN who knows your IP and Port can use it.
> 2.  **HTTP Plaintext**: Traffic between the client and your phone is unencrypted.
> 3.  **SSRF Risk**: As a reverse proxy, it can technically access internal services if configured to. Do not expose this app to the public internet.

## 📂 Project Structure

```text
LocalReverse/
├── AndroidManifest.xml       # App Manifest (Permissions, Activity)
├── build.py                  # Python build script (Raw SDK toolchain)
├── src/                      # Core Java Source
│   └── com/localreverse/app/
│       └── MainActivity.java # UI & Proxy Engine
├── assets/                   # Web UI
│   └── index.html            # Interface (HTML/JS)
├── res/                      # Resources
│   └── mipmap/
│       └── icon.png          # App Icon
└── release/                  # Pre-built APK
    └── LocalReverse_Proxy_1.18.4.apk
```

## 🛠️ Build Instructions

This project uses a **raw Android SDK toolchain** (`aapt2`, `javac`, `d8`, `apksigner`) instead of Gradle.

### Requirements

-   **JDK 25** (or compatible)
-   **Android SDK**: `build-tools` (36.1.0), `platforms/android-36`
-   **Python 3**

### Steps

1.  **Configure Paths**: Edit `build.py` if your SDK/JDK paths differ.
2.  **Run Build**:
    ```bash
    python build.py
    ```
3.  **Output**: The signed APK will be generated in the current directory.

## 📱 Usage

1.  **Install**: Download the APK from the `release/` folder and install it on your Android device.
2.  **Configure**: Open the app, enter a **Port** (e.g., 9999) and a **Target URL** (e.g., `https://github.com`).
3.  **Start**: Tap **Start**. The app will show your local IP (e.g., `192.168.1.5`).
4.  **Connect**: On another device in the same WiFi, open a browser and visit `http://192.168.1.5:9999`.
5.  **Save**: Tap **Save** to remember your configuration for next time.

## 🚧 Roadmap

-   [ ] **Background Service**: Keep the proxy running when the app is minimized.
-   [ ] **Request Logging**: Add a simple log viewer to monitor traffic.
-   [ ] **HTTPS Support**: Option to run the local proxy over HTTPS.
-   [ ] **Access Control**: Simple token/password protection.

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.

Copyright (c) 2026 FatFatYoung

## 🤝 Acknowledgments

-   **Platform**: Android SDK (Android Open Source Project).
-   **Icon**: Designed by FatFatYoung.
-   **No AI Attribution**: This project is manually crafted and reviewed.

---
*Made with ❤️ and raw Java code.*