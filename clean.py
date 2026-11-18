#!/usr/bin/env python3
"""Fetch dibdot DoH IP lists, strip comments, keep valid IPs only."""
import ipaddress, sys, urllib.request
BASE = "https://raw.githubusercontent.com/dibdot/DoH-IP-blocklists/master/"
MIN = 500
for ver, src, dst in ((4, "doh-ipv4.txt", "doh-ipv4.txt"),
                      (6, "doh-ipv6.txt", "doh-ipv6.txt")):
    raw = urllib.request.urlopen(BASE + src, timeout=60).read().decode()
    ips = set()
    for line in raw.splitlines():
        t = line.split("#", 1)[0].strip()
        if not t:
            continue
        try:
            n = ipaddress.ip_network(t, strict=False)
        except ValueError:
            continue
        if n.version != ver or n.is_private or n.is_loopback \
           or n.is_unspecified or n.is_multicast or n.is_link_local:
            continue
        ips.add(n)
    if len(ips) < MIN:
        sys.exit(f"STOP: only {len(ips)} IPv{ver} entries, keeping old file")
    out = sorted(ips, key=lambda n: (int(n.network_address), n.prefixlen))
    with open(dst, "w") as f:
        f.write("\n".join(str(n.network_address) if n.prefixlen ==
                          n.max_prefixlen else str(n) for n in out) + "\n")
    print(f"IPv{ver}: {len(out)} entries")
