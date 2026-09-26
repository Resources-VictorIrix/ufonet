#!/usr/bin/env python3
"""GlobalNet crypto: a blob produced by Cipher.encrypt must decrypt through the inline decrypt in main.py and webgui.py (same HMAC + base64)."""
import sys, base64
from core.tools.crypter import Cipher
from core.main import UFONet
from core.webgui import Pages

err = []
app = UFONet()
passphrase = app.crypto_key                       # default "U-NATi0n!"
key = base64.b64encode(passphrase.encode("utf-8"))  # key convention used by --crypter

def norm(v):
    return v.decode("utf-8", "replace") if isinstance(v, bytes) else v

# main.py inline decrypt (the real GlobalNet decrypt path)
for ip in ["1.2.3.4", "203.0.113.55", "8.8.8.8"]:
    blob = Cipher(key, ip).encrypt().decode("utf-8")
    app.decryptedtext = ""
    app.decrypt(passphrase, blob)
    if norm(app.decryptedtext) != ip:
        err.append(f"main.py decrypt mismatch: {ip!r} -> {norm(app.decryptedtext)!r}")

# webgui.py inline decrypt (bind the edited method onto a bare instance)
stub = object.__new__(Pages)
dec = Pages.decrypt.__get__(stub)
for ip in ["1.2.3.4", "9.9.9.9"]:
    blob = Cipher(key, ip).encrypt().decode("utf-8")
    stub.decryptedtext = ""
    dec(passphrase, blob)
    if norm(stub.decryptedtext) != ip:
        err.append(f"webgui.py decrypt mismatch: {ip!r} -> {norm(stub.decryptedtext)!r}")

print(f"globalnet crypto cross-path: {'OK' if not err else 'FAILED'}")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
