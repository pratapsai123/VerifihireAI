"""
Edge TTS Engine
Uses Microsoft Edge's Neural TTS for high-quality, lightweight speech synthesis.
"""
import io
import asyncio
import logging
import edge_tts

logger = logging.getLogger(__name__)

# Using Microsoft's neural voice - 'Ava' is very natural and clear
DEFAULT_VOICE = "en-US-AvaNeural"

class EdgeTTSEngine:
    """Wraps the edge-tts library for high-speed, high-quality synthesis."""

    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize text to WAV audio bytes using Edge TTS.
        """
        if not text or not text.strip():
            return b""

        try:
            communicate = edge_tts.Communicate(text, DEFAULT_VOICE)
            buffer = io.BytesIO()
            
            # edge-tts generates MP3/Opus data by default, 
            # we'll stream it into a buffer.
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    buffer.write(chunk["data"])

            buffer.seek(0)
            return buffer.read()
        except Exception as e:
            logger.error(f"Edge TTS Synthesis Error: {str(e)}")
            raise

def get_tts_engine():
    """Returns a simple instance (no singleton needed for Edge TTS as it's stateless)."""
    return EdgeTTSEngine()
