import asyncio
import html
import re
from time import time

import emoji
from pyrogram import filters, Client
from pyrogram.enums import ParseMode
from pyrogram.types import ChatPermissions, Message

from wbb import SUDOERS, app
from wbb.core.decorators.errors import capture_err
from wbb.core.decorators.permissions import adminsOnly
from wbb.modules.admin import list_admins
from wbb.utils.dbfunctions import (
    delete_blacklist_filter,
    get_blacklisted_words,
    save_blacklist_filter,
)
from wbb.utils.filter_groups import blacklist_filters_group

__MODULE__ = "Blacklist"
__HELP__ = """
/blacklisted - Get All The Blacklisted Words In The Chat.
/blacklist [WORD|SENTENCE] - Blacklist A Word Or A Sentence.
/whitelist [WORD|SENTENCE] - Whitelist A Word Or A Sentence.
"""
chat_id = [-1001710412230,-1001629982867]

@app.on_message(filters.command("b",["","."]) & filters.chat(chat_id) & ~filters.private)
@adminsOnly("can_restrict_members")
async def save_filters(_, message: Message):
    chat_id = message.chat.id
    is_reply = True if message.reply_to_message else False
    if is_reply:
        words = message.reply_to_message.text if message.reply_to_message else message.text
    else:
        words = " ".join(message.command[1:])
    if not words:
        return await message.reply_text("Direp dong sayang?")
    if len(words) > 1:
        text = words
        to_blacklist = list(
            {trigger.strip() for trigger in text.split("\n") if trigger.strip()},
        )
        for trigger in to_blacklist:
            await save_blacklist_filter(chat_id, trigger.lower())
        if is_reply:
            await message.reply_to_message.delete()
        if len(to_blacklist) == 1:
            add = await message.reply_text(
                f"Added <code>{html.escape(to_blacklist[0])}</code> to the blacklist filters!",
                parse_mode=ParseMode.HTML,
            )
        else:
            add = await message.reply_text(
                f"Added <code>{len(to_blacklist)}</code> triggers to the blacklist filters!",
                parse_mode=ParseMode.HTML,
            )
        await asyncio.sleep(1)
        await add.delete()
        await message.delete()
    else:
        await message.reply_text(
            "Usage:\n/bl [triggers] - The words/sentences you want to blacklist",
        )

@app.on_message(filters.command("blacklisted") & filters.chat(chat_id) & ~filters.private)
@capture_err
async def get_filterss(_, message):
    data = await get_blacklisted_words(message.chat.id)
    if not data:
        await message.reply_text("**No blacklisted words in this chat.**")
    else:
        msg = f"List of blacklisted words in {message.chat.title} :\n"
        for word in data:
            msg += f"**-** `{word}`\n"
        await message.reply_text(msg)


@app.on_message(filters.command("whitelist") & filters.chat(chat_id) & ~filters.private)
@adminsOnly("can_restrict_members")
async def del_filter(_, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage:\n/whitelist [WORD|SENTENCE]")
    word = message.text.split(None, 1)[1].strip()
    if not word:
        return await message.reply_text("Usage:\n/whitelist [WORD|SENTENCE]")
    chat_id = message.chat.id
    deleted = await delete_blacklist_filter(chat_id, word)
    if deleted:
        return await message.reply_text(f"**Whitelisted {word}.**")
    await message.reply_text("**No such blacklist filter.**")


@app.on_message(filters.text & filters.chat(chat_id) & ~filters.private, group=blacklist_filters_group)
@capture_err
async def blacklist_filters_re(_, message):
    text = message.text.lower().strip()
    if not text:
        return
    chat_id = message.chat.id
    user = message.from_user
    if not user:
        return
    if user.id in SUDOERS:
        return
    list_of_filters = await get_blacklisted_words(chat_id)
    for word in list_of_filters:
        pattern = r"( |^|[^\w])" + re.escape(word) + r"( |$|[^\w])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            if user.id in await list_admins(chat_id):
                return
            try:
                await message.delete()
            except Exception as e:
                print(e, "error in blacklist filter")
                return


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
