import sqlite3 as sql
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from .help import bot_help


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Привет, @{}! Это учебный бот для подготовки к коллоквиумам и контрольным работам! "
             "Здесь ты сможешь решать задачи, как из уже готовых коллекций, так и создавать свои коллекции и добавлять в них задачи. "
             "Подробнее - в /help. "
             "Удачи! Но перед тем, как приступить:".format(update.message.from_user.username)
        )

    keyboard = [
        [
            InlineKeyboardButton("Студент", callback_data="Студент"),
            InlineKeyboardButton("Преподаватель", callback_data="Преподаватель"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выбери, кто ты - студент или преподаватель.", reply_markup=reply_markup)
    return 'choose_role'


async def choose_role(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    if query.data == "Студент":
        query_db.execute(f"""SELECT * FROM Students WHERE ID = {query.from_user.id};""")
        res_stud = query_db.fetchone()
        query_db.execute(f"""SELECT * FROM Teachers WHERE ID = {query.from_user.id};""")
        res_teach = query_db.fetchone()
        if res_teach is not None:
            await context.bot.send_message(text="Вы уже зарегистрированы как преподаватель.",
                                           chat_id=query.message.chat_id)
        elif res_stud is not None:
            await context.bot.send_message(text="Вы уже зарегистрированы как студент.",
                                           chat_id=query.message.chat_id)
        else:
            query_db.execute("""INSERT INTO Students VALUES(?, ?, ?, ?, ?, ?);""",
                             (query.from_user.id, query.from_user.first_name, query.from_user.last_name, 0, 0, None))
            conn.commit()
            conn.close()
            await context.bot.send_message(text="Теперь вы можете решать задачи и готовиться к работам!",
                                           chat_id=query.message.chat_id)
    elif query.data == "Преподаватель":
        query_db.execute(f"""SELECT * FROM Students WHERE ID = {query.from_user.id};""")
        res_stud = query_db.fetchone()
        query_db.execute(f"""SELECT * FROM Teachers WHERE ID = {query.from_user.id};""")
        res_teach = query_db.fetchone()
        if res_stud is not None:
            await context.bot.send_message(text="Вы уже зарегистрированы как студент.",
                                           chat_id=query.message.chat_id)
        elif res_teach is not None:
            await context.bot.send_message(text="Вы уже зарегистрированы как преподаватель.",
                                           chat_id=query.message.chat_id)
        else:
            query_db.execute("""INSERT INTO Teachers VALUES(?, ?, ?);""",
                             (query.from_user.id, query.from_user.first_name, query.from_user.last_name))
            conn.commit()
            conn.close()
            await context.bot.send_message(
                text="Теперь вы можете добавлять сюда задачи, генерировать работы для студентов, а также смотреть их оценки.",
                chat_id=query.message.chat_id)
    await bot_help(update, context)
    return ConversationHandler.END
