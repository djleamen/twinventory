import { apiFetchForm } from "./client"

/** POST /speech/transcribe — sends a recorded audio clip, gets back the transcript. */
export async function transcribeAudio(audio: Blob): Promise<string> {
  const ext = audio.type.split("/")[1]?.split(";")[0] || "webm"
  const formData = new FormData()
  formData.append("audio", audio, `recording.${ext}`)
  const { text } = await apiFetchForm<{ text: string }>("/speech/transcribe", formData)
  return text
}
