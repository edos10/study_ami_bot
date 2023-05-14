from typing import Union
from telegram import (
    ForceReply
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import sqlite3 as sql

from .check_role import check_student


async def gen_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_id = update.message.from_user.id
    correct_person = check_student(user_id)
    if correct_person != "correct":
        await context.bot.sendMessage(text="Эта функция доступна только ученикам.",
                                      chat_id=update.message.chat_id)
        keyboard = [
            [
                InlineKeyboardButton("Выйти к списку команд", callback_data="Выйти к списку команд")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Что дальше?", reply_markup=reply_markup)
        return "what_to_do"
    keyboard = [
        [
            InlineKeyboardButton("Дефолтные", callback_data="Стандарт"),
            InlineKeyboardButton("От пользователей", callback_data="Пользователи"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выбери, какие задачи хочешь решать", reply_markup=reply_markup)
    return 'choose_cluster'


async def choose_tasks_cluster(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    if update.callback_query.data == "Стандарт":
        keyboard = [
            [
                InlineKeyboardButton("Матанализ", callback_data="Матанализ"),
                InlineKeyboardButton("Дискретная математика", callback_data="Дискретная математика"),
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text("Выбери предмет, по которому хочешь решать задачи:",
                                        reply_markup=reply_markup)
        return 'choose_subject'
    elif update.callback_query.data == "Пользователи":
        await update.callback_query.message.reply_text("Укажи коллекцию, из которой хочешь решать задачи:",
                                        reply_markup=ForceReply())
        return 'choose_collection'


async def choose_standard_task_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    query = update.callback_query
    if query.data == "Матанализ":
        context.user_data["group"] = "matan_default"
    elif query.data == "Дискретная математика":
        context.user_data["group"] = "discr_default"
    context.user_data["text_group"] = False
    context.user_data["query_group"] = True
    return await send_task_message(update, context)


async def choose_task_collection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[int, str, None]:
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    query_db.execute(
        f"""SELECT * FROM All_Tasks WHERE GROUP_ID = "{update.message.text}" ORDER BY RANDOM() LIMIT 1;""")
    res = query_db.fetchone()
    conn.commit()
    conn.close()
    if res is None:
        await context.bot.sendMessage(
            text="Упс! Такой коллекции не существует. Создайте ее, если хотите!", chat_id=update.message.chat_id)
        context.user_data.clear()
        await context.bot.sendMessage(
            text="Заканчиваем подбор задач.", chat_id=update.message.chat_id)
        keyboard = [
            [
                InlineKeyboardButton("Выйти к списку команд", callback_data="Выйти к списку команд")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Что дальше?", reply_markup=reply_markup)
        return "what_to_do"
    else:
        context.user_data["group"] = update.message.text
        context.user_data["text_group"] = True
        context.user_data["query_group"] = False
        return await send_task_message(update, context)


async def send_task_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    query_db.execute(f"""SELECT * FROM ALL_TASKS WHERE GROUP_ID = "{context.user_data["group"]}" ORDER BY RANDOM() LIMIT 1;""")
    res = query_db.fetchone()
    conn.commit()
    conn.close()
    if not context.user_data["text_group"] and context.user_data["query_group"]:
        await context.bot.send_message(text="Задача:", chat_id=update.callback_query.message.chat_id)
        context.user_data["task_number"] = res[0]
        if type(res[1]) == str:  # проверка на то, что перед нами, - фото или текст
            await context.bot.send_message(
                text=f"{res[1]}",
                chat_id=update.callback_query.message.chat_id)
        elif type(res[1]) == bytes:
            await context.bot.send_photo(
                photo=res[1],
                chat_id=update.callback_query.message.chat_id)
        await context.bot.send_message(text="Введите ваш ответ:",
                                       chat_id=update.callback_query.message.chat_id,
                                       reply_markup=ForceReply())
        return 'check_ans'
    elif context.user_data["text_group"] and not context.user_data["query_group"]:
        await context.bot.send_message(text="Задача:", chat_id=update.message.chat_id)
        context.user_data["task_number"] = res[0]
        if type(res[1]) == str:  # проверка на то, что перед нами, - фото или текст
            await context.bot.send_message(
                text=f"{res[1]}",
                chat_id=update.message.chat_id)
        elif type(res[1]) == bytes:
            await context.bot.send_photo(
                photo=res[1],
                chat_id=update.message.chat_id)
        await context.bot.send_message(text="Введите ваш ответ:",
                                       chat_id=update.message.chat_id,
                                       reply_markup=ForceReply())
        return 'check_ans'
