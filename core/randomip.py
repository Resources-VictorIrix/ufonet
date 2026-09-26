#!/usr/bin/env python3 
# -*- coding: utf-8 -*-"
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2026 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import secrets
import ipaddress

class RandomIP(object):
    """
    Class to generate random valid IP's
    """
    def _generateip(self, string=""):
        while True:
            first = secrets.randbelow(255) + 1
            second = secrets.randbelow(256)
            third = secrets.randbelow(256)
            fourth = secrets.randbelow(256)
            _ip = ".".join([str(first), str(second), str(third), str(fourth)])
            try:
                addr = ipaddress.IPv4Address(_ip)
            except ValueError:
                continue
            if not addr.is_global:
                continue
            if addr.is_multicast or addr.is_reserved or addr.is_unspecified:
                continue
            if addr.is_loopback or addr.is_private or addr.is_link_local:
                continue
            return _ip
