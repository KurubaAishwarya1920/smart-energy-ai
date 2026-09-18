#!/usr/bin/env python3
"""Start Smart Energy AI.

    python run.py            -> http://127.0.0.1:5000
    PORT=8080 python run.py  -> http://127.0.0.1:8080

If the chosen port is already taken (macOS AirPlay holds 5000 by default), the
next free port is used automatically and printed below.
"""

import os
import socket
import sys
import webbrowser
from threading import Timer

MIN_PYTHON = (3, 9)
if sys.version_info < MIN_PYTHON:
    sys.exit("Smart Energy AI needs Python %d.%d or newer. You are running %s."
             % (MIN_PYTHON[0], MIN_PYTHON[1], sys.version.split()[0]))

try:
    from backend.app import create_app
except ModuleNotFoundError as err:
    if "flask" in str(err).lower():
        sys.exit("Flask is not installed in this Python.\n"
                 "Run:  pip install -r requirements.txt\n"
                 "(or use ./run.sh on macOS/Linux, run.bat on Windows)")
    sys.exit("Could not import the app: %s\n"
             "Run this from the project folder, the one containing run.py." % err)


def free_port(preferred, host="127.0.0.1", tries=20):
    """Return the first port that will actually accept a bind."""
    for offset in range(tries):
        candidate = preferred + offset
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                probe.bind((host, candidate))
                return candidate, offset > 0
            except OSError:
                continue
    sys.exit("No free port found between %d and %d." % (preferred, preferred + tries))


app = create_app()

if __name__ == "__main__":
    wanted = int(os.environ.get("PORT", 5000))
    port, moved = free_port(wanted)
    url = "http://127.0.0.1:%d" % port

    print("\n  Smart Energy AI")
    if moved:
        print("  Port %d was busy, so this is running on %d instead." % (wanted, port))
    print("  Open this in your browser:  %s" % url)
    print("  API health check:           %s/api/health" % url)
    print("  Mode:                       demo data, no API key required")
    print("  Stop the server:            press Ctrl+C\n")

    if os.environ.get("OPEN_BROWSER", "1") == "1":
        Timer(1.2, lambda: webbrowser.open(url)).start()

    try:
        app.run(host="127.0.0.1", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
    except KeyboardInterrupt:
        print("\n  Stopped.\n")
