from enum import IntEnum
from typing import TypedDict

from .client_info import ClientInfo


SRS_VERSION = "2.1.0.7"


class MessageType(IntEnum):
    # Client sends to update non-radio client info
    # Server sends to update info about a client's (maybe non-radio) info
    UPDATE = 0

    # Nothing for now
    PING = 1

    # Client sends to connect to server
    # Server sends to update client about all state when connecting
    SYNC = 2

    # Client sends to update server about radio states
    # Server sends to client radio info on changes (if showing tune count)
    RADIO_UPDATE = 3

    # Client sends to trigger server to broadcast its settings
    # Server sends to update clients about settings
    SERVER_SETTINGS = 4

    # Server sends to inform that a client disconnected
    CLIENT_DISCONNECT = 5

    # Server sends to tell client its version string isn't supported
    VERSION_MISMATCH = 6

    # Client sends to enable AWACS mode
    # Server sends on correct AWACS mode password
    EXTERNAL_AWACS_MODE_PASSWORD = 7

    # Client sends leave AWACS mode
    EXTERNAL_AWACS_MODE_DISCONNECT = 8


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


class NetworkMessage(TypedDict):
    Version: str
    MsgType: MessageType
    Client: ClientInfo
    Clients: list[ClientInfo]
    ServerSettings: ServerSettings
    ExternalAwacsModePassword: str


#############
# These are for building messages to be sent from the client
#############


def sync_message(client_info: ClientInfo) -> NetworkMessage:
    return {
        "Version": SRS_VERSION,
        "MsgType": MessageType.SYNC,
        "Client": client_info,
    }


def radio_update_message(client_info: ClientInfo) -> NetworkMessage:
    return {
        "MsgType": MessageType.RADIO_UPDATE,
        "Client": client_info,
    }


def server_settings_message() -> NetworkMessage:
    return {
        "MsgType": MessageType.SERVER_SETTINGS,
    }


def external_awacs_mode_password_message(
    client_info: ClientInfo, password: str
) -> NetworkMessage:
    return {
        "MsgType": MessageType.EXTERNAL_AWACS_MODE_PASSWORD,
        "ExternalAwacsModePassword": password,
        "Client": client_info,
    }


def external_awacs_mode_disconnect_message(client_info: ClientInfo) -> NetworkMessage:
    return {
        "MsgType": MessageType.EXTERNAL_AWACS_MODE_DISCONNECT,
        "Client": client_info,
    }
