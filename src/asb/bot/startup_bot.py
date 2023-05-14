import logging

from telegram.ext import (
    filters,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
)

# bot config
from .load_config import BotConfig

# handlers
from .handlers.start import *
from .handlers.help import *
from .handlers.add import *
from .handlers.gen_tasks import *
from .handlers.check_ans import *
from .handlers.top import *
from .handlers.get_all_tasks import *
from .handlers.my_stat import *
from .handlers.delete_tasks import *
from .handlers.delete_groups import *
from .handlers.edit_tasks import *
from .handlers.results import *


def run_bot(config_file_path: str):
    # get bot configuration
    bot_config: BotConfig = BotConfig.from_file(config_file_path)

    # build the bot application using bot token
    application = ApplicationBuilder().token(bot_config.token).build()

    # add handlers
    start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={'choose_role': [CallbackQueryHandler(choose_role)]},
        fallbacks=[]
    )

    help_handler = CommandHandler('help', bot_help)

    add_task_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add_task)],
        states={'prep_task': [MessageHandler(filters=(filters.TEXT | filters.PHOTO), callback=prep_task)],
                'prep_ans': [MessageHandler(filters=filters.TEXT, callback=prep_ans)],
                'prep_solution': [MessageHandler(filters=(filters.TEXT | filters.PHOTO), callback=prep_solution)],
                'prep_collection': [MessageHandler(filters=filters.TEXT, callback=prep_collection)],
                'create_collection': [CallbackQueryHandler(create_collection)],
                'what_to_do': [CallbackQueryHandler(what_to_do)]
                },
        fallbacks=[]
    )

    solve_handler = ConversationHandler(
        entry_points=[CommandHandler('gen_task', gen_task)],
        states={
            'choose_cluster': [CallbackQueryHandler(choose_tasks_cluster)],
            'choose_subject': [CallbackQueryHandler(choose_standard_task_group)],
            'choose_collection': [MessageHandler(filters.TEXT, choose_task_collection)],
            'check_ans': [MessageHandler(filters.TEXT, check_ans)],
            'choose_next_when_correct': [CallbackQueryHandler(choose_next_step_correct)],
            'choose_next_when_incorrect': [CallbackQueryHandler(choose_next_step_incorrect)],
            'what_to_do': [CallbackQueryHandler(what_to_do)]
        },
        fallbacks=[]
    )

    all_tasks_handler = ConversationHandler(
        entry_points=[CommandHandler('all_tasks', all_tasks)],
        states={
            'input_group': [MessageHandler(filters.TEXT, get_all_tasks)],
            'what_to_do': [CallbackQueryHandler(what_to_do)]
        },
        fallbacks=[]
    )

    results_handler = ConversationHandler(
        entry_points=[CommandHandler('results', results)],
        states={
            'input_group': [MessageHandler(filters.TEXT, get_resuts)],
            'what_to_do': [CallbackQueryHandler(what_to_do)]
        },
        fallbacks=[]
    )

    top_handler = ConversationHandler(
        entry_points=[CommandHandler('top', top)],
        states={
            'what_to_do': [CallbackQueryHandler(what_to_do)]
        },
        fallbacks=[]
    )

    my_stat_handler = ConversationHandler(
        entry_points=[CommandHandler('my_stat', my_stat)],
        states={
            'what_to_do': [CallbackQueryHandler(what_to_do)]
        },
        fallbacks=[]
    )

    delete_task_handler = ConversationHandler(
        entry_points=[CommandHandler('delete_task', delete_task)],
        states={
            'specify_group': [MessageHandler(filters.TEXT, specify_group_dt)],
            'delete_task_from_db': [MessageHandler(filters.TEXT, delete_task_by_number)],
            'show_next_steps': [CallbackQueryHandler(show_next_steps_dt)],
            'what_to_do': [CallbackQueryHandler(what_to_do)]
        },
        fallbacks=[]
    )

    delete_group_handler = ConversationHandler(
        entry_points=[CommandHandler('delete_group', delete_group)],
        states={
            'specify_group': [MessageHandler(filters.TEXT, specify_group_dg)],
            'confirm_deletion': [CallbackQueryHandler(confirm_deletion)],
            'show_next_steps': [CallbackQueryHandler(show_next_steps_dg)],
            'what_to_do': [CallbackQueryHandler(what_to_do)]
        },
        fallbacks=[]
    )

    edit_task_handler = ConversationHandler(
        entry_points=[CommandHandler('edit_task', edit_task)],
        states={
            'specify_group': [MessageHandler(filters.TEXT, specify_group_et)],
            'pre_edit_condition': [MessageHandler(filters.TEXT, pre_edit_condition)],
            'edit_condition': [MessageHandler(filters.TEXT, edit_condition)],
            'show_next_steps_et': [CallbackQueryHandler(show_next_steps_et)],
            'what_to_do': [CallbackQueryHandler(what_to_do)]
        },
        fallbacks=[]
    )

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(add_task_handler)
    application.add_handler(solve_handler)
    application.add_handler(my_stat_handler)
    application.add_handler(all_tasks_handler)
    application.add_handler(top_handler)
    application.add_handler(delete_task_handler)
    application.add_handler(delete_group_handler)
    application.add_handler(edit_task_handler)
    application.add_handler(results_handler)
    # initialize and start the bot application
    application.run_polling()
