from keys import *
from utils import account_info

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,

)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)



WHAT_APP = {
    "Nekoray": {
        "name": "Nekoray",
        "image_path": os.path.join(real_dir,"images/nekoray.jpg")
    },

    "V2rayNG": {
        "name": "V2rayNG",
        "image_path": os.path.join(real_dir,"images/v2rayng.jpg")
    },

    "OneClick": {
        "name": "OneClick",
        "image_path": os.path.join(real_dir,"images/oneclick.jpg")
    },

    "NamsternetV": {
        "name": "NamsternetV",
        "image_path": os.path.join(real_dir,"images/napsternetv.jpg")
    },

}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inform user about what this bot can do"""
    user_name = update.message.from_user.first_name

    await update.message.reply_text(f"""سلام {user_name} عزیز خوش اومدی
برای اینکه اطلاعات فیلترشکن رو ببینی نیازه آیدی(uuid/id) اکانتتو بفرستی...
اگ نمیدونی چجوری آیدی رو بدست بیاری رو /what بزن""")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uuid = update.message.text
    if 'not found' in account_info(uuid):
        await update.message.reply_text("""⭕️اکانت شما پیدا نشد!
✅در صورتی که مطمعن هستید درست وارد کردید ولی اکانتتون پیدا نشده اکانت شما به پایان رسیده و از سرور پاک شده.
⛔️اگر نمیدونین چجوری آیدی رو بدست بیارین رو /what بزنید""")
        return None
    
    up,down,total,expire_time = account_info(uuid)
    keyboard = [
        [
            InlineKeyboardButton(f"⬆️ {up}",callback_data='1'),
            InlineKeyboardButton(f"⬇️ {down}",callback_data='1'),
            InlineKeyboardButton(f"حجم {total}",callback_data='1'),
        ],
        [InlineKeyboardButton(f"{expire_time}",callback_data='1')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('💠اطلاعات سرویس شما تا این لحظه💠', reply_markup=reply_markup)



async def show_what_app_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = []
    for what_app, what_app_dict in WHAT_APP.items():
        keyboard.append([InlineKeyboardButton(
            what_app_dict["name"], callback_data=f"what_app|{what_app}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("چه نرم افزاری استفاده میکنید؟", reply_markup=reply_markup)


async def what_app_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    what_app = query.data.split("|")[1]
    image_path = f"{WHAT_APP[what_app]['image_path']}"

    await query.message.reply_photo(open(image_path, 'rb'), what_app)
    await query.delete_message()


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display a help message"""
    user_id = update.message.from_user.id
    await update.message.reply_text("""نسبت به اینکه چه نرم افزاری نصب داری فرق میکنه...
اگ نمیدونی چجوری پیداش کنی روی /what بزن""")


def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()
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
