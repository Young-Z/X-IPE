/**
 * FEATURE-049-E: KB File Upload Component
 * Drag-drop upload zone with folder destination picker and archive auto-extraction.
 */

const KB_UPLOAD_MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const KB_UPLOAD_CLOSE_DELAY_MS = 300;

class KBFileUpload {
    constructor(options = {}) {
        this.folder = options.folder || '';
        this.onComplete = options.onComplete || null;
        this.overlay = null;
        this.folderTree = [];
        this.maxFileSize = KB_UPLOAD_MAX_FILE_SIZE;
    }

    async open() {
        await this._loadFolderTree();
        this._createModal();
        document.body.style.overflow = 'hidden';
        requestAnimationFrame(() => {
            if (this.overlay) this.overlay.classList.add('active');
        });
    }

    close() {
        if (this.overlay) {
            this.overlay.classList.remove('active');
            setTimeout(() => {
                if (this.overlay && this.overlay.parentNode) {
                    this.overlay.parentNode.removeChild(this.overlay);
                }
                this.overlay = null;
                document.body.style.overflow = '';
            }, KB_UPLOAD_CLOSE_DELAY_MS);
        }
    }

    async _loadFolderTree() {
        try {
            const res = await fetch('/api/kb/tree');
            if (res.ok) {
                const data = await res.json();
                this.folderTree = this._extractFolders(data.tree || []);
            }
        } catch (e) {
            console.error('Failed to load KB folder tree:', e);
        }
    }

    _extractFolders(nodes, prefix = '') {
        let folders = [];
        for (const node of nodes) {
            if (node.type === 'folder') {
                const path = prefix ? `${prefix}/${node.name}` : node.name;
                folders.push({ name: node.name, path, depth: prefix.split('/').filter(Boolean).length });
                if (node.children) {
                    folders = folders.concat(this._extractFolders(node.children, path));
                }
            }
        }
        return folders;
    }

    _buildFolderOptionsHTML() {
        return [
            '<option value="">/ (root)</option>',
            ...this.folderTree.map(f =>
                `<option value="${f.path}" ${f.path === this.folder ? 'selected' : ''}>${'  '.repeat(f.depth + 1)}📁 ${f.name}</option>`
            )
        ].join('');
    }

    _buildModalHTML() {
        return `
            <div class="kb-upload-modal">
                <div class="kb-upload-header">
                    <h3>📤 Upload Files</h3>
                    <button class="kb-upload-close" title="Close">&times;</button>
                </div>
                <div class="kb-upload-body">
                    <div class="kb-upload-folder-select">
                        <label>Destination folder:</label>
                        <div class="kb-upload-folder-row">
                            <select class="kb-upload-folder-dropdown">${this._buildFolderOptionsHTML()}</select>
                            <button class="kb-upload-newfolder-btn" title="New folder">+ Folder</button>
                        </div>
                        <div class="kb-upload-newfolder-input" style="display:none;">
                            <input type="text" placeholder="New folder name..." class="kb-newfolder-name">
                            <button class="kb-newfolder-create-btn">Create</button>
                            <button class="kb-newfolder-cancel-btn">Cancel</button>
                        </div>
                    </div>
                    <div class="kb-upload-dropzone" tabindex="0">
                        <input type="file" class="kb-upload-file-input" multiple style="display:none;">
                        <div class="kb-upload-dropzone-content">
                            <i class="bi bi-cloud-upload"></i>
                            <p>Drag & drop files here, or <span class="kb-upload-browse-link">browse</span></p>
                            <small>Supports all file types — Max 10MB per file</small>
                        </div>
                    </div>
                    <div class="kb-upload-progress" style="display:none;">
                        <div class="kb-upload-progress-list"></div>
                    </div>
                </div>
            </div>
        `;
    }

    _createModal() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'kb-upload-overlay';
        this.overlay.innerHTML = this._buildModalHTML();
        document.body.appendChild(this.overlay);
        this._bindModalEvents();
    }

    _bindModalEvents() {
        this._bindCloseEvents();
        this._bindFolderEvents();
        this._bindDropzoneEvents();
    }

    _bindCloseEvents() {
        const closeBtn = this.overlay.querySelector('.kb-upload-close');
        closeBtn.addEventListener('click', () => this.close());

        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) this.close();
        });
    }

    _bindFolderEvents() {
        const folderSelect = this.overlay.querySelector('.kb-upload-folder-dropdown');
        folderSelect.addEventListener('change', () => {
            this.folder = folderSelect.value;
        });

        const newFolderBtn = this.overlay.querySelector('.kb-upload-newfolder-btn');
        const newFolderInput = this.overlay.querySelector('.kb-upload-newfolder-input');
        newFolderBtn.addEventListener('click', () => {
            newFolderInput.style.display = newFolderInput.style.display === 'none' ? 'flex' : 'none';
        });

        const createFolderBtn = this.overlay.querySelector('.kb-newfolder-create-btn');
        createFolderBtn.addEventListener('click', async () => {
            const nameInput = this.overlay.querySelector('.kb-newfolder-name');
            const name = nameInput.value.trim();
            if (!name) return;

            const path = this.folder ? `${this.folder}/${name}` : name;
            try {
                const res = await fetch('/api/kb/folders', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path })
                });
                if (res.ok) {
                    this.folder = path;
                    nameInput.value = '';
                    newFolderInput.style.display = 'none';
                    await this._loadFolderTree();
                    this._updateFolderDropdown();
                    document.dispatchEvent(new CustomEvent('kb:changed'));
                }
            } catch (e) {
                console.error('Failed to create folder:', e);
            }
        });

        const cancelFolderBtn = this.overlay.querySelector('.kb-newfolder-cancel-btn');
        cancelFolderBtn.addEventListener('click', () => {
            newFolderInput.style.display = 'none';
        });
    }

    _bindDropzoneEvents() {
        const dropzone = this.overlay.querySelector('.kb-upload-dropzone');
        const fileInput = this.overlay.querySelector('.kb-upload-file-input');

        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                this._uploadFiles(e.dataTransfer.files);
            }
        });

        const browseLink = this.overlay.querySelector('.kb-upload-browse-link');
        browseLink.addEventListener('click', () => fileInput.click());
        dropzone.addEventListener('click', (e) => {
            if (e.target === dropzone || e.target.closest('.kb-upload-dropzone-content')) {
                fileInput.click();
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                this._uploadFiles(fileInput.files);
            }
        });
    }

    _updateFolderDropdown() {
        const dropdown = this.overlay?.querySelector('.kb-upload-folder-dropdown');
        if (!dropdown) return;
        dropdown.innerHTML = this._buildFolderOptionsHTML();
    }

    async _uploadFiles(fileList) {
        const progressArea = this.overlay.querySelector('.kb-upload-progress');
        const progressList = this.overlay.querySelector('.kb-upload-progress-list');
        progressArea.style.display = 'block';
        progressList.innerHTML = '';

        const validFiles = this._validateAndRenderFiles(fileList, progressList);
        if (validFiles.length === 0) return;

        const formData = new FormData();
        formData.append('folder', this.folder);
        for (const { file } of validFiles) {
            formData.append('files', file);
        }

        try {
            const res = await fetch('/api/kb/upload', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            this._updateFileStatuses(validFiles, data);

            if (data.total > 0) {
                document.dispatchEvent(new CustomEvent('kb:changed'));
                if (this.onComplete) this.onComplete();
            }
        } catch (e) {
            this._markAllFailed(validFiles);
        }
    }

    _validateAndRenderFiles(fileList, progressList) {
        const validFiles = [];
        for (const file of fileList) {
            const item = document.createElement('div');
            item.className = 'kb-upload-progress-item';

            if (file.size > this.maxFileSize) {
                item.innerHTML = `<span class="kb-upload-fname">${this._escapeHtml(file.name)}</span> <span class="kb-upload-status kb-upload-error">❌ Too large (>10MB)</span>`;
                progressList.appendChild(item);
                continue;
            }

            item.innerHTML = `<span class="kb-upload-fname">${this._escapeHtml(file.name)}</span> <span class="kb-upload-status kb-upload-pending">⏳ Uploading...</span>`;
            progressList.appendChild(item);
            validFiles.push({ file, item });
        }
        return validFiles;
    }

    _updateFileStatuses(validFiles, data) {
        for (const { file, item } of validFiles) {
            const statusEl = item.querySelector('.kb-upload-status');
            const err = (data.errors || []).find(e => e.file === file.name);
            if (err) {
                statusEl.className = 'kb-upload-status kb-upload-error';
                statusEl.textContent = `❌ ${err.error}`;
            } else {
                statusEl.className = 'kb-upload-status kb-upload-success';
                statusEl.textContent = '✅ Uploaded';
            }
        }
    }

    _markAllFailed(validFiles) {
        for (const { item } of validFiles) {
            const statusEl = item.querySelector('.kb-upload-status');
            statusEl.className = 'kb-upload-status kb-upload-error';
            statusEl.textContent = '❌ Upload failed';
        }
    }

    _escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
}
