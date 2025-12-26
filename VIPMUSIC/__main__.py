import asyncio
import importlib
from pyrogram import idle
import config
from VIPMUSIC import HELPABLE, LOGGER, app, userbot
from VIPMUSIC.core.call import VIP
from VIPMUSIC.plugins import ALL_MODULES
from VIPMUSIC.utils.database import get_banned_users, get_gbanned

async def init():
    # Assistant check
    if not any([config.STRING1, config.STRING2, config.STRING3, config.STRING4, config.STRING5]):
        LOGGER("VIPMUSIC").error("No Assistant Clients Vars Defined!.. Exiting Process.")
        return

    # Database loading (Silent)
    try:
        users = await get_gbanned()
        for user_id in users:
            config.BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            config.BANNED_USERS.add(user_id)
    except:
        pass

    # --- BOT START ---
    await app.start()
    try:
        await app.send_message(config.LOG_GROUP_ID, "🕊️ **Mᴀɪɴ Bᴏᴛ Sᴛᴀʀᴛᴇᴅ!**")
    except:
        pass

    # Modules Load
    for all_module in ALL_MODULES:
        importlib.import_module(all_module)
    
    # --- ASSISTANT START ---
    await userbot.start()
    try:
        # Userbot (Assistant) Logger group mein message bhejegi
        await userbot.one.send_message(config.LOG_GROUP_ID, "🕊️ **Assɪsᴛᴀɴᴛ ID Sᴛᴀʀᴛᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ!**")
    except Exception as e:
        LOGGER("VIPMUSIC").error(f"Assistant log fail: {e}")

    await VIP.start()
    await VIP.decorators()
    LOGGER("VIPMUSIC").info("VIPMUSIC STARTED SUCCESSFULLY 🕊️")
    
    await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
