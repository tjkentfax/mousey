# Mousey

Turn your iPhone into a wireless mouse for Linux and Windows over your local Wi-Fi network.

## What it does
- Tilt/move the iPhone to move the PC pointer.
- Tap the left half for left click.
- Tap the right half for right click.
- Long-press either side to drag.
- Two-finger vertical movement scrolls.
- Pair with a short PIN shown by the desktop receiver.

## Project layout
- `ios/Mousey/` — SwiftUI iPhone app using Core Motion.
- `desktop/` — Python receiver for Linux and Windows.

## Desktop setup
Python 3.10+ is recommended.

```bash
cd desktop
python -m pip install -r requirements.txt
python mousey_server.py
```

The receiver prints its LAN address and a 6-digit pairing PIN. Enter that address/PIN in the iPhone app.

On Linux, `pynput` uses the available desktop input backend. On Wayland, compositor security may prevent synthetic pointer input; running the desktop receiver under an X11 session is the most compatible option.

On Windows, `pynput` uses the Windows input APIs.

## iOS
Open `ios/Mousey.xcodeproj` in Xcode, select an iPhone target, and run. The app needs Motion permission; networking is local-network only.

For a production App Store build, set your development team/signing settings in Xcode.