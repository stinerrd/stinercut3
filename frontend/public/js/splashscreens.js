document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('svg-upload');
    const ttfFileInput = document.getElementById('ttf-upload');
    const videoFileInput = document.getElementById('video-upload');

    // Use event delegation for dynamically loaded buttons
    document.addEventListener('click', function(e) {
        // Import SVG button
        if (e.target.closest('#ss-import-btn')) {
            fileInput.click();
            return;
        }

        // Import TTF button
        if (e.target.closest('#ss-import-ttf-btn')) {
            ttfFileInput.click();
            return;
        }

        // Edit button (splashscreens)
        if (e.target.closest('.ss-edit-btn')) {
            const btn = e.target.closest('.ss-edit-btn');
            const row = btn.closest('tr');
            const id = row.getAttribute('data-id');
            openEditModal(id, row);
            return;
        }

        // Delete button (splashscreens)
        if (e.target.closest('.ss-delete-btn')) {
            const btn = e.target.closest('.ss-delete-btn');
            const row = btn.closest('tr');
            handleDelete(row);
            return;
        }

        // Preview click to open edit modal (splashscreens)
        if (e.target.closest('.ss-preview')) {
            const preview = e.target.closest('.ss-preview');
            const row = preview.closest('tr');
            const id = row.getAttribute('data-id');
            openEditModal(id, row);
            return;
        }

        // =====================
        // Videoparts handlers
        // =====================

        // Upload video button
        if (e.target.closest('#vp-upload-btn')) {
            videoFileInput.click();
            return;
        }

        // Edit button (videoparts)
        if (e.target.closest('.vp-edit-btn')) {
            const btn = e.target.closest('.vp-edit-btn');
            const row = btn.closest('tr');
            const id = row.getAttribute('data-id');
            openVpEditModal(id, row);
            return;
        }

        // Delete button (videoparts)
        if (e.target.closest('.vp-delete-btn')) {
            const btn = e.target.closest('.vp-delete-btn');
            const row = btn.closest('tr');
            handleVpDelete(row);
            return;
        }

        // Preview button (videoparts) - thumbnail or name click
        if (e.target.closest('.vp-preview-btn')) {
            const el = e.target.closest('.vp-preview-btn');
            const row = el.closest('tr');
            const id = el.getAttribute('data-id') || row.getAttribute('data-id');
            const name = row.querySelector('.vp-name').textContent;
            openVpPreviewModal(id, name);
            return;
        }

        // Upload modal submit
        if (e.target.closest('#vpUploadSubmitBtn')) {
            handleVpUploadSubmit();
            return;
        }

        // Edit modal save
        if (e.target.closest('#vpEditSaveBtn')) {
            handleVpEditSave();
            return;
        }
    });

    // Handle SVG file selection
    fileInput.addEventListener('change', handleImport);

    // Handle TTF file selection
    ttfFileInput.addEventListener('change', handleTtfImport);

    // Handle video file selection - opens upload modal
    videoFileInput.addEventListener('change', handleVideoSelect);

    // Initialize first tab content (eager loaded)
    const imagesTab = document.getElementById('content-images');
    if (imagesTab) {
        loadAllPreviews(imagesTab);
    }

    // Listen for lazy tab loaded events to initialize content
    document.addEventListener('lazyTabLoaded', function(e) {
        const { contentContainer } = e.detail;
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
                                showToast('Media updated', 'success');
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

    function handleDelete(row) {
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
                            showToast('Media deleted', 'success');
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

    // =====================
    // Videoparts functions
    // =====================

    let vpSelectedFile = null;
    let vpEditingId = null;
    let vpEditingRow = null;

    function handleVideoSelect() {
        const file = videoFileInput.files[0];
        if (!file) return;

        vpSelectedFile = file;

        // Reset form
        document.getElementById('vpUploadName').value = '';
        document.getElementById('vpUploadType').value = '';
        document.getElementById('vpUploadDescription').value = '';
        document.getElementById('vpUploadFilename').textContent = file.name;

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('vpUploadModal'));
        modal.show();
    }

    function handleVpUploadSubmit() {
        if (!vpSelectedFile) {
            showToast('No file selected', 'error');
            return;
        }

        const type = document.getElementById('vpUploadType').value;
        if (!type) {
            showToast('Please select a type (Intro or Outro)', 'error');
            return;
        }

        const name = document.getElementById('vpUploadName').value.trim();
        const description = document.getElementById('vpUploadDescription').value.trim();

        const formData = new FormData();
        formData.append('video', vpSelectedFile);
        formData.append('type', type);
        if (name) formData.append('name', name);
        if (description) formData.append('description', description);

        // Disable button during upload
        const submitBtn = document.getElementById('vpUploadSubmitBtn');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Uploading...';

        fetch('/api/videoparts/upload', {
            method: 'POST',
            body: formData,
        })
            .then(response => {
                if (!response.ok) {
                    if (response.status === 413) {
                        throw new Error('File too large');
                    }
                    return response.json().then(data => {
                        throw new Error(data.error || 'Server error');
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    showToast('Video uploaded successfully', 'success');
                    // Close modal
                    bootstrap.Modal.getInstance(document.getElementById('vpUploadModal')).hide();
                    // Reload tab
                    reloadTab('tab-videoparts');
                } else {
                    showToast(data.error || 'Failed to upload video', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast(error.message || 'Error uploading video', 'error');
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Upload';
                videoFileInput.value = '';
                vpSelectedFile = null;
            });
    }

    function openVpEditModal(id, row) {
        fetch(`/api/videoparts/${id}`)
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    showToast('Failed to load videopart', 'error');
                    return;
                }

                const videopart = data.data;
                vpEditingId = id;
                vpEditingRow = row;

                document.getElementById('vpEditModalLabel').textContent = `Edit ${videopart.type}: ${videopart.name}`;
                document.getElementById('vpEditName').value = videopart.name;
                document.getElementById('vpEditDescription').value = videopart.description || '';

                const modal = new bootstrap.Modal(document.getElementById('vpEditModal'));
                modal.show();
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Error loading videopart', 'error');
            });
    }

    function handleVpEditSave() {
        if (!vpEditingId) return;

        const name = document.getElementById('vpEditName').value.trim();
        const description = document.getElementById('vpEditDescription').value.trim();

        if (!name) {
            showToast('Name cannot be empty', 'error');
            return;
        }

        fetch(`/api/videoparts/${vpEditingId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                description: description,
            }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update row
                    if (vpEditingRow) {
                        vpEditingRow.querySelector('.vp-name').textContent = name;
                        const descCell = vpEditingRow.querySelector('.vp-description');
                        if (descCell) {
                            descCell.textContent = description || '-';
                        }
                    }
                    bootstrap.Modal.getInstance(document.getElementById('vpEditModal')).hide();
                    showToast('Videopart updated', 'success');
                } else {
                    showToast(data.error || 'Failed to update', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Error updating videopart', 'error');
            })
            .finally(() => {
                vpEditingId = null;
                vpEditingRow = null;
            });
    }

    function handleVpDelete(row) {
        const id = row.getAttribute('data-id');
        const name = row.querySelector('.vp-name').textContent;
        const type = row.getAttribute('data-type');

        showConfirmDialog(
            `Delete ${type}`,
            `Are you sure you want to delete "${escapeHtml(name)}"?`,
            function() {
                fetch(`/api/videoparts/${id}`, {
                    method: 'DELETE',
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showToast('Videopart deleted', 'success');
                            row.remove();
                            // Check if table is empty
                            const tbody = document.getElementById('vp-body');
                            if (tbody && tbody.querySelectorAll('tr:not(.vp-empty-row)').length === 0) {
                                const emptyRow = document.createElement('tr');
                                emptyRow.className = 'vp-empty-row';
                                emptyRow.innerHTML = '<td colspan="6" class="text-center text-muted">No videos yet. Upload a video to get started.</td>';
                                tbody.appendChild(emptyRow);
                            }
                        } else {
                            showToast(data.error || 'Failed to delete', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showToast('Error deleting videopart', 'error');
                    });
            }
        );
    }

    function openVpPreviewModal(id, name) {
        const modalEl = document.getElementById('vpPreviewModal');
        const player = document.getElementById('vpPreviewPlayer');
        const source = document.getElementById('vpPreviewSource');

        // Set title
        document.getElementById('vpPreviewModalLabel').textContent = name;

        // Set video source
        source.src = `/api/videoparts/${id}/video`;
        player.load();

        // Show modal
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    }

    // Stop video when preview modal closes
    const vpPreviewModal = document.getElementById('vpPreviewModal');
    if (vpPreviewModal) {
        vpPreviewModal.addEventListener('hidden.bs.modal', function() {
            const player = document.getElementById('vpPreviewPlayer');
            if (player) {
                player.pause();
                player.currentTime = 0;
            }
        });
    }
});
