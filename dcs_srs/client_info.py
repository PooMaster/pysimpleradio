from enum import IntEnum
from typing import TypedDict

from .utils import Guid


class Modulation(IntEnum):
    AM = 0
    FM = 1
    INTERCOM = 2
    DISABLED = 3
    HAVEQUICK = 4
    SATCOM = 5
    MIDS = 6
    SINCGARS = 7


class Coalition(IntEnum):
    SPECTATOR = 0
    RED = 1
    BLUE = 2


class RadioSwitchControls(IntEnum):
    HOTAS = 0
    IN_COCKPIT = 1


class EncryptionMode(IntEnum):
    NO_ENCRYPTION = 0
    ENCRYPTION_JUST_OVERLAY = 1
    ENCRYPTION_FULL = 2
    ENCRYPTION_COCKPIT_TOGGLE_OVERLAY_CODE = 3


class VolumeMode(IntEnum):
    COCKPIT = 0
    OVERLAY = 1


class FreqMode(IntEnum):
    COCKPIT = 0
    OVERLAY = 1


class RetransmitMode(IntEnum):
    COCKPIT = 0
    OVERLAY = 1
    DISABLED = 2


class IFFControlMode(IntEnum):
    COCKPIT = 0  # Realistic
    OVERLAY = 1  # SRS
    DISABLED = 2  # NOT FITTED AT ALL


class IFFStatus(IntEnum):
    OFF = 0
    NORMAL = 1
    IDENT = 2  # IDENT means Blink on LotATC


class RadioInformation(TypedDict):
    enc: bool
    encKey: int
    freq: float
    modulation: Modulation
    secFreq: float
    retransmit: bool


class Transponder(TypedDict):
    control: IFFControlMode
    mode1: int  # -1 = off, any other number on
    mode2: int  # -1 = OFF, any other number on
    mode3: int  # -1 = OFF, any other number on
    mode4: bool  # 1 = ON or 0 = OFF
    mic: int
    status: IFFStatus


class Ambient(TypedDict):
    vol: float
    abType: str


class RadioInfo(TypedDict):
    radios: list[RadioInformation]  # length of 11: 10 + intercom
    unit: str
    unitId: int
    iff: Transponder
    ambient: Ambient


class LatLngPosition(TypedDict):
    lat: float
    lng: float
    alt: float


class ClientInfo(TypedDict):
    Coalition: Coalition
    Name: str
    ClientGuid: Guid
    RadioInfo: RadioInfo
    LatLngPosition: LatLngPosition
    AllowRecord: bool
    Seat: int


def default_client_info(guid: Guid) -> ClientInfo:
    return {
        "Coalition": Coalition.SPECTATOR,
        "Name": "",
        "ClientGuid": guid,
        "RadioInfo": {
            "radios": [
                make_radio_information(),  # 0
                make_radio_information(),  # 1
                make_radio_information(),  # 2
                make_radio_information(),  # 3
                make_radio_information(),  # 4
                make_radio_information(),  # 5
                make_radio_information(),  # 6
                make_radio_information(),  # 7
                make_radio_information(),  # 8
                make_radio_information(),  # 9
                make_radio_information(),  # 10 (intercom)
            ],
            "unit": "",
            "unitId": 0,
            "iff": {
                "control": IFFControlMode.DISABLED,
                "mode1": -1,
                "mode2": -1,
                "mode3": -1,
                "mode4": False,
                "mic": -1,
                "status": IFFStatus.OFF,
            },
            "ambient": {
                "vol": 1.0,
                "abType": "",
            },
        },
        "LatLngPosition": {
            "lat": 0.0,
            "lng": 0.0,
            "alt": 0.0,
        },
        "AllowRecord": True,
        "Seat": 0,
    }


def make_radio_information(
    frequency: float = 1, modulation: Modulation = Modulation.DISABLED
) -> RadioInformation:
    return {
        "enc": False,
        "encKey": 0,
        "freq": frequency,
        "modulation": modulation,
        "secFreq": 1,
        "retransmit": False,
    }


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
