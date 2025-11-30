document.addEventListener('DOMContentLoaded', function() {
    const importBtn = document.getElementById('ss-import-btn');
    const importTtfBtn = document.getElementById('ss-import-ttf-btn');
    const fileInput = document.getElementById('svg-upload');
    const ttfFileInput = document.getElementById('ttf-upload');

    // Import SVG button
    importBtn.addEventListener('click', function() {
        fileInput.click();
    });

    // Import TTF button
    importTtfBtn.addEventListener('click', function() {
        ttfFileInput.click();
    });

    // Handle SVG file selection
    fileInput.addEventListener('change', handleImport);

    // Handle TTF file selection
    ttfFileInput.addEventListener('change', handleTtfImport);

    // Initialize first tab content (eager loaded)
    const imagesTab = document.getElementById('content-images');
    if (imagesTab) {
        attachRowListeners(imagesTab);
        loadAllPreviews(imagesTab);
    }

    // Listen for lazy tab loaded events to initialize content
    document.addEventListener('lazyTabLoaded', function(e) {
        const { contentContainer } = e.detail;
        attachRowListeners(contentContainer);
        loadAllPreviews(contentContainer);
    });

    function handleImport() {
        const file = fileInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('svg', file);

        fetch('/api/splashscreens/import', {
            method: 'POST',
            body: formData,
        })
            .then(response => {
                if (!response.ok) {
                    if (response.status === 413) {
                        throw new Error('File too large');
                    }
                    throw new Error('Server error: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    showToast('SVG imported successfully', 'success');
                    // Reload both tabs since import creates image + font
                    reloadTab('tab-images');
                    reloadTab('tab-fonts');
                } else {
                    showToast(data.error || 'Failed to import SVG', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast(error.message || 'Error importing SVG', 'error');
            })
            .finally(() => {
                fileInput.value = '';
            });
    }

    function handleTtfImport() {
        const file = ttfFileInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('ttf', file);

        fetch('/api/splashscreens/import/ttf', {
            method: 'POST',
            body: formData,
        })
            .then(response => {
                if (!response.ok) {
                    if (response.status === 413) {
                        throw new Error('File too large');
                    }
                    throw new Error('Server error: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    showToast('TTF font imported successfully', 'success');
                    // Reload fonts tab
                    reloadTab('tab-fonts');
                } else {
                    showToast(data.error || 'Failed to import TTF', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast(error.message || 'Error importing TTF', 'error');
            })
            .finally(() => {
                ttfFileInput.value = '';
            });
    }

    function reloadTab(tabId) {
        const tabEl = document.getElementById(tabId);
        if (tabEl && window.LazyTabs) {
            window.LazyTabs.reload(tabEl);
        }
    }

    function attachRowListeners(container) {
        const scope = container || document;

        // Edit button
        scope.querySelectorAll('.ss-edit-btn').forEach(btn => {
            btn.removeEventListener('click', handleEdit);
            btn.addEventListener('click', handleEdit);
        });

        // Delete button
        scope.querySelectorAll('.ss-delete-btn').forEach(btn => {
            btn.removeEventListener('click', handleDelete);
            btn.addEventListener('click', handleDelete);
        });

        // Preview click to open edit modal
        scope.querySelectorAll('.ss-preview').forEach(preview => {
            preview.removeEventListener('click', handlePreviewClick);
            preview.addEventListener('click', handlePreviewClick);
        });
    }

    function loadAllPreviews(container) {
        const scope = container || document;
        scope.querySelectorAll('.ss-preview').forEach(preview => {
            loadPreview(preview);
        });
    }

    function loadPreview(previewDiv) {
        const id = previewDiv.getAttribute('data-id');
        if (!id) return;

        fetch(`/api/splashscreens/${id}/svg`)
            .then(response => response.text())
            .then(svg => {
                previewDiv.innerHTML = svg;
                // Scale SVG to fit container
                const svgEl = previewDiv.querySelector('svg');
                if (svgEl) {
                    svgEl.setAttribute('width', '100%');
                    svgEl.setAttribute('height', '100%');
                    svgEl.style.objectFit = 'contain';
                }
            })
            .catch(error => {
                console.error('Error loading preview:', error);
                previewDiv.innerHTML = '<div class="text-muted text-center" style="padding-top: 18px;"><i class="bi bi-image"></i></div>';
            });
    }

    function handlePreviewClick(e) {
        const preview = e.currentTarget;
        const row = preview.closest('tr');
        const id = row.getAttribute('data-id');
        openEditModal(id, row);
    }

    function handleEdit(e) {
        const btn = e.target.closest('button');
        const row = btn.closest('tr');
        const id = row.getAttribute('data-id');
        openEditModal(id, row);
    }

    // Track current edit category for preview generation
    let currentEditCategory = 'image';

    function openEditModal(id, row) {
        // Fetch full data including svg_content
        fetch(`/api/splashscreens/${id}`)
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    showToast('Failed to load splashscreen', 'error');
                    return;
                }

                const splashscreen = data.data;
                const category = row.getAttribute('data-category');
                currentEditCategory = category;

                document.getElementById('editModalLabel').textContent = `Edit ${category === 'font' ? 'Font' : 'Image'}: ${splashscreen.name}`;
                document.getElementById('editNameInput').value = splashscreen.name;
                document.getElementById('editSvgContent').value = splashscreen.svg_content || '';

                // Update preview (use appropriate method based on category)
                updateEditPreview(splashscreen.svg_content, category);

                const modal = new bootstrap.Modal(document.getElementById('editModal'));
                const saveBtn = document.getElementById('editModalSaveBtn');
                const svgTextarea = document.getElementById('editSvgContent');

                // Live preview update on textarea change
                svgTextarea.removeEventListener('input', handleSvgInput);
                svgTextarea.addEventListener('input', handleSvgInput);

                // Remove previous listener and add new one
                const newSaveBtn = saveBtn.cloneNode(true);
                saveBtn.parentNode.replaceChild(newSaveBtn, saveBtn);

                newSaveBtn.addEventListener('click', function() {
                    const newName = document.getElementById('editNameInput').value.trim();
                    const newSvgContent = document.getElementById('editSvgContent').value;

                    if (!newName) {
                        showToast('Name cannot be empty', 'error');
                        return;
                    }

                    fetch(`/api/splashscreens/${id}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            name: newName,
                            svg_content: newSvgContent,
                        }),
                    })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                row.querySelector('.ss-name').textContent = newName;
                                loadPreview(row.querySelector('.ss-preview'));
                                modal.hide();
                                showToast('Splashscreen updated', 'success');
                            } else {
                                showToast(data.error || 'Failed to update', 'error');
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            showToast('Error updating splashscreen', 'error');
                        });
                });

                modal.show();
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Error loading splashscreen', 'error');
            });
    }

    function handleSvgInput(e) {
        updateEditPreview(e.target.value, currentEditCategory);
    }

    // Debounce timer for font preview requests
    let fontPreviewTimer = null;

    function updateEditPreview(svgContent, category) {
        const previewDiv = document.getElementById('editPreview');

        if (category === 'font') {
            // For fonts, use the API to generate preview with <use> elements
            // Debounce to avoid too many requests while typing
            clearTimeout(fontPreviewTimer);
            fontPreviewTimer = setTimeout(() => {
                fetch('/api/splashscreens/preview/font', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ svg_content: svgContent }),
                })
                    .then(response => response.text())
                    .then(svg => {
                        previewDiv.innerHTML = svg;
                        const svgEl = previewDiv.querySelector('svg');
                        if (svgEl) {
                            svgEl.style.maxWidth = '100%';
                            svgEl.style.maxHeight = '300px';
                        }
                    })
                    .catch(error => {
                        console.error('Error generating font preview:', error);
                        previewDiv.innerHTML = '<div class="text-danger">Error generating preview</div>';
                    });
            }, 300);
        } else {
            // For images, render directly (replace dimension placeholders)
            try {
                let processedSvg = svgContent
                    .replace(/\[\[\[WIDTH\]\]\]/g, '1920')
                    .replace(/\[\[\[HEIGHT\]\]\]/g, '1080');
                previewDiv.innerHTML = processedSvg;
                const svgEl = previewDiv.querySelector('svg');
                if (svgEl) {
                    svgEl.style.maxWidth = '100%';
                    svgEl.style.maxHeight = '300px';
                }
            } catch (e) {
                previewDiv.innerHTML = '<div class="text-danger">Invalid SVG</div>';
            }
        }
    }

    function handleDelete(e) {
        const btn = e.target.closest('button');
        const row = btn.closest('tr');
        const id = row.getAttribute('data-id');
        const name = row.querySelector('.ss-name').textContent;
        const category = row.getAttribute('data-category');

        showConfirmDialog(
            `Delete ${category === 'font' ? 'Font' : 'Image'}`,
            `Are you sure you want to delete "${escapeHtml(name)}"?`,
            function() {
                fetch(`/api/splashscreens/${id}`, {
                    method: 'DELETE',
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showToast('Splashscreen deleted', 'success');
                            row.remove();
                            // Check if table is empty and add empty row
                            const tbody = row.closest('tbody') || document.getElementById(category === 'font' ? 'ss-fonts-body' : 'ss-images-body');
                            if (tbody && tbody.querySelectorAll('tr:not(.ss-empty-row)').length === 0) {
                                addEmptyRow(tbody, category);
                            }
                        } else {
                            showToast(data.error || 'Failed to delete', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showToast('Error deleting splashscreen', 'error');
                    });
            }
        );
    }

    function addEmptyRow(tbody, category) {
        const row = document.createElement('tr');
        row.className = 'ss-empty-row';
        row.innerHTML = `<td colspan="3" class="text-center text-muted">No ${category === 'font' ? 'fonts' : 'images'} yet. Import an SVG to get started.</td>`;
        tbody.appendChild(row);
    }

    function showConfirmDialog(title, message, onConfirm) {
        const modalEl = document.getElementById('confirmModal');
        document.getElementById('confirmModalLabel').textContent = title;
        document.getElementById('confirmModalBody').innerHTML = message;

        const modal = new bootstrap.Modal(modalEl);
        const confirmBtn = document.getElementById('confirmModalBtn');

        // Remove previous listener and add new one
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

        newConfirmBtn.addEventListener('click', function() {
            modal.hide();
            onConfirm();
        });

        modal.show();
    }

    function showToast(message, type = 'info') {
        const alertClass = type === 'success' ? 'alert-success' : type === 'error' ? 'alert-danger' : 'alert-info';
        const toast = document.createElement('div');
        toast.className = `alert ${alertClass} alert-dismissible fade show`;
        toast.style.position = 'fixed';
        toast.style.top = '20px';
        toast.style.right = '20px';
        toast.style.zIndex = '9999';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
