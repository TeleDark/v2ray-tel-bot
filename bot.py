import qrcode
import requests
import base64
import re
from io import BytesIO
from PIL import Image
from pyzbar.pyzbar import decode
from keys import *
from utils import account_info

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
    error
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)
from telegram.constants import ParseMode

ACCOUNT_LINK_INPUT = 1
AFTER_QR_SENT = 2

WHAT_APP = {
    "Nekoray": {
        "name": "Nekoray",
        'desc': "Nekoray",
        "image_path": os.path.join(real_dir,"images/nekoray.jpg")
    },

    "V2rayNG": {
        "name": "V2rayNG",
        "desc": "V2rayNG",
        "image_path": os.path.join(real_dir,"images/v2rayng.jpg")
    },

    "OneClick": {
        "name": "OneClick",
        "desc": "OneClick",
        "image_path": os.path.join(real_dir,"images/oneclick.jpg")
    },

    "NamsternetV": {
        "name": "NapsterNetV",
        "desc": "NapsterNetV",
        "image_path": os.path.join(real_dir,"images/napsternetv.jpg")
    },

}
def is_base64(s):
    try:
        return base64.b64encode(base64.b64decode(s)) == s
    except Exception:
        return False

def is_url(text):
    url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
    return url_pattern.match(text) is not None


async def check_membership(context: ContextTypes.DEFAULT_TYPE, channel_id: str, user_id: int) -> tuple[bool, str]:
    try:
        member_status = await context.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        valid_statuses = {'member', 'administrator', 'creator'}
        is_member = member_status.status in valid_statuses
        return is_member, "OK" if is_member else ""
    except error.Forbidden:
        return False, "ربات ادمین کانال نیس⛔"
    except error.BadRequest:
        return False, "ربات دسترسی به کانال ندارد⛔"
    except error.TelegramError as e:
        return False, f"خطای ناشناخته: {str(e)}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.message.from_user.first_name
    user_id = update.message.from_user.id

    if channel_id:
        is_member, message = await check_membership(context, channel_id, user_id)
        if not is_member:
            await update.message.reply_text(msg_yaml['channel_msg'] + message)
            return

    await update.message.reply_text(f"سلام {user_name} عزیز خوش اومدی\n" + msg_yaml['start_msg'])


async def generate_qrcode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(msg_yaml['qrcode']) 
    return ACCOUNT_LINK_INPUT


async def process_account_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    account_link = update.message.text

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=3
    )
    qr.add_data(account_link)
    qr.make(fit=True)
    
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    qr_image_buffer = BytesIO()
    qr_image.save(qr_image_buffer)
    
    qr_image_buffer.seek(0)

    await update.message.reply_photo(photo=qr_image_buffer)    
    return AFTER_QR_SENT


async def get_account_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # check if message is edited
    if update.edited_message is not None:
        return
    
    user_id = update.message.from_user.id

    if channel_id:
        is_member, message = await check_membership(context, channel_id, user_id)
        if not is_member:
            await update.message.reply_text(msg_yaml['channel_msg'] + message)
            return

    if update.message.photo:
        # If the message contains a photo, decode the QR code
        photo_id = update.message.photo[-1].file_id
        photo_file = await context.bot.get_file(photo_id)
        photo_data = await photo_file.download_as_bytearray()
        img = Image.open(BytesIO(photo_data))
        decode_objects = decode(img)

        if decode_objects:
            # If a QR code is found, extract the decoded text
            decode_qrcode = decode_objects[0].data.decode("utf-8")
            acc_info = account_info(decode_qrcode)
        else:
            await update.message.reply_text("لطفا QRCode ارسال کنید")
            return ConversationHandler.END

    else:
        # If the message doesn't contain a photo, use the text message
        client_msg = update.message.text

        """
        Fetch the first account detail from the given subscription URL.
        If the URL content is base64 encoded, it decodes it.
        Returns the first account or None if an error occurs.
        """
        if is_url(client_msg):
            request_url = client_msg
            try:
                res = requests.get(request_url)
                res_content = res.content
                if is_base64(res_content):
                    accounts = base64.b64decode(res_content).decode('utf-8')
                else: 
                    accounts = res_content.decode('utf-8')

                client_msg = accounts.split()[0]

            except requests.exceptions.RequestException as e:
                await update.message.reply_text("در خواندن لینک ساب شما مشکلی پیش آمد")

        acc_info = account_info(client_msg)

    if acc_info == 'not found':
        await update.message.reply_text(msg_yaml['not_found'], parse_mode=ParseMode.HTML)
        return ConversationHandler.END
    
    status, account_name, up, down, used, total, traffic_remaining, expiry = acc_info
    rem_time, expiry = expiry
    
    keyboard = [
        [InlineKeyboardButton(f"نام اکانت: {account_name}", callback_data='1')],
        [InlineKeyboardButton(f"⚙️ وضعیت اکانت: {status}", callback_data='1')],

        [
            InlineKeyboardButton(f"⬆️ {up} :آپلود",callback_data='1'),
            InlineKeyboardButton(f"⬇️ {down} :دانلود",callback_data='1',)
        ],
        [InlineKeyboardButton(f"{used} :میزان مصرف⏳", callback_data='1')],
        [InlineKeyboardButton(
            f"📡 حجم باقی مانده : {traffic_remaining}", callback_data='1')],
        [InlineKeyboardButton(
            f"🕒 زمان باقی مانده : {rem_time}", callback_data='1')],
        [InlineKeyboardButton(f" 🌐 حجم کل: {total}", callback_data='1')],
        [InlineKeyboardButton(f"{expiry} 🔚", callback_data='1')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(msg_yaml['acc_info'], reply_markup=reply_markup)
    
    return ConversationHandler.END

async def show_what_app_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = []
    for what_app, what_app_dict in WHAT_APP.items():
        keyboard.append([InlineKeyboardButton(
            what_app_dict["name"], callback_data=f"what_app|{what_app}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(msg_yaml['whatapp_msg'], reply_markup=reply_markup)
    

async def what_app_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if channel_id:
        
        user_id = update.message.from_user.id
        is_member = await check_membership(context, channel_id, user_id)
        
        if not is_member:
            await update.message.reply_text(msg_yaml['channel_msg'])
            return 
    
    query = update.callback_query
    await query.answer()
    what_app = query.data.split("|")[1]
    desc_app = f"{WHAT_APP[what_app]['desc']}"
    image_path = f"{WHAT_APP[what_app]['image_path']}"

    await query.message.reply_photo(open(image_path, 'rb'), desc_app)
    await query.delete_message()

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if channel_id:
        
        user_id = update.message.from_user.id
        is_member = await check_membership(context, channel_id, user_id)
        
        if not is_member:
            await update.message.reply_text(msg_yaml['channel_msg'])
            return 
    
    await update.message.reply_text(msg_yaml['help_msg'])


async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("/start", "استارت"),
        BotCommand("/qrcode", "ساخت QRCode"),
        BotCommand("/what", "چه نرم افزاری استفاده میکنید؟"),
    ])


def main() -> None:
    """Run bot."""
    try:
        # Create the Application and pass it your bot's token.
        application = Application.builder().token(telegram_token).post_init(post_init).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_handler))

        conv_handler = ConversationHandler(

        entry_points= [
            CommandHandler("qrcode", generate_qrcode), MessageHandler(
            ~filters.COMMAND, get_account_info)
            ],

        states= {
            ACCOUNT_LINK_INPUT: [MessageHandler(filters.TEXT, process_account_link)],
            AFTER_QR_SENT: [MessageHandler(filters.TEXT, get_account_info)]
        },

        fallbacks=[],
        )

        application.add_handler(conv_handler)

        application.add_handler(CommandHandler(
        "what", show_what_app_handle))
        application.add_handler(CallbackQueryHandler(
        what_app_handle, pattern="^what_app"))

        # Run the bot until the user presses Ctrl-C
        application.run_polling()
    
    except error.InvalidToken:
        print('You must pass the token you received from https://t.me/Botfather!')
    except Exception as e:
        print("error:", e)
        

if __name__ == "__main__":
    main()
