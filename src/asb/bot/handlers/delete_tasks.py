from typing import Union
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
import sqlite3 as sql
from telegram.ext import ConversationHandler, ContextTypes

from .check_role import check_teacher
from .help import bot_help


async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
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
    context.user_data["chat_id"] = update.message.chat_id
    await context.bot.send_message(
        text="Выберите коллекцию, из которой хотите удалить задачи. Для этого напишите ниже название коллекции:",
        chat_id=context.user_data["chat_id"], reply_markup=ForceReply()
    )
    return 'specify_group'


async def specify_group_dt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[str, int]:
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    user_id = update.message.from_user.id
    query_db.execute(f"""SELECT * FROM Groups WHERE GROUP_ID = "{update.message.text}";""")
    res = query_db.fetchone()
    conn.commit()
    conn.close()
    if res is None:
        await context.bot.send_message(
            text=f"Такой коллекции не существует, пожалуйста, введите команду еще раз.",
            chat_id=context.user_data["chat_id"])
        context.user_data.clear()
        await bot_help(update, context)
        return ConversationHandler.END
    if res[1] == user_id:
        context.user_data["group_id"] = update.message.text
        return await show_tasks_in_group(update, context)
    else:
        await context.bot.send_message(
            text=f"Вы не создавали эту коллекцию, поэтому удалить в ней ничего не можете :(",
            chat_id=context.user_data["chat_id"])
        context.user_data.clear()
        await bot_help(update, context)
        return ConversationHandler.END


async def specify_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await context.bot.send_message(text="Укажите номер задачи, который хотите удалить.",
                                   chat_id=context.user_data["chat_id"], reply_markup=ForceReply())
    return 'delete_task_from_db'


async def delete_task_by_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    all_tasks = context.user_data["tasks"]
    num_task = update.message.text

    keyboard = [
        [
            InlineKeyboardButton("Продолжить", callback_data="Продолжить"),
            InlineKeyboardButton("Выйти", callback_data="Выйти к списку команд")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if num_task not in all_tasks.keys():
        await context.bot.send_message(text="Вы ввели несуществующий номер задачи. Возможно задача была удалена ранее. Повторите попытку.",
                                       chat_id=context.user_data["chat_id"], reply_markup=reply_markup)
    else:
        conn = sql.connect('database/study_bot.db')
        query_db = conn.cursor()
        query_db.execute(f"""DELETE FROM All_Tasks WHERE ID = "{all_tasks[num_task]}";""")
        conn.commit()
        conn.close()
        await context.bot.send_message(text=f"Задача {num_task} была успешно удалена!",
                                       chat_id=context.user_data["chat_id"])
        await context.bot.send_message(text="Что дальше?",
                                       chat_id=context.user_data["chat_id"],
                                       reply_markup=reply_markup)
    return 'show_next_steps'


async def show_next_steps_dt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[str, int]:
    if update.callback_query.data == 'Продолжить':
        return await show_tasks_in_group(update, context)
    elif update.callback_query.data == 'Выйти к списку команд':
        context.user_data.clear()
        await bot_help(update, context)
        return ConversationHandler.END


async def show_tasks_in_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[str, int]:
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    query_db.execute(
        f"""SELECT * FROM All_Tasks WHERE GROUP_ID = "{context.user_data["group_id"]}";""")
    res = query_db.fetchall()
    conn.commit()
    conn.close()
    if res is None or len(res) == 0:
        await context.bot.send_message(
            text=f"Эта коллекция пуста. Для добавления новых задач воспользуйтесь командой /add.",
            chat_id=context.user_data["chat_id"])
        context.user_data.clear()
        await bot_help(update, context)
        return ConversationHandler.END
    from_numbers_to_tasks = dict()
    for i in range(len(res)):
        task = res[i][1]
        if type(task) != str:
            await context.bot.send_photo(photo=task, chat_id=context.user_data["chat_id"])
            task = 'Изображение выше'
        ans = str(i + 1) + '. ' + task + '\n'
        from_numbers_to_tasks[str(i + 1)] = res[i][0]
        await context.bot.send_message(
            text=f"{ans}",
            chat_id=context.user_data["chat_id"])
    context.user_data["tasks"] = from_numbers_to_tasks
    return await specify_task(update, context)
