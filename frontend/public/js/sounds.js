document.addEventListener('DOMContentLoaded', function() {
    const audioFileInput = document.getElementById('audio-upload');

    // =====================
    // WebSocket handler for sound processing
    // =====================

    if (window.App && window.App.ws) {
        window.App.ws.on('sound:processed', function(data) {
            if (data.success) {
                console.log('Sound processed:', data);
                // Reload tab to show waveform and duration
                reloadTab('tab-sounds');
            } else {
                console.error('Sound processing failed:', data.error);
                showToast('Sound processing failed: ' + (data.error || 'Unknown error'), 'error');
            }
        });
    }

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
    // Sound functions
    // =====================

    let sndSelectedFile = null;
    let sndEditingId = null;
    let sndEditingRow = null;

    function handleAudioSelect() {
        const file = audioFileInput.files[0];
        if (!file) return;

        sndSelectedFile = file;

        // Reset form
        document.getElementById('sndUploadName').value = '';
        document.getElementById('sndUploadType').value = '';
        document.getElementById('sndUploadDescription').value = '';
        document.getElementById('sndUploadFilename').textContent = file.name;

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('sndUploadModal'));
        modal.show();
    }

    function handleSndUploadSubmit() {
        if (!sndSelectedFile) {
            showToast('No file selected', 'error');
            return;
        }

        const type = document.getElementById('sndUploadType').value;
        if (!type) {
            showToast('Please select a type', 'error');
            return;
        }

        const name = document.getElementById('sndUploadName').value.trim();
        const description = document.getElementById('sndUploadDescription').value.trim();

        const formData = new FormData();
        formData.append('audio', sndSelectedFile);
        formData.append('type', type);
        if (name) formData.append('name', name);
        if (description) formData.append('description', description);

        // Disable button during upload
        const submitBtn = document.getElementById('sndUploadSubmitBtn');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Uploading...';

        fetch('/api/sounds/upload', {
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
                    // Send WebSocket signal to backend for processing
                    if (window.App && window.App.ws) {
                        window.App.ws.send('sound:uploaded', {
                            id: data.data.id,
                            name: data.data.name,
                            type: data.data.type,
                            file_path: data.data.file_path
                        }, 'backend');
                    }
                    showToast('Sound uploaded successfully', 'success');
                    // Close modal
                    bootstrap.Modal.getInstance(document.getElementById('sndUploadModal')).hide();
                    // Reload tab
                    reloadTab('tab-sounds');
                } else {
                    showToast(data.error || 'Failed to upload sound', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast(error.message || 'Error uploading sound', 'error');
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Upload';
                audioFileInput.value = '';
                sndSelectedFile = null;
            });
    }

    function openSndEditModal(id, row) {
        fetch(`/api/sounds/${id}`)
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    showToast('Failed to load sound', 'error');
                    return;
                }

                const sound = data.data;
                sndEditingId = id;
                sndEditingRow = row;

                document.getElementById('sndEditModalLabel').textContent = `Edit ${sound.type}: ${sound.name}`;
                document.getElementById('sndEditName').value = sound.name;
                document.getElementById('sndEditDescription').value = sound.description || '';

                const modal = new bootstrap.Modal(document.getElementById('sndEditModal'));
                modal.show();
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Error loading sound', 'error');
            });
    }

    function handleSndEditSave() {
        if (!sndEditingId) return;

        const name = document.getElementById('sndEditName').value.trim();
        const description = document.getElementById('sndEditDescription').value.trim();

        if (!name) {
            showToast('Name cannot be empty', 'error');
            return;
        }

        fetch(`/api/sounds/${sndEditingId}`, {
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
                    if (sndEditingRow) {
                        sndEditingRow.querySelector('.snd-name').textContent = name;
                        const descCell = sndEditingRow.querySelector('.snd-description');
                        if (descCell) {
                            descCell.textContent = description || '-';
                        }
                    }
                    bootstrap.Modal.getInstance(document.getElementById('sndEditModal')).hide();
                    showToast('Sound updated', 'success');
                } else {
                    showToast(data.error || 'Failed to update', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Error updating sound', 'error');
            })
            .finally(() => {
                sndEditingId = null;
                sndEditingRow = null;
            });
    }

    function handleSndDelete(row) {
        const id = row.getAttribute('data-id');
        const name = row.querySelector('.snd-name').textContent;
        const type = row.getAttribute('data-type');

        showConfirmDialog(
            `Delete ${type} sound`,
            `Are you sure you want to delete "${escapeHtml(name)}"?`,
            function() {
                fetch(`/api/sounds/${id}`, {
                    method: 'DELETE',
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showToast('Sound deleted', 'success');
                            row.remove();
                            // Check if table is empty
                            const tbody = document.getElementById('snd-body');
                            if (tbody && tbody.querySelectorAll('tr:not(.snd-empty-row)').length === 0) {
                                const emptyRow = document.createElement('tr');
                                emptyRow.className = 'snd-empty-row';
                                emptyRow.innerHTML = '<td colspan="7" class="text-center text-muted">No sounds yet. Upload an MP3 or WAV file to get started.</td>';
                                tbody.appendChild(emptyRow);
                            }
                        } else {
                            showToast(data.error || 'Failed to delete', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showToast('Error deleting sound', 'error');
                    });
            }
        );
    }

    function openSndPreviewModal(id, name, hasWaveform) {
        const modalEl = document.getElementById('sndPreviewModal');
        const player = document.getElementById('sndPreviewPlayer');
        const waveformContainer = document.getElementById('sndPreviewWaveform');
        const waveformImg = document.getElementById('sndPreviewWaveformImg');
        const progressOverlay = document.getElementById('sndPreviewProgress');
        const cursorLine = document.getElementById('sndPreviewCursor');

        // Set title
        document.getElementById('sndPreviewModalLabel').textContent = name;

        // Set audio source
        player.src = `/api/sounds/${id}/audio`;
        player.load();

        // Reset progress
        progressOverlay.style.width = '0%';
        cursorLine.style.left = '0';

        // Show waveform if available
        if (hasWaveform) {
            waveformImg.src = `/api/sounds/${id}/waveform`;
            waveformContainer.style.display = 'block';
        } else {
            waveformImg.src = '';
            waveformContainer.style.display = 'none';
        }

        // Show modal
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    }

    // Update waveform progress as audio plays
    function updateWaveformProgress() {
        const player = document.getElementById('sndPreviewPlayer');
        const progressOverlay = document.getElementById('sndPreviewProgress');
        const cursorLine = document.getElementById('sndPreviewCursor');

        if (player && player.duration && !isNaN(player.duration)) {
            const percent = (player.currentTime / player.duration) * 100;
            progressOverlay.style.width = percent + '%';
            cursorLine.style.left = percent + '%';
        }
    }

    // Handle click on waveform to seek
    function handleWaveformClick(e) {
        const player = document.getElementById('sndPreviewPlayer');
        const waveformContainer = document.getElementById('sndPreviewWaveform');

        if (player && player.duration && !isNaN(player.duration)) {
            const rect = waveformContainer.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const percent = clickX / rect.width;
            player.currentTime = percent * player.duration;
        }
    }

    // =====================
    // Event handlers
    // =====================

    // Handle audio file selection
    if (audioFileInput) {
        audioFileInput.addEventListener('change', handleAudioSelect);
    }

    // Event delegation for dynamically loaded buttons
    document.addEventListener('click', function(e) {
        // Upload sound button
        if (e.target.closest('#snd-upload-btn')) {
            audioFileInput.click();
            return;
        }

        // Edit button (sounds)
        if (e.target.closest('.snd-edit-btn')) {
            const btn = e.target.closest('.snd-edit-btn');
            const row = btn.closest('tr');
            const id = row.getAttribute('data-id');
            openSndEditModal(id, row);
            return;
        }

        // Delete button (sounds)
        if (e.target.closest('.snd-delete-btn')) {
            const btn = e.target.closest('.snd-delete-btn');
            const row = btn.closest('tr');
            handleSndDelete(row);
            return;
        }

        // Preview button (sounds) - waveform or name click
        if (e.target.closest('.snd-preview-btn')) {
            const el = e.target.closest('.snd-preview-btn');
            const row = el.closest('tr');
            const id = el.getAttribute('data-id') || row.getAttribute('data-id');
            const name = row.querySelector('.snd-name').textContent;
            // Check if waveform is available from the waveform cell
            const waveformCell = row.querySelector('.snd-waveform');
            const hasWaveform = waveformCell && waveformCell.getAttribute('data-has-waveform') === '1';
            openSndPreviewModal(id, name, hasWaveform);
            return;
        }

        // Upload modal submit
        if (e.target.closest('#sndUploadSubmitBtn')) {
            handleSndUploadSubmit();
            return;
        }

        // Edit modal save
        if (e.target.closest('#sndEditSaveBtn')) {
            handleSndEditSave();
            return;
        }
    });

    // Audio player timeupdate event for waveform progress
    const sndPlayer = document.getElementById('sndPreviewPlayer');
    if (sndPlayer) {
        sndPlayer.addEventListener('timeupdate', updateWaveformProgress);
    }

    // Waveform click to seek
    const sndWaveformContainer = document.getElementById('sndPreviewWaveform');
    if (sndWaveformContainer) {
        sndWaveformContainer.style.cursor = 'pointer';
        sndWaveformContainer.addEventListener('click', handleWaveformClick);
    }

    // Stop audio and reset waveform when preview modal closes
    const sndPreviewModal = document.getElementById('sndPreviewModal');
    if (sndPreviewModal) {
        sndPreviewModal.addEventListener('hidden.bs.modal', function() {
            const player = document.getElementById('sndPreviewPlayer');
            if (player) {
                player.pause();
                player.currentTime = 0;
                player.src = '';
            }
            // Reset waveform and progress
            const waveformContainer = document.getElementById('sndPreviewWaveform');
            const waveformImg = document.getElementById('sndPreviewWaveformImg');
            const progressOverlay = document.getElementById('sndPreviewProgress');
            const cursorLine = document.getElementById('sndPreviewCursor');
            if (waveformContainer) {
                waveformContainer.style.display = 'none';
            }
            if (waveformImg) {
                waveformImg.src = '';
            }
            if (progressOverlay) {
                progressOverlay.style.width = '0%';
            }
            if (cursorLine) {
                cursorLine.style.left = '0';
            }
        });
    }
});
