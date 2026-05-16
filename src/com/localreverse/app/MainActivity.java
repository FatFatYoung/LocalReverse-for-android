package com.localreverse.app;
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
                
                out.write(("HTTP/1.1 " + code + " " + conn.getResponseMessage() + "\r\n").getBytes());
                
                for (int i = 0; ; i++) {
                    String headerName = conn.getHeaderFieldKey(i);
                    if (headerName == null) break;
                    String headerValue = conn.getHeaderField(i);
                    if (headerValue != null) {
                        out.write((headerName + ": " + headerValue + "\r\n").getBytes());
                    }
                }
                out.write("Connection: close\r\n".getBytes());
                out.write("\r\n".getBytes());

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
                    out.write(("HTTP/1.1 500 Error\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: " + errHtml.getBytes().length + "\r\n\r\n" + errHtml).getBytes());
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
}
