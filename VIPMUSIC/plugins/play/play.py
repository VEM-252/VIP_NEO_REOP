#
# Copyright (C) 2024 by THE-VIP-BOY-OP@Github, < https://github.com/THE-VIP-BOY-OP >.
#
# This file is part of < https://github.com/THE-VIP-BOY-OP/VIP-MUSIC > project,
# and is released under the MIT License.
# Please see < https://github.com/THE-VIP-BOY-OP/VIP-MUSIC/blob/master/LICENSE >
#
# All rights reserved.
#
import asyncio
import random
import string
from time import time

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto, Message
from pytgcalls.exceptions import NoActiveGroupCall

import config
from config import BANNED_USERS, lyrical
from VIPMUSIC import Apple, Resso, SoundCloud, Spotify, Telegram, YouTube, app
from VIPMUSIC.core.call import VIP
from VIPMUSIC.utils import seconds_to_min, time_to_seconds
from VIPMUSIC.utils.channelplay import get_channeplayCB
from VIPMUSIC.utils.database import add_served_chat, get_assistant, is_video_allowed
from VIPMUSIC.utils.decorators.language import languageCB
from VIPMUSIC.utils.decorators.play import PlayWrapper
from VIPMUSIC.utils.formatters import formats
from VIPMUSIC.utils.inline.play import (
    livestream_markup,
    playlist_markup,
    slider_markup,
    track_markup,
)
from VIPMUSIC.utils.inline.playlist import botplaylist_markup
from VIPMUSIC.utils.logger import play_logs
from VIPMUSIC.utils.stream.stream import stream

user_last_message_time = {}
user_command_count = {}
SPAM_WINDOW_SECONDS = 5 
SPAM_THRESHOLD = 2


@app.on_message(
    filters.command(
        [
            "play",
            "vplay",
            "cplay",
            "cvplay",
            "playforce",
            "vplayforce",
            "cplayforce",
            "cvplayforce",
        ],
        prefixes=["/", "!", "%", ",", "@", "#"],
    )
    & filters.group
    & ~BANNED_USERS
)
@PlayWrapper
async def play_commnd(
    client, message: Message, _, chat_id, video, channel, playmode, url, fplay
):
    # Force Audio/Video Logic
    command_check = message.command[0].lower()
    if command_check.startswith("v") or command_check.startswith("cv"):
        video = True
    else:
        video = None

    userbot = await get_assistant(message.chat.id)
    user_id = message.from_user.id
    current_time = time()
    last_message_time = user_last_message_time.get(user_id, 0)

    if current_time - last_message_time < SPAM_WINDOW_SECONDS:
        user_last_message_time[user_id] = current_time
        user_command_count[user_id] = user_command_count.get(user_id, 0) + 1
        if user_command_count[user_id] > SPAM_THRESHOLD:
            hu = await message.reply_text(f"**{message.from_user.mention} ᴘʟᴇᴀsᴇ ᴅᴏɴ'ᴛ sᴘᴀᴍ.**")
            await asyncio.sleep(3)
            await hu.delete()
            return
    else:
        user_command_count[user_id] = 1
        user_last_message_time[user_id] = current_time

    await add_served_chat(message.chat.id)
    mystic = await message.reply_text(_["play_2"].format(channel) if channel else _["play_1"])

    plist_id = None
    slider = None
    plist_type = None
    spotify = None
    user_name = message.from_user.first_name

    # Check for Audio files only (Video reply disabled)
    audio_telegram = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )

    if audio_telegram:
        if audio_telegram.file_size > config.TG_AUDIO_FILESIZE_LIMIT:
            return await mystic.edit_text(_["play_5"])
        duration_min = seconds_to_min(audio_telegram.duration)
        if (audio_telegram.duration) > config.DURATION_LIMIT:
            return await mystic.edit_text(_["play_6"].format(config.DURATION_LIMIT_MIN, duration_min))
        
        file_path = await Telegram.get_filepath(audio=audio_telegram)
        if await Telegram.download(_, message, mystic, file_path):
            message_link = await Telegram.get_link(message)
            file_name = await Telegram.get_filename(audio_telegram, audio=True)
            dur = await Telegram.get_duration(audio_telegram)
            details = {"title": file_name, "link": message_link, "path": file_path, "dur": dur}

            try:
                await stream(_, mystic, user_id, details, chat_id, user_name, message.chat.id, streamtype="telegram", forceplay=fplay)
            except Exception as e:
                return await mystic.edit_text(f"Error: {e}")
            return await mystic.delete()
        return

    # If it's a URL
    elif url:
        if await YouTube.exists(url):
            if "playlist" in url:
                try:
                    details = await YouTube.playlist(url, config.PLAYLIST_FETCH_LIMIT, message.from_user.id)
                except:
                    return await mystic.edit_text(_["play_3"])
                streamtype = "playlist"
                plist_type = "yt"
                plist_id = (url.split("=")[1]).split("&")[0] if "&" in url else url.split("=")[1]
                img = config.PLAYLIST_IMG_URL
                cap = _["play_10"]
            else:
                try:
                    details, track_id = await YouTube.track(url)
                except:
                    return await mystic.edit_text(_["play_3"])
                streamtype = "youtube"
                img = details["thumb"]
                cap = _["play_11"].format(details["title"], details["duration_min"])
        
        elif await Spotify.valid(url):
            spotify = True
            if "track" in url:
                try: details, track_id = await Spotify.track(url)
                except: return await mystic.edit_text(_["play_3"])
                streamtype = "youtube"
                img = details["thumb"]
                cap = _["play_11"].format(details["title"], details["duration_min"])
            elif "playlist" in url:
                try: details, plist_id = await Spotify.playlist(url)
                except: return await mystic.edit_text(_["play_3"])
                streamtype = "playlist"
                plist_type = "spplay"
                img = config.SPOTIFY_PLAYLIST_IMG_URL
                cap = _["play_12"].format(message.from_user.first_name)
            else:
                return await mystic.edit_text("Invalid Spotify URL")
        
        # Other URL types (Soundcloud, etc.) remain same...
        else:
            # Simple handling for other streamable URLs
            try:
                await stream(_, mystic, user_id, url, chat_id, user_name, message.chat.id, video=video, streamtype="index", forceplay=fplay)
            except Exception as e:
                return await mystic.edit_text(f"Error: {e}")
            return await mystic.delete()

    # Search Query logic
    else:
        if len(message.command) < 2:
            buttons = botplaylist_markup(_)
            return await mystic.edit_text(_["playlist_1"], reply_markup=InlineKeyboardMarkup(buttons))
        
        slider = True
        query = message.text.split(None, 1)[1]
        try:
            details, track_id = await YouTube.track(query)
        except:
            return await mystic.edit_text(_["play_3"])
        streamtype = "youtube"

    # Play logic execution
    if str(playmode) == "Direct":
        try:
            await stream(_, mystic, user_id, details, chat_id, user_name, message.chat.id, video=video, streamtype=streamtype, spotify=spotify, forceplay=fplay)
        except Exception as e:
            return await mystic.edit_text(f"Error: {e}")
        await mystic.delete()
        return await play_logs(message, streamtype=streamtype)
    
    else:
        # Inline markup / Slider logic remains same
        if slider:
            buttons = slider_markup(_, track_id, message.from_user.id, query, 0, "c" if channel else "g", "f" if fplay else "d")
            await mystic.delete()
            await message.reply_photo(photo=details["thumb"], caption=_["play_11"].format(details["title"].title(), details["duration_min"]), reply_markup=InlineKeyboardMarkup(buttons))
        else:
            buttons = track_markup(_, track_id, message.from_user.id, "c" if channel else "g", "f" if fplay else "d")
            await mystic.delete()
            await message.reply_photo(photo=img, caption=cap, reply_markup=InlineKeyboardMarkup(buttons))
        return await play_logs(message, streamtype="Search")

# Baki ke callback functions (MusicStream, slider, etc.) same rahenge...
# (Aapki file ke niche wale callback query functions ko yahan as it is rehne dein)