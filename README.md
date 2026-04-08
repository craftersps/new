# Mini Task Manager

A small full-stack web application built with:
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python Flask
- **Database:** SQLite

## Features
- Add a task
- View all tasks
- Change task status (Pending / Done)
- Delete a task
- Data saved in SQLite database

## Project Structure

```text
simple_task_app/
├── app.py
├── requirements.txt
├── tasks.db              # created automatically when app runs
├── templates/
│   └── index.html
└── static/
    ├── styles.css
    └── app.js
```

## Run the app

### 1) Create virtual environment (optional)
```bash
python -m venv venv
```

### 2) Activate it
#### Windows
```bash
venv\Scripts\activate
```

#### macOS / Linux
```bash
source venv/bin/activate
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Start the server
```bash
python app.py
```

### 5) Open in browser
```text
http://127.0.0.1:5000
```

## API Endpoints
- `GET /api/tasks` → get all tasks
- `POST /api/tasks` → add a new task
- `PUT /api/tasks/<id>` → update status
- `DELETE /api/tasks/<id>` → delete task

## Notes
- The database file is created automatically.
- This project is good as a starter template for learning CRUD apps.
