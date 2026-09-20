from functools import cache

from rembg import remove, new_session


@cache
def get_session():
    return new_session("birefnet-general")


def remove_background(image_bytes: bytes) -> bytes:
    return remove(image_bytes, session=get_session(), alpha_matting=True)
