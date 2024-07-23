import base64
import uuid


def make_short_guid() -> str:
    guid = uuid.uuid4()
    b64guid = base64.b64encode(guid.bytes, altchars=b"-_")
    return b64guid[0:22].decode()
