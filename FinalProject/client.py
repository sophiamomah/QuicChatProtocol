import argparse
import asyncio

from aioquic.asyncio import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived

from MessageType import MessageType
from protocol import build, parse

# Default configuration
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 54400


#QuicChat Client
class QuicChatClientProtocol(QuicConnectionProtocol):
    # Initialize queue
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_queue = asyncio.Queue()

    # Handle data from the server
    def quic_event_received(self, event):
        if isinstance(event, StreamDataReceived):
            self.response_queue.put_nowait(event.data)

    # parse protocol message from the top of the server
    async def receive_message(self):
        data = await self.response_queue.get()
        return parse(data)

# Main client function
async def main():
    parser = argparse.ArgumentParser(description="QuicChat Client")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--token", default="test-token")
    args = parser.parse_args()

    configuration = QuicConfiguration(
        is_client=True,
        alpn_protocols=["quicchat"]
    )
    configuration.verify_mode = False

    # Connect to server
    async with connect(
        args.host,
        args.port,
        configuration=configuration,
        create_protocol=QuicChatClientProtocol
    ) as client:

        stream_id = client._quic.get_next_available_stream_id()

        #Send authentication request to the server
        client._quic.send_stream_data(
            stream_id,
            build(MessageType.AUTH, args.token)
        )
        client.transmit()

        # Wait for authentication response
        response_type, response_payload = await client.receive_message()
        print("Server:", response_type.name, response_payload)

        # Close if authentication fails
        if response_type != MessageType.AUTH_OK:
            print("Authentication failed. Now closing the client.")
            return

        while True:
            user_input = input("Enter message, or type quit to exit: ")

            # Send CLOSE message and close connection
            if user_input.lower() == "quit":
                client._quic.send_stream_data(
                    stream_id,
                    build(MessageType.CLOSE, "close"),
                    end_stream=True
                )
                client.transmit()

                client.close()
                await asyncio.sleep(0.1)
                break
            
            # Send chat message to the server
            client._quic.send_stream_data(
                stream_id,
                build(MessageType.SEND_MESSAGE, user_input)
            )
            client.transmit()

            # Wait for delivery_ack
            response_type, response_payload = await client.receive_message()
            print("Server:", response_type.name, response_payload)


if __name__ == "__main__":
    asyncio.run(main())