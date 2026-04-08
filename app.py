from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("RAILWAY_VOLUME_MOUNT_PATH", BASE_DIR))
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "tasks.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    conn.commit()
    conn.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_connection()
    tasks = conn.execute(
        'SELECT id, title, description, status, created_at FROM tasks ORDER BY id DESC'
    ).fetchall()
    conn.close()
    return jsonify([dict(task) for task in tasks])


@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json() or {}
    title = str(data.get('title', '')).strip()
    description = str(data.get('description', '')).strip()

    if not title:
        return jsonify({'error': 'Title is required.'}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tasks (title, description) VALUES (?, ?)',
        (title, description)
    )
    conn.commit()
    task_id = cursor.lastrowid

    task = conn.execute(
        'SELECT id, title, description, status, created_at FROM tasks WHERE id = ?',
        (task_id,)
    ).fetchone()
    conn.close()

    return jsonify(dict(task)), 201


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json() or {}
    new_status = str(data.get('status', '')).strip()

    if new_status not in ['Pending', 'Done']:
        return jsonify({'error': 'Status must be Pending or Done.'}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET status = ? WHERE id = ?', (new_status, task_id))
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Task not found.'}), 404

    task = conn.execute(
        'SELECT id, title, description, status, created_at FROM tasks WHERE id = ?',
        (task_id,)
    ).fetchone()
    conn.close()

    return jsonify(dict(task))


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({'error': 'Task not found.'}), 404

    return jsonify({'message': 'Task deleted successfully.'})


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
else:
    init_db()
