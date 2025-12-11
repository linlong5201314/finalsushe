import sqlite3
import os

# 数据库路径
db_path = os.path.join('instance', 'database.db')
if not os.path.exists(db_path):
    # 尝试在 app 目录下查找
    db_path = os.path.join('app', 'dormitory.db')

print(f"Connecting to database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 添加 email 列到 users 表
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email VARCHAR(120)")
        print("Successfully added 'email' column to 'users' table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("'email' column already exists in 'users' table.")
        else:
            print(f"Error adding 'email' column: {e}")

    conn.commit()
    conn.close()

except Exception as e:
    print(f"Database connection error: {e}")
