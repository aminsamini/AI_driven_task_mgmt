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
    },
    updateStatus: async (taskId, status) => {
        const response = await fetch(`/api/tasks/${taskId}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });
        if (!response.ok) {
            const errorText = await response.text();
            try {
                const errorJson = JSON.parse(errorText);
                throw new Error(errorJson.detail || errorText);
            } catch (e) {
                throw new Error(errorText || 'Failed to update status');
            }
        }
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
    currentPage: 1,
    itemsPerPage: 6,
    currentTab: 'assigned_to_me',

    switchTab: (tab) => {
        app.currentTab = tab;
        app.currentPage = 1; // Reset to first page

        // Update UI
        const assignedToMeBtn = document.getElementById('tab-assigned-to-me');
        const assignedByMeBtn = document.getElementById('tab-assigned-by-me');

        if (tab === 'assigned_to_me') {
            assignedToMeBtn.classList.add('border-primary', 'text-primary');
            assignedToMeBtn.classList.remove('border-transparent', 'text-gray-500');
            assignedByMeBtn.classList.remove('border-primary', 'text-primary');
            assignedByMeBtn.classList.add('border-transparent', 'text-gray-500');
        } else {
            assignedByMeBtn.classList.add('border-primary', 'text-primary');
            assignedByMeBtn.classList.remove('border-transparent', 'text-gray-500');
            assignedToMeBtn.classList.remove('border-primary', 'text-primary');
            assignedToMeBtn.classList.add('border-transparent', 'text-gray-500');
        }

        app.loadTasks();
    },

    loadTasks: async () => {
        const allTasks = await api.getTasks();

        // Filter tasks based on current tab
        const tasks = allTasks.filter(task => {
            if (app.currentTab === 'assigned_to_me') {
                return task.assignee == app.user.id;
            } else {
                return task.assign_by == app.user.id;
            }
        });

        const taskList = document.getElementById('task-list');
        taskList.innerHTML = '';

        // Pagination Logic
        const startIndex = (app.currentPage - 1) * app.itemsPerPage;
        const endIndex = startIndex + app.itemsPerPage;
        const paginatedTasks = tasks.slice(startIndex, endIndex);
        const totalPages = Math.ceil(tasks.length / app.itemsPerPage);

        paginatedTasks.forEach(task => {
            const div = document.createElement('div');
            div.className = 'bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition duration-200 border border-gray-100 cursor-pointer';
            div.onclick = () => app.openModal(task);
            div.innerHTML = `
                <div class="flex justify-between items-start mb-4">
                    <span class="text-lg font-semibold text-gray-800 line-clamp-1" title="${task.title}">${task.title}</span>
                    <span class="px-2 py-1 rounded text-xs font-medium ${app.getPriorityClass(task.priority)}">P${task.priority}</span>
                </div>
                <div class="text-sm text-gray-500 mb-4 pb-4 border-b border-gray-100">
                    <div class="flex items-center gap-2 mb-1">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                        ${task.deadline || 'No deadline'}
                    </div>
                    <div class="flex items-center gap-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                        ${task.assignee_name || task.assignee}
                    </div>
                </div>
                <p class="text-gray-600 text-sm line-clamp-3">${task.description}</p>
            `;
            taskList.appendChild(div);
        });

        app.renderPagination(totalPages);
    },

    openModal: (task) => {
        const modal = document.getElementById('task-modal');
        document.getElementById('modal-task-title').textContent = task.title;

        const priorityBadge = document.createElement('span');
        priorityBadge.className = `px-2 py-1 rounded text-xs font-medium ${app.getPriorityClass(task.priority)}`;
        priorityBadge.textContent = `P${task.priority}`;
        const priorityContainer = document.getElementById('modal-priority');
        priorityContainer.innerHTML = '';
        priorityContainer.appendChild(priorityBadge);

        const importanceBadge = document.createElement('span');
        importanceBadge.className = `px-2 py-1 rounded text-xs font-medium ${app.getImportanceClass(task.importance)}`;
        importanceBadge.textContent = `I${task.importance}`;
        const importanceContainer = document.getElementById('modal-importance');
        importanceContainer.innerHTML = '';
        importanceContainer.appendChild(importanceBadge);

        document.getElementById('modal-deadline').textContent = task.deadline || 'No deadline';
        document.getElementById('modal-assignee').textContent = task.assignee_name || task.assignee;
        document.getElementById('modal-assigned-by').textContent = task.assign_by_name || 'Unknown';
        document.getElementById('modal-description').textContent = task.description;

        // Handle status changes
        const statusSelect = document.getElementById('modal-status');
        if (statusSelect) {
            // Remove any existing event listeners to prevent duplicates
            const newStatusSelect = statusSelect.cloneNode(true);
            statusSelect.parentNode.replaceChild(newStatusSelect, statusSelect);

            newStatusSelect.value = task.status;

            // Disable if not assignee
            if (task.assignee != app.user.id) {
                newStatusSelect.disabled = true;
                newStatusSelect.title = "Only the assignee can change the status";
                newStatusSelect.classList.add('opacity-50', 'cursor-not-allowed');
            } else {
                newStatusSelect.disabled = false;
                newStatusSelect.title = "";
                newStatusSelect.classList.remove('opacity-50', 'cursor-not-allowed');

                newStatusSelect.addEventListener('change', async (e) => {
                    const newStatus = e.target.value;
                    try {
                        await api.updateStatus(task.id, newStatus);
                        // Update the local task object
                        task.status = newStatus;
                        // Refresh the task list to reflect changes
                        await app.loadTasks();
                        app.showToast(`Status updated to ${newStatus}`, 'success');
                    } catch (error) {
                        console.error('Failed to update status:', error);
                        app.showToast('Failed to update status', 'error');
                        // Revert the select value on error
                        e.target.value = task.status;
                    }
                });
            }
        }

        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    },

    closeModal: () => {
        const modal = document.getElementById('task-modal');
        modal.classList.add('hidden');
        document.body.style.overflow = ''; // Restore scrolling
    },

    renderPagination: (totalPages) => {
        const paginationContainer = document.getElementById('pagination');
        paginationContainer.innerHTML = '';

        if (totalPages <= 1) return;

        const nav = document.createElement('nav');
        nav.className = 'isolate inline-flex -space-x-px rounded-md shadow-sm';
        nav.setAttribute('aria-label', 'Pagination');

        // Helper to create button
        const createButton = (text, onClick, disabled, isActive, isFirst, isLast, isIcon = false) => {
            const btn = document.createElement('a');
            btn.href = '#';
            btn.onclick = (e) => {
                e.preventDefault();
                if (!disabled && onClick) onClick();
            };

            let baseClasses = 'relative inline-flex items-center px-4 py-2 text-sm font-semibold ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0';

            if (isIcon) {
                baseClasses = 'relative inline-flex items-center px-2 py-2 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0';
            }

            if (isActive) {
                baseClasses = 'relative z-10 inline-flex items-center bg-blue-600 px-4 py-2 text-sm font-semibold text-white focus:z-20 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600';
            } else if (disabled) {
                baseClasses += ' text-gray-300 cursor-not-allowed hover:bg-white';
            } else {
                baseClasses += ' text-gray-900';
            }

            if (isFirst) baseClasses += ' rounded-l-md';
            if (isLast) baseClasses += ' rounded-r-md';

            btn.className = baseClasses;

            if (isIcon) {
                btn.innerHTML = text; // Expecting SVG HTML
            } else {
                btn.textContent = text;
            }

            return btn;
        };

        // Previous Button
        nav.appendChild(createButton(
            `<span class="sr-only">Previous</span>
            <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z" clip-rule="evenodd" />
            </svg>`,
            () => {
                if (app.currentPage > 1) {
                    app.currentPage--;
                    app.loadTasks();
                }
            },
            app.currentPage === 1,
            false,
            true,
            false,
            true
        ));

        // Page Numbers
        for (let i = 1; i <= totalPages; i++) {
            nav.appendChild(createButton(
                i,
                () => {
                    app.currentPage = i;
                    app.loadTasks();
                },
                false,
                app.currentPage === i,
                false,
                false
            ));
        }

        // Next Button
        nav.appendChild(createButton(
            `<span class="sr-only">Next</span>
            <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
            </svg>`,
            () => {
                if (app.currentPage < totalPages) {
                    app.currentPage++;
                    app.loadTasks();
                }
            },
            app.currentPage === totalPages,
            false,
            false,
            true,
            true
        ));

        paginationContainer.appendChild(nav);
    },
    getPriorityClass: (priority) => {
        if (priority >= 4) return 'bg-red-100 text-red-800';
        if (priority >= 3) return 'bg-yellow-100 text-yellow-800';
        return 'bg-green-100 text-green-800';
    },
    getImportanceClass: (importance) => {
        if (importance >= 4) return 'bg-purple-100 text-purple-800';
        if (importance >= 3) return 'bg-blue-100 text-blue-800';
        return 'bg-gray-100 text-gray-800';
    },
    showToast: (message, type = 'success') => {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        const bgClass = type === 'success' ? 'bg-green-500' : 'bg-red-500';
        toast.className = `${bgClass} text-white px-6 py-3 rounded-lg shadow-lg transform transition-all duration-300 translate-y-10 opacity-0 flex items-center gap-2`;
        toast.innerHTML = `
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                ${type === 'success'
                ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>'
                : '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>'}
            </svg>
            <span>${message}</span>
        `;
        container.appendChild(toast);

        // Trigger animation
        requestAnimationFrame(() => {
            toast.classList.remove('translate-y-10', 'opacity-0');
        });

        setTimeout(() => {
            toast.classList.add('translate-y-10', 'opacity-0');
            setTimeout(() => {
                container.removeChild(toast);
            }, 300);
        }, 3000);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    app.init();

    // Tab Listeners
    document.getElementById('tab-assigned-to-me').addEventListener('click', () => app.switchTab('assigned_to_me'));
    document.getElementById('tab-assigned-by-me').addEventListener('click', () => app.switchTab('assigned_by_me'));

    // Login Form
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = e.target.email.value;
        const password = e.target.password.value;
        try {
            await api.login(email, password);
            app.init();
            app.showToast('Login successful', 'success');
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
            app.showToast('Registration successful', 'success');
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
        const button = e.target.querySelector('button');
        const originalText = button.textContent;

        button.disabled = true;
        button.textContent = 'Creating...';

        try {
            await api.createTask(description);
            e.target.reset();
            app.showToast('Task created successfully');
            app.loadTasks();
        } catch (err) {
            app.showToast(err.message, 'error');
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    });
});
