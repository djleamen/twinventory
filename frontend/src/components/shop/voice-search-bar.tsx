"use client"

import { useEffect, useRef, useState } from "react"
import { LoaderCircleIcon, MicIcon } from "lucide-react"
import { toast } from "sonner"
import { Input } from "@/components/ui/input"
import { transcribeAudio } from "@/lib/api/speech"
import { cn } from "@/lib/utils"

const WAVE_BARS = [
  { height: "h-2", delay: "0s" },
  { height: "h-4", delay: "0.1s" },
  { height: "h-5", delay: "0.2s" },
  { height: "h-4", delay: "0.3s" },
  { height: "h-2", delay: "0.4s" },
]

type Props = {
  value: string
  onChange: (value: string) => void
  isLoading?: boolean
}

export function VoiceSearchBar({ value, onChange, isLoading }: Props) {
  const [isRecording, setIsRecording] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])

  useEffect(() => {
    return () => {
      const recorder = mediaRecorderRef.current
      if (recorder && recorder.state !== "inactive") recorder.stop()
    }
  }, [])

  async function startRecording() {
    if (isRecording || isTranscribing) return
    if (typeof navigator === "undefined" || !navigator.mediaDevices?.getUserMedia) {
      toast.error("Voice search isn't supported in this browser.")
      return
    }

    let stream: MediaStream
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    } catch {
      toast.error("Couldn't access the microphone. Check your browser permissions.")
      return
    }

    const recorder = new MediaRecorder(stream)
    chunksRef.current = []
    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data)
    }
    recorder.onstop = () => {
      stream.getTracks().forEach((track) => track.stop())
      void finishRecording(new Blob(chunksRef.current, { type: recorder.mimeType }))
    }
    mediaRecorderRef.current = recorder
    recorder.start()
    setIsRecording(true)
  }

  function stopRecording() {
    const recorder = mediaRecorderRef.current
    if (!recorder || recorder.state === "inactive") return
    recorder.stop()
    setIsRecording(false)
  }

  async function finishRecording(audio: Blob) {
    if (!audio.size) return
    setIsTranscribing(true)
    try {
      const text = await transcribeAudio(audio)
      if (text) onChange(text)
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Voice search failed. Try again.")
    } finally {
      setIsTranscribing(false)
    }
  }

  const busy = isTranscribing || isLoading

  return (
    <div className="relative">
      <label htmlFor="search" className="sr-only">
        Search clothing
      </label>

      <button
        type="button"
        aria-label={isRecording ? "Release to stop speaking" : "Hold to speak your search"}
        aria-pressed={isRecording}
        disabled={isTranscribing}
        onPointerDown={(e) => {
          e.preventDefault()
          e.currentTarget.setPointerCapture(e.pointerId)
          void startRecording()
        }}
        onPointerUp={stopRecording}
        onPointerLeave={() => isRecording && stopRecording()}
        onPointerCancel={stopRecording}
        onKeyDown={(e) => {
          if ((e.key === " " || e.key === "Enter") && !isRecording) {
            e.preventDefault()
            void startRecording()
          }
        }}
        onKeyUp={(e) => {
          if (e.key === " " || e.key === "Enter") stopRecording()
        }}
        className={cn(
          "absolute top-1/2 left-2.5 z-10 flex size-8 -translate-y-1/2 touch-none items-center justify-center rounded-lg transition-colors select-none disabled:opacity-50",
          isRecording
            ? "bg-primary text-primary-foreground"
            : "text-muted-foreground hover:bg-accent hover:text-foreground",
        )}
      >
        <MicIcon className="size-5" aria-hidden="true" />
      </button>

      <Input
        id="search"
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        readOnly={isRecording}
        placeholder={'Try speaking "winter layers" or "something for a summer wedding"'}
        className={cn("h-13 rounded-xl bg-card pl-12 text-base md:text-base", isRecording && "text-transparent")}
      />

      {isRecording && (
        <div
          className="pointer-events-none absolute top-1/2 left-12 flex -translate-y-1/2 items-center gap-1"
          aria-hidden="true"
        >
          {WAVE_BARS.map((bar, i) => (
            <span
              key={i}
              style={{ animationDelay: bar.delay }}
              className={cn("w-1 animate-[waveform_1s_ease-in-out_infinite] rounded-full bg-primary", bar.height)}
            />
          ))}
        </div>
      )}

      {busy && !isRecording && (
        <LoaderCircleIcon
          className="pointer-events-none absolute top-1/2 right-4 size-4 -translate-y-1/2 animate-spin text-muted-foreground"
          aria-hidden="true"
        />
      )}
    </div>
  )
}
