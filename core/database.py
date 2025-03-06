import os
import sqlite3

_database = './data/database.db'

if not os.path.exists('./data'):
    os.makedirs('./data')

# 初始化数据库
def init_db():
    conn = sqlite3.connect(_database)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT down,
            python_version TEXT NOT NULL,
            upload_time TEXT NOT NULL,
            path TEXT NOT NULL,
            pid TEXT DEFAULT NULL
        )
    ''')
    conn.commit()
    conn.close()

# 插入文件记录
def update_file_record(project_name, status, pid):
    conn = sqlite3.connect(_database)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE files set status = ?, pid = ? where project_name = ?
    ''', (status, pid, project_name))
    conn.commit()
    conn.close()

# 更新文件记录
def insert_file_record(project_name, description, python_version, upload_time, server_path):
    conn = sqlite3.connect(_database)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO files (project_name, description, python_version, upload_time, path)
        VALUES (?, ?, ?, ?, ?)
    ''', (project_name, description, python_version, upload_time, server_path))
    conn.commit()
    conn.close()

# 获取所有文件记录
def get_all_files():
    conn = sqlite3.connect(_database)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM files')
    files = cursor.fetchall()
    conn.close()
    return files

# 获取指定工程记录
def get_file(project_name):
    conn = sqlite3.connect(_database)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM files WHERE project_name = ?', (project_name,))
    existing_project = cursor.fetchone()
    conn.close()
    return existing_project

# 删除
def delete(project_name):
    # 删除旧记录
    conn = sqlite3.connect(_database)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM files WHERE project_name = ?', (project_name,))
    conn.commit()
    conn.close()