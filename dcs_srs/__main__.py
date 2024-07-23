import argparse
import asyncio
import logging
from pprint import pprint

from . import messages
from .client_info import (
    ClientInfo,
    Coalition,
    Modulation,
    default_client_info,
    make_radio_information,
)
from .connection import connect_client
from .utils import make_short_guid

logger = logging.getLogger(__name__)


async def main():
    parser = argparse.ArgumentParser(
        description="Connect to an SRS server and send some audio"
    )
    parser.add_argument("host", help="Hostname or IP address of the SRS server")
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=5002,
        help="Port for connecting to the SRS server",
    )
    args = parser.parse_args()

    guid = make_short_guid()

    client_info = default_client_info(guid)
    client_info["RadioInfo"]["radios"][1] = make_radio_information(
        31_000_000.0, Modulation.FM
    )

    send_queue = asyncio.Queue()
    receive_queue = asyncio.Queue()

    await send_queue.put(messages.sync_message(client_info))

    await asyncio.gather(
        connect_client(args.host, args.port, send_queue, receive_queue),
        handle_messages(receive_queue),
    )


async def handle_messages(message_receive_queue: asyncio.Queue):
    while True:
        msg: messages.BaseNetworkMessage = await message_receive_queue.get()
        logger.info("Received message: %r", messages.MessageType(msg["MsgType"]))
        try:
            match msg["MsgType"]:
                case messages.MessageType.SYNC:
                    print_server_sync(msg)

                case messages.MessageType.RADIO_UPDATE:
                    msg: messages.RadioUpdateMessage = msg
                    print_client_info(msg["Client"])

                case messages.MessageType.UPDATE:
                    msg: messages.UpdateMessage = msg
                    print_client_info(msg["Client"])

                case messages.MessageType.CLIENT_DISCONNECT:
                    msg: messages.ClientDisconnectMessage = msg
                    print_client_info(msg["Client"])

                case _:
                    pprint(msg)
        except KeyError:
            logger.info("Message keys weren't as expected!")
            pprint(msg)


def print_server_sync(sync_message: messages.SyncMessage):
    for client in sync_message["Clients"]:
        print_client_info(client)


def print_client_info(client: ClientInfo):
    coalition = Coalition(client["Coalition"])
    print(
        f'{client["Name"]}: {client.get("RadioInfo", {}).get("ambient", {}).get("abType", "")} <{coalition.name}>'
    )
    for radio in client["RadioInfo"]["radios"]:
        if radio["freq"] > 1.0 and radio["modulation"] != Modulation.INTERCOM:
            freq = radio["freq"]
            if freq >= 10_000_000:
                freq_str = f"{freq / 1_000_000 : .03f} MHz"
            else:
                freq_str = f"{freq / 1_000 : .03f} KHz"

            print(f'    {freq_str} {Modulation(radio["modulation"]).name}')


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
