# app/speech/stt.py
# Deepgram real-time STT.

import asyncio
from contextlib import asynccontextmanager
from deepgram import AsyncDeepgramClient # async variant (DGClient is sync-only)
from deepgram.listen.v1.types.listen_v1results import ListenV1Results # type

async def _listen_loop(connection, on_transcript):
    # SDK yields parsed message objects as Deepgram sends them
    async for msg in connection:
        # skip interim/partial results and metadata messages
        if isinstance(msg, ListenV1Results) and msg.is_final:
            # best transcript candidate
            text = msg.channel.alternatives[0].transcript
            if text: # skip empty finals (silence, noise)
                await on_transcript(text)

@asynccontextmanager
async def deepgram_stream(on_transcript):
    client = AsyncDeepgramClient() # reads DEEPGRAM_API_KEY from env
    async with client.listen.v1.connect(
        model="nova-2",
        encoding="mulaw", # matches Twilio Media Streams audio format
        sample_rate=8000, # matches Twilio Media Streams sample rate
        punctuate=True,
    ) as connection:
        # run listener concurrently while caller sends audio
        task = asyncio.create_task(_listen_loop(connection, on_transcript))
        try:
            # handler.py sends audio via connection.send_media(bytes) here
            yield connection
        finally:
            task.cancel() # stop listener when WebSocket closes