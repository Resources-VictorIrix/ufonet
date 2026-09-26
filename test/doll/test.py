#!/usr/bin/env python3
"""doll.Needle handles requests over a real socket and always sends bytes (Python 3 fix)."""
import sys, socket, os, tempfile, shutil
from core.doll import Needle

class StubParent:
    def __init__(self):
        self.arrived = []
    def data_arrived(self, data):
        self.arrived.append(data)
    def client_finished(self, t):
        pass

err = []

def handle(request_bytes, cwd=None):
    a, b = socket.socketpair()
    a.settimeout(3); b.settimeout(3)
    b.sendall(request_bytes)
    parent = StubParent()
    n = Needle(a, ("127.0.0.1", 0), parent)
    old = os.getcwd()
    if cwd:
        os.chdir(cwd)
    try:
        n.run()
    finally:
        if cwd:
            os.chdir(old)
    chunks = b""
    try:
        while True:
            d = b.recv(4096)
            if not d:
                break
            chunks += d
    except socket.timeout:
        pass
    a.close(); b.close()
    return chunks, parent

# HEAD -> HTTP 200 response as bytes
resp, parent = handle(b"HEAD / HTTP/1.1\r\nHost: x\r\n\r\n")
if not isinstance(resp, (bytes, bytearray)):
    err.append("HEAD response is not bytes")
if not resp.startswith(b"HTTP/1.1 200 OK"):
    err.append(f"HEAD response missing status line: {resp[:40]!r}")
if not parent.arrived:
    err.append("data_arrived not called for HEAD")

# non-HEAD with no 'mothership' file -> welcome banner + FileNotFoundError branch
tmp = tempfile.mkdtemp(prefix="ufonet_doll_")
resp2, _ = handle(b"GET / HTTP/1.1\r\nHost: x\r\n\r\n", cwd=tmp)
shutil.rmtree(tmp, ignore_errors=True)
if b"Welcome to UFONet mothership" not in resp2:
    err.append(f"welcome banner missing/garbled: {resp2[:60]!r}")
if b"Mothership stream not found." not in resp2:
    err.append("FileNotFoundError branch did not run for missing mothership")

print(f"doll Needle socket I/O: {'OK' if not err else 'FAILED'}")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
