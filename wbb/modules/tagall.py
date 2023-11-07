import asyncio
import html
import re
from random import shuffle
from time import time

from pyrogram import filters, Client
from pyrogram.enums import ParseMode
from pyrogram.types import ChatPermissions, Message

from wbb import SUDOERS, app

__MODULE__ = "Tagall"
__HELP__ = """
/all atau @all - To tag all of members.
/stoptg - To stop tagging.
"""
chat_id = [-1001710412230,-1001629982867]
tagallgcid = []

@app.on_message(filters.command("all",["/","@","."]) & filters.chat(chat_id) & ~filters.private)
async def tagall_batal_cmd(client, message: Message):
    if message.chat.id in tagallgcid:
        return
    tagallgcid.append(message.chat.id)
    text = message.text.split(None, 1)[1] if len(message.text.split()) != 1 else ""
    users = [
        member.user.mention
        async for member in message.chat.get_members()
        if not (member.user.is_bot or member.user.is_deleted)
    ]
    shuffle(users)
    m = message.reply_to_message or message
    for output in [users[i : i + 5] for i in range(0, len(users), 5)]:
        if message.chat.id not in tagallgcid:
            break
        await asyncio.sleep(1.5)
        await m.reply_text(
            ", ".join(output) + "\n\n" + text, quote=bool(message.reply_to_message)
        )
    try:
        tagallgcid.remove(message.chat.id)
    except Exception:
        pass


@app.on_message(filters.command("stoptg",["/","."]) & filters.chat(chat_id) & ~filters.private)
async def on_stop_tag_handler(c: Client, m: Message):
    if m.chat.id not in tagallgcid:
        return await m.reply_text(
            "sedang tidak ada perintah: <code>all</code> yang digunakan"
        )
    try:
        tagallgcid.remove(m.chat.id)
    except Exception:
        pass
    await m.reply_text("ok tagall berhasil dibatalkan")
