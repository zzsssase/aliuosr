# Ayra - UserBot
# Copyright (C) 2021-2022 senpai80
#
# This file is a part of < https://github.com/senpai80/Ayra/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/senpai80/Ayra/blob/main/LICENSE/>.
"""
 **اوامــر المنشن**

๏ ** `منشن` 
◉ **الاستخدام:** يستخدم لعمل منشن للأعضاء دخل المجموعة**

๏ `الغاء منشن`
◉ **الاستخدام:** يستخدم لايقاف المنشن داخل المجموعة**
"""

import asyncio

from . import *


class FlagContainer:
    is_active = False


@ayra_cmd(pattern="mention(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    await event.delete()
    query = event.pattern_match.group(1)
    mentions = f"@all {query}"
    chat = await event.get_input_chat()
    async for x in event.client.iter_participants(chat, 100500):
        mentions += f"[\u2063](tg://user?id={x.id} {query})"
    await event.client.send_message(
        chat, mentions, reply_to=event.message.reply_to_msg_id
    )


@ayra_cmd(pattern="الغاء منشن(?: |$)")
async def cancel_all(event):
    FlagContainer.is_active = False
    await event.reply("✅ Berhasil membatalkan tagall.")


@ayra_cmd(pattern="منشن(?: |$)(.*)")
async def _(event):
    if event.fwd_from or FlagContainer.is_active:
        return
    try:
        FlagContainer.is_active = True
        args = event.message.text.split(" ", 1)
        text = await event.get_reply_message() if event.reply_to else args[1]
        chat = await event.get_input_chat()
        await event.delete()
        tags = list(
            map(
                lambda m: f"👤 [{m.first_name}](tg://user?id={m.id})\n",
                await event.client.get_participants(chat),
            ),
        )
        jumlah = []
        async for participant in event.client.iter_participants(chat):
            if not FlagContainer.is_active:
                break
            jumlah.append(participant)
            if len(jumlah) == 5:
                tags = list(
                    map(
                        lambda m: f"👤 [{m.first_name}](tg://user?id={m.id})\n",
                        jumlah,
                    ),
                )
                jumlah = []
                if text:
                    tags.append(str(text))
                await event.client.send_message(event.chat_id, "".join(tags))
                await asyncio.sleep(5)
            elif not FlagContainer.is_active:
                break
    finally:
        FlagContainer.is_active = False
