"""Lightweight voice in/out for consumer GUI (Windows-first)."""

from __future__ import annotations

import logging

logger = logging.getLogger("main")


def speak_text(assistant, text: str) -> None:
    """Speak via assistant TTS if configured."""
    if not text or not assistant:
        return
    try:
        if getattr(assistant, "voice_type", "none") == "none":
            return
        if hasattr(assistant, "speak"):
            assistant.speak(text)
    except Exception as exc:
        logger.warning("[VOICE] TTS failed: %s", exc)


def listen_once(timeout: int = 8, phrase_limit: int = 20) -> str | None:
    """Push-to-talk: capture one utterance from the default microphone.

    Uses Google Web Speech API (free tier, requires internet — same as Groq brain).
    Returns transcribed text or None on failure/cancel.
    """
    try:
        import speech_recognition as sr
    except ImportError:
        logger.warning("[VOICE] speech_recognition not installed")
        return None

    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.4)
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_limit,
            )
        return recognizer.recognize_google(audio)
    except sr.WaitTimeoutError:
        return None
    except sr.UnknownValueError:
        return None
    except Exception as exc:
        logger.warning("[VOICE] STT failed: %s", exc)
        return None
