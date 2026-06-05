from enum import Enum

class ConnectionState(Enum):
    INIT = 1
    AUTHENTICATING = 2
    ACTIVE = 3
    CLOSED = 4