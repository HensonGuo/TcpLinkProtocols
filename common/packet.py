
# -*- coding: utf-8 -*-
from enum import Enum
import logging

_logger = logging.getLogger("protocol")


class PacketTypes(Enum):
    uint8 = 1
    uint16 = 2
    uint32 = 3
    string = 4
    buffer = 5
    intmap = 6
    strmap = 7
    longbuffer = 8
    intlist = 9
    strlist = 10
    bufferlist = 11
    int2int_map = 12
    compactMap = 13

    custom = 100


class Packet(object):
    def __init__(self):
        self._buffer: bytes = b''
        self._typeToFunc = {
            PacketTypes.uint8: self.putUint8,
            PacketTypes.uint16: self.putUint16,
            PacketTypes.uint32: self.putUint32,
            PacketTypes.string: self.putString,
            PacketTypes.buffer: self.putBuffer,
            PacketTypes.intmap: self.putIntMap,
            PacketTypes.strmap: self.putStrMap,
            PacketTypes.longbuffer: self.putLongBuffer,
            PacketTypes.intlist: self.putIntList,
            PacketTypes.strlist: self.putStrList,
            PacketTypes.bufferlist:self.putBufferList,
            PacketTypes.int2int_map:self.putInt2IntMap,
        }

    def serialize(self) -> bytes:
        return self._buffer

    def putUint8(self, number: int):
        self._buffer += number.to_bytes(1, byteorder='little', signed=False)

    def putUint16(self, number: int):
        self._buffer += number.to_bytes(2, byteorder='little', signed=False)

    def putUint32(self, number: int):
        self._buffer += number.to_bytes(4, byteorder='little', signed=False)

    def putString(self, s: str):
        self.putBuffer(s.encode('utf-8'))

    def putBuffer(self, buffer: bytes):
        length = len(buffer)
        self.putUint16(length)
        self._buffer += buffer

    def putLongBuffer(self, buffer: bytes):
        length = len(buffer)
        self.putUint32(length)
        self._buffer += buffer

    def putIntMap(self, intMap: dict):
        length = len(intMap)
        self.putUint32(length)
        for key, value in intMap.items():
            self.putUint32(key)
            self.putString(value)

    def putStrMap(self, strMap):
        length = len(strMap)
        self.putUint32(length)
        for key, value in strMap.items():
            self.putString(key)
            self.putString(value)

    def putRaw(self, buffer: bytes):
        self._buffer += buffer

    def putValue(self, packetType, value):
        func = self._typeToFunc.get(packetType)
        if func:
            func(value)

    def putIntList(self, values: list):
        size = len(values)
        self.putUint32(size)
        for value in values:
            self.putUint32(value)

    def putStrList(self, values: list):
        size = len(values)
        self.putUint32(size)
        for value in values:
            self.putString(value)

    def putBufferList(self, values:list):
        size = len(values)
        self.putUint32(size)
        for value in values:
            self.putBuffer(value)

    def putInt2IntMap(self, strMap):
        length = len(strMap)
        self.putUint32(length)
        for key, value in strMap.items():
            self.putUint32(key)
            self.putUint32(value)


class UnPack(object):
    def __init__(self, buffer: bytes, isLittleEndian=True):
        self._buffer = buffer
        self._index = 0
        self._typeToFunc = {
            PacketTypes.uint8: self.getUint8,
            PacketTypes.uint16: self.getUint16,
            PacketTypes.uint32: self.getUint32,
            PacketTypes.string: self.getString,
            PacketTypes.buffer: self.getBuffer,
            PacketTypes.intmap: self.getIntMap,
            PacketTypes.strmap: self.getStrMap,
            PacketTypes.longbuffer: self.getLongBuffer,
            PacketTypes.intlist: self.getIntList,
            PacketTypes.strlist: self.getStrList,
            PacketTypes.bufferlist: self.getBufferList,
            PacketTypes.int2int_map: self.getInt2IntMap,
            PacketTypes.compactMap: self.getCompactMap,
        }
        self._byteOrder = 'little' if isLittleEndian else 'big'

    def getUint8(self) -> int:
        end = self._index + 1
        b = self._buffer[self._index:end]
        n = int.from_bytes(b, byteorder=self._byteOrder, signed=False)
        self._index = end
        return n

    def getUint16(self) -> int:
        end = self._index + 2
        b = self._buffer[self._index:end]
        n = int.from_bytes(b, byteorder=self._byteOrder, signed=False)
        self._index = end
        return n

    def getUint32(self) -> int:
        end = self._index + 4
        b = self._buffer[self._index:end]
        n = int.from_bytes(b, byteorder=self._byteOrder, signed=False)
        self._index = end
        return n

    def getString(self) -> str:
        buffer = self.getBuffer()
        return buffer.decode('utf-8')

    def getBuffer(self) -> bytes:
        length = self.getUint16()
        end = self._index + length
        buffer = self._buffer[self._index:end]
        self._index = end
        return buffer

    def getLongBuffer(self):
        length = self.getUint32()
        end = self._index + length
        buffer = self._buffer[self._index:end]
        self._index = end
        return buffer

    def getIntMap(self) -> dict:
        length = self.getUint32()
        d = {}
        for i in range(length):
            key = self.getUint32()
            value = self.getString()
            d[key] = value
        return d

    def getStrMap(self) -> dict:
        length = self.getUint32()
        d = {}
        for i in range(length):
            key = self.getBuffer()
            value = self.getBuffer()
            d[key] = value
        return d

    def getValue(self, packetType):
        value = None
        func = self._typeToFunc.get(packetType)
        if func:
            value = func()
        return value

    def getIntList(self) -> list:
        length = self.getUint32()
        values = []
        for i in range(length):
            values.append(self.getUint32())
        return values

    def getStrList(self) -> list:
        length = self.getUint32()
        values = []
        for i in range(length):
            values.append(self.getString())
        return values

    def getBufferList(self)-> list:
        length = self.getUint32()
        values = []
        for i in range(length):
            values.append(self.getBuffer())
        return values

    def getInt2IntMap(self) -> dict:
        length = self.getUint32()
        d = {}
        for i in range(length):
            key = self.getUint32()
            value = self.getUint32()
            d[key] = value
        return d

    def getCompactMap(self):
        num = self.getUint8()
        tags = [self.getUint8() for i in range(num)]
        u = {}
        for tag in tags:
            t = (tag & 0xC0) >> 6
            if t == 0:
                u[tag] = self.getUint8()
            elif t == 1:
                u[tag] = self.getUint16()
            elif t == 2:
                u[tag] = self.getUint32()
            else:
                u[tag] = self.getBuffer()
        return u