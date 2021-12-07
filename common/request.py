from common.packet import Packet
import json


class Request(object):
    def __init__(self, sid: int, command: int, packet: Packet, src: int = 0, dst: int = 0):
        self.sid = sid
        self.command = command
        p = Packet()
        p.putUint16(sid)
        p.putUint16(command)
        p.putUint32(src)
        p.putUint32(dst)
        p.putUint32(0)
        p.putRaw(packet.serialize())
        self._buffer: bytes = p.serialize()

    def serialize(self):
        buffer = self._buffer
        length = len(buffer) + 4
        buffer = length.to_bytes(4, byteorder='little', signed=False) + buffer
        return buffer

    def key(self):
        return self.sid, self.command

    def __str__(self):
        return f'{self.sid}-{self.command}'


class PacketRequest(Request):
    def __init__(self, sid: int, command: int, data: list, src: int = 0, dst: int = 0, packet=None):
        if not packet:
            packet = Packet()
        for value, packetType in data:
            packet.putValue(packetType, value)
        super(PacketRequest, self).__init__(sid, command, packet, src, dst)


class JsonRequest(Request):
    def __init__(self, sid: int, command: int, data: dict, src: int = 0, dst: int = 0):
        s = json.dumps(data)
        packet = Packet()
        packet.putString(s)
        super(JsonRequest, self).__init__(sid, command, packet, src, dst)