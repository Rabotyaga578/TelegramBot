from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import json
import os
import csv
from datetime import datetime

SELECT_QUESTION, ANSWER_QUESTION = range(2)
DATA_FILE = "coffee_bot_data.json"
CSV_FILE = "winners.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"questions": {}, "user_answers": {}}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['question_number', 'username', 'date'])

def save_winner_to_csv(question_number, username):
    try:
        # Сначала проверяем, не занят ли уже вопрос
        winners = {}
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    winners[row['question_number']] = row
        
        # Проверяем, не занят ли вопрос
        if question_number in winners:
            return False
        
        # Добавляем нового победителя
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([question_number, username, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def is_question_available(question_number):
    try:
        if not os.path.exists(CSV_FILE):
            return True
        
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['question_number'] == question_number:
                    return False
        return True
    except:
        return True

def get_available_questions():
    try:
        if not os.path.exists(CSV_FILE):
            return [str(i) for i in range(1, 101)]
        
        taken_questions = set()
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                taken_questions.add(row['question_number'])
        
        return [str(i) for i in range(1, 101) if str(i) not in taken_questions]
    except:
        return [str(i) for i in range(1, 101)]

def get_user_answered_questions(user_id):
    data = load_data()
    user_answers = data["user_answers"].get(user_id, {})
    return list(user_answers.keys())

def init_questions():
    data = load_data()
    if not data["questions"]:
        questions = {}
        coffee_questions = [
            {"question": "Сколько градусов должна быть вода для идеального заваривания кофе?", "answer": "90-96"},
            {"question": "Как называется кофейный напиток с молоком?", "answer": "латте"},
            {"question": "В какой стране больше всего пьют кофе?", "answer": "финляндия"},
            {"question": "Какой сорт кофе считается самым дорогим в мире?", "answer": "копи лувак"},
            {"question": "Сколько мл в стандартной чашке эспрессо?", "answer": "30"}
        ]
        
        for i in range(1, 101):
            if i <= len(coffee_questions):
                questions[str(i)] = coffee_questions[i-1]
            else:
                questions[str(i)] = {"question": f"Кофейный досье #{i}", "answer": f"ответ{i}"}
        
        data["questions"] = questions
        save_data(data)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    welcome_text = f"""☕Добро пожаловать в библиотеку «Фабрика кофе»!», {user.first_name}!

🎯 Здесь мы будем разгадывать досье, чтобы принять участие в розыгрыше призов!

📝 Правила:

• При покупке любого напитка из осеннего меню в нашей Фабрике - вы получаете на руки одно досье: самое время его разгадать и назвать имя подозреваемого 🕵

•Чем больше досье вы разгадаете, тем больше шансов выиграть приз!

🏆 Итоги розыгрыша будут в нашем Telegram канале!

Уже получил свое досье? Тогда давай приступим к игре!

🎁 Чтобы приступить к разгадке - напишите ниже номер досье, которое вам попалось (1-100)"""
    
    keyboard = [
        [KeyboardButton("📋 Список свободных досье")],
        [KeyboardButton("🏆 Мои досье"), KeyboardButton("❓ Помощь")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    return SELECT_QUESTION

async def show_available_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        available_questions = get_available_questions()
        if available_questions:
            text = "📋 Свободные досье:\n" + "\n".join([f"• досье {q}" for q in available_questions[:15]])
            if len(available_questions) > 15:
                text += f"\n\n... и еще {len(available_questions) - 15} свободных досье!"
        else:
            text = "❌ Все досье уже заняты!"
        text += "\n\n📝 Чтобы разгадать досье, напишите его номер"
        await update.message.reply_text(text)
    except:
        await update.message.reply_text("📋 Попробуйте выбрать любой досье от 1 до 100")

async def show_my_answers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    answered_questions = get_user_answered_questions(user_id)
    
    if answered_questions:
        text = "🏆 Ваши разгаданные ответы:\n" + "\n".join([f"• досье {q}" for q in answered_questions])
        text += f"\n\n🎯 Всего правильных досье: {len(answered_questions)}"
    else:
        text = "📝 Вы еще не разгадали ни одиин досье."
    
    text += "\n\n🎁 Продолжайте участвовать в розыгрыше!"
    await update.message.reply_text(text)

async def select_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_input = update.message.text
    data = load_data()
    
    if user_input == "📋 Список свободных досье":
        await show_available_questions(update, context)
        return SELECT_QUESTION
    elif user_input == "🏆 Мои досье":
        await show_my_answers(update, context)
        return SELECT_QUESTION
    elif user_input == "❓ Помощь":
        await help_command(update, context)
        return SELECT_QUESTION
    
    if not user_input.isdigit() or not (1 <= int(user_input) <= 100):
        await update.message.reply_text("❌ досье с таким номером не найден. Выберите номер от 1 до 100")
        return SELECT_QUESTION
    
    question_number = user_input
    
    user_answers = data["user_answers"].get(user_id, {})
    if question_number in user_answers:
        await update.message.reply_text("❌ Вы уже отвечали на этот досье!")
        return SELECT_QUESTION
    
    if not is_question_available(question_number):
        await update.message.reply_text("❌ Ксожалению этот досье уже занят! Выберите другой досье.")
        return SELECT_QUESTION
    
    context.user_data['current_question'] = question_number
    await update.message.reply_text(f"❓ Досье#{question_number}\n\n📝 Напишите ваш ответ! Кто этот подозреваемый?")
    return ANSWER_QUESTION

async def answer_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text.lower().strip()
    user_id = str(update.message.from_user.id)
    user = update.message.from_user
    question_number = context.user_data.get('current_question')
    
    data = load_data()
    question_data = data["questions"][question_number]
    correct_answer = question_data["answer"].lower().strip()
    
    if user_answer == correct_answer:
        username = f"@{user.username}" if user.username else f"{user.first_name} {user.last_name or ''}".strip()
        
        if save_winner_to_csv(question_number, username):
            if user_id not in data["user_answers"]:
                data["user_answers"][user_id] = {}
            
            data["user_answers"][user_id][question_number] = {
                "username": username,
                "date": datetime.now().isoformat()
            }
            save_data(data)
            
            user_answers_count = len(data["user_answers"][user_id])
            
            success_text = f"""🎉 ПРАВИЛЬНО! 

🏆 Вы успешно ответили на досье #{question_number}!

📊 Всего ваших правильных ответов: {user_answers_count}

📢 Итоги розыгрыша в нашем канале:

👉 @fabrika_coffee_life 👈

💫 Чем больше правильных ответов - тем выше шанс на приз!"""
            
            await update.message.reply_text(success_text)
        else:
            await update.message.reply_text("❌ Этот досье уже занят другим участником.")
    else:
        await update.message.reply_text("❌ К сожалению, ответ неверный. Попробуйте другой досье!")
    
    context.user_data.pop('current_question', None)
    return SELECT_QUESTION

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """❓ Помощь:

📝 Розыгрыш призов:
• Разгадыай ЛЮБОЕ количество досье
• Выберите номер досье от 1 до 100
• Правильный ответ = шанс на приз
• Чем больше ответов - тем выше шанс!

🏆 Итоги в канале: @fabrika_coffee_life

🎯 Команды:
• Список свободных досье - доступные досье
• Мои досье - ваши правильные ответы"""
    await update.message.reply_text(help_text)

def main():
    init_questions()
    init_csv()
    app = Application.builder().token("8450057853:AAGVsuOUyK0s3F3LsrC07wGwgukC6e7V8GI").build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            SELECT_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_question)],
            ANSWER_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, answer_question)],
        },
        fallbacks=[CommandHandler("help", help_command)]
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", help_command))
    print("☕ Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()