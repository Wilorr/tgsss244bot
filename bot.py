import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ChatJoinRequestHandler,
    ContextTypes,
    filters
)

# Конфигурация
TOKEN = "7863685675:AAG6OY1khfMVi4MfIP5Lo--F0zcGAiZWS44"
CHANNEL_ID = -1002509915735  # Ваш закрытый канал
CHANNEL1 = "@GrowGate"  # Первый канал для подписки
CHANNEL2 = "@GrowGateTrade"  # Второй канал для подписки

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def send_welcome_message(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Отправляем приветственное сообщение"""
    try:
        buttons = [
            [InlineKeyboardButton("GrowGate", url=f"t.me/GrowGate")],
            [InlineKeyboardButton("GrowGateTrade", url=f"t.me/GrowGateTrade")],
            [InlineKeyboardButton("✅ Я подписался", callback_data="check_subs")]
        ]
        await context.bot.send_message(
            chat_id=user_id,
            text="🔐 Для доступа к закрытому каналу нужно подписаться на:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка новой заявки в канал"""
    user = update.chat_join_request.from_user
    logger.info(f"Новая заявка от @{user.username} (ID: {user.id})")
    await send_welcome_message(user.id, context)

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Проверка подписки и одобрение заявки"""
    query = update.callback_query
    await query.answer()
    user = query.from_user

    try:
        # Проверяем подписку на оба канала
        channel1_member = await context.bot.get_chat_member(CHANNEL1, user.id)
        channel2_member = await context.bot.get_chat_member(CHANNEL2, user.id)

        if channel1_member.status in ['member', 'administrator', 'creator'] and \
           channel2_member.status in ['member', 'administrator', 'creator']:
            try:
                await context.bot.approve_chat_join_request(CHANNEL_ID, user.id)
                await query.edit_message_text("🎉 Спасибо за подписки! Доступ к каналу открыт.")
            except Exception as e:
                logger.error(f"Ошибка принятия заявки: {e}")
                await query.edit_message_text("⚠️ Не удалось принять заявку. Убедитесь, что вы подавали заявку в канал.")
        else:
            await query.edit_message_text("❌ Вы подписаны не на все каналы! Пожалуйста, подпишитесь на оба канала и попробуйте снова.")
            
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        await query.edit_message_text("⚠️ Произошла ошибка. Попробуйте позже.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка команды /start"""
    await send_welcome_message(update.effective_user.id, context)

def main() -> None:
    """Запуск бота"""
    app = ApplicationBuilder().token(TOKEN).build()

    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(ChatJoinRequestHandler(handle_join_request))
    app.add_handler(CallbackQueryHandler(check_subscription))

    # Запуск
    app.run_polling()
    logger.info("Бот запущен и готов к работе")

if __name__ == '__main__':
    main()