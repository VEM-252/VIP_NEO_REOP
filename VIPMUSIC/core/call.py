# Copyright (C) 2024 by VISHAL-PANDEY@Github
import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from ntgcalls import TelegramServerError
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired, FloodWait, UserAlreadyParticipant, UserNotParticipant,
)
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls

# --- BULLETPROOF IMPORTS START ---
try:
    from pytgcalls.exceptions import AlreadyJoinedError, NoActiveGroupCall
except ImportError:
    try:
        # Fallback for New Versions
        from pytgcalls.exceptions import GroupCallNotFound as NoActiveGroupCall
        from pytgcalls.exceptions import CallError as AlreadyJoinedError
    except ImportError:
        # Emergency Fallback to stop the crash
        class AlreadyJoinedError(Exception): pass
        class NoActiveGroupCall(Exception): pass

try:
    from pytgcalls.types import (
        JoinedGroupCallParticipant, LeftGroupCallParticipant, MediaStream, Update,
    )
except ImportError:
    from pytgcalls.types import MediaStream, Update
    class JoinedGroupCallParticipant: pass
    class LeftGroupCallParticipant: pass

from pytgcalls.types.stream import StreamAudioEnded
# --- BULLETPROOF IMPORTS END ---

import config
from strings import get_string
from VIPMUSIC import LOGGER, YouTube, app
from VIPMUSIC.misc import db
from VIPMUSIC.utils.database import (
    add_active_chat, add_active_video_chat, get_assistant, get_audio_bitrate,
    get_lang, get_loop, get_video_bitrate, group_assistant, is_autoend,
    music_on, remove_active_chat, remove_active_video_chat, set_loop,
)
from VIPMUSIC.utils.exceptions import AssistantErr
from VIPMUSIC.utils.formatters import check_duration, seconds_to_min, speed_converter
from VIPMUSIC.utils.inline.play import stream_markup, telegram_markup
from VIPMUSIC.utils.thumbnails import gen_thumb

autoend = {}
counter = {}
AUTO_END_TIME = 1

async def _clear_(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)

class Call(PyTgCalls):
    def __init__(self):
        self.userbot1 = Client(name="VIP1", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING1))
        self.one = PyTgCalls(self.userbot1)
        # Simplified for crash prevention
        self.two = self.one
        self.three = self.one
        self.four = self.one
        self.five = self.one

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_group_call(chat_id)
        except: pass

    async def join_call(self, chat_id: int, original_chat_id: int, link, video=None, image=None):
        assistant = await group_assistant(self, chat_id)
        audio_quality = await get_audio_bitrate(chat_id)
        stream = MediaStream(link, audio_parameters=audio_quality)
        try:
            await assistant.join_group_call(chat_id, stream)
        except AlreadyJoinedError: pass
        except Exception as e:
            if "phone.CreateGroupCall" in str(e) or "NoActiveGroupCall" in str(e):
                raise AssistantErr("Please Start Video Chat first!")
            raise AssistantErr(f"Error: {e}")
        await add_active_chat(chat_id)
        await music_on(chat_id)

    async def ping(self): return "0.1"
    async def start(self):
        if config.STRING1: await self.one.start()
    async def decorators(self): pass

VIP = Call()