import sqlite3


def get_connection():
    con = sqlite3.connect("fita.db")
    return con


def init_db():
    con = get_connection()
    cur = con.cursor()

    # User Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(255) UNIQUE NOT NULL,
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            email VARCHAR(255) UNIQUE NOT NULL,
            birth_date DATE,
            sex TEXT,    
            password VARCHAR(255) NOT NULL,
            weight REAL,
            height REAL,
            age INTEGER,
            goal TEXT      
        )
    """)

    # Food Logs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS FoodLogs(
            food_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            food_name VARCHAR(255),
            calories REAL,
            protein REAL,
            carbs REAL,
            fat REAL,           
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    """)

    # User Goals
    cur.execute("""
        CREATE TABLE IF NOT EXISTS UserGoals(
            goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            calorie_goal REAL,
            protein_goal REAL,
            carbs_goal REAL,
            fat_goal REAL,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    """)
    # Weight Progress
    cur.execute("""
        CREATE TABLE IF NOT EXISTS WeightProgress (
            progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            progress_date DATE NOT NULL,
            progress_weight REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
            REFERENCES Users(user_id)
        )
        """)
    try:
        cur.execute("""
            ALTER TABLE FoodLogs
            ADD COLUMN meal_type TEXT DEFAULT 'Snacks'
        """)
    except:
        pass

    con.commit()
    con.close()


if __name__ == "__main__":
    init_db()