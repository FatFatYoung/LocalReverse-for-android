#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Proxy V18.4 - Refresh IP Restored & Settings
- Version 1.18.4
- Restored Refresh IP button.
- Save/Load Settings functionality.
- Icon support.
"""
import os
import sys
import subprocess
import shutil
import zipfile
import glob

print("Building PROXY V18.4...")

jdk_bin = r"C:\Program Files\Eclipse Adoptium\jdk-25.0.3.9-hotspot\bin"
sdk_path = r"C:\Users\Administrator\AppData\Local\Android\Sdk"
build_tools = os.path.join(sdk_path, "build-tools", "36.1.0")
android_jar = os.path.join(sdk_path, "platforms", "android-36.1", "android.jar")

env = os.environ.copy()
env['PATH'] = f"{jdk_bin};{build_tools};" + env['PATH']

work_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxy_build_v184")
if os.path.exists(work_dir):
    shutil.rmtree(work_dir)
os.makedirs(work_dir)
os.chdir(work_dir)

# Copy icon
icon_src = r"C:\Users\Administrator\Desktop\LocalReverse.png"
res_dir = "res/mipmap"
os.makedirs(res_dir)
shutil.copy(icon_src, os.path.join(res_dir, "icon.png"))

# 1. Manifest
with open("AndroidManifest.xml", "w") as f:
    f.write("""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.localreverse.app" android:versionCode="25" android:versionName="1.18.4">
    <uses-sdk android:minSdkVersion="21" android:targetSdkVersion="33" />
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
    <application android:label="LocalReverse" android:icon="@mipmap/icon" android:debuggable="true" android:usesCleartextTraffic="true">
        <activity android:name="MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>""")

# 2. Java
src_dir = "src/com/localreverse/app"
os.makedirs(src_dir)

with open(os.path.join(src_dir, "MainActivity.java"), "w", encoding="utf-8") as f:
    f.write("""package com.localreverse.app;
import android.app.Activity; import android.os.Bundle; import android.webkit.WebView; import android.webkit.WebSettings; import android.webkit.JavascriptInterface;
import java.net.*; import java.io.*;
import java.util.Enumeration;
import android.content.Intent; import android.net.Uri;
import android.content.SharedPreferences;

public class MainActivity extends Activity {
    ProxyEngine engine;
    WebView wv;
    String currentIp = "";
    int currentPort = 9999;

    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        System.setProperty("java.net.preferIPv4Stack", "true");
        
        engine = new ProxyEngine();
        
        wv = new WebView(this);
        wv.setLayoutParams(new android.widget.LinearLayout.LayoutParams(
            android.widget.LinearLayout.LayoutParams.MATCH_PARENT, 
            android.widget.LinearLayout.LayoutParams.MATCH_PARENT));
        WebSettings ws = wv.getSettings();
        ws.setJavaScriptEnabled(true);
        ws.setDomStorageEnabled(true);
        wv.addJavascriptInterface(engine, "AndroidProxy");
        setContentView(wv);
        wv.loadUrl("file:///android_asset/index.html");
    }

    private String getLocalIpAddress() {
        try {
            for (Enumeration<NetworkInterface> en = NetworkInterface.getNetworkInterfaces(); en.hasMoreElements();) {
                NetworkInterface intf = en.nextElement();
                for (Enumeration<InetAddress> enumIpAddr = intf.getInetAddresses(); enumIpAddr.hasMoreElements();) {
                    InetAddress inetAddress = enumIpAddr.nextElement();
                    if (!inetAddress.isLoopbackAddress() && inetAddress.getHostAddress().contains(".")) {
                        return inetAddress.getHostAddress();
                    }
                }
            }
        } catch (Exception e) {}
        return "";
    }
    
    public void openInBrowser() {
        Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse("http://" + currentIp + ":" + currentPort));
        startActivity(intent);
    }

    public class ProxyEngine {
        ServerSocket server;
        boolean running = false;
        String TARGET_URL = "";

        @JavascriptInterface
        public void start(String localHost, int localPort, String proxyUrl) {
            try {
                running = true;
                TARGET_URL = proxyUrl.replaceAll("/+$", "");
                currentPort = localPort;
                
                String ip = getLocalIpAddress();
                currentIp = ip;
                if (!ip.isEmpty()) updateIp(ip);

                addLog("Target: " + TARGET_URL);
                addLog("Listening on: " + localHost + ":" + localPort);
                if (!ip.isEmpty()) addLog("IP: " + ip);

                server = new ServerSocket(localPort, 50, InetAddress.getByName(localHost));
                
                new Thread(() -> {
                    while (running && server != null) {
                        try {
                            Socket client = server.accept();
                            new Thread(() -> handleClient(client)).start();
                        } catch (Exception e) { 
                            if (running) addLog("Accept Error: " + e.getMessage()); 
                        }
                    }
                }).start();
            } catch (Exception e) { 
                addLog("Start Failed: " + e.getMessage()); 
            }
        }

        private void handleClient(Socket client) {
            try {
                BufferedReader in = new BufferedReader(new InputStreamReader(client.getInputStream()));
                String requestLine = in.readLine(); 
                if (requestLine == null) { client.close(); return; }

                String[] parts = requestLine.split(" ");
                if (parts.length < 2) { client.close(); return; }
                String path = parts[1];
                String method = parts[0];

                java.util.Map clientHeaders = new java.util.HashMap();
                String line;
                while ((line = in.readLine()) != null && !line.isEmpty()) {
                    int idx = line.indexOf(":");
                    if (idx > 0) {
                        String key = line.substring(0, idx).trim();
                        String val = line.substring(idx + 1).trim();
                        clientHeaders.put(key, val);
                    }
                }

                String fullUrl = TARGET_URL + path;
                
                URL url = new URL(fullUrl);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod(method);
                conn.setInstanceFollowRedirects(true);
                conn.setConnectTimeout(10000);
                conn.setReadTimeout(10000);

                for (Object o : clientHeaders.entrySet()) {
                    java.util.Map.Entry entry = (java.util.Map.Entry) o;
                    String key = (String) entry.getKey();
                    String val = (String) entry.getValue();
                    if (!key.equalsIgnoreCase("Host") && !key.equalsIgnoreCase("Content-Length")) {
                        conn.setRequestProperty(key, val);
                    }
                }
                if (!clientHeaders.containsKey("User-Agent")) {
                     conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36");
                }

                OutputStream out = client.getOutputStream();
                int code = conn.getResponseCode();
                
                out.write(("HTTP/1.1 " + code + " " + conn.getResponseMessage() + "\\r\\n").getBytes());
                
                for (int i = 0; ; i++) {
                    String headerName = conn.getHeaderFieldKey(i);
                    if (headerName == null) break;
                    String headerValue = conn.getHeaderField(i);
                    if (headerValue != null) {
                        out.write((headerName + ": " + headerValue + "\\r\\n").getBytes());
                    }
                }
                out.write("Connection: close\\r\\n".getBytes());
                out.write("\\r\\n".getBytes());

                InputStream bodyIn = (code >= 400) ? conn.getErrorStream() : conn.getInputStream();
                if (bodyIn != null) {
                    byte[] buf = new byte[8192];
                    int len;
                    while ((len = bodyIn.read(buf)) != -1) {
                        out.write(buf, 0, len);
                    }
                }
                
                out.flush();
                client.close();
                conn.disconnect();

            } catch (Exception e) {
                try {
                    addLog("Error: " + e.getMessage());
                    OutputStream out = client.getOutputStream();
                    String errHtml = "<html><body><h2>Proxy Error</h2><p>" + e.getMessage() + "</p></body></html>";
                    out.write(("HTTP/1.1 500 Error\\r\\nContent-Type: text/html; charset=utf-8\\r\\nContent-Length: " + errHtml.getBytes().length + "\\r\\n\\r\\n" + errHtml).getBytes());
                    client.close();
                } catch (Exception ex) {}
            }
        }

        @JavascriptInterface
        public void stop() {
            running = false;
            try { 
                if (server != null) server.close(); 
                addLog("Stopped"); 
            } catch (Exception e) { 
                addLog("Stop Error"); 
            }
        }

        @JavascriptInterface
        public void addLog(String msg) {
            wv.post(() -> {
                wv.evaluateJavascript("window.addLog('" + msg.replace("'", "\\'") + "');", null);
            });
        }
        
        @JavascriptInterface
        public void updateIp(String ip) {
            currentIp = ip;
            wv.post(() -> {
                wv.evaluateJavascript("window.updateIp('" + ip + "');", null);
            });
        }

        @JavascriptInterface
        public String getIp() {
            return getLocalIpAddress();
        }

        @JavascriptInterface
        public void openInBrowser() {
            MainActivity.this.openInBrowser();
        }

        @JavascriptInterface
        public void saveSettings(String port, String url) {
            SharedPreferences prefs = getSharedPreferences("LocalReversePrefs", MODE_PRIVATE);
            prefs.edit().putString("port", port).putString("url", url).apply();
            addLog("Settings Saved");
        }

        @JavascriptInterface
        public String getSavedSettings() {
            SharedPreferences prefs = getSharedPreferences("LocalReversePrefs", MODE_PRIVATE);
            String port = prefs.getString("port", "9999");
            String url = prefs.getString("url", "https://github.com/FatFatYoung");
            return "{\\\"port\\\":\\\"" + port + "\\\",\\\"url\\\":\\\"" + url + "\\\"}";
        }
    }
}""")

# 3. HTML
os.makedirs("assets")
with open(os.path.join("assets", "index.html"), "w", encoding="utf-8") as f:
    f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LocalReverse</title>
    <style>
        body { font-family: sans-serif; padding: 20px; background: #f0f2f5; }
        .container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        input { width: 100%; padding: 10px; margin: 5px 0 15px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 5px; }
        button { width: 100%; padding: 15px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; margin-bottom: 10px; color: white; }
        #btn { background: #007bff; }
        #btn.stop { background: #dc3545; }
        .row { display: flex; gap: 10px; margin-bottom: 10px; }
        .row button { flex: 1; margin-bottom: 0; padding: 12px; }
        #btnSave { background: #fd7e14; }
        #btnLoad { background: #17a2b8; }
        #btnRefresh { background: #6c757d; }
        #btnOpen { background: #28a745; }
        #log { margin-top: 20px; padding: 10px; background: #333; color: #0f0; font-family: monospace; min-height: 100px; max-height: 200px; overflow-y: auto; border-radius: 5px; }
        .ip-box { background: #e7f3ff; padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center; font-weight: bold; color: #0056b3; display: none; }
        label { font-weight: bold; margin-top: 5px; display: block; }
    </style>
</head>
<body>
    <div class="container">
        <h2 style="text-align:center">LocalReverse 1.18.4</h2>
        
        <div class="ip-box" id="ipDisplay"></div>
        
        <label>Local Port</label>
        <input id="lPort" value="9999">
        
        <label>Proxy URL</label>
        <input id="proxyUrl" value="https://github.com/FatFatYoung">
        
        <div class="row">
            <button id="btnSave" onclick="saveSettings()">Save</button>
            <button id="btnLoad" onclick="loadSettings()">Load</button>
        </div>
        <div class="row">
            <button id="btnRefresh" onclick="refreshIp()">Refresh IP</button>
        </div>

        <button id="btn" onclick="toggle()">Start</button>
        <button id="btnOpen" class="open" style="display:none;" onclick="openBrowser()">Open in Browser</button>
        
        <div id="log">Waiting...</div>
    </div>
    <script>
        let isRunning = false;
        
        window.onload = function() {
            try {
                let saved = AndroidProxy.getSavedSettings();
                let data = JSON.parse(saved);
                if(data.port) document.getElementById('lPort').value = data.port;
                if(data.url) document.getElementById('proxyUrl').value = data.url;
                addLog("Settings loaded.");
            } catch(e) {}
        };

        function toggle() {
            if (isRunning) {
                AndroidProxy.stop();
                document.getElementById('btn').textContent = "Start";
                document.getElementById('btn').classList.remove('stop');
                document.getElementById('btnOpen').style.display = 'none';
                document.getElementById('ipDisplay').style.display = 'none';
                isRunning = false;
            } else {
                let lp = parseInt(document.getElementById('lPort').value);
                let url = document.getElementById('proxyUrl').value;
                
                AndroidProxy.start("0.0.0.0", lp, url);
                document.getElementById('btn').textContent = "Stop";
                document.getElementById('btn').classList.add('stop');
                document.getElementById('btnOpen').style.display = 'block';
                document.getElementById('ipDisplay').style.display = 'block';
                isRunning = true;
            }
        }
        
        window.saveSettings = function() {
            let p = document.getElementById('lPort').value;
            let u = document.getElementById('proxyUrl').value;
            AndroidProxy.saveSettings(p, u);
        }

        window.loadSettings = function() {
            try {
                let saved = AndroidProxy.getSavedSettings();
                let data = JSON.parse(saved);
                if(data.port) document.getElementById('lPort').value = data.port;
                if(data.url) document.getElementById('proxyUrl').value = data.url;
                addLog("Settings restored.");
            } catch(e) {}
        }

        window.refreshIp = function() {
            let ip = AndroidProxy.getIp();
            if (ip) {
                updateIp(ip);
                addLog("IP refreshed: " + ip);
            } else {
                addLog("Failed to get IP");
            }
        }

        window.updateIp = function(ip) {
            document.getElementById('ipDisplay').textContent = "IP: " + ip;
        }
        window.openBrowser = function() {
            AndroidProxy.openInBrowser();
        }
        window.addLog = function(msg) {
            let d = document.getElementById('log');
            d.innerHTML += new Date().toLocaleTimeString() + " " + msg + "<br>";
            d.scrollTop = d.scrollHeight;
        }
    </script>
</body>
</html>""")

# 4. Build - Compile resources and link
os.makedirs("compiled-res", exist_ok=True)
subprocess.run(f'aapt2 compile --dir res/ -o compiled-res/', shell=True, env=env, check=True)
subprocess.run(f'aapt2 link -o resources.ap_ --manifest AndroidManifest.xml -I "{android_jar}" -R compiled-res/mipmap_icon.png.flat', shell=True, env=env, check=True)

java_files = glob.glob("src/com/localreverse/app/*.java")
java_files_str = " ".join([f'"{f}"' for f in java_files])
subprocess.run(f'javac -encoding UTF-8 -classpath "{android_jar}" -d out {java_files_str}', shell=True, env=env, check=True)

class_files = glob.glob("out/com/localreverse/app/*.class")
class_args = " ".join([f'"{f}"' for f in class_files])
subprocess.run(f'd8.bat --lib "{android_jar}" --output . {class_args}', shell=True, env=env, check=True)

# 5. Package
final_apk = "LocalReverse_Proxy_1.18.4.apk"
with zipfile.ZipFile(final_apk, 'w') as apk:
    with zipfile.ZipFile('resources.ap_', 'r') as res_zip:
        for item in res_zip.infolist():
            apk.writestr(item.filename, res_zip.read(item.filename))
    apk.write('classes.dex')
    for root, dirs, files in os.walk('assets'):
        for file in files:
            apk.write(os.path.join(root, file), 'assets/' + file)

# 6. Sign
keystore = "debug.keystore"
if not os.path.exists(keystore):
    subprocess.run(f'keytool -genkey -v -keystore {keystore} -alias mykey -keyalg RSA -keysize 2048 -validity 10000 -storepass android -keypass android -dname "CN=ProxyV184, OU=Dev, O=Local, L=City, S=State, C=CN"', shell=True, env=env, check=True)
subprocess.run(f'apksigner sign --ks {keystore} --ks-pass pass:android --out app_signed.apk {final_apk}', shell=True, env=env, check=True)
shutil.copy("app_signed.apk", final_apk)
shutil.copy(final_apk, os.path.join(os.path.dirname(os.path.abspath(__file__)), "LocalReverse_Proxy_1.18.4.apk"))
print("Done! Proxy V18.4 APK created.")
