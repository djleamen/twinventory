from rembg import remove, new_session

# birefnet-general: better edge discrimination, handles same-color fg/bg well
# Model cached to ~/.rembg/ after first download
_session = new_session("birefnet-general")


def remove_background(image_bytes: bytes) -> bytes:
    return remove(image_bytes, session=_session, alpha_matting=True)
