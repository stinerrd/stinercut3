document.addEventListener('DOMContentLoaded', function() {
    const addBtn = document.getElementById('tm-add-btn');
    const nameInput = document.getElementById('tm-name');
    const tableBody = document.getElementById('tm-table-body');
    const fileInput = document.getElementById('avatar-upload');

    // Add new tandem master
    addBtn.addEventListener('click', addTandemMaster);
    nameInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            addTandemMaster();
        }
    });

    // Attach event listeners to existing rows
    attachRowListeners();

    function addTandemMaster() {
        const name = nameInput.value.trim();
        if (!name) {
            alert('Please enter a tandem master name');
            return;
        }

        fetch('/api/tandem-masters', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                active: true,
            }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Tandem master added successfully', 'success');
                    addRowToTable(data.data);
                    nameInput.value = '';
                } else {
                    showToast(data.error || 'Failed to add tandem master', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Error adding tandem master', 'error');
            });
    }

    function addRowToTable(tandemMaster) {
        const row = document.createElement('tr');
        row.setAttribute('data-id', tandemMaster.id);
        row.setAttribute('data-has-image', tandemMaster.has_image ? '1' : '0');

        const avatarHtml = tandemMaster.has_image
            ? `<img class="tm-avatar" src="/api/tandem-masters/${tandemMaster.id}/image" alt="${escapeHtml(tandemMaster.name)}"
                   style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px; cursor: pointer;" />`
            : `<div class="tm-avatar tm-placeholder" style="width: 60px; height: 60px; background: #dee2e6; border-radius: 4px; cursor: pointer; display: flex; align-items: center; justify-content: center;">
                   <i class="bi bi-person" style="font-size: 28px; color: #6c757d;"></i>
               </div>`;

        row.innerHTML = `
            <td>${avatarHtml}</td>
            <td class="tm-name">${escapeHtml(tandemMaster.name)}</td>
            <td>
                <input type="checkbox" class="tm-active form-check-input" ${tandemMaster.active ? 'checked' : ''} />
            </td>
            <td>
                <button type="button" class="btn btn-sm btn-outline-primary tm-edit-btn me-1" title="Edit">
                    <i class="bi bi-pencil"></i>
                </button>
                <button type="button" class="btn btn-sm btn-danger tm-delete-btn" title="Delete">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;
        tableBody.appendChild(row);
        attachRowListeners();
    }

    function attachRowListeners() {
        // Avatar click to upload
        tableBody.querySelectorAll('.tm-avatar').forEach(img => {
            img.removeEventListener('click', handleAvatarClick);
            img.addEventListener('click', handleAvatarClick);
        });

        // Active checkbox toggle
        tableBody.querySelectorAll('.tm-active').forEach(checkbox => {
            checkbox.removeEventListener('change', handleActiveToggle);
            checkbox.addEventListener('change', handleActiveToggle);
        });

        // Delete button
        tableBody.querySelectorAll('.tm-delete-btn').forEach(btn => {
            btn.removeEventListener('click', handleDelete);
            btn.addEventListener('click', handleDelete);
        });

        // Edit button
        tableBody.querySelectorAll('.tm-edit-btn').forEach(btn => {
            btn.removeEventListener('click', handleEdit);
            btn.addEventListener('click', handleEdit);
        });
    }

    function handleAvatarClick(e) {
        const img = e.target;
        const row = img.closest('tr');
        const id = row.getAttribute('data-id');

        // Store ID and trigger file input
        fileInput.setAttribute('data-id', id);
        fileInput.click();
    }

    fileInput.addEventListener('change', function() {
        const file = this.files[0];
        if (!file) return;

        const id = this.getAttribute('data-id');
        const maxSize = parseInt(window.App.avatarMaxUploadSize) || 5242880;

        // Validate file size client-side
        if (file.size > maxSize) {
            showToast(`File size exceeds ${maxSize / 1024 / 1024}MB limit`, 'error');
            this.value = '';
            return;
        }

        // Upload file
        const formData = new FormData();
        formData.append('image', file);

        fetch(`/api/tandem-masters/${id}/image`, {
            method: 'POST',
            body: formData,
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Avatar uploaded successfully', 'success');
                    // Replace placeholder or refresh avatar image
                    const row = document.querySelector(`tr[data-id="${id}"]`);
                    const avatarCell = row.querySelector('td:first-child');
                    const name = row.querySelector('td:nth-child(2)').textContent;

                    avatarCell.innerHTML = `<img class="tm-avatar" src="/api/tandem-masters/${id}/image?t=${Date.now()}" alt="${escapeHtml(name)}"
                         style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px; cursor: pointer;" />`;
                    row.setAttribute('data-has-image', '1');
                    attachRowListeners();
                } else {
                    showToast(data.error || 'Failed to upload avatar', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Error uploading avatar', 'error');
            })
            .finally(() => {
                this.value = '';
            });
    });

    function handleEdit(e) {
        const btn = e.target.closest('button');
        const row = btn.closest('tr');
        const id = row.getAttribute('data-id');
        const nameCell = row.querySelector('.tm-name');
        const currentName = nameCell.textContent;

        // Show edit modal
        document.getElementById('editModalLabel').textContent = 'Edit Tandem Master';
        document.getElementById('editNameInput').value = currentName;

        const modal = new bootstrap.Modal(document.getElementById('editModal'));
        const saveBtn = document.getElementById('editModalSaveBtn');

        // Remove previous listener and add new one
        const newSaveBtn = saveBtn.cloneNode(true);
        saveBtn.parentNode.replaceChild(newSaveBtn, saveBtn);

        newSaveBtn.addEventListener('click', function() {
            const newName = document.getElementById('editNameInput').value.trim();
            if (!newName) {
                showToast('Name cannot be empty', 'error');
                return;
            }

            fetch(`/api/tandem-masters/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: newName }),
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        nameCell.textContent = newName;
                        modal.hide();
                        showToast('Name updated', 'success');
                    } else {
                        showToast(data.error || 'Failed to update', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showToast('Error updating name', 'error');
                });
        });

        modal.show();
    }

    function handleActiveToggle(e) {
        const checkbox = e.target;
        const row = checkbox.closest('tr');
        const id = row.getAttribute('data-id');
        const active = checkbox.checked;

        fetch(`/api/tandem-masters/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                active: active,
            }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast(active ? 'Activated' : 'Deactivated', 'success');
                } else {
                    checkbox.checked = !active;
                    showToast(data.error || 'Failed to update status', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                checkbox.checked = !active;
                showToast('Error updating status', 'error');
            });
    }

    function handleDelete(e) {
        const btn = e.target.closest('button');
        const row = btn.closest('tr');
        const id = row.getAttribute('data-id');
        const name = row.querySelector('td:nth-child(2)').textContent;

        showConfirmDialog(
            'Delete Tandem Master',
            `Are you sure you want to delete "${escapeHtml(name)}"?`,
            function() {
                fetch(`/api/tandem-masters/${id}`, {
                    method: 'DELETE',
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showToast('Tandem master deleted', 'success');
                            row.remove();
                        } else {
                            showToast(data.error || 'Failed to delete', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showToast('Error deleting tandem master', 'error');
                    });
            }
        );
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
        // Simple toast notification (can be enhanced with a proper library)
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
