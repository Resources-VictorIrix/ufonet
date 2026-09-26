#!/usr/bin/env python3
"""ufoscan.scan: a None response counts as a closed port; a SYN-ACK counts as open (Python 3 fix)."""
import sys
from core.tools import ufoscan

err = []

class FakeSelf:
    pass

orig_sr1 = ufoscan.sr1
orig_sr = ufoscan.sr
try:
    # 1) resp is None -> closed increments, no open port
    ufoscan.sr1 = lambda *a, **k: None
    openp, closed = ufoscan.scan(FakeSelf(), "203.0.113.5", 80, [], 0)
    if closed != 1:
        err.append(f"None response: closed={closed}, expected 1")
    if openp:
        err.append(f"None response should not open a port: {openp}")

    # 2) SYN-ACK (flags 0x12) -> open port recorded
    class FakeTCP:
        flags = 0x12
    class FakeResp:
        def haslayer(self, layer):
            return True
        def getlayer(self, layer):
            return FakeTCP()
    ufoscan.sr1 = lambda *a, **k: FakeResp()
    ufoscan.sr = lambda *a, **k: None
    openp, closed = ufoscan.scan(FakeSelf(), "203.0.113.5", 80, [], 0)
    if 80 not in openp:
        err.append(f"SYN-ACK should open port 80: {openp}")
finally:
    ufoscan.sr1 = orig_sr1
    ufoscan.sr = orig_sr

print(f"ufoscan scan: {'OK' if not err else 'FAILED'}")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
