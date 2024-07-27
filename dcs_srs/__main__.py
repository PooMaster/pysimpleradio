import argparse
import asyncio
import logging

from .client import SrsClient
from .client_info import Modulation

logger = logging.getLogger(__name__)


async def main(addr: tuple[str, int], name: str):
    # Make a new client instance
    client = SrsClient(name)

    # Connect to the SRS server
    host, port = addr
    await client.connect(host, port)

    # Grab the first global frequency and tune radio 1 to it
    global_freq = client.server_settings["GLOBAL_LOBBY_FREQUENCIES"].split(",")[0]
    global_freq_mhz = float(global_freq)
    await client.tune_radio(1, global_freq_mhz * 1_000_000, Modulation.AM)

    # Log in to external AWACS mode
    if not await client.log_in_awacs("blue"):
        print("Bad password")
        return

    await asyncio.to_thread(input, "press enter to end...")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

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
    parser.add_argument(
        "--name", default="PySimpleAudio", help="Client name to use in SRS"
    )
    args = parser.parse_args()

    asyncio.run(main((args.host, args.port), args.name))
