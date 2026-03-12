/**
 * Bootstrap 5 Dialog Utilities (CR-001)
 *
 * Replaces native browser alert(), confirm(), prompt() with
 * styled Bootstrap 5 modals. All functions return Promises.
 */

const _MODAL_ID = 'bs-dialog-modal';

function _getOrCreateModal() {
    let el = document.getElementById(_MODAL_ID);
    if (el) return el;

    el = document.createElement('div');
    el.id = _MODAL_ID;
    el.className = 'modal fade';
    el.tabIndex = -1;
    el.setAttribute('aria-hidden', 'true');
    el.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"></h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body"></div>
                <div class="modal-footer"></div>
            </div>
        </div>`;
    document.body.appendChild(el);
    return el;
}

/**
 * Show a confirmation modal (replaces native confirm()).
 * @param {string} title - Modal title
 * @param {string} body - Body text (supports HTML)
 * @param {Object} [opts] - Options
 * @param {string} [opts.confirmLabel='Confirm'] - Confirm button label
 * @param {string} [opts.cancelLabel='Cancel'] - Cancel button label
 * @param {boolean} [opts.danger=false] - Use danger (red) confirm button
 * @returns {Promise<boolean>} true if confirmed, false if cancelled
 */
function showConfirmModal(title, body, opts = {}) {
    const { confirmLabel = 'Confirm', cancelLabel = 'Cancel', danger = false } = opts;

    return new Promise(resolve => {
        const modal = _getOrCreateModal();
        modal.querySelector('.modal-title').textContent = title;
        modal.querySelector('.modal-body').innerHTML = body;

        const btnClass = danger ? 'btn btn-danger' : 'btn btn-primary';
        modal.querySelector('.modal-footer').innerHTML = `
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">${cancelLabel}</button>
            <button type="button" class="${btnClass} bs-dialog-confirm">${confirmLabel}</button>`;

        const bsModal = new bootstrap.Modal(modal, { backdrop: 'static' });
        let confirmed = false;

        const confirmBtn = modal.querySelector('.bs-dialog-confirm');
        const onConfirm = () => { confirmed = true; bsModal.hide(); };
        confirmBtn.addEventListener('click', onConfirm, { once: true });

        modal.addEventListener('hidden.bs.modal', () => {
            confirmBtn.removeEventListener('click', onConfirm);
            resolve(confirmed);
        }, { once: true });

        bsModal.show();
    });
}

/**
 * Show a prompt modal (replaces native prompt()).
 * @param {string} title - Modal title
 * @param {string} message - Instructional message
 * @param {Object} [opts] - Options
 * @param {string} [opts.placeholder=''] - Input placeholder
 * @param {string} [opts.defaultValue=''] - Pre-filled value
 * @param {boolean} [opts.required=true] - Require non-empty input
 * @returns {Promise<string|null>} entered text, or null if cancelled
 */
function showPromptModal(title, message, opts = {}) {
    const { placeholder = '', defaultValue = '', required = true } = opts;

    return new Promise(resolve => {
        const modal = _getOrCreateModal();
        modal.querySelector('.modal-title').textContent = title;
        modal.querySelector('.modal-body').innerHTML = `
            <p class="text-secondary mb-2">${message}</p>
            <input type="text" class="form-control bs-dialog-input" placeholder="${placeholder}" value="${defaultValue}" autocomplete="off" />
            <div class="text-danger small mt-1 bs-dialog-error"></div>`;
        modal.querySelector('.modal-footer').innerHTML = `
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary bs-dialog-ok">OK</button>`;

        const bsModal = new bootstrap.Modal(modal, { backdrop: 'static' });
        let result = null;

        const input = modal.querySelector('.bs-dialog-input');
        const errDiv = modal.querySelector('.bs-dialog-error');
        const okBtn = modal.querySelector('.bs-dialog-ok');

        const submit = () => {
            const v = input.value.trim();
            if (required && !v) { errDiv.textContent = 'Value is required'; return; }
            result = v || null;
            bsModal.hide();
        };

        okBtn.addEventListener('click', submit, { once: false });
        input.addEventListener('keydown', e => { if (e.key === 'Enter') submit(); });

        modal.addEventListener('hidden.bs.modal', () => {
            okBtn.removeEventListener('click', submit);
            resolve(result);
        }, { once: true });

        bsModal.show();
        setTimeout(() => input.focus(), 200);
    });
}

/**
 * Show an alert modal (replaces native alert()).
 * @param {string} title - Modal title
 * @param {string} body - Body text (supports HTML)
 * @param {Object} [opts] - Options
 * @param {string} [opts.okLabel='OK'] - OK button label
 * @returns {Promise<void>} resolves when dismissed
 */
function showAlertModal(title, body, opts = {}) {
    const { okLabel = 'OK' } = opts;

    return new Promise(resolve => {
        const modal = _getOrCreateModal();
        modal.querySelector('.modal-title').textContent = title;
        modal.querySelector('.modal-body').innerHTML = body;
        modal.querySelector('.modal-footer').innerHTML = `
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal">${okLabel}</button>`;

        const bsModal = new bootstrap.Modal(modal, { backdrop: 'static' });

        modal.addEventListener('hidden.bs.modal', () => resolve(), { once: true });

        bsModal.show();
    });
}

// Export for use across the application
if (typeof window !== 'undefined') {
    window.showConfirmModal = showConfirmModal;
    window.showPromptModal = showPromptModal;
    window.showAlertModal = showAlertModal;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { showConfirmModal, showPromptModal, showAlertModal };
}
