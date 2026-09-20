from fastapi import APIRouter, HTTPException, UploadFile

from services.elevenlabs_client import transcribe_audio

router = APIRouter(prefix="/speech", tags=["speech"])


@router.post("/transcribe")
async def transcribe_route(audio: UploadFile) -> dict[str, str]:
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="No audio received.")
    filename = audio.filename or "recording.webm"
    content_type = audio.content_type or "audio/webm"
    return {"text": transcribe_audio(audio_bytes, filename, content_type)}
