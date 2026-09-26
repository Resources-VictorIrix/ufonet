#!/usr/bin/env python3
"""nuke.nukeize guards Unix-only calls: no iptables/epoll on non-Linux, no crash; module imports without top-level 'resource'."""
import sys, types, inspect
from core.mods import nuke

err = []
calls = []

class FakeSock:
    def fileno(self):
        return 3

orig_system = nuke.os.system
orig_connect = nuke.connect
orig_sys = nuke.sys

nuke.os.system = lambda cmd: calls.append(cmd)
nuke.connect = lambda ip, port: FakeSock()
nuke.sys = types.SimpleNamespace(platform="win32")  # simulate Windows
try:
    nuke.nukeize("203.0.113.5", 80, 3)  # must not call iptables, must not crash
    if any("iptables" in c for c in calls):
        err.append(f"iptables invoked on non-Linux: {calls}")
except Exception as e:
    err.append(f"nukeize crashed on non-Linux: {type(e).__name__}: {e}")
finally:
    nuke.os.system = orig_system
    nuke.connect = orig_connect
    nuke.sys = orig_sys

if "import socket, select, os, time, resource" in inspect.getsource(nuke):
    err.append("'resource' still imported at module top (breaks Windows import)")

print(f"nuke platform-guard: {'OK' if not err else 'FAILED'}; iptables calls on win32: {sum('iptables' in c for c in calls)}")
for e in err:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
