"""
An SRS client starts with forming a TCP connection and trading messages with the
server in the form of single-line JSON objects. This file has an async function
for forming this TCP connection and sending and receiving those objects. Other
code can interact with this connection via two async queues. Messages added to
the send queue will be sent and any received messages will be deserialized and
added to the receive queue for some other code to pop and process. 👌
"""

import asyncio
import json
import logging

from . import messages

logger = logging.getLogger(__name__)


async def connect_client(
    host: str,
    port: int,
    send_queue: asyncio.Queue,
    receive_queue: asyncio.Queue,
):
    """
    Form a TCP connection and just send and receive single-line JSON data
    objects. Messages are forwarded in and out via the send and received queues.
    """
    logger.info(f"Opening TCP connection to {host}:{port}")
    reader, writer = await asyncio.open_connection(host, port)

    await asyncio.gather(
        send_messages(writer, send_queue),
        receive_messages(reader, receive_queue),
    )


async def send_messages(writer: asyncio.StreamWriter, send_queue: asyncio.Queue):
    """Send messages from the queue to the TCP socket"""
    while True:
        # Get the next message to be sent
        msg: messages.NetworkMessage = await send_queue.get()

        # And serialize and send it
        logger.debug("Sending %r message", messages.MessageType(msg["MsgType"]))
        writer.write(json.dumps(msg).encode() + b"\n")


async def receive_messages(reader: asyncio.StreamReader, receive_queue: asyncio.Queue):
    """Receive messages from the TCP socket and put them on the receive queue"""
    while True:
        # Get the next line of data
        line = (await reader.readline()).decode()
        if not line.endswith("\n"):
            raise RuntimeError("Client TCP connection broken")

        # And deserialize it and place it on the receive queue
        msg: messages.NetworkMessage = json.loads(line.rstrip())
        logger.debug("Received %r message", messages.MessageType(msg["MsgType"]))
        await receive_queue.put(msg)
