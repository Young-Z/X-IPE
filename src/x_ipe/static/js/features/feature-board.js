/**
 * Feature Board — vanilla JS controller.
 * Feature: FEATURE-057-B
 * Consumes: GET /api/features/epic-summary, /api/features/list, /api/features/get/<id>
 */
(function () {
    'use strict';

    // ── State ────────────────────────────────────────────────────────
    var state = {
        status: '',
        search: '',
        summaries: [],
        epicFeatures: {},   // epicId → features[]
        epicLoaded: {},     // epicId → bool (lazy-load flag)
        expandedEpic: null,
        expandedFeature: null,
    };

    // ── Constants ────────────────────────────────────────────────────
    var STATUS_ORDER = ['Planned', 'Refined', 'Designed', 'Implemented', 'Tested', 'Completed', 'Retired'];

    var STATUS_COLORS = {
        'Planned':     { color: '#94a3b8', bg: '#f1f5f9' },
        'Refined':     { color: '#8b5cf6', bg: '#f5f3ff' },
        'Designed':    { color: '#3b82f6', bg: '#eff6ff' },
        'Implemented': { color: '#f59e0b', bg: '#fffbeb' },
        'Tested':      { color: '#06b6d4', bg: '#ecfeff' },
        'Completed':   { color: '#22c55e', bg: '#f0fdf4' },
        'Retired':     { color: '#64748b', bg: '#f1f5f9' },
    };

    // ── DOM refs ─────────────────────────────────────────────────────
    var elEpics, elError, elErrorMsg, elEmpty;

    // ── API ──────────────────────────────────────────────────────────
    async function fetchSummary() {
        try {
            hideError();
            var resp = await fetch('/api/features/epic-summary');
            if (!resp.ok) throw new Error('HTTP ' + resp.status);
            var json = await resp.json();
            if (!json.success) throw new Error(json.message || 'API error');
            state.summaries = json.data.summaries || [];
            state.epicFeatures = {};
            state.epicLoaded = {};
            state.expandedEpic = null;
            state.expandedFeature = null;
            renderEpics();
        } catch (err) {
            showError('Error loading features: ' + err.message);
            state.summaries = [];
            renderEpics();
        }
    }

    async function fetchEpicFeatures(epicId) {
        var params = new URLSearchParams({ epic_id: epicId, page_size: '200' });
        if (state.status) params.set('status', state.status);
        if (state.search) params.set('search', state.search);

        try {
            var resp = await fetch('/api/features/list?' + params.toString());
            if (!resp.ok) throw new Error('HTTP ' + resp.status);
            var json = await resp.json();
            if (!json.success) throw new Error(json.message || 'API error');
            var features = json.data.features || [];
            state.epicFeatures[epicId] = sortByStatusPriority(features);
            state.epicLoaded[epicId] = true;
            renderEpicBody(epicId);
        } catch (err) {
            var body = document.getElementById('fb-body-' + epicId);
            if (body) body.innerHTML = '<div class="fb-loading">Error loading features</div>';
        }
    }

    // ── Render ───────────────────────────────────────────────────────
    function renderEpics() {
        if (state.summaries.length === 0) {
            elEpics.innerHTML = '';
            elEmpty.style.display = '';
            return;
        }
        elEmpty.style.display = 'none';

        // Sort epics by epic_id descending (newest first)
        var sorted = state.summaries.slice().sort(function (a, b) {
            return b.epic_id.localeCompare(a.epic_id);
        });

        elEpics.innerHTML = sorted.map(function (s, i) {
            var total = s.total || 0;
            var progressHtml = renderProgressBar(s, total);
            var isOpen = state.expandedEpic === s.epic_id;

            return '<div class="fb-epic-group' + (isOpen ? ' open' : '') +
                '" id="fb-epic-' + esc(s.epic_id) + '" style="animation-delay:' + (i * 0.05) + 's">' +
                '<div class="fb-epic-header" data-epic="' + esc(s.epic_id) + '">' +
                '<span class="fb-epic-chevron">▶</span>' +
                '<span class="fb-epic-id">' + esc(s.epic_id) + '</span>' +
                '<span class="fb-epic-name">' + esc(s.epic_id) + '</span>' +
                '<span class="fb-epic-count">' + total + ' feature' + (total !== 1 ? 's' : '') + '</span>' +
                progressHtml +
                '</div>' +
                '<div class="fb-epic-body" id="fb-body-' + esc(s.epic_id) + '">' +
                (isOpen && state.epicLoaded[s.epic_id] ? '' : '<div class="fb-loading">Loading…</div>') +
                '</div></div>';
        }).join('');

        // Re-render loaded epic bodies
        sorted.forEach(function (s) {
            if (state.expandedEpic === s.epic_id && state.epicLoaded[s.epic_id]) {
                renderEpicBody(s.epic_id);
            }
        });
    }

    function renderProgressBar(summary, total) {
        if (total === 0) return '<div class="fb-progress-bar"></div>';
        var segments = STATUS_ORDER.map(function (status) {
            var count = summary[status] || 0;
            if (count === 0) return '';
            var pct = (count / total * 100).toFixed(1);
            var color = (STATUS_COLORS[status] || {}).color || '#94a3b8';
            return '<div class="fb-progress-segment" style="width:' + pct + '%;background:' + color + '"></div>';
        }).join('');
        return '<div class="fb-progress-bar">' + segments + '</div>';
    }

    function renderEpicBody(epicId) {
        var body = document.getElementById('fb-body-' + epicId);
        if (!body) return;
        var features = state.epicFeatures[epicId] || [];

        if (features.length === 0) {
            body.innerHTML = '<div class="fb-loading">No features in this epic</div>';
            return;
        }

        var html = '<table class="fb-feature-table"><thead><tr>' +
            '<th>Feature ID</th><th>Title</th><th>Version</th><th>Status</th><th>Spec</th><th>Updated</th>' +
            '</tr></thead><tbody>';

        html += features.map(function (f) {
            var statusCls = (f.status || '').toLowerCase();
            var specHtml = f.specification_link
                ? '<a class="fb-spec-link" href="' + esc(f.specification_link) + '" target="_blank" rel="noopener">specification.md</a>'
                : '<span class="fb-dash">—</span>';

            var row = '<tr data-feature-id="' + esc(f.feature_id) + '">' +
                '<td><span class="fb-feature-id">' + esc(f.feature_id) + '</span></td>' +
                '<td>' + esc(f.title || '') + '</td>' +
                '<td><span class="fb-version-badge">' + esc(f.version || '') + '</span></td>' +
                '<td><span class="fb-status-badge ' + statusCls + '">' +
                '<span class="fb-status-dot"></span>' + esc(f.status || '—') + '</span></td>' +
                '<td>' + specHtml + '</td>' +
                '<td><span class="fb-date">' + esc(formatDate(f.last_updated)) + '</span></td></tr>';

            if (state.expandedFeature === f.feature_id) {
                row += renderDetailRow(f);
            }
            return row;
        }).join('');

        html += '</tbody></table>';
        body.innerHTML = html;
    }

    function renderDetailRow(f) {
        var deps = '';
        if (f.dependencies && f.dependencies.length > 0) {
            deps = '<div class="fb-detail-deps"><strong>Dependencies:</strong> ' +
                f.dependencies.map(function (d) { return '<span>' + esc(d) + '</span>'; }).join('') +
                '</div>';
        }
        var specLink = f.specification_link
            ? '<div style="margin-top:8px"><a class="fb-spec-link" href="' + esc(f.specification_link) +
              '" target="_blank" rel="noopener">' + esc(f.specification_link) + '</a></div>'
            : '';

        return '<tr class="fb-detail-row"><td colspan="6"><div class="fb-detail-content">' +
            '<h4>' + esc(f.feature_id) + ' — ' + esc(f.title || '') + '</h4>' +
            '<p>' + esc(f.description || 'No description') + '</p>' +
            '<div class="fb-detail-meta">' +
            '<span><strong>Epic:</strong> ' + esc(f.epic_id || '—') + '</span>' +
            '<span><strong>Version:</strong> ' + esc(f.version || '—') + '</span>' +
            '<span><strong>Created:</strong> ' + esc(formatDate(f.created_at)) + '</span>' +
            '<span><strong>Updated:</strong> ' + esc(formatDate(f.last_updated)) + '</span>' +
            '</div>' + deps + specLink + '</div></td></tr>';
    }

    // ── Helpers ──────────────────────────────────────────────────────
    function sortByStatusPriority(features) {
        return features.slice().sort(function (a, b) {
            var ia = STATUS_ORDER.indexOf(a.status);
            var ib = STATUS_ORDER.indexOf(b.status);
            if (ia === -1) ia = 999;
            if (ib === -1) ib = 999;
            if (ia !== ib) return ia - ib;
            return (a.feature_id || '').localeCompare(b.feature_id || '');
        });
    }

    function debounce(fn, ms) {
        var timer;
        return function () {
            clearTimeout(timer);
            timer = setTimeout(fn, ms);
        };
    }

    function esc(str) {
        if (str == null) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function formatDate(dateStr) {
        if (!dateStr) return '—';
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
    var TEMPLATE = '<div class="fb-page">' +
        '<div class="fb-header"><h1 class="fb-title">Feature Board</h1>' +
        '<p class="fb-subtitle">Track features across epics in the engineering workflow</p></div>' +
        '<div class="fb-filters">' +
        '<div class="fb-search-wrap"><i class="bi bi-search fb-search-icon"></i>' +
        '<input id="fb-search" class="fb-search-input" type="text" placeholder="Search by feature ID, title, or Epic…"></div>' +
        '<div class="fb-filter-divider"></div>' +
        '<select id="fb-status-filter" class="fb-select">' +
        '<option value="">All Statuses</option><option value="Planned">Planned</option>' +
        '<option value="Refined">Refined</option><option value="Designed">Designed</option>' +
        '<option value="Implemented">Implemented</option><option value="Tested">Tested</option>' +
        '<option value="Completed">Completed</option><option value="Retired">Retired</option></select></div>' +
        '<div id="fb-error" class="fb-error" style="display:none;">' +
        '<i class="bi bi-exclamation-triangle-fill"></i><span id="fb-error-msg"></span></div>' +
        '<div id="fb-epics" class="fb-epics"></div>' +
        '<div id="fb-empty" class="fb-empty" style="display:none;">' +
        '<i class="bi bi-inbox"></i><p>No features found</p>' +
        '<span>Try adjusting your search or status filter</span></div></div>';

    // ── Bind & Init ─────────────────────────────────────────────────
    function init() {
        // Reset state for fresh render
        state.status = '';
        state.search = '';
        state.summaries = [];
        state.epicFeatures = {};
        state.epicLoaded = {};
        state.expandedEpic = null;
        state.expandedFeature = null;

        elEpics = document.getElementById('fb-epics');
        elError = document.getElementById('fb-error');
        elErrorMsg = document.getElementById('fb-error-msg');
        elEmpty = document.getElementById('fb-empty');

        if (!elEpics) return;

        // Epic header click (delegated)
        elEpics.addEventListener('click', function (e) {
            var featureRow = e.target.closest('tr[data-feature-id]');
            if (featureRow) {
                if (e.target.closest('a')) return;
                var fid = featureRow.getAttribute('data-feature-id');
                state.expandedFeature = (state.expandedFeature === fid) ? null : fid;
                var epicGroup = featureRow.closest('.fb-epic-group');
                if (epicGroup) {
                    var epicId = epicGroup.querySelector('.fb-epic-header').getAttribute('data-epic');
                    renderEpicBody(epicId);
                }
                return;
            }

            var header = e.target.closest('.fb-epic-header');
            if (!header) return;
            var epicId = header.getAttribute('data-epic');
            var group = document.getElementById('fb-epic-' + epicId);
            if (!group) return;

            if (state.expandedEpic === epicId) {
                state.expandedEpic = null;
                group.classList.remove('open');
            } else {
                if (state.expandedEpic) {
                    var prev = document.getElementById('fb-epic-' + state.expandedEpic);
                    if (prev) prev.classList.remove('open');
                }
                state.expandedEpic = epicId;
                state.expandedFeature = null;
                group.classList.add('open');

                if (!state.epicLoaded[epicId]) {
                    fetchEpicFeatures(epicId);
                }
            }
        });

        // Status filter
        document.getElementById('fb-status-filter').addEventListener('change', function (e) {
            state.status = e.target.value;
            state.epicLoaded = {};
            state.epicFeatures = {};
            state.expandedFeature = null;
            if (state.expandedEpic) {
                fetchEpicFeatures(state.expandedEpic);
            }
        });

        // Search with debounce
        var searchInput = document.getElementById('fb-search');
        searchInput.addEventListener('input', debounce(function () {
            state.search = searchInput.value.trim();
            state.epicLoaded = {};
            state.epicFeatures = {};
            state.expandedFeature = null;
            if (state.expandedEpic) {
                fetchEpicFeatures(state.expandedEpic);
            }
        }, 300));

        fetchSummary();
    }

    // ── SPA entry point ─────────────────────────────────────────────
    window.FeatureBoardPanel = {
        render: function (container) {
            if (!document.getElementById('feature-board-css')) {
                var link = document.createElement('link');
                link.id = 'feature-board-css';
                link.rel = 'stylesheet';
                link.href = '/static/css/feature-board.css';
                document.head.appendChild(link);
            }
            container.innerHTML = TEMPLATE;
            init();
        }
    };

    // ── Full-page route entry point ─────────────────────────────────
    document.addEventListener('DOMContentLoaded', function () {
        if (document.getElementById('fb-epics')) {
            init();
        }
    });
})();
