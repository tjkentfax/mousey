# Mousey

Turn your iPhone into a wireless mouse for Linux and Windows over local Wi-Fi.

## iPhone website
The root of this repo is now an iPhone-optimized web app. It works in Safari and can be added to the Home Screen.

The web app provides:
- Motion-controlled pointer movement using iPhone motion sensors.
- Left half = left click.
- Right half = right click.
- Hold either button = drag.
- Two-finger gesture = scroll.
- Sensitivity and Y-axis controls.
- 6-digit pairing PIN.

### Important
For iPhone motion sensors, Safari requires the page to be served from a secure context (HTTPS). The website can be hosted on Vercel/GitHub Pages, but the PC receiver must also be reachable in a way Safari permits from that page. For a simple local setup, serve the web app from an HTTPS-capable local server or use the native iOS app in `ios/`.

## Desktop receiver
Python 3.10+ is recommended.

```bash
cd desktop
python -m pip install -r requirements.txt
python mousey_server.py
```

The receiver prints its LAN address and a 6-digit pairing PIN. Enter both in the iPhone website.

On Linux, `pynput` uses the available desktop input backend. Wayland may restrict synthetic pointer input; X11 is the most compatible configuration.

On Windows, `pynput` uses the Windows input APIs.

## Native iOS app
The SwiftUI version remains in `ios/Mousey/` and uses Core Motion directly.

## Web files
- `index.html` — iPhone UI
- `styles.css` — responsive dark UI
- `app.js` — motion, touch, click, drag and scroll controls
- `manifest.webmanifest` — Home Screen/PWA metadata
