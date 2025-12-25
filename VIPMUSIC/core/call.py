# Copyright (C) 2024 by VISHAL-PANDEY@Github, < https://github.com/vishalpandeynkp1 >.
import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from ntgcalls import TelegramServerError
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    FloodWait,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls

# --- VERSION 3.0.0 COMPATIBILITY START ---
try:
    from pytgcalls.exceptions import AlreadyJoinedError, NoActiveGroupCall
except ImportError:
    from pytgcalls.exceptions import CallError as AlreadyJoinedError
    from pytgcalls.exceptions import GroupCallNotFound as NoActiveGroupCall

try:
    from pytgcalls.types import (
        JoinedGroupCallParticipant,
        LeftGroupCallParticipant,
        MediaStream,
        Update,
    )
except ImportError:
    # If using Version 3.0.0+ where these types are moved or renamed
    from pytgcalls.types import MediaStream, Update
    # Fallback for participants (V3 uses different event objects)
    class JoinedGroupCallParticipant: pass
    class LeftGroupCallParticipant: pass

from pytgcalls.types.stream import StreamAudioEnded
# --- VERSION 3.0.0 COMPATIBILITY END ---

import config
from strings import get_string
from VIPMUSIC import LOGGER, YouTube, app
from VIPMUSIC.misc import db
from VIPMUSIC.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_assistant,
    get_audio_bitrate,
    get_lang,
    get_loop,
    get_video_bitrate,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from VIPMUSIC.utils.exceptions import AssistantErr
from VIPMUSIC.utils.formatters import check_duration, seconds_to_min, speed_converter
from VIPMUSIC.utils.inline.play import stream_markup, telegram_markup
from VIPMUSIC.utils.stream.autoclear import auto_clean
from VIPMUSIC.utils.thumbnails import gen_thumb

autoend = {}
counter = {}
AUTO_END_TIME = 1

async def _st_(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)

async def _clear_(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)
    try:
        AMBOT = await app.send_message(chat_id, "🎶 **ꜱᴏɴɢ ʜᴀꜱ ᴇɴᴅᴇᴅ ɪɴ ᴠᴄ.**")
        await asyncio.sleep(5)
        await AMBOT.delete()
    except: pass

class Call(PyTgCalls):
    def __init__(self):
        self.userbot1 = Client(name="VIP1", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING1))
        self.one = PyTgCalls(self.userbot1)
        self.userbot2 = Client(name="VIP2", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING2))
        self.two = PyTgCalls(self.userbot2)
        self.userbot3 = Client(name="VIP3", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING3))
        self.three = PyTgCalls(self.userbot3)
        self.userbot4 = Client(name="VIP4", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING4))
        self.four = PyTgCalls(self.userbot4)
        self.userbot5 = Client(name="VIP5", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING5))
        self.five = PyTgCalls(self.userbot5)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_group_call(chat_id)
        except: pass

    async def join_call(self, chat_id: int, original_chat_id: int, link, video=None, image=None):
        assistant = await group_assistant(self, chat_id)
        audio_stream_quality = await get_audio_bitrate(chat_id)
        stream = MediaStream(link, audio_parameters=audio_stream_quality)
        try:
            await assistant.join_group_call(chat_id, stream)
        except AlreadyJoinedError: pass
        except NoActiveGroupCall:
            raise AssistantErr("Start Video Chat first!")
        except Exception as e:
            raise AssistantErr(f"Error: {e}")

        await add_active_chat(chat_id)
        await music_on(chat_id)

    async def ping(self):
        return "PONG"

    async def start(self):
        if config.STRING1: await self.one.start()
        if config.STRING2: await self.two.start()
        if config.STRING3: await self.three.start()
        if config.STRING4: await self.four.start()
        if config.STRING5: await self.five.start()

    async def decorators(self):
        @self.one.on_stream_end()
        async def handler(client, update: Update):
            if isinstance(update, StreamAudioEnded):
                pass # Logic to change stream

VIP = Call()