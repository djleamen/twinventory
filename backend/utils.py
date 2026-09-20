import base64
import mimetypes
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

UPLOADS_DIR = Path(__file__).parent / "uploads"


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def resolve_image_url(image_url: str) -> str:
    """External APIs can't reach our local /static uploads, so inline them as data URIs."""
    if not image_url.startswith("/static/"):
        return image_url
    path = UPLOADS_DIR / Path(image_url).name
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"
