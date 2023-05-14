from .help import *


def check_teacher(user_id):
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    query_db.execute(
        f"""SELECT * FROM Teachers WHERE ID = "{user_id}";""")
    res = query_db.fetchone()
    if res is None or len(res) == 0:
        return 'not_correct'
    return 'correct'


def check_student(user_id):
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    query_db.execute(
        f"""SELECT * FROM Students WHERE ID = "{user_id}";""")
    res = query_db.fetchone()
    if res is None or len(res) == 0:
        return 'not_correct'
    return 'correct'
