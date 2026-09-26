#!/usr/bin/env python3 
# -*- coding: utf-8 -*-"
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2026 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
################################################################### 
# Code extracted from project: AnonTwi (anontwi.03c8.net)
###################################################################

KEY_SIZE = 32
BLOCK_SIZE = 16
MAC_SIZE = 20

import base64
import hmac
from os import urandom
from hashlib import sha1, sha256
from Cryptodome.Cipher import AES

def hmac_sha1(key, msg):
    return hmac.new(key, msg, sha1).digest()

def derive_keys(key):
    h = sha256()
    h.update(key)
    h.update('cipher'.encode('utf-8'))
    cipher_key = h.digest()
    h = sha256()
    h.update(key)
    h.update('mac'.encode('utf-8'))
    mac_key = h.digest()
    return (cipher_key, mac_key)

def generate_key():
    return base64.b64encode(urandom(KEY_SIZE))

class Cipher(object):
    def __init__(self, key="", text=""):
        self.block_size = 16
        self.mac_size = 20
        self.key = self.set_key(key)
        self.text = self.set_text(text)
        self.mode = AES.MODE_CFB
  
    def set_key(self, key):
        try:
            key = base64.b64decode(key)
        except TypeError:
            raise ValueError
        self.key = key
        return self.key

    def set_text(self, text):
        self.text = text.encode("utf-8") 
        return self.text

    def encrypt(self):
        if BLOCK_SIZE + len(self.text) + MAC_SIZE > 105:
            self.text = self.text[:105 - BLOCK_SIZE - MAC_SIZE]
        (cipher_key, mac_key) = derive_keys(self.key)
        iv = urandom(BLOCK_SIZE)
        aes = AES.new(cipher_key, self.mode, iv)
        ciphertext = aes.encrypt(self.text)
        mac = hmac_sha1(mac_key, iv + ciphertext)
        return base64.b64encode(iv + ciphertext + mac)

    def decrypt(self):
        try:
            iv_ciphertext_mac = base64.b64decode(self.text)
        except:
            try:
                padding = len(self.text) % 4
                if padding == 1:
                    return ''
                elif padding == 2:
                    self.text += b'=='
                elif padding == 3:
                    self.text += b'='
                iv_ciphertext_mac = base64.b64decode(self.text)
            except TypeError:
                return None
        iv = iv_ciphertext_mac[:BLOCK_SIZE]
        ciphertext = iv_ciphertext_mac[BLOCK_SIZE:-MAC_SIZE]
        mac = iv_ciphertext_mac[-MAC_SIZE:]
        (cipher_key, mac_key) = derive_keys(self.key)
        expected_mac = hmac_sha1(mac_key, iv + ciphertext)
        if mac != expected_mac:
            return None
        aes = AES.new(cipher_key, self.mode, iv)
        return aes.decrypt(ciphertext)

if __name__ == "__main__":
    print("\nUFONet Crypter (AES256+HMAC-SHA1) -> (140 plain text chars = 69 encrypted chars)\n")
    text = str(input("-> Enter TEXT: "))
    input_key = str(input("\n-> Enter KEY: "))
    key = base64.b64encode(input_key.encode('utf-8'))
    c = Cipher(key, text)
    msg = c.encrypt()
    msg = msg.decode('utf-8')
    c.set_text(msg)
    print("\n" + "  " + '-'*44)
    print('\n-> Ciphertext: [', msg, ']')
    print('\n-> Length:', len(msg))
    print("\n" + "  " + '-'*44)
    print('\n-> Key (share it using SNEAKNET!):', input_key)
    print('\n-> Decryption PoC:', c.decrypt().decode('utf-8'), "\n")
