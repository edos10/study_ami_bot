from typing import Union
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
import sqlite3 as sql
from telegram.ext import ConversationHandler, ContextTypes

from .check_role import check_teacher
from .help import bot_help


async def delete_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
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
    return await delete_group_start_state(update, context)


async def delete_group_start_state(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await context.bot.send_message(
        text="Выберите коллекцию, которую хотите удалить. Для этого напишите ниже название коллекции:",
        chat_id=context.user_data["chat_id"], reply_markup=ForceReply()
    )
    return 'specify_group'


async def specify_group_dg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    user_id = update.message.from_user.id
    query_db.execute(f"""SELECT * FROM Groups WHERE GROUP_ID = "{update.message.text}";""")
    res = query_db.fetchone()
    conn.commit()
    conn.close()

    keyboard = [
        [
            InlineKeyboardButton("Продолжить", callback_data="Продолжить"),
            InlineKeyboardButton("Выйти", callback_data="Выйти к списку команд")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if res is None:
        await context.bot.send_message(
            text=f"Такой коллекции не существует, пожалуйста, попробуйте другое название.",
            chat_id=context.user_data["chat_id"])

        await context.bot.send_message(
            text="Что дальше?",
            chat_id=context.user_data["chat_id"],
            reply_markup=reply_markup
        )
        return 'show_next_steps'

    if res[1] == user_id:
        context.user_data["group_id"] = update.message.text

        conn = sql.connect('database/study_bot.db')
        query_db = conn.cursor()
        query_db.execute(
            f"""SELECT * FROM All_Tasks WHERE GROUP_ID = "{context.user_data["group_id"]}";""")
        res = query_db.fetchall()
        conn.commit()
        conn.close()

        if len(res) > 0:
            context.user_data["tasks"] = res
            return await show_warning_tasks_in_group(update, context)
        else:
            await delete_group_from_db(update, context)

            await context.bot.send_message(
                text="Что дальше?",
                chat_id=context.user_data["chat_id"],
                reply_markup=reply_markup
            )
            return 'show_next_steps'
    else:
        await context.bot.send_message(
            text=f"Вы не создавали эту коллекцию, поэтому не можете её удалить :(",
            chat_id=context.user_data["chat_id"])

        await context.bot.send_message(
            text="Что дальше?",
            chat_id=context.user_data["chat_id"],
            reply_markup=reply_markup
        )
        return 'show_next_steps'


async def show_warning_tasks_in_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await context.bot.send_message(
        text="Внимание! В коллекции, которую вы хотите удалить, есть задачи:",
        chat_id=context.user_data["chat_id"]
    )
    tasks = []
    for i in range(len(context.user_data["tasks"])):
        task = context.user_data["tasks"][i][1]
        if type(task) != str:
            await context.bot.send_photo(photo=task, chat_id=context.user_data["chat_id"])
            task = 'Изображение выше'
        ans = str(i + 1) + '. ' + task + '\n'
        tasks.append(context.user_data["tasks"][i][0])
        await context.bot.send_message(
            text=f"{ans}",
            chat_id=context.user_data["chat_id"])

    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data="Да"),
            InlineKeyboardButton("Нет", callback_data="Нет")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        text="Вы действительно хотите удалить её?",
        chat_id=context.user_data["chat_id"],
        reply_markup=reply_markup
    )

    context.user_data["tasks"] = tasks
    return 'confirm_deletion'


async def confirm_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[str, int]:
    keyboard = [
        [
            InlineKeyboardButton("Продолжить", callback_data="Продолжить"),
            InlineKeyboardButton("Выйти", callback_data="Выйти к списку команд")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query.data == 'Да':
        await delete_group_from_db(update, context)

    await context.bot.send_message(
        text="Что дальше?",
        chat_id=context.user_data["chat_id"],
        reply_markup=reply_markup
    )
    return 'show_next_steps'


async def delete_group_from_db(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    if "tasks" in context.user_data:
        for task in context.user_data["tasks"]:
            query_db.execute(f"""DELETE FROM All_Tasks WHERE ID = "{task}";""")
    query_db.execute(f"""DELETE FROM Groups WHERE GROUP_ID = "{context.user_data["group_id"]}";""")
    conn.commit()
    conn.close()

    await context.bot.send_message(
        text="Коллекция была успешно удалена.",
        chat_id=context.user_data["chat_id"]
    )


async def show_next_steps_dg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[str, int]:
    if update.callback_query.data == 'Продолжить':
        return await delete_group_start_state(update, context)
    elif update.callback_query.data == 'Выйти к списку команд':
        context.user_data.clear()
        await bot_help(update, context)
        return ConversationHandler.END
