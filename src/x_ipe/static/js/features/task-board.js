/**
 * Task Board — vanilla JS controller.
 * Feature: FEATURE-057-A
 * Consumes: GET /api/tasks/list, GET /api/tasks/get/<task_id>
 */
(function () {
    'use strict';

    // ── State ────────────────────────────────────────────────────────
    const state = {
        range: '1w',
        status: '',
        search: '',
        page: 1,
        pageSize: 50,
        tasks: [],
        pagination: null,
        expandedTaskId: null,
        sortField: 'task_id',
        sortDir: 'desc',
    };

    // ── Constants ────────────────────────────────────────────────────
    const STATUS_COLORS = {
        done: { color: '#22c55e', bg: '#f0fdf4', label: 'Done' },
        completed: { color: '#22c55e', bg: '#f0fdf4', label: 'Completed' },
        in_progress: { color: '#3b82f6', bg: '#eff6ff', label: 'In Progress' },
        pending: { color: '#f59e0b', bg: '#fffbeb', label: 'Pending' },
        blocked: { color: '#ef4444', bg: '#fef2f2', label: 'Blocked' },
        deferred: { color: '#8b5cf6', bg: '#f5f3ff', label: 'Deferred' },
    };

    const TYPE_COLORS = {
        'Ideation': { bg: '#fef3c7', color: '#92400e' },
        'Bug Fix': { bg: '#fce7f3', color: '#9d174d' },
        'Implementation': { bg: '#dbeafe', color: '#1e40af' },
        'Code Implementation': { bg: '#dbeafe', color: '#1e40af' },
        'Refinement': { bg: '#e0e7ff', color: '#3730a3' },
        'Feature Refinement': { bg: '#e0e7ff', color: '#3730a3' },
        'Feature Closing': { bg: '#d1fae5', color: '#065f46' },
        'Acceptance Test': { bg: '#fae8ff', color: '#86198f' },
        'Feature Acceptance Test': { bg: '#fae8ff', color: '#86198f' },
        'Technical Design': { bg: '#f1f5f9', color: '#334155' },
        'Skill Creation': { bg: '#ccfbf1', color: '#134e4a' },
        'Skill Update': { bg: '#ccfbf1', color: '#134e4a' },
        'Breakdown': { bg: '#fed7aa', color: '#9a3412' },
        'Feature Breakdown': { bg: '#fed7aa', color: '#9a3412' },
        'Feature Pipeline': { bg: '#dbeafe', color: '#1e40af' },
        'Code Refactor': { bg: '#f1f5f9', color: '#334155' },
        'Human Playground': { bg: '#fef3c7', color: '#92400e' },
        'Requirement Gathering': { bg: '#e0e7ff', color: '#3730a3' },
        'KB Librarian': { bg: '#ccfbf1', color: '#134e4a' },
    };

    const STAT_CARDS = [
        { key: 'total', label: 'Total Tasks', borderColor: '#475569' },
        { key: 'in_progress', label: 'In Progress', borderColor: '#3b82f6' },
        { key: 'done', label: 'Completed', borderColor: '#22c55e' },
        { key: 'blocked', label: 'Blocked', borderColor: '#ef4444' },
        { key: 'pending', label: 'Pending', borderColor: '#f59e0b' },
    ];

    // ── DOM refs ─────────────────────────────────────────────────────
    let elStats, elBody, elPagination, elError, elErrorMsg, elEmpty, elTable;

    // ── API ──────────────────────────────────────────────────────────
    async function fetchTasks() {
        const params = new URLSearchParams({
            range: state.range,
            page: String(state.page),
            page_size: String(state.pageSize),
        });
        if (state.status) params.set('status', state.status);
        if (state.search) params.set('search', state.search);

        try {
            hideError();
            const resp = await fetch('/api/tasks/list?' + params.toString());
            if (!resp.ok) throw new Error('HTTP ' + resp.status);
            const json = await resp.json();
            if (!json.success) throw new Error(json.message || 'API error');
            state.tasks = json.data.tasks || [];
            state.pagination = json.data.pagination || null;
            state.expandedTaskId = null;
            renderAll();
        } catch (err) {
            showError('Error loading tasks: ' + err.message);
            state.tasks = [];
            state.pagination = null;
            renderAll();
        }
    }

    // ── Sorting ───────────────────────────────────────────────────────
    function extractTaskNum(id) {
        var m = (id || '').match(/(\d+)$/);
        return m ? parseInt(m[1], 10) : 0;
    }

    function sortTasks(tasks) {
        var field = state.sortField;
        var dir = state.sortDir === 'asc' ? 1 : -1;
        return tasks.slice().sort(function (a, b) {
            var va, vb;
            if (field === 'task_id') {
                va = extractTaskNum(a.task_id);
                vb = extractTaskNum(b.task_id);
            } else {
                va = (a[field] || '').toLowerCase();
                vb = (b[field] || '').toLowerCase();
            }
            if (va < vb) return -1 * dir;
            if (va > vb) return 1 * dir;
            return 0;
        });
    }

    function sortArrow(field) {
        if (state.sortField !== field) return ' <span class="tb-sort-arrow inactive">⇅</span>';
        return state.sortDir === 'asc'
            ? ' <span class="tb-sort-arrow">↑</span>'
            : ' <span class="tb-sort-arrow">↓</span>';
    }

    function updateSortHeaders() {
        document.querySelectorAll('.tb-table thead th[data-sort]').forEach(function (th) {
            var field = th.dataset.sort;
            var label = th.dataset.label;
            th.innerHTML = escapeHtml(label) + sortArrow(field);
        });
    }

    // ── Render ───────────────────────────────────────────────────────
    function renderAll() {
        renderStats();
        updateSortHeaders();
        renderTable();
        renderPagination();
    }

    function renderStats() {
        const counts = { total: 0, in_progress: 0, done: 0, blocked: 0, pending: 0 };
        if (state.pagination) {
            counts.total = state.pagination.total;
        }
        state.tasks.forEach(function (t) {
            const s = (t.status || '').toLowerCase();
            if (s === 'in_progress') counts.in_progress++;
            else if (s === 'done' || s === 'completed') counts.done++;
            else if (s === 'blocked') counts.blocked++;
            else if (s === 'pending') counts.pending++;
        });

        elStats.innerHTML = STAT_CARDS.map(function (card, i) {
            return '<div class="tb-stat-card" style="border-top-color:' + card.borderColor +
                ';animation-delay:' + (i * 0.05) + 's">' +
                '<p class="tb-stat-label">' + escapeHtml(card.label) + '</p>' +
                '<p class="tb-stat-value">' + counts[card.key] + '</p></div>';
        }).join('');
    }

    function renderTable() {
        if (state.tasks.length === 0) {
            elTable.style.display = 'none';
            elEmpty.style.display = '';
            elBody.innerHTML = '';
            return;
        }
        elTable.style.display = '';
        elEmpty.style.display = 'none';

        var sorted = sortTasks(state.tasks);
        elBody.innerHTML = sorted.map(function (task) {
            var statusCls = (task.status || '').toLowerCase().replace(/\s+/g, '_');
            var statusInfo = STATUS_COLORS[statusCls] || { label: task.status || '—' };
            var typeInfo = TYPE_COLORS[task.task_type] || { bg: '#f1f5f9', color: '#334155' };
            var outputHtml = renderOutputLinks(task.output_links);
            var nextHtml = task.next_task ? escapeHtml(task.next_task) : '<span class="tb-dash">—</span>';

            var row = '<tr data-task-id="' + escapeHtml(task.task_id) + '">' +
                '<td><span class="tb-task-id">' + escapeHtml(task.task_id) + '</span></td>' +
                '<td><span class="tb-type-badge" style="background:' + typeInfo.bg + ';color:' + typeInfo.color + '">' +
                escapeHtml(task.task_type || '—') + '</span></td>' +
                '<td><span class="tb-description">' + escapeHtml(task.description || '') + '</span></td>' +
                '<td>' + escapeHtml(task.role || '—') + '</td>' +
                '<td><span class="tb-status-badge ' + statusCls + '">' +
                '<span class="tb-status-dot"></span>' + escapeHtml(statusInfo.label || task.status || '—') +
                '</span></td>' +
                '<td><span class="tb-date">' + escapeHtml(formatDate(task.last_updated)) + '</span></td>' +
                '<td>' + outputHtml + '</td>' +
                '<td>' + nextHtml + '</td></tr>';

            if (state.expandedTaskId === task.task_id) {
                row += renderDetailRow(task);
            }
            return row;
        }).join('');
    }

    function renderDetailRow(task) {
        var links = '';
        if (task.output_links && task.output_links.length > 0) {
            links = '<div class="tb-detail-links"><strong>Output Links:</strong><br>' +
                task.output_links.map(function (link) {
                    return '<a href="' + escapeHtml(link) + '" target="_blank" rel="noopener">' +
                        escapeHtml(link) + '</a>';
                }).join('') + '</div>';
        }
        return '<tr class="tb-detail-row"><td colspan="8"><div class="tb-detail-content">' +
            '<h4>' + escapeHtml(task.task_id) + ' — ' + escapeHtml(task.task_type || '') + '</h4>' +
            '<p>' + escapeHtml(task.description || 'No description') + '</p>' +
            '<div class="tb-detail-meta">' +
            '<span><strong>Role:</strong> ' + escapeHtml(task.role || '—') + '</span>' +
            '<span><strong>Created:</strong> ' + escapeHtml(formatDate(task.created_at)) + '</span>' +
            '<span><strong>Updated:</strong> ' + escapeHtml(formatDate(task.last_updated)) + '</span>' +
            '<span><strong>Next:</strong> ' + escapeHtml(task.next_task || '—') + '</span>' +
            '</div>' + links + '</div></td></tr>';
    }

    function renderOutputLinks(links) {
        if (!links || links.length === 0) return '<span class="tb-dash">—</span>';
        return links.slice(0, 2).map(function (link) {
            var short = link.length > 30 ? '…' + link.slice(-28) : link;
            return '<a class="tb-output-link" href="' + escapeHtml(link) +
                '" target="_blank" rel="noopener" title="' + escapeHtml(link) + '">' +
                escapeHtml(short) + '</a>';
        }).join(' ');
    }

    function renderPagination() {
        if (!state.pagination || state.pagination.total_pages <= 1) {
            elPagination.innerHTML = '';
            return;
        }
        var p = state.pagination;
        var start = (p.page - 1) * p.page_size + 1;
        var end = Math.min(p.page * p.page_size, p.total);
        var html = '<span class="tb-pagination-info">Showing ' + start + '–' + end + ' of ' + p.total + ' tasks</span>';

        html += '<button class="tb-page-btn" data-page="' + (p.page - 1) + '"' +
            (p.page <= 1 ? ' disabled' : '') + '>‹</button>';

        var maxVisible = 5;
        var startPage = Math.max(1, p.page - Math.floor(maxVisible / 2));
        var endPage = Math.min(p.total_pages, startPage + maxVisible - 1);
        if (endPage - startPage < maxVisible - 1) {
            startPage = Math.max(1, endPage - maxVisible + 1);
        }

        for (var i = startPage; i <= endPage; i++) {
            html += '<button class="tb-page-btn' + (i === p.page ? ' active' : '') +
                '" data-page="' + i + '">' + i + '</button>';
        }

        html += '<button class="tb-page-btn" data-page="' + (p.page + 1) + '"' +
            (p.page >= p.total_pages ? ' disabled' : '') + '>›</button>';

        elPagination.innerHTML = html;
    }

    // ── Helpers ──────────────────────────────────────────────────────
    function debounce(fn, ms) {
        var timer;
        return function () {
            clearTimeout(timer);
            timer = setTimeout(fn, ms);
        };
    }

    function escapeHtml(str) {
        if (str == null) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function formatDate(dateStr) {
        if (!dateStr) return '—';
        // Handle ISO dates, return as MM-DD-YYYY
        var d = new Date(dateStr);
        if (isNaN(d.getTime())) return dateStr;
        var mm = String(d.getMonth() + 1).padStart(2, '0');
        var dd = String(d.getDate()).padStart(2, '0');
        return mm + '-' + dd + '-' + d.getFullYear();
    }

    function showError(msg) {
        elErrorMsg.textContent = msg;
        elError.style.display = '';
    }

    function hideError() {
        elError.style.display = 'none';
        elErrorMsg.textContent = '';
    }

    // ── Template HTML (for SPA rendering) ─────────────────────────
    var TEMPLATE = '<div class="tb-page">' +
        '<div class="tb-header"><h1 class="tb-title">Task Board</h1>' +
        '<p class="tb-subtitle">Track all development tasks across the engineering workflow</p></div>' +
        '<div class="tb-stats" id="tb-stats"></div>' +
        '<div class="tb-filters">' +
        '<div class="tb-search-wrap"><i class="bi bi-search tb-search-icon"></i>' +
        '<input id="tb-search" class="tb-search-input" type="text" placeholder="Search by task ID, description, or role…"></div>' +
        '<div class="tb-filter-divider"></div>' +
        '<select id="tb-status-filter" class="tb-select">' +
        '<option value="">All Statuses</option><option value="in_progress">In Progress</option>' +
        '<option value="done">Done</option><option value="completed">Completed</option>' +
        '<option value="pending">Pending</option><option value="blocked">Blocked</option>' +
        '<option value="deferred">Deferred</option></select>' +
        '<div class="tb-filter-divider"></div>' +
        '<div class="tb-range-group" id="tb-range-group">' +
        '<button class="tb-range-btn active" data-range="1w">1W</button>' +
        '<button class="tb-range-btn" data-range="1m">1M</button>' +
        '<button class="tb-range-btn" data-range="all">All</button></div></div>' +
        '<div id="tb-error" class="tb-error" style="display:none;">' +
        '<i class="bi bi-exclamation-triangle-fill"></i><span id="tb-error-msg"></span></div>' +
        '<div class="tb-table-wrap"><table class="tb-table" id="tb-table">' +
        '<thead><tr>' +
        '<th class="tb-sortable" data-sort="task_id" data-label="Task ID">Task ID ↓</th>' +
        '<th class="tb-sortable" data-sort="task_type" data-label="Type">Type ⇅</th>' +
        '<th>Description</th><th>Role</th>' +
        '<th>Status</th><th>Updated</th><th>Output</th><th>Next</th>' +
        '</tr></thead><tbody id="tb-body"></tbody></table></div>' +
        '<div id="tb-empty" class="tb-empty" style="display:none;">' +
        '<i class="bi bi-inbox"></i><p>No tasks found</p>' +
        '<span>Try expanding the time range or adjusting filters</span></div>' +
        '<div class="tb-pagination" id="tb-pagination"></div></div>';

    // ── Bind & Init ─────────────────────────────────────────────────
    function init() {
        // Reset state for fresh render
        state.range = '1w';
        state.status = '';
        state.search = '';
        state.page = 1;
        state.tasks = [];
        state.pagination = null;
        state.expandedTaskId = null;
        state.sortField = 'task_id';
        state.sortDir = 'desc';

        elStats = document.getElementById('tb-stats');
        elBody = document.getElementById('tb-body');
        elPagination = document.getElementById('tb-pagination');
        elError = document.getElementById('tb-error');
        elErrorMsg = document.getElementById('tb-error-msg');
        elEmpty = document.getElementById('tb-empty');
        elTable = document.getElementById('tb-table');

        if (!elStats || !elBody) return;

        // Range buttons
        document.querySelectorAll('.tb-range-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                document.querySelector('.tb-range-btn.active').classList.remove('active');
                btn.classList.add('active');
                state.range = btn.dataset.range;
                state.page = 1;
                fetchTasks();
            });
        });

        // Sortable column headers
        document.querySelectorAll('.tb-sortable').forEach(function (th) {
            th.addEventListener('click', function () {
                var field = th.dataset.sort;
                if (state.sortField === field) {
                    state.sortDir = state.sortDir === 'asc' ? 'desc' : 'asc';
                } else {
                    state.sortField = field;
                    state.sortDir = field === 'task_id' ? 'desc' : 'asc';
                }
                updateSortHeaders();
                renderTable();
            });
        });

        // Status filter
        document.getElementById('tb-status-filter').addEventListener('change', function (e) {
            state.status = e.target.value;
            state.page = 1;
            fetchTasks();
        });

        // Search with debounce
        var searchInput = document.getElementById('tb-search');
        searchInput.addEventListener('input', debounce(function () {
            state.search = searchInput.value.trim();
            state.page = 1;
            fetchTasks();
        }, 300));

        // Pagination clicks (delegated)
        elPagination.addEventListener('click', function (e) {
            var btn = e.target.closest('.tb-page-btn');
            if (!btn || btn.disabled) return;
            state.page = parseInt(btn.dataset.page, 10);
            fetchTasks();
        });

        // Row click for detail expansion (delegated)
        elBody.addEventListener('click', function (e) {
            var row = e.target.closest('tr[data-task-id]');
            if (!row) return;
            if (e.target.closest('a')) return;
            var taskId = row.getAttribute('data-task-id');
            state.expandedTaskId = (state.expandedTaskId === taskId) ? null : taskId;
            renderTable();
        });

        fetchTasks();
    }

    // ── SPA entry point ─────────────────────────────────────────────
    window.TaskBoardPanel = {
        render: function (container) {
            if (!document.getElementById('task-board-css')) {
                var link = document.createElement('link');
                link.id = 'task-board-css';
                link.rel = 'stylesheet';
                link.href = '/static/css/task-board.css';
                document.head.appendChild(link);
            }
            container.innerHTML = TEMPLATE;
            init();
        }
    };

    // ── Full-page route entry point ─────────────────────────────────
    document.addEventListener('DOMContentLoaded', function () {
        if (document.getElementById('tb-stats')) {
            init();
        }
    });
})();
