from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserAdminInvalid, ChatAdminRequired
import asyncio
import re
from config import Config

app = Client('BanArabic',
             api_id=Config.API_ID,
             api_hash=Config.API_HASH,
             bot_token=Config.TOKEN)

HAS_ARABIC = "[\u0600-\u06ff]|[\u0750-\u077f]|[\ufb50-\ufbc1]|[\ufbd3-\ufd3f]|[\ufd50-\ufd8f]|[\ufd92-\ufdc7]|[\ufe70-\ufefc]|[\uFDF0-\uFDFD]+"


def check(string):
    """check if the string containing an arabic char"""
    return True if re.search(HAS_ARABIC, string) else False


markup = InlineKeyboardMarkup([[InlineKeyboardButton('📣 לערוץ העדכונים 📣', url='https://t.me/JewishBots'),
                                InlineKeyboardButton("🗯 לקבוצת התמיכה 🗯", url="https://t.me/JewsSupport")],
                               [InlineKeyboardButton('➕ להוספת הרובוט לקבוצה ➕',
                                                     url="https://t.me/ArabicBanBot?startgroup=true")],
                               [InlineKeyboardButton('🗒 לכל הערבים שהעפתי 🗒', url='https://t.me/ArabicBanLog')]])

log_markup = InlineKeyboardMarkup([[InlineKeyboardButton('🗒 לכל הערבים שהעפתי 🗒', url='https://t.me/ArabicBanLog')]])


@app.on_message(filters.command('start') & filters.private)
async def start(_, m: Message):
    await app.send_message(m.chat.id,
                           '**היי {}**\nהגעת לבוט מסיר ערבים. להוראות שימוש שלח /help'.format(
                               m.from_user.first_name),
                           reply_markup=markup)


@app.on_message(filters.command('help') & filters.private)
async def helper(_, m: Message):
    text = "פשוט תוסיפו אותי לקבוצה ואם יצטרף משתמש חדש עם שם / אודות בערבית אני אעיף אותו מהקבוצה! ❌" \
           " אל תשכח לתת הרשאות להסרת משתמשים ושינוי הרשאות!"
    await m.reply_text(text, reply_markup=markup)


@app.on_message(filters.new_chat_members)
async def ban(_, m: Message):
    id = m.from_user.id
    get = await app.get_chat(id)
    name = get.first_name
    last = get.last_name
    bio = get.bio

    if check(str(name)) or check(str(last)) or check(str(bio)):
        try:
            await m.chat.ban_member(id)
            send = await m.reply_text(
                'המשתמש הערבי {} הוסר בהצלחה!\nרוצים לראות את כל הערבים שהעפתי 🗒? 👇 לחצו בכפתור 👇'.format(
                    m.from_user.mention), reply_markup=log_markup)

            await app.send_message(Config.LOG_CHANNEL,
                                   '🗒 המשתמש הערבי: {} הוסר בהצלחה! מקבוצת: {}'.format(m.from_user.mention,
                                                                                        m.chat.title))
            await asyncio.sleep(15)
            await send.delete()
        except ChatAdminRequired:
            await m.reply_text('נראה ששכחתם לתת לי הרשאות מתאימות...')


@app.on_message(filters.text & filters.group & filters.incoming)
async def delete(_, m: Message):
    if check(m.text):
        try:
            await m.delete()
            await m.chat.restrict_member(m.from_user.id, permissions=ChatPermissions())
            send = await m.reply_text('המשתמש {} הושתק לצמיתות בגלל הודעה בערבית!'.format(m.from_user.mention))
            await app.send_message(Config.LOG_CHANNEL,
                                 'המשתמש הערבי: {} הושתק בהצלחה! בקבוצת: {}'.format(m.from_user.mention, m.chat.title))
            await asyncio.sleep(10)
            await send.delete()
        except UserAdminInvalid:
            return
        except ChatAdminRequired:
            await m.reply_text('נראה ששכחתם לתת לי הרשאות מתאימות...')

app.run()
