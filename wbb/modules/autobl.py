import re
import traceback

import emoji
from pyrogram import filters, Client
from pyrogram.types import Message

from wbb import app
from wbb.modules.admin import list_admins

__MODULE__ = "AutoBlacklist"
__HELP__ = """
/autoblacklist - apa ini?
/autoblacklistd - ini apa?
"""

chat_id = [-1001710412230, -1001629982867]


@app.on_message(filters.text & filters.chat(chat_id) & ~filters.private, group=1)
async def dk_validate_bl(c: Client, message: Message):
    try:
        text = message.text or None
        if message.from_user.id in await list_admins(message.chat.id):
            return
        if not text:
            return False
        # remove emojis first
        text_parts = []
        current_text = ""
        for char in text:
            if emoji.emoji_count(char) == 0:
                current_text += char
            else:
                if current_text:
                    text_parts.append(current_text)
                current_text = ""
        if current_text:
            text_parts.append(current_text)
        text_2 = ""
        for part in text_parts:
            text_2 += part

        # remove numbers from text
        text_3 = re.sub(r'[0-9]+', '', text_2)
        #check if text is uppercase
        # text_4 = text_3.isupper()
        # check if text uppercase is more than lowercase
        text_5 = sum(1 for c in text_3 if c.isupper()) > sum(1 for c in text_3 if c.islower())
        if text_5:
            await message.delete()
            return True
    except Exception as e:
        print(traceback.format_exc())
        return False

@app.on_message(filters.command("asu",["/","."]))
async def dk_autoblacklist(_, message: Message):
    await message.reply_text("apa ini2?")
