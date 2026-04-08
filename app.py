from flask import Flask, render_template, request, jsonify
from html import escape
import os
import psycopg

app = Flask(__name__)


def get_conn():
    return psycopg.connect(os.environ["DATABASE_URL"])


def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'Pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, description, status, created_at
                FROM tasks
                ORDER BY id DESC
            """)
            rows = cur.fetchall()

    tasks = []
    for row in rows:
        tasks.append({
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'status': row[3],
            'created_at': row[4].isoformat() if row[4] else None
        })

    return jsonify(tasks)


@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json() or {}
    title = str(data.get('title', '')).strip()
    description = str(data.get('description', '')).strip()

    if not title:
        return jsonify({'error': 'Title is required.'}), 400

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tasks (title, description)
                VALUES (%s, %s)
                RETURNING id, title, description, status, created_at
            """, (title, description))
            row = cur.fetchone()
        conn.commit()

    task = {
        'id': row[0],
        'title': row[1],
        'description': row[2],
        'status': row[3],
        'created_at': row[4].isoformat() if row[4] else None
    }

    return jsonify(task), 201


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json() or {}
    new_status = str(data.get('status', '')).strip()

    if new_status not in ['Pending', 'Done']:
        return jsonify({'error': 'Status must be Pending or Done.'}), 400

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE tasks
                SET status = %s
                WHERE id = %s
                RETURNING id, title, description, status, created_at
            """, (new_status, task_id))
            row = cur.fetchone()
        conn.commit()

    if row is None:
        return jsonify({'error': 'Task not found.'}), 404

    task = {
        'id': row[0],
        'title': row[1],
        'description': row[2],
        'status': row[3],
        'created_at': row[4].isoformat() if row[4] else None
    }

    return jsonify(task)


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            deleted = cur.rowcount
        conn.commit()

    if deleted == 0:
        return jsonify({'error': 'Task not found.'}), 404

    return jsonify({'message': 'Task deleted successfully.'})


@app.route("/admin/tasks")
def admin_tasks():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, description, status, created_at
                FROM tasks
                ORDER BY id DESC
            """)
            rows = cur.fetchall()

    columns = ["id", "title", "description", "status", "created_at"]
    header_html = "".join(f"<th>{escape(col)}</th>" for col in columns)

    body_html = ""
    for row in rows:
        body_html += "<tr>"
        for value in row:
            body_html += f"<td>{escape(str(value))}</td>"
        body_html += "</tr>"

    return f"""
    <html>
    <head>
        <title>Tasks Database</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 30px; background: #f7f7f7; }}
            h2 {{ margin-bottom: 20px; }}
            table {{ border-collapse: collapse; width: 100%; background: white; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background: #222; color: white; }}
            tr:nth-child(even) {{ background: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h2>Tasks Database</h2>
        <table>
            <thead>
                <tr>{header_html}</tr>
            </thead>
            <tbody>
                {body_html}
            </tbody>
        </table>
    </body>
    </html>
    """


init_db()

if __name__ == '__main__':
    app.run(debug=True)
