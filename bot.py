from keys import *
from utils import account_info

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,

)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from telegram.constants import ParseMode



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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inform user about what this bot can do"""
    user_name = update.message.from_user.first_name

    await update.message.reply_text(f"سلام {user_name} عزیز خوش اومدی\n" + msg_yaml['start_msg'])



async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # check if message is edited
    if update.edited_message is not None:
        return
        
    uuid = update.message.text
    if 'not found' in account_info(uuid):
        await update.message.reply_text(msg_yaml['not_found'], parse_mode=ParseMode.HTML)
        return 
    
    status, up, down, used, total, traffic_remaining, expiry = account_info(uuid)
    rem_time, expiry = expiry
    
    keyboard = [
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



async def show_what_app_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = []
    for what_app, what_app_dict in WHAT_APP.items():
        keyboard.append([InlineKeyboardButton(
            what_app_dict["name"], callback_data=f"what_app|{what_app}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(msg_yaml['whatapp_msg'], reply_markup=reply_markup)


async def what_app_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    what_app = query.data.split("|")[1]
    desc_app = f"{WHAT_APP[what_app]['desc']}"
    image_path = f"{WHAT_APP[what_app]['image_path']}"

    await query.message.reply_photo(open(image_path, 'rb'), desc_app)
    await query.delete_message()

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(msg_yaml['help_msg'])


async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("/start", "استارت"),
        BotCommand("/what", "چه نرم افزاری استفاده میکنید؟"),
    ])


def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(telegram_token).post_init(post_init).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_handler))

    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(CommandHandler(
        "what", show_what_app_handle))
    application.add_handler(CallbackQueryHandler(
        what_app_handle, pattern="^what_app"))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
