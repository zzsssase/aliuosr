# Ayra - UserBot
# Copyright (C) 2021-2022 senpai80
#
# This file is a part of < https://github.com/senpai80/Ayra/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/senpai80/Ayra/blob/main/LICENSE/>.

"""
~ **اوامـر الميوزك**

๏  `انضمام`
◉ **الاستخدام:**يتم استخدام الامر اذا كانت اغنيه فيها تقطيع.

๏  `تخطي`
◉ **الاستخدام:** يستخدم لتخطي تشغيل الاغنيه**.

๏  `تشغيل` 
◉ **الاستخدام:** تشغيل + اسم الاغنية او بالرد على ملف صوتي**.

๏  `فيديو`
◉ **الاستخدام:** فيديو + اسم الاغنية او بالرد على مقطع فيديو**.

๏ `مؤقت`
◉ **الاستخدام:** لكتم الاغنيه مؤقت.

๏ ** `ايقاف مؤقت`
◉ **الاستخدام:**يستخدم لايقاف تشغيل الاغنيه مؤقت**.

๏ `الغاء مؤقت`
◉ **الاستخدام:**يستخدم لألغاء كتم عن الاغنية**.

๏ `استئناف`
◉ **الاستخدام:** يستخدم لاستئناف التشغيل**.

๏ `رفع معنمد`
◉ **الاستخدام:** يستخدم لاضافة الشخص لقائمة المعتمدين لتشغيل الاغاني.

๏ `ازاله المعتمد`
◉ **الاستخدام:** يستخدم لازالة صلاحيات المستخدم المعتمد**.

๏  `المعتمدين`
◉ **الاستخدام:** يستخدم لعرض قائمة المستخدمين المعتمدين**.


"""

import os
import re

from Ayra.dB.vc_sudos import *
from Ayra.fns.helper import *
from Ayra.fns.info import *
from Ayra.fns.misc import *
from Ayra.fns.tools import *
from pytgcalls.exceptions import NotConnectedError
from telethon.errors.rpcerrorlist import (ChatSendMediaForbiddenError,
                                          MessageIdInvalidError)

from . import *
from ._music import *


@vc_asst("تشغيل")
async def play_music_(event):
    if "playfrom" in event.text.split()[0]:
        return  # For PlayFrom Conflict
    try:
        xx = await event.eor(get_string("com_1"), parse_mode="md")
    except MessageIdInvalidError:
        # Changing the way, things work
        xx = event
        xx.out = False
    chat = event.chat_id
    from_user = inline_mention(event.sender, html=True)
    reply, song = None, None
    if event.reply_to:
        reply = await event.get_reply_message()
    if len(event.text.split()) > 1:
        input = event.text.split(maxsplit=1)[1]
        tiny_input = input.split()[0]
        if tiny_input[0] in ["@", "-"]:
            try:
                chat = await event.client.parse_id(tiny_input)
            except Exception as er:
                LOGS.exception(er)
                return await xx.edit(str(er))
            try:
                song = input.split(maxsplit=1)[1]
            except IndexError:
                pass
            except Exception as e:
                return await event.eor(str(e))
        else:
            song = input
    if not (reply or song):
        return await xx.eor(
            "Harap tentukan nama lagu atau balas ke file audio !", time=5
        )
    await xx.eor(get_string("vcbot_20"), parse_mode="md")
    if reply and reply.media and mediainfo(reply.media).startswith(("audio", "video")):
        song, thumb, song_name, link, duration = await file_download(xx, reply)
    else:
        song, thumb, song_name, link, duration = await download(song)
        if len(link.strip().split()) > 1:
            link = link.strip().split()
    aySongs = Player(chat, event)
    song_name = f"{song_name[:30]}..."
    if not aySongs.group_call.is_connected:
        if not (await aySongs.vc_joiner()):
            return
        await aySongs.group_call.start_audio(song)
        if isinstance(link, list):
            for lin in link[1:]:
                add_to_queue(chat, song, lin, lin, None, from_user, duration)
            link = song_name = link[0]
        text = "📀 <strong>Sedang dimainkan: <a href={}>{}</a>\n⏰ Durasi:</strong> <code>{}</code>\n👥 <strong>Di:</strong> <code>{}</code>\n🙋‍♂ <strong>Diminta oleh: {}</strong>".format(
            link, song_name, duration, chat, from_user
        )
        try:
            await xx.reply(
                text,
                file=thumb,
                link_preview=False,
                parse_mode="html",
            )
            await xx.delete()
        except ChatSendMediaForbiddenError:
            await xx.eor(text, link_preview=False)
        if thumb and os.path.exists(thumb):
            os.remove(thumb)
    else:
        if not (
            reply
            and reply.media
            and mediainfo(reply.media).startswith(("audio", "video"))
        ):
            song = None
        if isinstance(link, list):
            for lin in link[1:]:
                add_to_queue(chat, song, lin, lin, None, from_user, duration)
            link = song_name = link[0]
        add_to_queue(chat, song, song_name, link, thumb, from_user, duration)
        return await xx.eor(
            f"✚ Ditambahkan 🎵 <a href={link}>{song_name}</a> antrian ke #{list(VC_QUEUE[chat].keys())[-1]}.",
            parse_mode="html",
        )


@vc_asst("مؤقت")
async def mute(event):
    if len(event.text.split()) > 1:
        chat = event.text.split()[1]
        try:
            chat = await event.client.parse_id(chat)
        except Exception as e:
            return await event.eor(f"**ERROR:**\n{str(e)}")
    else:
        chat = event.chat_id
    aySongs = Player(chat)
    await aySongs.group_call.set_is_mute(True)
    await event.eor(get_string("vcbot_12"))


@vc_asst("الغاء مؤقت")
async def unmute(event):
    if len(event.text.split()) > 1:
        chat = event.text.split()[1]
        try:
            chat = await event.client.parse_id(chat)
        except Exception as e:
            return await event.eor(f"**ERROR:**\n{str(e)}")
    else:
        chat = event.chat_id
    aySongs = Player(chat)
    await aySongs.group_call.set_is_mute(False)
    await event.eor("`Menyalakan pemutaran di obrolan ini.`")


@vc_asst("ايقاف مؤقت")
async def pauser(event):
    if len(event.text.split()) > 1:
        chat = event.text.split()[1]
        try:
            chat = await event.client.parse_id(chat)
        except Exception as e:
            return await event.eor(f"**ERROR:**\n{str(e)}")
    else:
        chat = event.chat_id
    aySongs = Player(chat)
    await aySongs.group_call.set_pause(True)
    await event.eor(get_string("vcbot_14"))


@vc_asst("استئناف")
async def resumer(event):
    if len(event.text.split()) > 1:
        chat = event.text.split()[1]
        try:
            chat = await event.client.parse_id(chat)
        except Exception as e:
            return await event.eor(f"**ERROR:**\n{str(e)}")
    else:
        chat = event.chat_id
    aySongs = Player(chat)
    await aySongs.group_call.set_pause(False)
    await event.eor(get_string("vcbot_13"))


@vc_asst("رفع معتمد", from_users=owner_and_sudos(), vc_auth=False)
async def auth_group(event):
    try:
        key = event.text.split(" ", maxsplit=1)[1]
        admins = "admins" in key
    except IndexError:
        admins = False
    chat = event.chat_id
    key = udB.get_key("VC_AUTH_GROUPS") or {}
    cha, adm = (key[chat], key[chat]["admins"]) if key.get(chat) else (None, None)
    if cha and adm == admins:
        return await event.reply(get_string("vcbot_19"))
    key.update({chat: {"admins": admins}})
    udB.set_key("VC_AUTH_GROUPS", key)
    kem = "Admins" if admins else "All"
    await event.eor(
        f"• Berhasil Ditambahkan ke Grup AUTH Untuk <code>{kem}</code>.",
        parse_mode="html",
    )


@vc_asst("ازاله معتمد", from_users=owner_and_sudos(), vc_auth=False)
async def auth_group(event):
    chat = event.chat_id
    key = udB.get_key("VC_AUTH_GROUPS") or {}
    gc = key.get(chat)
    if not gc:
        return await event.eor(get_string("vcbot_16"))
    del key[chat]
    if key:
        udB.set_key("VC_AUTH_GROUPS", key)
    else:
        udB.del_key("VC_AUTH_GROUPS")
    await event.eor(get_string("vcbot_10"))


@vc_asst("listauth", from_users=owner_and_sudos(), vc_auth=False)
async def listVc(e):
    chats = udB.get_key("VC_AUTH_GROUPS")
    if not chats:
        return await e.eor(get_string("vcbot_18"))
    text = "• <strong>Vc Auth Chats •</strong>\n\n"
    for on in chats.keys():
        st = "Admins" if chats[on]["admins"] else "All"
        try:
            title = (await e.client.get_entity(on)).title
        except ValueError:
            title = "No Info"
        text += f"∆ <strong>{title}</strong> [ <code>{on}</code> ] : <code>{st}</code>"
    await e.eor(text, parse_mode="html")


@vc_asst("المعتمدين")
async def lstqueue(event):
    if len(event.text.split()) > 1:
        chat = event.text.split()[1]
        try:
            chat = await event.client.parse_id(chat)
        except Exception as e:
            return await event.eor(get_string("vcbot_2").format(str(e)))
    else:
        chat = event.chat_id
    if q := list_queue(chat):
        await event.eor(f"• <strong>Queue:</strong>\n\n{q}", parse_mode="html")
    else:
        return await event.eor(get_string("vcbot_21"))


@vc_asst("انضمام")
async def rejoiner(event):
    if len(event.text.split()) > 1:
        chat = event.text.split()[1]
        try:
            chat = await event.client.parse_id(chat)
        except Exception as e:
            return await event.eor(get_string("vcbot_2").format(str(e)))
    else:
        chat = event.chat_id
    aySongs = Player(chat)
    try:
        await aySongs.group_call.reconnect()
    except NotConnectedError:
        return await event.eor(get_string("vcbot_6"))
    await event.eor(get_string("vcbot_5"))


@vc_asst("تخطي")
async def skipper(event):
    if len(event.text.split()) > 1:
        chat = event.text.split()[1]
        try:
            chat = await event.client.parse_id(chat)
        except Exception as e:
            return await event.eor(f"**ERROR:**\n{str(e)}")
    else:
        chat = event.chat_id
    aySongs = Player(chat, event)
    await aySongs.play_from_queue()


@vc_asst("فيديو")
async def video_c(event):
    xx = await event.eor(get_string("com_1"))
    chat = event.chat_id
    from_user = inline_mention(event.sender)
    reply, song = None, None
    if event.reply_to:
        reply = await event.get_reply_message()
    if len(event.text.split()) > 1:
        input = event.text.split(maxsplit=1)[1]
        tiny_input = input.split()[0]
        if tiny_input[0] in ["@", "-"]:
            try:
                chat = await event.client.parse_id(tiny_input)
            except Exception as er:
                LOGS.exception(er)
                return await xx.edit(str(er))
            try:
                song = input.split(maxsplit=1)[1]
            except BaseException:
                pass
        else:
            song = input
    if not (reply or song):
        return await xx.eor(get_string("vcbot_15"), time=5)
    await xx.eor(get_string("vcbot_20"))
    if reply and reply.media and mediainfo(reply.media).startswith("video"):
        song, thumb, title, link, duration = await file_download(xx, reply)
    else:
        is_link = is_url_ok(song)
        if is_link is False:
            return await xx.eor(f"`{song}`\n\nBukan link yang bisa dimainkan.🥱")
        if is_link is None:
            song, thumb, title, link, duration = await vid_download(song)
        elif re.search("youtube", song) or re.search("youtu", song):
            song, thumb, title, link, duration = await vid_download(song)
        else:
            song, thumb, title, link, duration = (
                song,
                "https://telegra.ph/file/22bb2349da20c7524e4db.mp4",
                song,
                song,
                "♾",
            )
    aySongs = Player(chat, xx, True)
    if not (await aySongs.vc_joiner()):
        return
    text = "🎥 **Sedang dimainkan:** [{}]({})\n⏰ **Durasi:** `{}`\n👥 **Di:** `{}`\n🙋‍♂ **Diminta oleh:** {}".format(
        title, link, duration, chat, from_user
    )
    try:
        await xx.reply(
            text,
            file=thumb,
            link_preview=False,
        )
    except ChatSendMediaForbiddenError:
        await xx.reply(text, link_preview=False)
    await asyncio.sleep(1)
    await aySongs.group_call.start_video(song, with_audio=True)
    await xx.delete()


@vc_asst("listvcaccess$", from_users=owner_and_sudos(), vc_auth=False)
async def _(e):
    xx = await e.eor(get_string("vcbot_11"))
    mm = get_vcsudos()
    pp = f"<strong>{len(mm)} Pengguna yang Disetujui Bot Obrolan Suara</strong>\n"
    if len(mm) > 0:
        for m in mm:
            try:
                name = (await e.client.get_entity(int(m))).first_name
                pp += f"• <a href=tg://user?id={int(m)}>{name}</a>\n"
            except ValueError:
                pp += f"• <code>{int(m)} » No Info</code>\n"
    await xx.edit(pp, parse_mode="html")


@vc_asst("rmvcaccess( (.*)|$)", from_users=owner_and_sudos(), vc_auth=False)
async def _(e):
    xx = await e.eor("`Disapproving to access Voice Chat features...`")
    input = e.pattern_match.group(1).strip()
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
        name = (await e.client.get_entity(userid)).first_name
    elif input:
        try:
            userid = await e.client.parse_id(input)
            name = (await e.client.get_entity(userid)).first_name
        except ValueError as ex:
            return await xx.edit(f"`{str(ex)}`", time=5)
    else:
        return await xx.edit(get_string("vcbot_17"), time=3)
    if not is_vcsudo(userid):
        return await xx.eor(
            xx,
            f"[{name}](tg://user?id={userid})` is not approved to use my Voice Chat Bot.`",
            time=5,
        )
    try:
        del_vcsudo(userid)
        await xx.eor(
            f"[{name}](tg://user?id={userid})` is removed from Voice Chat Bot Users.`",
            time=5,
        )
    except Exception as ex:
        return await xx.edit(f"`{ex}`", time=5)


@vc_asst("vcaccess( (.*)|$)", from_users=owner_and_sudos(), vc_auth=False)
async def _(e):
    xx = await e.eor("`Approving to access Voice Chat features...`")
    input = e.pattern_match.group(1).strip()
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
        name = (await e.client.get_entity(userid)).first_name
    elif input:
        try:
            userid = await e.client.parse_id(input)
            name = (await e.client.get_entity(userid)).first_name
        except ValueError as ex:
            return await xx.eor(f"`{str(ex)}`", time=5)
    else:
        return await xx.eor(get_string("vcbot_17"), time=3)
    if is_vcsudo(userid):
        return await xx.eor(
            f"[{name}](tg://user?id={userid})` is already approved to use my Voice Chat Bot.`",
            time=5,
        )
    try:
        add_vcsudo(userid)
        await xx.eor(
            f"[{name}](tg://user?id={userid})` is added to Voice Chat Bot Users.`",
            time=5,
        )
    except Exception as ex:
        return await xx.eor(f"`{ex}`", time=5)


@vc_asst("ytplaylist")
async def live_stream(e):
    xx = await e.eor(get_string("com_1"))
    if len(e.text.split()) <= 1:
        return await xx.eor("`Berikan saya link playlist YouTube...`")
    input = e.text.split()
    if input[1].startswith("-"):
        chat = int(input[1])
        song = e.text.split(maxsplit=2)[2]
    elif input[1].startswith("@"):
        cid_moosa = (await e.client.get_entity(input[1])).id
        chat = int(f"-100{str(cid_moosa)}")
        song = e.text.split(maxsplit=2)[2]
    else:
        song = e.text.split(maxsplit=1)[1]
        chat = e.chat_id
    if not (re.search("youtu", song) and re.search("playlist\\?list", song)):
        return await xx.eor(get_string("vcbot_8"))
    if not is_url_ok(song):
        return await xx.eor("`Hanya link playlist Youtube...`")
    await xx.edit(get_string("vcbot_7"))
    file, thumb, title, link, duration = await dl_playlist(
        chat, inline_mention(e), song
    )
    aySongs = Player(chat, e)
    if not aySongs.group_call.is_connected:
        if not (await aySongs.vc_joiner()):
            return
        from_user = inline_mention(e.sender)
        await xx.reply(
            "📀 **Sedang dimainkan:** [{}]({})\n⏰ **Durasi:** `{}`\n👥 **Di:** `{}`\n🙋‍♂ **Diminta oleh:** {}".format(
                f"{title[:30]}...", link, duration, chat, from_user
            ),
            file=thumb,
            link_preview=False,
        )

        await xx.delete()
        await aySongs.group_call.start_audio(file)
    else:
        from_user = inline_mention(e)
        add_to_queue(chat, file, title, link, thumb, from_user, duration)
        return await xx.eor(
            f"✚ Ditambahkan 🎵 **[{title}]({link})** antrian ke #{list(VC_QUEUE[chat].keys())[-1]}.",
        )
