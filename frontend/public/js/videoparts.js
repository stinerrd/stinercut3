document.addEventListener('DOMContentLoaded', function() {
    const videoFileInput = document.getElementById('video-upload');

    // =====================
    // Utility functions
    // =====================

    function reloadTab(tabId) {
        const tabEl = document.getElementById(tabId);
        if (tabEl && window.LazyTabs) {
            window.LazyTabs.reload(tabEl);
        }
    }

    function showConfirmDialog(title, message, onConfirm) {
        const modalEl = document.getElementById('confirmModal');
        document.getElementById('confirmModalLabel').textContent = title;
        document.getElementById('confirmModalBody').innerHTML = message;

        // Get existing modal instance or create new one
        const modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
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

        // Show modal - get existing instance or create new one
        const modalEl = document.getElementById('vpUploadModal');
        const modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
        modal.show();
    }

    let vpUploading = false;

    function handleVpUploadSubmit() {
        // Prevent double submission
        if (vpUploading) return;

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
        vpUploading = true;
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
                    // Send WebSocket notification to backend (fire-and-forget)
                    if (window.App && window.App.ws) {
                        window.App.ws.send('videopart:uploaded', {
                            id: data.data.id,
                            name: data.data.name,
                            type: data.data.type,
                            file_path: data.data.file_path
                        }, 'backend');
                    }

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
                vpUploading = false;
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

                const modalEl = document.getElementById('vpEditModal');
                const modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
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
                                emptyRow.innerHTML = '<td colspan="7" class="text-center text-muted">No videos yet. Upload a video to get started.</td>';
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

        // Set title
        document.getElementById('vpPreviewModalLabel').textContent = name;

        // Set video source
        player.src = `/api/videoparts/${id}/video`;
        player.load();

        // Show modal - get existing instance or create new one
        const modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
        modal.show();
    }

    // =====================
    // Event handlers
    // =====================

    // Handle video file selection
    if (videoFileInput) {
        videoFileInput.addEventListener('change', handleVideoSelect);
    }

    // Event delegation for dynamically loaded buttons
    document.addEventListener('click', function(e) {
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
            e.preventDefault();
            e.stopPropagation();
            handleVpUploadSubmit();
            return;
        }

        // Edit modal save
        if (e.target.closest('#vpEditSaveBtn')) {
            handleVpEditSave();
            return;
        }
    });

    // Stop video when preview modal closes
    const vpPreviewModal = document.getElementById('vpPreviewModal');
    if (vpPreviewModal) {
        vpPreviewModal.addEventListener('hidden.bs.modal', function() {
            const player = document.getElementById('vpPreviewPlayer');
            if (player) {
                player.pause();
                player.currentTime = 0;
                player.src = '';
            }
        });
    }
});
