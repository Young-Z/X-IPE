/** Accessible, server-backed local directory picker. */
class LocalDirectoryPicker {
    constructor(api) { this.api = api; this.overlay = null; this.returnFocus = null; }

    async open(startPath, onSelect) {
        this.returnFocus = document.activeElement;
        this.onSelect = onSelect;
        this.overlay = document.createElement('div');
        this.overlay.className = 'cr-picker-backdrop';
        this.overlay.innerHTML = `<section class="cr-picker" role="dialog" aria-modal="true" aria-labelledby="cr-picker-title"><header><h2 id="cr-picker-title">Select codebase directory</h2><button type="button" data-close aria-label="Close directory picker">×</button></header><div class="cr-picker__path"><input aria-label="Directory path"><button type="button" data-go>Go</button></div><div class="cr-picker__body" role="listbox" aria-label="Child directories"></div><footer><button type="button" data-cancel>Cancel</button><button type="button" data-select>Select this directory</button></footer></section>`;
        document.body.appendChild(this.overlay);
        this.overlay.querySelector('[data-close]').addEventListener('click', () => this.close());
        this.overlay.querySelector('[data-cancel]').addEventListener('click', () => this.close());
        this.overlay.querySelector('[data-go]').addEventListener('click', () => this.navigate(this.overlay.querySelector('input').value));
        this.overlay.querySelector('[data-select]').addEventListener('click', () => { this.onSelect?.(this.currentPath); this.close(); });
        this.overlay.addEventListener('keydown', (event) => { if (event.key === 'Escape') this.close(); });
        await this.navigate(startPath);
        this.overlay.querySelector('[data-close]').focus();
    }

    async navigate(path) {
        const body = this.overlay.querySelector('.cr-picker__body');
        body.textContent = 'Loading…';
        try {
            const data = await this.api.listDirectories(path);
            this.currentPath = data.path;
            this.overlay.querySelector('input').value = data.path;
            body.replaceChildren();
            if (data.parent) body.appendChild(this._row('..', data.parent));
            for (const directory of data.directories) body.appendChild(this._row(directory.name, directory.path));
            if (!body.children.length) body.textContent = 'No readable child directories.';
        } catch (error) { body.textContent = error.message; }
    }

    _row(name, path) {
        const button = document.createElement('button');
        button.type = 'button'; button.setAttribute('role', 'option');
        button.innerHTML = `<i class="bi bi-folder2" aria-hidden="true"></i><span></span>`;
        button.querySelector('span').textContent = name;
        button.addEventListener('click', () => this.navigate(path));
        return button;
    }

    close() {
        this.overlay?.remove(); this.overlay = null;
        this.returnFocus?.focus?.();
    }
}
globalThis.LocalDirectoryPicker = LocalDirectoryPicker;
