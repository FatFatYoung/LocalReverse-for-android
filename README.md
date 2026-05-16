# LocalReverse

**LocalReverse** is a lightweight, zero-dependency Android HTTP proxy application. It allows you to proxy traffic from any device on your local network to a specified target URL.

## Features

-   **HTTP Content Proxy**: Reverse proxies requests to a target website.
-   **Zero Dependencies**: No Gradle, no Android Studio required. Built using raw Android SDK tools.
-   **Header Forwarding**: Automatically forwards client headers (User-Agent, etc.) to bypass modern bot detection.
-   **Auto Redirect**: Follows 301/302 redirects automatically.
-   **IPv4 Fix**: Optimized for stable local network connections.
-   **Settings Persistence**: Save and load your favorite proxy configurations.
-   **One-Click Browser**: Opens the proxy link in the system browser instantly.
-   **Custom Icon**: Includes the original project icon.

## Project Structure

```text
LocalReverse/
├── AndroidManifest.xml       # Android App Manifest
├── build.py                  # Python build script (compiles APK from source)
├── src/                      # Java Source Code
│   └── com/localreverse/app/
│       └── MainActivity.java
├── assets/                   # App Assets
│   └── index.html            # Web UI Interface
├── res/                      # Resources (Icon)
│   └── mipmap/
│       └── icon.png
└── release/                  # Compiled APK
    └── LocalReverse_Proxy_1.18.4.apk
```

## Requirements

To build this project locally, you need:
-   **JDK 25** (or compatible version)
-   **Android SDK** (with `build-tools`, `platforms/android-36`)
-   **Python 3**

## Build Instructions

1.  Ensure your environment paths are correctly set in `build.py`.
2.  Run the build script:
    ```bash
    python build.py
    ```
3.  The signed APK will be generated in the current directory.

## Installation

1.  Download the APK from the `release/` folder.
2.  Transfer it to your Android device.
3.  Install the APK (enable "Install from Unknown Sources" if prompted).
4.  Open the app, configure your target URL, and hit **Start**.

## Usage

1.  **Start**: Set the port (default 9999) and Target URL. Click Start.
2.  **Connect**: On any device in the same WiFi network, open a browser and go to `http://[Your-Phone-IP]:9999`.
3.  **Save/Load**: Click "Save" to store settings locally. Click "Load" to restore them.
4.  **Open in Browser**: Click the button inside the app to open the proxy page immediately in your system browser.

## License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for more information.

Copyright (c) 2026 FatFatYoung

## Acknowledgments

-   **Platform**: Android SDK (Android Open Source Project).
-   **Icon**: Created by FatFatYoung.
-   **No Third-Party Dependencies**: This project relies solely on standard Java and Android APIs.

---

*Copyright © 2026 FatFatYoung*
