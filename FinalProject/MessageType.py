from enum import IntEnum

class MessageType(IntEnum):
    AUTH = 1
    AUTH_OK = 2
    AUTH_FAIL = 3
    SEND_MESSAGE = 6
    ERROR = 12
    CLOSE = 99