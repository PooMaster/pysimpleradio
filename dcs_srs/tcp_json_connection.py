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

from .messages import NetworkMessage, MessageType

logger = logging.getLogger(__name__)


async def connect_tcp_json(
    host: str,
    port: int,
) -> tuple[asyncio.Queue[NetworkMessage], asyncio.Queue[NetworkMessage]]:
    """
    Form a TCP connection and just send and receive single-line JSON data
    objects. Messages are forwarded in and out via the send and received queues.
    """
    logger.info(f"Opening TCP connection to {host}:{port}")
    reader, writer = await asyncio.open_connection(host, port)

    send_queue = asyncio.Queue[NetworkMessage]()
    receive_queue = asyncio.Queue[NetworkMessage]()

    asyncio.create_task(send_messages(writer, send_queue))
    asyncio.create_task(receive_messages(reader, receive_queue))

    return receive_queue, send_queue


async def send_messages(
    writer: asyncio.StreamWriter, send_queue: asyncio.Queue[NetworkMessage]
):
    """Send messages from the queue to the TCP socket"""
    logger.info("Starting TCP message sender")
    while True:
        # Get the next message to be sent
        msg = await send_queue.get()

        # And serialize and send it
        logger.debug("Sending %r message", MessageType(msg["MsgType"]))
        writer.write(json.dumps(msg).encode() + b"\n")


async def receive_messages(
    reader: asyncio.StreamReader, receive_queue: asyncio.Queue[NetworkMessage]
):
    """Receive messages from the TCP socket and put them on the receive queue"""
    logger.info("Starting TCP message receiver")
    while True:
        # Get the next line of data
        line = (await reader.readline()).decode()
        if not line.endswith("\n"):
            raise RuntimeError("Client TCP connection broken")

        # And deserialize it and place it on the receive queue
        msg: NetworkMessage = json.loads(line.rstrip())
        logger.debug("Received %r message", MessageType(msg["MsgType"]))
        await receive_queue.put(msg)
