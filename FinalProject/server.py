import argparse
import asyncio

from ConnectionState import ConnectionState
from protocol import parse, build
from MessageType import MessageType

from aioquic.asyncio import serve
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived

# Default configuration
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 54400

# authentication token 
TOKEN = "test-token"

# authentication failure test token 
#TOKEN = "wrong-token"

#QuicChat Server
class QuicChatServer(QuicConnectionProtocol):

    # INIT state
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = ConnectionState.INIT

    #Process data and apply DFA state transitions
    def quic_event_received(self, event):
        if isinstance(event, StreamDataReceived):
            msg_type, payload = parse(event.data)

            print(f"\nType: {msg_type.name}")
            print(f"Payload: {payload}")

            # INIT -> AUTHENTICATING transition
            if self.state == ConnectionState.INIT:
                if msg_type == MessageType.AUTH:
                    self.state = ConnectionState.AUTHENTICATING
                    print("State changed to AUTHENTICATING")

                    # Validate authentication token
                    if payload == TOKEN:
                        response = build( MessageType.AUTH_OK, "Authentication successful" )
                        self._quic.send_stream_data(event.stream_id, response)
                        self.transmit()

                        self.state = ConnectionState.ACTIVE
                        print("State changed to ACTIVE")
                    else:
                        # Send AUTH_FAIL and close connection
                        response = build( MessageType.AUTH_FAIL, "Authentication failed" )
                        self._quic.send_stream_data(event.stream_id, response, end_stream=True)
                        self.transmit()

                        self.state = ConnectionState.CLOSED
                        print("State changed to CLOSED")
                else:
                    # Error handling: Message received before authentication
                    response = build( MessageType.ERROR, "You neeed to authenticate first" )
                    self._quic.send_stream_data(event.stream_id, response, end_stream=True)
                    self.transmit()
                    self.state = ConnectionState.CLOSED

            elif self.state == ConnectionState.ACTIVE:
                # Process chat messages
                if msg_type == MessageType.SEND_MESSAGE:
                    print(f"Chat message: {payload}")
                    response = build( MessageType.DELIVERED_ACK, "Message received" )
                    self._quic.send_stream_data(event.stream_id, response)
                    self.transmit()

                # Close the connection
                elif msg_type == MessageType.CLOSE:
                    response = build(MessageType.CLOSE, "Closing")
                    self._quic.send_stream_data(event.stream_id, response, end_stream=True)
                    self.transmit()
                    self.state = ConnectionState.CLOSED

                # Invalid message so close the connection
                else:
                    response = build(MessageType.ERROR, "Invalid message")
                    self._quic.send_stream_data(event.stream_id, response, end_stream=True)
                    self.transmit()
                    self.state = ConnectionState.CLOSED


# start the QUIC server
async def main():
    parser = argparse.ArgumentParser(description="QuicChat Server")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Input host/IP address to bind server to")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Input port number to bind server to")
    args = parser.parse_args()

    configuration = QuicConfiguration(
        is_client=False,
        alpn_protocols=["quicchat"]
    )
    configuration.load_cert_chain("ssl_cert.pem", "ssl_key.pem")

    print(f"QUIC server listening on {args.host}:{args.port}")

    await serve(
        args.host,
        args.port,
        configuration=configuration,
        create_protocol=QuicChatServer
    )

    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())