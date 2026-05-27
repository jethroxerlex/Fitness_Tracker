from db.db import get_connection

def get_user_profile(user_id):

    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        SELECT username, first_name, birth_date, sex, weight, height, goal
        FROM Users
        WHERE user_id = ?
    """, (user_id,))

    user = cur.fetchone()

    con.close()

    return user


def get_food_logs(user_id):

    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        SELECT meal_type, food_name, calories, protein, carbs, fat
        FROM FoodLogs
        WHERE user_id = ?
        AND DATE(created_at) = DATE('now')
    """, (user_id,))

    logs = cur.fetchall()

    con.close()

    return logs


def get_weight_logs(user_id):

    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        SELECT progress_date, progress_weight
        FROM WeightProgress
        WHERE user_id = ?
        ORDER BY progress_date ASC
    """, (user_id,))

    logs = cur.fetchall()

    con.close()

    return logs