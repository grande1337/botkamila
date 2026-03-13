import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

BOT_TOKEN = "8633042205:AAEg6eDIpHTihogiCYzdIX1rTB_h2GUaduM"
ADMIN_CHAT_ID = -5272928503

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

CHOOSE_ACTION, CHOOSE_CATEGORY, WAIT_TEXT = range(3)

IDEA_CATEGORIES = {
    "love": "❤️ Любовь",
    "career": "💼 Карьера",
    "money": "💰 Деньги",
    "motherhood": "🤱 Материнство",
    "travel": "✈️ Путешествия",
}


def main_menu():
    keyboard = [
        [InlineKeyboardButton("💡 Предложить идею", callback_data="idea")],
        [InlineKeyboardButton("❓ Задать вопрос", callback_data="question")],
    ]
    return InlineKeyboardMarkup(keyboard)


def category_menu():
    buttons = [
        [InlineKeyboardButton(name, callback_data=key)]
        for key, name in IDEA_CATEGORIES.items()
    ]
    return InlineKeyboardMarkup(buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "👋 Привет!\n\n"
        "Выберите действие:"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )

    return CHOOSE_ACTION


async def choose_action(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    action = query.data

    if action == "idea":

        await query.edit_message_text(
            "Выберите категорию идеи:",
            reply_markup=category_menu()
        )

        context.user_data["type"] = "idea"

        return CHOOSE_CATEGORY

    if action == "question":

        context.user_data["type"] = "question"

        await query.edit_message_text(
            "Напишите ваш вопрос:"
        )

        return WAIT_TEXT


async def choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    category_key = query.data
    context.user_data["category"] = IDEA_CATEGORIES[category_key]

    await query.edit_message_text(
        f"Категория: {IDEA_CATEGORIES[category_key]}\n\n"
        "Напишите вашу идею:"
    )

    return WAIT_TEXT


async def receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    content_type = context.user_data.get("type")

    if content_type == "idea":

        category = context.user_data.get("category", "Без категории")

        admin_message = (
            "💡 <b>Новая идея</b>\n\n"
            f"Категория: {category}\n\n"
            f"{text}"
        )

    else:

        admin_message = (
            "❓ <b>Новый вопрос</b>\n\n"
            f"{text}"
        )

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=admin_message,
        parse_mode="HTML"
    )

    await update.message.reply_text(
        "✅ Сообщение отправлено анонимно!",
        reply_markup=main_menu()
    )

    return CHOOSE_ACTION


def main():

    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(

        entry_points=[CommandHandler("start", start)],

        states={

            CHOOSE_ACTION: [
                CallbackQueryHandler(choose_action)
            ],

            CHOOSE_CATEGORY: [
                CallbackQueryHandler(choose_category)
            ],

            WAIT_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text)
            ],

        },

        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv)

    logger.info("Bot started")

    app.run_polling()


if __name__ == "__main__":
    main()