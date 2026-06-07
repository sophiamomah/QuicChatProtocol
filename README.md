# QuicChatProtocol

QuicChat is a stateful messaging service built on top of QUIC. The service allows users to send and receive messages across private and group conversations.

This project uses aioquic only to provide QUIC transport support. The QuicChat protocol logic, including message framing, serialization/parsing, PDU processing, message types, authentication handling, and DFA state validation, is implemented manually in the project source code.

## Features Implemented

- QUIC client and server written in Python
- Stateful protocol implementation using a DFA
- Authentication workflow:
    - AUTH
    - AUTH_OK
    - AUTH_FAIL
- Message sending using SEND_MESSAGE
- DELIVERED_ACK responses
- Binary message serialization and parsing
- Command-line configuration for host and port
- Command-line client interface

## Connection States
- INIT
- AUTHENTICATING
- ACTIVE
- CLOSED

## Message Types
- AUTH
- AUTH_OK
- AUTH_FAIL
- SEND_MESSAGE
- DELIVERED_ACK
- ERROR
- CLOSE

## Files
- server.py – QUIC server 
- client.py – QUIC client 
- protocol.py – message serialization and parsing functions
- MessageType.py – message types
- ConnectionState.py – DFA state definitions

## Requirements

Create and activate a virtual environment:
    python3 -m venv venv
    source venv/bin/activate

pip install aioquic

Generate a self-signed certificate for local testing:
    openssl req -x509 -newkey rsa:2048 -keyout ssl_key.pem -o

## Run the server

    python3 server.py
    or
    python3 server.py --host 127.0.0.1 --port 54400

## Run the client

    python3 client.py
    or
    python3 client.py --host 127.0.0.1 --port 54400

    To test authentication failure:
        python3 client.py --token wrong-token

## Notes
- The client exits when the user types quit. The server remains running to accept future QUIC client connections and can be stopped manually with Ctrl+C.
- IDLE state was listed as a possible stretch goal but was not implemented in the final prototype due to time constraints.