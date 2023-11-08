import re

import emoji
from pyrogram import filters
from pyrogram.types import Message

from wbb import app

__MODULE__ = "Auto"
__HELP__ = """
/ah ah 
"""
chat_id = [-1001710412230,-1001629982867]


@app.on_message(filters.text & filters.chat(-1001629982867) & ~filters.private, group=5)
async def dk_validate_bl(message: Message):
    text = message.text or None
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
    return text_5
