"""
Tracks overall SRS state.

my guid
client dict
server settings
"""

import asyncio
from collections import defaultdict
import logging
from pprint import pprint

from .client_info import (
    ClientInfo,
    Coalition,
    Modulation,
    default_client_info,
    make_radio_information,
    print_client_info,
)
from .connection import connect_client
from . import messages
from .messages import MessageType
from .utils import Guid, make_short_guid

logger = logging.getLogger(__name__)


class SrsClient:
    def __init__(self, name: str):
        self.guid = make_short_guid()
        self.clients: dict[Guid, ClientInfo] = {
            self.guid: default_client_info(self.guid)
        }
        self.server_settings: messages.ServerSettings = {}

        self.my_info["Name"] = name

        self._send_queue = asyncio.Queue()
        self._receive_queue = asyncio.Queue()
        self._message_futures: defaultdict[
            MessageType, list[asyncio.Future[messages.NetworkMessage]]
        ] = defaultdict(list)

        self._tcp_task = None
        self._message_receive_task = None

    @property
    def my_info(self) -> ClientInfo:
        return self.clients[self.guid]

    #
    # Public methods
    #
    async def connect(self, host: str, port: int):
        """Connect to an SRS server"""
        logger.info(f"Connecting to SRS server {host}:{port}")

        # Start up tasks to handle TCP connection
        self._tcp_task = asyncio.create_task(
            connect_client(host, port, self._send_queue, self._receive_queue)
        )
        self._message_receive_task = asyncio.create_task(self._handle_messages())

        # Send sync message
        await self._send_queue.put(messages.sync_message(self.my_info))
        try:
            await asyncio.wait_for(self._future_message(MessageType.SYNC), 5)
        except TimeoutError:
            raise TimeoutError("Timed out trying to log in")

        logger.info("Connected")

    async def log_in_awacs(self, password: str) -> bool:
        """Log in as AWACS"""
        await self._send_queue.put(
            messages.external_awacs_mode_password_message(
                self.clients[self.guid], password
            )
        )
        try:
            response = await asyncio.wait_for(
                self._future_message(MessageType.EXTERNAL_AWACS_MODE_PASSWORD), 5
            )
        except TimeoutError:
            logger.error("Timed out trying to log in to external awacs mode")
            return False

        # On AWACS log in success, the client info will contain the new coalition
        return response["Client"]["Coalition"] != Coalition.SPECTATOR

    async def tune_radio(
        self, radio_index: int, frequency: float, modulation: Modulation
    ):
        my_info = self.clients[self.guid]
        my_info["RadioInfo"]["radios"][radio_index] = make_radio_information(
            frequency, modulation
        )

        await self._send_queue.put(messages.radio_update_message(my_info))

    async def transmit_audio(self, audio_stream, radio_index: int):
        pass

    #
    # Class internal methods
    #
    def _future_message(
        self, message_type: MessageType
    ) -> asyncio.Future[messages.NetworkMessage]:
        """Future that completes when a message of the given type is received."""
        future = asyncio.Future()
        self._message_futures[message_type].append(future)
        return future

    async def _handle_messages(self):
        """Take messages from receive queue forever."""
        while True:
            msg: messages.NetworkMessage = await self._receive_queue.get()
            msg_type = MessageType(msg["MsgType"])

            # Update SRS server state
            try:
                match msg_type:
                    case MessageType.SYNC:
                        sync_client_dict = {
                            client["ClientGuid"]: client for client in msg["Clients"]
                        }
                        self.clients.update(sync_client_dict)
                        self.server_settings.update(msg["ServerSettings"])

                        self._print_server_settings()
                        self._print_clients()

                    case MessageType.RADIO_UPDATE:
                        updated_guid = msg["Client"]["ClientGuid"]
                        self.clients[updated_guid].update(msg["Client"])
                        self._print_clients()

                    case MessageType.UPDATE:
                        updated_guid = msg["Client"]["ClientGuid"]
                        self.clients[updated_guid].update(msg["Client"])
                        self._print_clients()

                    case MessageType.CLIENT_DISCONNECT:
                        disconnected_client = msg["Client"]["ClientGuid"]
                        del self.clients[disconnected_client]
                        self._print_clients()

                    case MessageType.VERSION_MISMATCH:
                        logger.error("SRS version mismatch")
                        pprint(msg)
                        exit()

                    case MessageType.EXTERNAL_AWACS_MODE_PASSWORD:
                        # Do nothing and don't print
                        pass

                    case _:
                        logger.warning("This message type is unhandled")
                        pprint(msg)

            except KeyError as err:
                logger.error(str(err))
                pprint(msg)

            except ValueError as err:
                logger.error(str(err))
                pprint(msg)

            # Trigger any waiting futures
            for future in self._message_futures[msg_type]:
                future.set_result(msg)

    def _print_clients(self):
        print("Current users:")
        for client in self.clients.values():
            print_client_info(client)
        print()

    def _print_server_settings(self):
        print("Current server settings:")
        pprint(self.server_settings)
        print()
