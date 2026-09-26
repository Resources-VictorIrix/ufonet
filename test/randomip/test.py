#!/usr/bin/env python3
"""RandomIP._generateip returns only valid, public IPv4 (no private/reserved/loopback)."""
import sys, ipaddress
from core.randomip import RandomIP

r = RandomIP()
err = []
N = 20000
for _ in range(N):
    ip = r._generateip('')
    try:
        a = ipaddress.IPv4Address(ip)
    except Exception as e:
        err.append(f"invalid IP {ip!r}: {e}")
        continue
    if (not a.is_global) or a.is_private or a.is_multicast or a.is_loopback or a.is_reserved or a.is_link_local:
        err.append(f"non-public IP generated: {ip}")

print(f"generated {N} IPs, invalid/non-public: {len(err)}")
for e in err[:10]:
    print("FAIL:", e)
sys.exit(0 if not err else 1)
