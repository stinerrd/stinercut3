/**
 * Settings Form Handler - Inline Editing
 *
 * Handles per-row inline editing of settings via AJAX.
 * Uses event delegation for Edit/Save/Cancel buttons.
 * Supports entity reference types (splashscreen, sound) with custom dropdowns.
 */
(function() {
    'use strict';

    // Cache for entity options to avoid repeated API calls
    const entityCache = {};

    document.addEventListener('DOMContentLoaded', init);

    function init() {
        // Initialize entity views on page load
        initEntityViews();

        // Handle select change for options with descriptions
        document.addEventListener('change', function(e) {
            const select = e.target.closest('select.setting-input[data-has-descriptions]');
            if (select) {
                updateOptionDescription(select);
            }
        });

        // Event delegation for buttons
        document.addEventListener('click', function(e) {
            const editBtn = e.target.closest('.btn-edit');
            const saveBtn = e.target.closest('.btn-save');
            const cancelBtn = e.target.closest('.btn-cancel');

            // Entity select dropdown handling
            const entityTrigger = e.target.closest('.entity-select-trigger');
            const entityOption = e.target.closest('.entity-option');

            const previewBtn = e.target.closest('.btn-preview');

            if (editBtn) enterEditMode(editBtn.closest('tr'));
            if (saveBtn) saveSetting(saveBtn.closest('tr'));
            if (cancelBtn) exitEditMode(cancelBtn.closest('tr'));
            if (previewBtn) openPreview(previewBtn);

            if (entityTrigger) toggleEntityDropdown(entityTrigger.closest('.entity-select'));
            if (entityOption) selectEntityOption(entityOption);

            // Close dropdowns when clicking outside
            if (!e.target.closest('.entity-select')) {
                closeAllEntityDropdowns();
            }
        });
    }

    /**
     * Initialize entity view displays on page load
     */
    function initEntityViews() {
        document.querySelectorAll('.entity-view').forEach(function(view) {
            const type = view.dataset.type;
            const value = view.dataset.value;
            updateEntityView(view, type, value);
        });
    }

    /**
     * Update entity view display with thumbnail + name
     */
    function updateEntityView(view, type, value) {
        if (!value) {
            view.innerHTML = '<span class="text-muted">None</span>';
            return;
        }

        // Parse value format: "type:id" or just "id" for backwards compatibility
        let entityId;
        if (value.includes(':')) {
            entityId = parseInt(value.split(':')[1]);
        } else {
            entityId = parseInt(value);
        }

        if (isNaN(entityId)) {
            view.innerHTML = '<span class="text-muted">None</span>';
            return;
        }

        // Fetch entity data
        loadEntityOptions(type).then(function(options) {
            const entity = options.find(function(opt) { return opt.id === entityId; });
            if (entity) {
                view.innerHTML = renderEntityPreview(entity, type);
                loadSvgThumbnails(view);
            } else {
                view.innerHTML = '<span class="text-muted">Unknown (#' + entityId + ')</span>';
            }
        });
    }

    /**
     * Render entity preview HTML (thumbnail + name)
     */
    function renderEntityPreview(entity, type) {
        if (type === 'splashscreen') {
            return '<span class="entity-preview">' +
                '<span class="entity-thumb entity-thumb-svg" data-svg-url="' + entity.previewUrl + '"></span>' +
                '<span class="entity-name">' + escapeHtml(entity.name) + '</span>' +
                '</span>';
        } else if (type === 'sound') {
            return '<span class="entity-preview">' +
                '<img src="' + entity.previewUrl + '" class="entity-thumb entity-thumb-sound" alt="">' +
                '<span class="entity-name">' + escapeHtml(entity.name) + '</span>' +
                '<span class="badge bg-secondary ms-1">' + entity.type + '</span>' +
                '</span>';
        } else if (type === 'videopart') {
            return '<span class="entity-preview">' +
                '<img src="' + entity.previewUrl + '" class="entity-thumb entity-thumb-video" alt="">' +
                '<span class="entity-name">' + escapeHtml(entity.name) + '</span>' +
                '<span class="badge bg-' + (entity.type === 'intro' ? 'info' : 'success') + ' ms-1">' + entity.type + '</span>' +
                '</span>';
        }
        return '<span class="text-muted">None</span>';
    }

    /**
     * Load SVG thumbnails for splashscreens (inline SVG for better rendering)
     */
    function loadSvgThumbnails(container) {
        container.querySelectorAll('.entity-thumb-svg[data-svg-url]').forEach(function(thumb) {
            const url = thumb.dataset.svgUrl;
            if (!url || thumb.dataset.loaded) return;
            thumb.dataset.loaded = 'true';

            fetch(url)
                .then(function(response) { return response.text(); })
                .then(function(svg) {
                    thumb.innerHTML = svg;
                    const svgEl = thumb.querySelector('svg');
                    if (svgEl) {
                        svgEl.setAttribute('width', '100%');
                        svgEl.setAttribute('height', '100%');
                        svgEl.style.display = 'block';
                    }
                })
                .catch(function() {
                    thumb.innerHTML = '<i class="bi bi-image text-muted"></i>';
                });
        });
    }

    /**
     * Load entity options from API (with caching)
     */
    function loadEntityOptions(type) {
        if (entityCache[type]) {
            return Promise.resolve(entityCache[type]);
        }

        return fetch('/api/settings/entity-options/' + type)
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success) {
                    entityCache[type] = data.data;
                    return data.data;
                }
                return [];
            })
            .catch(function() { return []; });
    }

    /**
     * Initialize entity select dropdown for edit mode
     */
    function initEntitySelect(wrapper) {
        const type = wrapper.dataset.type;
        const currentValue = wrapper.dataset.value || '';

        loadEntityOptions(type).then(function(options) {
            // Build dropdown HTML
            let html = '<div class="entity-select" data-type="' + type + '">' +
                '<div class="entity-select-trigger form-control form-control-sm">';

            // Current selection display
            let currentEntity = null;
            if (currentValue) {
                let entityId;
                if (currentValue.includes(':')) {
                    entityId = parseInt(currentValue.split(':')[1]);
                } else {
                    entityId = parseInt(currentValue);
                }
                currentEntity = options.find(function(opt) { return opt.id === entityId; });
            }

            if (currentEntity) {
                html += renderEntityPreview(currentEntity, type);
            } else {
                html += '<span class="text-muted">None</span>';
            }

            html += '<i class="bi bi-chevron-down entity-select-arrow"></i></div>';

            // Dropdown options
            html += '<div class="entity-select-dropdown">';
            html += '<div class="entity-option" data-value="">' +
                '<span class="text-muted">None</span></div>';

            options.forEach(function(entity) {
                const optValue = type + ':' + entity.id;
                html += '<div class="entity-option" data-value="' + optValue + '">' +
                    renderEntityPreview(entity, type) + '</div>';
            });

            html += '</div></div>';

            wrapper.innerHTML = html;
            loadSvgThumbnails(wrapper);
        });
    }

    /**
     * Toggle entity dropdown visibility
     */
    function toggleEntityDropdown(select) {
        const dropdown = select.querySelector('.entity-select-dropdown');
        const trigger = select.querySelector('.entity-select-trigger');
        const isOpen = dropdown.classList.contains('show');

        closeAllEntityDropdowns();

        if (!isOpen) {
            // Position dropdown below trigger using fixed positioning
            const rect = trigger.getBoundingClientRect();
            dropdown.style.top = rect.bottom + 'px';
            dropdown.style.left = rect.left + 'px';
            dropdown.style.width = Math.max(rect.width, 250) + 'px';

            dropdown.classList.add('show');
            select.classList.add('open');
        }
    }

    /**
     * Close all open entity dropdowns
     */
    function closeAllEntityDropdowns() {
        document.querySelectorAll('.entity-select-dropdown.show').forEach(function(dd) {
            dd.classList.remove('show');
            dd.closest('.entity-select').classList.remove('open');
        });
    }

    /**
     * Handle entity option selection
     */
    function selectEntityOption(option) {
        const select = option.closest('.entity-select');
        const wrapper = select.closest('.entity-select-wrapper');
        const trigger = select.querySelector('.entity-select-trigger');
        const value = option.dataset.value;
        const type = select.dataset.type;

        // Update wrapper data
        wrapper.dataset.value = value;

        // Update trigger display
        const arrowHtml = '<i class="bi bi-chevron-down entity-select-arrow"></i>';
        if (value) {
            trigger.innerHTML = option.innerHTML + arrowHtml;
        } else {
            trigger.innerHTML = '<span class="text-muted">None</span>' + arrowHtml;
        }

        closeAllEntityDropdowns();
    }

    function enterEditMode(row) {
        row.querySelector('.setting-view').style.display = 'none';
        row.querySelector('.setting-edit').style.display = '';
        row.querySelector('.setting-view-buttons').style.display = 'none';
        row.querySelector('.setting-edit-buttons').style.display = '';

        // Check for entity select wrapper
        const entityWrapper = row.querySelector('.entity-select-wrapper');
        if (entityWrapper) {
            initEntitySelect(entityWrapper);
            return;
        }

        const input = row.querySelector('.setting-input');
        if (input) {
            input.focus();
            if (input.select) input.select();
        }
    }

    function exitEditMode(row) {
        row.querySelector('.setting-view').style.display = '';
        row.querySelector('.setting-edit').style.display = 'none';
        row.querySelector('.setting-view-buttons').style.display = '';
        row.querySelector('.setting-edit-buttons').style.display = 'none';

        // Reset entity selector to original
        const entityWrapper = row.querySelector('.entity-select-wrapper');
        if (entityWrapper) {
            entityWrapper.dataset.value = entityWrapper.dataset.original;
            // Reset the loading state for next edit
            entityWrapper.innerHTML = '<div class="entity-select-loading text-muted">Loading...</div>';
            return;
        }

        // Reset to original value for regular inputs
        const input = row.querySelector('.setting-input');
        if (input && input.dataset.original !== undefined) {
            input.value = input.dataset.original;
        }
    }

    function saveSetting(row) {
        const key = row.dataset.settingKey;
        let newValue, type;

        // Check for entity select
        const entityWrapper = row.querySelector('.entity-select-wrapper');
        if (entityWrapper) {
            newValue = entityWrapper.dataset.value || '';
            type = entityWrapper.dataset.type;
        } else {
            const input = row.querySelector('.setting-input');
            newValue = input.value;
            type = input.dataset.type;
        }

        fetch('/api/settings/' + encodeURIComponent(key), {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ value: newValue })
        })
        .then(function(response) { return response.json(); })
        .then(function(data) {
            if (data.success) {
                updateViewDisplay(row, newValue, type);

                // Update original value
                if (entityWrapper) {
                    entityWrapper.dataset.original = newValue;
                } else {
                    row.querySelector('.setting-input').dataset.original = newValue;
                }

                exitEditMode(row);
                showToast('Setting updated successfully', 'success');
            } else {
                showToast(data.error || 'Failed to save', 'danger');
            }
        })
        .catch(function(error) {
            console.error('[Settings] Error:', error);
            showToast('Network error', 'danger');
        });
    }

    function updateViewDisplay(row, value, type) {
        // Handle entity types
        if (type === 'splashscreen' || type === 'sound' || type === 'videopart') {
            const entityView = row.querySelector('.entity-view');
            if (entityView) {
                entityView.dataset.value = value;
                updateEntityView(entityView, type, value);
            }

            // Update preview button for sound/videopart
            if (type === 'sound' || type === 'videopart') {
                updatePreviewButton(row, type, value);
            }
            return;
        }

        // Handle regular types
        const code = row.querySelector('.setting-view code');
        if (code) {
            code.textContent = value;
        }

        // Update description for options with descriptions
        updateDescriptionAfterSave(row, value);
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Update description based on selected option
     */
    function updateOptionDescription(select) {
        const row = select.closest('tr');
        const descCell = row.querySelector('.setting-description');
        if (!descCell) return;

        const selectedOption = select.options[select.selectedIndex];
        const optionDesc = selectedOption ? selectedOption.dataset.description : null;
        const defaultDesc = descCell.dataset.defaultDescription || '—';

        descCell.textContent = optionDesc || defaultDesc;
    }

    /**
     * Update description after saving (for options with descriptions)
     */
    function updateDescriptionAfterSave(row, value) {
        const descCell = row.querySelector('.setting-description');
        if (!descCell || !descCell.dataset.optionsJson) return;

        try {
            const options = JSON.parse(descCell.dataset.optionsJson);
            const defaultDesc = descCell.dataset.defaultDescription || '—';
            descCell.textContent = (value && options[value]) ? options[value] : defaultDesc;
        } catch (e) {
            // Ignore parse errors
        }
    }

    /**
     * Update preview button visibility and data
     */
    function updatePreviewButton(row, type, value) {
        const btnGroup = row.querySelector('.setting-view-buttons');
        let previewBtn = btnGroup.querySelector('.btn-preview');

        if (value) {
            // Add or update preview button
            if (!previewBtn) {
                previewBtn = document.createElement('button');
                previewBtn.type = 'button';
                previewBtn.className = 'btn btn-sm btn-outline-info btn-preview';
                previewBtn.title = 'Preview';
                previewBtn.innerHTML = '<i class="bi bi-play-fill"></i>';
                btnGroup.insertBefore(previewBtn, btnGroup.firstChild);
            }
            previewBtn.dataset.type = type;
            previewBtn.dataset.value = value;
        } else {
            // Remove preview button if no value
            if (previewBtn) {
                previewBtn.remove();
            }
        }
    }

    /**
     * Open preview modal for sound or videopart
     */
    function openPreview(btn) {
        const type = btn.dataset.type;
        const value = btn.dataset.value;

        if (!value) return;

        // Parse entity ID from value (format: "type:id" or just "id")
        let entityId;
        if (value.includes(':')) {
            entityId = parseInt(value.split(':')[1]);
        } else {
            entityId = parseInt(value);
        }

        if (isNaN(entityId)) return;

        const modalEl = document.getElementById('settingsPreviewModal');
        const audioEl = document.getElementById('settingsPreviewAudio');
        const videoEl = document.getElementById('settingsPreviewVideo');
        const titleEl = document.getElementById('settingsPreviewModalLabel');

        // Reset and hide both players
        audioEl.pause();
        audioEl.src = '';
        audioEl.classList.add('d-none');
        videoEl.pause();
        videoEl.src = '';
        videoEl.classList.add('d-none');

        // Get entity name from cache or row
        loadEntityOptions(type).then(function(options) {
            const entity = options.find(function(opt) { return opt.id === entityId; });
            const name = entity ? entity.name : 'Preview';

            titleEl.textContent = name;

            if (type === 'sound') {
                audioEl.src = '/api/sounds/' + entityId + '/audio';
                audioEl.classList.remove('d-none');
                audioEl.load();
            } else if (type === 'videopart') {
                videoEl.src = '/api/videoparts/' + entityId + '/video';
                videoEl.classList.remove('d-none');
                videoEl.load();
            }

            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        });
    }

    // Stop playback when modal is closed
    document.addEventListener('DOMContentLoaded', function() {
        const modalEl = document.getElementById('settingsPreviewModal');
        if (modalEl) {
            modalEl.addEventListener('hidden.bs.modal', function() {
                const audioEl = document.getElementById('settingsPreviewAudio');
                const videoEl = document.getElementById('settingsPreviewVideo');
                if (audioEl) { audioEl.pause(); audioEl.src = ''; }
                if (videoEl) { videoEl.pause(); videoEl.src = ''; }
            });
        }
    });

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
        toastEl.addEventListener('hidden.bs.toast', function() { toastEl.remove(); });
    }
})();
