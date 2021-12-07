import sys
import base64

# ======================================================================
# RC4 cryption
# ======================================================================

class rc4crypt(object):
    def __init__(self, key=''):
        self._key = key
        self._init_sbox()

    def _init_sbox(self):
        box = [x for x in range(256)]
        x = y = 0
        if len(self._key) > 0:
            for i in range(256):
                x = (x + box[i] + ord(self._key[i % len(self._key)])) & 255
                box[i], box[x] = box[x], box[i]
            x = y = 0
        self._box = box
        self._x = x
        self._y = y

    def crypt(self, data):
        box = self._box
        x, y = self._x, self._y
        if len(self._key) == 0:
            return data
        out = []
        for ch in data:
            x = (x + 1) & 255
            y = (y + box[x]) & 255
            box[x], box[y] = box[y], box[x]
            if isinstance(ch, int):
                out.append(chr(ch ^ box[(box[x] + box[y]) & 255]))
            else:
                out.append(chr(ord(ch) ^ box[(box[x] + box[y]) & 255]))
        self._x, self._y = x, y
        return ''.join(out)

    def excrypt(self, plain):
        res = []
        i = j = 0
        box = self._box
        for s in plain:
            i = (i + 1) % 256
            j = (j + box[i]) % 256
            box[i], box[j] = box[j], box[i]
            t = (box[i] + box[j]) % 256
            k = box[t]
            res.append(chr(ord(s) ^ k))
        cipher = "".join(res)
        return cipher


aa = rc4crypt("123456sh")
v = aa.crypt("123456")
print(v)

bb = rc4crypt("123456sh")
print(bb.excrypt(v))