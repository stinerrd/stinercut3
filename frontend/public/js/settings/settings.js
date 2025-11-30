/**
 * Settings Form Handler - Inline Editing
 *
 * Handles per-row inline editing of settings via AJAX.
 * Uses event delegation for Edit/Save/Cancel buttons.
 */
(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', init);

    function init() {
        document.addEventListener('click', function(e) {
            const editBtn = e.target.closest('.btn-edit');
            const saveBtn = e.target.closest('.btn-save');
            const cancelBtn = e.target.closest('.btn-cancel');

            if (editBtn) enterEditMode(editBtn.closest('tr'));
            if (saveBtn) saveSetting(saveBtn.closest('tr'));
            if (cancelBtn) exitEditMode(cancelBtn.closest('tr'));
        });
    }

    function enterEditMode(row) {
        row.querySelector('.setting-view').style.display = 'none';
        row.querySelector('.setting-edit').style.display = '';
        row.querySelector('.setting-view-buttons').style.display = 'none';
        row.querySelector('.setting-edit-buttons').style.display = '';

        const input = row.querySelector('.setting-input');
        input.focus();
        if (input.select) input.select();
    }

    function exitEditMode(row) {
        row.querySelector('.setting-view').style.display = '';
        row.querySelector('.setting-edit').style.display = 'none';
        row.querySelector('.setting-view-buttons').style.display = '';
        row.querySelector('.setting-edit-buttons').style.display = 'none';

        // Reset to original value
        const input = row.querySelector('.setting-input');
        if (input.dataset.original !== undefined) {
            input.value = input.dataset.original;
        }
    }

    function saveSetting(row) {
        const key = row.dataset.settingKey;
        const input = row.querySelector('.setting-input');
        const newValue = input.value;
        const type = input.dataset.type;

        fetch('/api/settings/' + encodeURIComponent(key), {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ value: newValue })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateViewDisplay(row, newValue, type);
                input.dataset.original = newValue;
                exitEditMode(row);
                showToast('Setting updated successfully', 'success');
            } else {
                showToast(data.error || 'Failed to save', 'danger');
            }
        })
        .catch(error => {
            console.error('[Settings] Error:', error);
            showToast('Network error', 'danger');
        });
    }

    function updateViewDisplay(row, value, type) {
        const code = row.querySelector('.setting-view code');
        if (code) {
            code.textContent = value;
        }
    }

    function showToast(message, type) {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(container);
        }

        const toastEl = document.createElement('div');
        toastEl.className = 'toast align-items-center text-bg-' + type + ' border-0';
        toastEl.innerHTML = '<div class="d-flex"><div class="toast-body">' + message +
            '</div><button class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>';

        container.appendChild(toastEl);
        new bootstrap.Toast(toastEl, { delay: 3000 }).show();
        toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
    }
})();
