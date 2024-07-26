import asyncio
import logging

from .utils import Guid
from .voice_packet import VoicePacket

logger = logging.getLogger(__name__)


VOICE_KEEPALIVE_PERIOD = 15


async def connect_voice(addr: tuple[str, int], guid: Guid):
    loop = asyncio.get_running_loop()

    receive_datagram_queue = asyncio.Queue[bytes]()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UdpProtocol(receive_datagram_queue), remote_addr=addr
    )

    voice_receive_queue = asyncio.Queue[VoicePacket]()
    voice_send_queue = asyncio.Queue[VoicePacket]()

    asyncio.create_task(keep_voice_alive(transport, guid))
    asyncio.create_task(send_voice(transport, voice_send_queue))
    asyncio.create_task(receive_voice(receive_datagram_queue, voice_receive_queue))

    return voice_receive_queue, voice_send_queue


class UdpProtocol(asyncio.DatagramProtocol):
    def __init__(
        self,
        receive_queue: asyncio.Queue[bytes],
    ):
        self.receive_queue = receive_queue

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        pass

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        self.receive_queue.put_nowait(data)


async def keep_voice_alive(transport: asyncio.DatagramTransport, guid: Guid):
    ping_data = guid.encode()
    while True:
        transport.sendto(ping_data)
        await asyncio.sleep(VOICE_KEEPALIVE_PERIOD)


async def send_voice(
    transport: asyncio.DatagramTransport,
    voice_send_queue: asyncio.Queue[VoicePacket],
):
    while True:
        voice_packet = await voice_send_queue.get()
        transport.sendto(voice_packet)


async def receive_voice(
    receive_datagram_queue: asyncio.Queue[bytes],
    voice_receive_queue: asyncio.Queue[VoicePacket],
):
    while True:
        data = await receive_datagram_queue.get()

        if len(data) == 22:
            # Ping response
            # TODO track udp connection health with timeout
            continue

        await voice_receive_queue.put(VoicePacket.deserialize(data))
