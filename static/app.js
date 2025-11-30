const api = {
    login: async (email, password) => {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        if (!response.ok) throw new Error('Login failed');
        return response.json();
    },
    register: async (data) => {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(await response.text());
        return response.json();
    },
    logout: async () => {
        await fetch('/api/logout', { method: 'POST' });
        window.location.reload();
    },
    getMe: async () => {
        const response = await fetch('/api/me');
        if (!response.ok) return null;
        return response.json();
    },
    createTask: async (description) => {
        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ description })
        });
        if (!response.ok) {
            const errorText = await response.text();
            try {
                const errorJson = JSON.parse(errorText);
                throw new Error(errorJson.detail || errorJson.error || errorText);
            } catch (e) {
                throw new Error(errorText || 'Failed to create task');
            }
        }
        return response.json();
    },
    getTasks: async () => {
        const response = await fetch('/api/tasks');
        if (!response.ok) return [];
        return response.json();
    }
};

const app = {
    user: null,
    init: async () => {
        app.user = await api.getMe();
        app.render();
    },
    render: () => {
        const authContainer = document.getElementById('auth-container');
        const appContainer = document.getElementById('app-container');
        const userInfo = document.getElementById('user-info');

        if (app.user) {
            authContainer.classList.add('hidden');
            appContainer.classList.remove('hidden');
            userInfo.textContent = `${app.user.name}`;
            app.loadTasks();
        } else {
            authContainer.classList.remove('hidden');
            appContainer.classList.add('hidden');
        }
    },
    loadTasks: async () => {
        const tasks = await api.getTasks();
        const taskList = document.getElementById('task-list');
        taskList.innerHTML = '';
        tasks.forEach(task => {
            const div = document.createElement('div');
            div.className = 'task-item';
            div.innerHTML = `
                <div class="task-header">
                    <span class="task-title">${task.title}</span>
                    <span class="badge badge-${app.getPriorityClass(task.priority)}">P${task.priority}</span>
                </div>
                <div class="task-meta">
                    Due: ${task.deadline || 'No deadline'} | Assignee: ${task.assignee}
                </div>
                <p>${task.description}</p>
            `;
            taskList.appendChild(div);
        });
    },
    getPriorityClass: (priority) => {
        if (priority >= 4) return 'high';
        if (priority >= 3) return 'medium';
        return 'low';
    },
    showToast: (message, type = 'success') => {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);

        // Trigger reflow
        toast.offsetHeight;

        toast.classList.add('show');

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                container.removeChild(toast);
            }, 300);
        }, 3000);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    app.init();

    // Login Form
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = e.target.email.value;
        const password = e.target.password.value;
        try {
            await api.login(email, password);
            app.init();
        } catch (err) {
            app.showToast(err.message, 'error');
        }
    });

    // Register Form
    document.getElementById('register-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            first_name: e.target.first_name.value,
            last_name: e.target.last_name.value,
            email: e.target.email.value,
            password: e.target.password.value,
            position: e.target.position.value,
            job_description: e.target.job_description.value
        };
        try {
            await api.register(data);
            app.init();
        } catch (err) {
            app.showToast(err.message, 'error');
        }
    });

    // Toggle Auth Mode
    document.getElementById('show-register').addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('login-form').classList.add('hidden');
        document.getElementById('register-form').classList.remove('hidden');
    });

    document.getElementById('show-login').addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('register-form').classList.add('hidden');
        document.getElementById('login-form').classList.remove('hidden');
    });

    // Logout
    document.getElementById('logout-btn').addEventListener('click', () => {
        api.logout();
    });

    // Create Task
    document.getElementById('task-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const description = e.target.description.value;
        const btn = e.target.querySelector('button');
        const originalText = btn.textContent;

        btn.textContent = 'Processing...';
        btn.disabled = true;

        try {
            const result = await api.createTask(description);
            // Result is { message: { status: 'success', message: '...', assignee_name: '...', task_title: '...' } }
            // Wait, server returns { message: result_from_workflow }
            // If workflow returns dict, server returns { message: dict }
            // So result.message is the dict.

            const data = result.message;

            if (typeof data === 'string') {
                app.showToast(data, 'success');
            } else {
                app.showToast(`Task "${data.task_title}" assigned to ${data.assignee_name} successfully`, 'success');
            }

            e.target.reset();
            app.loadTasks();
        } catch (err) {
            console.error('Task creation error:', err);
            app.showToast(`Error: ${err.message}`, 'error');
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    });
});
