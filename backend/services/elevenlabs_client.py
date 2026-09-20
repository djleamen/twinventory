from functools import lru_cache
from io import BytesIO

from elevenlabs import ElevenLabs

from utils import _get_required_env


@lru_cache(maxsize=1)
def get_elevenlabs_client() -> ElevenLabs:
    return ElevenLabs(api_key=_get_required_env("ELEVENLABS_API_KEY"))


def transcribe_audio(audio_bytes: bytes, filename: str, content_type: str) -> str:
    response = get_elevenlabs_client().speech_to_text.convert(
        model_id="scribe_v2",
        file=(filename, BytesIO(audio_bytes), content_type),
    )
    return response.text
