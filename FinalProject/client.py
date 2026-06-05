import socket
from protocol import build_message, parse_message
from MessageType import MessageType
import argparse

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 54400

parser = argparse.ArgumentParser(description="QuicChat Client")
parser.add_argument("--host", default=DEFAULT_HOST, help="Input server hostname or IP address")
parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Input server port number")
args = parser.parse_args()

HOST = args.host
PORT = args.port

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

client_socket.sendall(build_message(MessageType.AUTH, "wrong-token"))
data = client_socket.recv(1024)
response_type, response_payload = parse_message(data)
print("Server:", response_type.name, response_payload)

if response_type == MessageType.AUTH_FAIL:
    print("Authentication failed. Closing client.")
    client_socket.close()
    exit()
elif response_type != MessageType.AUTH_OK:
    print("Unexpected authentication response. Closing client.")
    client_socket.close()
    exit()

while True:
    user_input = input("Enter message, or type quit to exit: ")

    if user_input.lower() == "quit":
        break

    client_socket.sendall(
        build_message(MessageType.SEND_MESSAGE, user_input)
    )

    data = client_socket.recv(1024)
    response_type, response_payload = parse_message(data)

    print("Server:", response_type.name, response_payload)

client_socket.close()