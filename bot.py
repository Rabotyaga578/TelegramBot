from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import requests

# Вставьте сюда токен, который вы получили от @BotFather
BOT_TOKEN = "8450057853:AAGVsuOUyK0s3F3LsrC07wGwgukC6e7V8GI"

# Функция-обработчик команды /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Я бот. Отправь мне любое сообщение, и я его повторю!')

# Функция-обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Просто напиши что-нибудь, и я отвечу!')

# Функция-обработчик обычных текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем текст сообщения от пользователя
    user_message = update.message.text
    # Просто возвращаем его обратно
    await update.message.reply_text(f"Вы сказали: {user_message}")

# Обработчик команды /btc - показывает цену биткоина
async def btc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Используем бесплатный API CoinGecko
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        
        price = data['bitcoin']['usd']
        await update.message.reply_text(f"💰 Цена Биткоина: ${price}")
    except:
        await update.message.reply_text("❌ Не удалось получить цену биткоина")

# Обработчик ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Ошибка: {context.error}")

# Основная функция
def main():
    # Создаем приложение и передаем ему токен
    app = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("btc", btc_command))
    
    # Добавляем обработчик текстовых сообщений (НЕ команд)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Добавляем обработчик ошибок
    app.add_error_handler(error_handler)

    # Запускаем бота на опрос серверов Telegram
    print("Бот запущен...")
    app.run_polling()

# Точка входа
if __name__ == '__main__':
    main()