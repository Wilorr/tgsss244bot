from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import os
import logging

# Настройки
TOKEN = os.environ['BOT_TOKEN']  # Получаем токен из переменных окружения
CHANNEL1 = "@GrowGate"  # Первый канал для подписки
CHANNEL2 = "@GrowGateTrade"  # Второй канал для подписки

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context):
    """Обработка команды /start"""
    keyboard = [
        [InlineKeyboardButton("Канал 1", url=f"https://t.me/{CHANNEL1[1:]}")],
        [InlineKeyboardButton("Канал 2", url=f"https://t.me/{CHANNEL2[1:]}")],
        [InlineKeyboardButton("✅ Я подписался", callback_data="check_subs")]
    ]
    update.message.reply_text(
        "🔐 Для доступа подпишитесь на оба канала:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def check_subscription(update: Update, context):
    """Проверка подписки на каналы"""
    query = update.callback_query
    user = query.from_user
    
    try:
        # Проверяем подписку
        member1 = context.bot.get_chat_member(chat_id=CHANNEL1, user_id=user.id)
        member2 = context.bot.get_chat_member(chat_id=CHANNEL2, user_id=user.id)
        
        if member1.status in ['member', 'administrator', 'creator'] and member2.status in ['member', 'administrator', 'creator']:
            query.answer("🎉 Доступ разрешен!")
            query.edit_message_text("✅ Спасибо за подписку! Теперь вам доступен закрытый канал.")
            # Здесь можно добавить логику принятия заявки
        else:
            query.answer("❌ Вы подписаны не на все каналы!")
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        query.answer("⚠️ Ошибка проверки. Попробуйте позже.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(check_subscription, pattern="^check_subs$"))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
