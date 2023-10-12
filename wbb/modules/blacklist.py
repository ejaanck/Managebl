"""
MIT License

Copyright (c) 2023 TheHamkerCat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import re
from time import time

from pyrogram import filters
from pyrogram.types import ChatPermissions

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


@app.on_message(filters.command("bl") & ~filters.private)
@adminsOnly("can_restrict_members")
async def save_filters(_, message):
    chat = update.effective_chat
    user = update.effective_user
    args = context.args

    conn = connected(context.bot, update, chat, user.id, need_admin=False)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if chat.type == "private":
            return
        chat_id = update.effective_chat.id
        chat_name = chat.title

    filter_list = "Current blacklisted words in <b>{}</b>:\n".format(chat_name)

    all_blacklisted = sql.get_chat_blacklist(chat_id)

    if len(args) > 0 and args[0].lower() == "copy":
        for trigger in all_blacklisted:
            filter_list += "<code>{}</code>\n".format(html.escape(trigger))
    else:
        for trigger in all_blacklisted:
            filter_list += " - <code>{}</code>\n".format(html.escape(trigger))

    # for trigger in all_blacklisted:
    #     filter_list += " - <code>{}</code>\n".format(html.escape(trigger))

    split_text = split_message(filter_list)
    for text in split_text:
        if filter_list == "Current blacklisted words in <b>{}</b>:\n".format(
            html.escape(chat_name),
        ):
            send_message(
                update.effective_message,
                "No blacklisted words in <b>{}</b>!".format(html.escape(chat_name)),
                parse_mode=ParseMode.HTML,
            )
            return
        send_message(update.effective_message, text, parse_mode=ParseMode.HTML)

@app.on_message(filters.command("blacklisted") & ~filters.private)
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


@app.on_message(filters.command("whitelist") & ~filters.private)
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


@app.on_message(filters.text & ~filters.private, group=blacklist_filters_group)
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
                await message.chat.restrict_member(
                    user.id,
                    ChatPermissions(),
                    until_date=int(time() + 3600),
                )
            except Exception:
                return
            return await app.send_message(
                chat_id,
                f"Muted {user.mention} [`{user.id}`] for 1 hour "
                + f"due to a blacklist match on {word}.",
            )
