import base64
from typing import NewType
import uuid


Guid = NewType("Guid", str)


def make_short_guid() -> Guid:
    guid = uuid.uuid4()
    b64guid = base64.b64encode(guid.bytes, altchars=b"-_")
    return b64guid[0:22].decode()
