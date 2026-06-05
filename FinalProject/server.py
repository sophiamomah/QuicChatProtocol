import socket
from ConnectionState import ConnectionState
from protocol import parse_message, build_message
from MessageType import MessageType
import argparse

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 54400

parser = argparse.ArgumentParser(description="QuicChat Server")
parser.add_argument("--host", default=DEFAULT_HOST, help="Input host/IP address to bind server to")
parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Input port number to bind server to")
args = parser.parse_args()

HOST = args.host
PORT = args.port

state = ConnectionState.INIT

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Server listening on {HOST}:{PORT}")

conn, addr = server_socket.accept()
print(f"Connected by {addr}")

VALID_TOKEN = "test-token"

while state != ConnectionState.CLOSED:
    data = conn.recv(1024)

    if not data:
        state = ConnectionState.CLOSED
        break

    msg_type, payload = parse_message(data)

    print(f"Type: {msg_type}")
    print(f"Payload: {payload}")

    if state == ConnectionState.INIT:
        if msg_type == MessageType.AUTH:
            state = ConnectionState.AUTHENTICATING
            print("State changed to AUTHENTICATING")

            if payload == VALID_TOKEN:
                conn.sendall(build_message(MessageType.AUTH_OK, "Authentication successful"))
                state = ConnectionState.ACTIVE
                print("State changed to ACTIVE")
            else:
                conn.sendall(build_message(MessageType.AUTH_FAIL, "Authentication failed"))
                state = ConnectionState.CLOSED
                print("State changed to CLOSED")
        else:
            conn.sendall(build_message(MessageType.ERROR, "You must authenticate first"))
            state = ConnectionState.CLOSED

    elif state == ConnectionState.ACTIVE:
        if msg_type == MessageType.SEND_MESSAGE:
            user_message = payload
            print(f"Chat message: {user_message}")
            conn.sendall(build_message(MessageType.SEND_MESSAGE, "Message received"))
        elif msg_type == MessageType.CLOSE:
            conn.sendall(build_message(MessageType.CLOSE, "Closing"))
            state = ConnectionState.CLOSED
        else:
            conn.sendall(build_message(MessageType.ERROR, "Invalid message"))
            state = ConnectionState.CLOSED

conn.close()
server_socket.close()
print("Server closed")