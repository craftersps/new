const taskForm = document.getElementById('taskForm');
const titleInput = document.getElementById('title');
const descriptionInput = document.getElementById('description');
const taskList = document.getElementById('taskList');
const refreshBtn = document.getElementById('refreshBtn');
const message = document.getElementById('message');

async function loadTasks() {
  const response = await fetch('/api/tasks');
  const tasks = await response.json();

  if (tasks.length === 0) {
    taskList.innerHTML = '<div class="empty">No tasks yet.</div>';
    return;
  }

  taskList.innerHTML = tasks.map(task => {
    const badgeClass = task.status === 'Done' ? 'done' : 'pending';
    const nextStatus = task.status === 'Done' ? 'Pending' : 'Done';

    return `
      <div class="task-card">
        <h3>${escapeHtml(task.title)}</h3>
        <div class="task-meta">
          <span class="badge ${badgeClass}">${task.status}</span>
          <span> • Created: ${task.created_at}</span>
        </div>
        <p>${escapeHtml(task.description || 'No description')}</p>
        <div class="task-actions">
          <button onclick="changeStatus(${task.id}, '${nextStatus}')">Mark as ${nextStatus}</button>
          <button onclick="deleteTask(${task.id})">Delete</button>
        </div>
      </div>
    `;
  }).join('');
}

async function createTask(event) {
  event.preventDefault();
  message.textContent = '';

  const payload = {
    title: titleInput.value.trim(),
    description: descriptionInput.value.trim()
  };

  const response = await fetch('/api/tasks', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  const data = await response.json();

  if (!response.ok) {
    message.textContent = data.error || 'Something went wrong.';
    return;
  }

  taskForm.reset();
  loadTasks();
}

async function changeStatus(taskId, status) {
  const response = await fetch(`/api/tasks/${taskId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ status })
  });

  if (response.ok) {
    loadTasks();
  }
}

async function deleteTask(taskId) {
  const response = await fetch(`/api/tasks/${taskId}`, {
    method: 'DELETE'
  });

  if (response.ok) {
    loadTasks();
  }
}

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

taskForm.addEventListener('submit', createTask);
refreshBtn.addEventListener('click', loadTasks);
window.changeStatus = changeStatus;
window.deleteTask = deleteTask;

loadTasks();
