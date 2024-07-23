from enum import IntEnum
from typing import TypedDict

from .client_info import ClientInfo


SRS_VERSION = "2.1.0.7"


class MessageType(IntEnum):
    UPDATE = 0
    PING = 1
    SYNC = 2
    RADIO_UPDATE = 3
    SERVER_SETTINGS = 4
    CLIENT_DISCONNECT = 5
    VERSION_MISMATCH = 6
    EXTERNAL_AWACS_MODE_PASSWORD = 7
    EXTERNAL_AWACS_MODE_DISCONNECT = 8


class BaseNetworkMessage(TypedDict):
    Version: str
    MsgType: MessageType


class ServerSettings(TypedDict):
    ALLOW_RADIO_ENCRYPTION: str  # Example: "true"
    CLIENT_EXPORT_ENABLED: str  # Example: "false"
    COALITION_AUDIO_SECURITY: str  # Example: "false"
    DISTANCE_ENABLED: str  # Example: "False"
    EXTERNAL_AWACS_MODE: str  # Example: "True"
    GLOBAL_LOBBY_FREQUENCIES: str  # Example: "248.22"
    IRL_RADIO_RX_INTERFERENCE: str  # Example: "false"
    IRL_RADIO_TX: str  # Example: "false"
    LOS_ENABLED: str  # Example: "False"
    LOTATC_EXPORT_ENABLED: str  # Example: "True"
    LOTATC_EXPORT_IP: str  # Example: "127.0.0.1"
    LOTATC_EXPORT_PORT: str  # Example: "10712"
    RADIO_EFFECT_OVERRIDE: str  # Example: "false"
    RADIO_EXPANSION: str  # Example: "false"
    RETRANSMISSION_NODE_LIMIT: str  # Example: "0"
    SHOW_TRANSMITTER_NAME: str  # Example: "True"
    SHOW_TUNED_COUNT: str  # Example: "true"
    SPECTATORS_AUDIO_DISABLED: str  # Example: "false"
    STRICT_RADIO_ENCRYPTION: str  # Example: "false"
    TEST_FREQUENCIES: str  # Example: "247.2,120.3"
    TRANSMISSION_LOG_ENABLED: str  # Example: "false"
    TRANSMISSION_LOG_RETENTION: str  # Example: "2"


#############
# These messages types are as they come from the server
#############


# Lists all clients and server settings
class SyncMessage(TypedDict):
    Version: str
    Clients: list[ClientInfo]
    MsgType: MessageType
    ServerSettings: ServerSettings


# One client may have retuned a radio
class RadioUpdateMessage(TypedDict):
    Version: str
    Client: ClientInfo
    MsgType: MessageType


# Have just seen this return your own canonical client info right after connecting
class UpdateMessage(TypedDict):
    Version: str
    Client: ClientInfo
    MsgType: MessageType


# Given client just disconnected
class ClientDisconnectMessage(TypedDict):
    Version: str
    Client: ClientInfo
    MsgType: MessageType


#############
# These are for building messages to be sent from the client
#############


def sync_message(client_info: ClientInfo):
    return {
        "MsgType": MessageType.SYNC,
        "Version": SRS_VERSION,
        "Client": client_info,
    }


def radio_update(client_info: ClientInfo):
    return {
        "MsgType": MessageType.RADIO_UPDATE,
        "Version": SRS_VERSION,
        "Client": client_info,
    }
