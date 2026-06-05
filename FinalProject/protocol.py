from MessageType import MessageType
import struct

VERSION = 1

HEADER_FORMAT = "!BBBBQI"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

def build_message(m_type, payload=""):
    payload_bytes = payload.encode("utf-8")

    header = struct.pack(
        HEADER_FORMAT,
        VERSION,
        m_type,
        0,
        0,
        1,
        len(payload_bytes)
    )

    return header + payload_bytes

def parse_message(data):
    version, msg_type, flags, reserved, m_id, length = struct.unpack(
        HEADER_FORMAT,
        data[:HEADER_SIZE]
    )

    payload = data[HEADER_SIZE:HEADER_SIZE + length].decode()

    return MessageType(msg_type), payload