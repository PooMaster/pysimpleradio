"""
UDP PACKET LAYOUT

- HEADER SEGMENT
UInt16 Packet Length - 2 bytes
UInt16 AudioPart1 Length - 2 bytes
UInt16 FrequencyPart Length - 2 bytes
- AUDIO SEGMENT
Bytes AudioPart1 - variable bytes
- FREQUENCY SEGMENT (one or multiple)
double Frequency - 8 bytes
byte Modulation - 1 byte
byte Encryption - 1 byte
- FIXED SEGMENT
UInt UnitId - 4 bytes
UInt64 PacketId - 8 bytes
byte Retransmit / node / hop count - 1 byte
Bytes / ASCII String TRANSMISSION GUID - 22 bytes used for transmission relay
Bytes / ASCII String CLIENT GUID - 22 bytes
"""

from dataclasses import dataclass
from typing import NamedTuple, Self
import struct

from .client_info import Modulation
from .utils import Guid


class Frequency(NamedTuple):
    frequency: float
    modulation: Modulation


header_length = 2 + 2 + 2
trailer_length = 4 + 8 + 1 + 22 + 22
single_frequency_length = 8 + 1 + 1


@dataclass
class VoicePacket:
    audio_data: bytes
    frequencies: list[Frequency]
    unit_id: int
    packet_id: int
    guid: Guid
    hop_count: int = 0
    original_client_guid: Guid = ""

    def serialize(self) -> bytes:
        if self.original_client_guid == "":
            self.original_client_guid = self.guid

        audio_length = len(self.audio_data)
        frequency_length = single_frequency_length * len(self.frequencies)

        packet_length = header_length + audio_length + frequency_length + trailer_length

        header = struct.pack("<HHH", packet_length, audio_length, frequency_length)
        frequency_segment = b"".join(
            struct.pack("<dBB", f.frequency, f.modulation, 0) for f in self.frequencies
        )
        trailer_segment = struct.pack(
            "<IQB", self.unit_id, self.packet_id, self.hop_count
        )

        return (
            header
            + self.audio_data
            + frequency_segment
            + trailer_segment
            + self.original_client_guid.encode()
            + self.guid.encode()
        )

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        packet_length, audio_length, frequency_length = struct.unpack_from(
            "<HHH", data, offset=0
        )

        audio_data = data[header_length : header_length + audio_length]

        frequencies = []
        for offset in range(0, frequency_length, single_frequency_length):
            freq, modulation, encryption = struct.unpack_from(
                "<dBB", data, header_length + audio_length + offset
            )
            frequencies.append(Frequency(freq, Modulation(modulation)))

        unit_id, packet_id, hop_count = struct.unpack_from(
            "<IQB", data, offset=header_length + audio_length + frequency_length
        )

        original_client_guid = data[-44:-22].decode()
        guid = data[-22:].decode()

        return cls(
            audio_data,
            frequencies,
            unit_id,
            packet_id,
            guid,
            hop_count,
            original_client_guid,
        )
