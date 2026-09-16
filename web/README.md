# Mousey web client

Open `index.html` in Safari on iPhone, or deploy the `web/` directory as a static site.

The browser client connects to the Mousey desktop receiver over the local network. The receiver works on Windows and Linux.

For iPhone motion access, serve the page over HTTPS. If the desktop receiver is plain HTTP on a private LAN address, the browser may block the request because of mixed-content/security rules. For production use, put the receiver behind a secure WebSocket/HTTPS transport.
