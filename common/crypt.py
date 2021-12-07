# ======================================================================
# RC4 cryption
# ======================================================================
class rc4crypt(object):
    def __init__(self, key=''):
        self._key = key
        box = [x for x in range(256)]
        x = y = 0
        if len(key) > 0:
            for i in range(256):
                x = (x + box[i] + ord(key[i % len(key)])) & 255
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
            out.append(chr(ord(ch) ^ box[(box[x] + box[y]) & 255]))
        self._x, self._y = x, y
        return ''.join(out)