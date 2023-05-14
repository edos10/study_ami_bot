from typing import Union
from telegram import (
    ForceReply,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import ConversationHandler, ContextTypes

from .check_role import check_teacher
from .help import *


async def all_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    correct_person = check_teacher(user_id)
    if correct_person != "correct":
        await context.bot.sendMessage(text="Эта функция доступна только преподавателю.",
                                      chat_id=update.message.chat_id)
        keyboard = [
            [
                InlineKeyboardButton("Выйти к списку команд", callback_data="Выйти к списку команд")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Что дальше?", reply_markup=reply_markup)
        return "what_to_do"
    await context.bot.sendMessage(text="Введите название коллекции, задания которой вы хотите посмотреть:",
                                  chat_id=update.message.chat_id, reply_markup=ForceReply())
    context.user_data["chat_id"] = update.message.chat_id
    return "input_group"


async def get_all_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    user_id = update.message.from_user.id
    message = update.message.text
    query_db.execute(f"""SELECT * FROM Groups WHERE GROUP_ID = "{message}";""")
    group = query_db.fetchone()
    query_db.execute(
        f"""SELECT * FROM All_Tasks WHERE GROUP_ID = "{message}";""")
    res = query_db.fetchall()
    conn.commit()
    conn.close()
    if group is None:
        await context.bot.send_message(
            text=f"Такой коллекции не существует.",
            chat_id=context.user_data["chat_id"])
        context.user_data.clear()
        keyboard = [
            [
                InlineKeyboardButton("Выйти к списку команд", callback_data="Выйти к списку команд")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Что дальше?", reply_markup=reply_markup)
        return 'what_to_do'
    if group[1] != user_id:
        await context.bot.send_message(
            text=f"Вы не создавали эту коллекцию, поэтому посмотреть ее задания не можете :(",
            chat_id=context.user_data["chat_id"])
        context.user_data.clear()
        keyboard = [
            [
                InlineKeyboardButton("Выйти к списку команд", callback_data="Выйти к списку команд")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Что дальше?", reply_markup=reply_markup)
        return 'what_to_do'
    for i in range(len(res)):
        answer = res[i][2]
        solution = res[i][3]
        task = res[i][1]
        if type(task) != str:
            await context.bot.send_photo(photo=task, chat_id=update.message.chat_id)
            task = 'Изображение выше'
        if type(answer) != str:
            await context.bot.send_photo(photo=answer, chat_id=update.message.chat_id)
            answer = 'Изображение выше'
        if type(solution) != str:
            await context.bot.send_photo(photo=solution, chat_id=update.message.chat_id)
            solution = 'Изображение выше'
        ans = str(i + 1) + '. ' + task + '\n Ответ: ' + answer + '\n Решение: ' + solution + '\n'
        await context.bot.send_message(
            text=f"{ans}",
            chat_id=update.message.chat_id)
    keyboard = [
        [
            InlineKeyboardButton("Выйти к списку команд", callback_data="Выйти к списку команд")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Что дальше?", reply_markup=reply_markup)
    return 'what_to_do'


async def what_to_do(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[int, str]:
    query = update.callback_query
    if query.data == "Выйти к списку команд":
        await bot_help(update, context)
        return ConversationHandler.END
