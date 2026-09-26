#!/usr/bin/env python3
"""Herd.kill_zombie tallies numeric replies, tolerates string/int replies, drains active."""
import sys, threading
from core.herd import Herd

h = object.__new__(Herd)  # skip __init__ (avoids UFONet dependency)
h.lock = threading.Lock()
h.result = {}; h.connection = {}; h.done = []; h.stats = {}
h.total_hits = 0; h.total_fails = 0; h.total_connection_fails = 0
h.total_time = 0; h.total_size = 0

def prep(z):
    h.active = [z]; h.stats.setdefault(z, [])

err = []
prep("z1"); h.kill_zombie("z1", [200, 0.5, 1234], False)   # attack-mode hit
prep("z2"); h.kill_zombie("z2", [404, 0.3, 50], False)     # attack-mode fail
prep("z3"); h.kill_zombie("z3", "<html>reply</html>", True)  # HEAD/external -> str
prep("z4"); h.kill_zombie("z4", 0, False)                    # empty reply -> int

if h.total_hits != 1: err.append(f"hits {h.total_hits} != 1")
if h.total_fails != 3: err.append(f"fails {h.total_fails} != 3")
if h.total_connection_fails != 1: err.append(f"conn_fails {h.total_connection_fails} != 1")
if abs(h.total_time - 0.8) > 1e-9: err.append(f"time {h.total_time} != 0.8")
if h.total_size != 1284: err.append(f"size {h.total_size} != 1284")
if h.active: err.append(f"active not drained: {h.active}")
if sorted(h.done) != ["z1", "z2", "z3", "z4"]: err.append(f"done wrong: {h.done}")
if h.stats.get("z3"): err.append("non-numeric reply must not be stored in stats")
if h.stats.get("z1") != [[200, 0.5, 1234]]: err.append(f"numeric stat not stored: {h.stats.get('z1')}")

print(f"kill_zombie checks: {'OK' if not err else 'FAILED'}")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
