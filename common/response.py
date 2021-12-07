# -*- coding: utf-8 -*-
import json
import zlib
import logging
from common.packet import UnPack, PacketTypes


_logger = logging.getLogger("protocol")


def decompress(buffer: bytes) -> bytes:
    # logger.debug(f"decompress {len(buffer)}")
    length = int.from_bytes(buffer[:4], byteorder='little', signed=False)
    buf = zlib.decompress(buffer[4:])
    # logger.debug(f"decompress {len(buf)} {length}")
    return buf


class Response(object):
    def __init__(self, sid: int, command: int, buffer: bytes):
        self._sid, self._command, self._buffer = sid, command, buffer

    @property
    def sid(self):
        return self._sid

    @property
    def command(self):
        return self._command

    @property
    def buffer(self):
        return self._buffer

    def getUnPacket(self):
        return UnPack(self._buffer)

    def extract(self, types: list):
        up = self.getUnPacket()
        values = [up.getValue(packetType) for packetType in types]
        return values

    def toJson(self, isLong=False) -> (int, str, dict):
        result, reason, js = self.extract(
            [PacketTypes.uint32, PacketTypes.string,
             PacketTypes.longbuffer if isLong else PacketTypes.buffer])
        return result, reason, json.loads(js)

    def key(self):
        return self._sid, self._command

    def __str__(self):
        return f'{self._sid}-{self._command}'


protocol2class = {}


class PacketParser(type):
    def __init__(cls, name, bases, dic):
        # print("init packet parser", cls, name, bases, dic)
        super().__init__(name, bases, dic)
        protocol2class[(dic['__sid__'], dic['__command__'])] = cls

    def __call__(cls, resp):
        obj = Response.__new__(Response)
        Response.__init__(obj, resp._sid, resp._command, resp._buffer)
        cls.__init__(obj)
        # print("packet parser cls", cls, obj, getattr(cls, '__proto__'))
        proto = getattr(cls, '__proto__')
        slots = getattr(cls, '__slots__')
        if proto is not None:
            up = obj.getUnPacket()
            customMethod = getattr(cls, 'getCustom', lambda obj, name, up: obj.__dict__.__setitem__(name, name))
            for name, format in zip(slots, proto):
                if format == PacketTypes.custom:
                    value = customMethod(obj, name, up)
                else:
                    value = up.getValue(format)
                # print("format", name, format, value)
                obj.__dict__.__setitem__(name, value)
        return obj


class PacketResponse(Response):
    def __init__(self, buffer: bytes):
        up = UnPack(buffer)
        sid = up.getUint16()
        command = up.getUint16()
        src = up.getUint32()
        dst = up.getUint32()
        composite = up.getUint32()
        isCompressed = (composite & 0x20000) != 0
        # logger.debug(f"response {sid} {command} {isCompressed}")
        buf = buffer[16:]
        if isCompressed:
            try:
                buf = decompress(buf)
            except Exception as e:
                import sys
                _logger.debug(f"sid:{sid} command:{command} packet decompress fail: {e}", sys.exc_info())
        super(PacketResponse, self).__init__(sid, command, buf)

class JsonResponse(Response):
    def __init__(self, resp: PacketResponse, isLong=False):
        super(JsonResponse, self).__init__(resp._sid, resp._command, resp._buffer)
        self._result, self._reason, self._obj = resp.toJson(isLong)

    @property
    def result(self):
        return self._result

    @property
    def reason(self):
        return self._reason

    @property
    def jsondata(self):
        return self._obj

    def __str__(self):
        return f'{self.key()}-{self.result}-{self.jsondata}'