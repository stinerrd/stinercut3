/**
 * Project Management JavaScript
 * Handles CRUD operations, filtering, and pagination for projects
 */

(function() {
    'use strict';

    // Configuration from window.App (injected by controller)
    const config = {
        apiUrl: '/api/projects',
        contentId: 'projects_content',
        filterFormId: 'project-filter-form',
        perPage: 20
    };

    // Current state
    let currentPage = 1;
    let deleteProjectId = null;

    // Bootstrap modals
    let projectModal = null;
    let deleteModal = null;
    let qrModal = null;

    /**
     * Initialize the module
     */
    function init() {
        // Initialize Bootstrap modals
        const projectModalEl = document.getElementById('projectModal');
        const deleteModalEl = document.getElementById('deleteModal');
        const qrModalEl = document.getElementById('qrModal');

        if (projectModalEl) {
            projectModal = new bootstrap.Modal(projectModalEl);
        }
        if (deleteModalEl) {
            deleteModal = new bootstrap.Modal(deleteModalEl);
        }
        if (qrModalEl) {
            qrModal = new bootstrap.Modal(qrModalEl);
        }

        // Bind event handlers
        bindEventHandlers();

        // Load initial data with today's date filter
        loadPage(1);
    }

    /**
     * Bind all event handlers
     */
    function bindEventHandlers() {
        // Filter form submit
        const filterForm = document.getElementById(config.filterFormId);
        if (filterForm) {
            filterForm.addEventListener('submit', function(e) {
                e.preventDefault();
                currentPage = 1;
                loadPage(1);
            });
        }

        // Filter reset button
        const resetBtn = document.getElementById('filter-reset-btn');
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                resetFilters();
                loadPage(1);
            });
        }

        // Add project button
        const addBtn = document.getElementById('project-add-btn');
        if (addBtn) {
            addBtn.addEventListener('click', function() {
                openCreateModal();
            });
        }

        // Save project button
        const saveBtn = document.getElementById('project-save-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', function() {
                saveProject();
            });
        }

        // Delete confirm button
        const deleteConfirmBtn = document.getElementById('delete-confirm-btn');
        if (deleteConfirmBtn) {
            deleteConfirmBtn.addEventListener('click', function() {
                confirmDelete();
            });
        }

        // Delegate click events for table rows (edit, delete, pagination)
        document.addEventListener('click', function(e) {
            // Edit button
            if (e.target.closest('.project-edit-btn')) {
                const row = e.target.closest('tr');
                if (row) {
                    openEditModal(row.dataset.id);
                }
            }

            // Delete button
            if (e.target.closest('.project-delete-btn')) {
                const row = e.target.closest('tr');
                if (row) {
                    openDeleteModal(row.dataset.id);
                }
            }

            // QR code button
            if (e.target.closest('.project-qr-btn')) {
                const btn = e.target.closest('.project-qr-btn');
                if (btn) {
                    openQrModal(btn.dataset.qr, btn.dataset.uuid);
                }
            }

            // Pagination link
            if (e.target.closest('.pagination .page-link[data-page]')) {
                e.preventDefault();
                const page = parseInt(e.target.closest('.page-link').dataset.page);
                if (page && page !== currentPage) {
                    loadPage(page);
                }
            }
        });
    }

    /**
     * Get current filter values from form
     */
    function getFilters() {
        const form = document.getElementById(config.filterFormId);
        if (!form) return {};

        const formData = new FormData(form);
        const filters = {};

        for (const [key, value] of formData.entries()) {
            if (value && value !== '') {
                filters[key] = value;
            }
        }

        return filters;
    }

    /**
     * Reset filter form to defaults
     */
    function resetFilters() {
        const form = document.getElementById(config.filterFormId);
        if (!form) return;

        // Reset date to today
        const dateInput = form.querySelector('#filter-date');
        if (dateInput) {
            dateInput.value = new Date().toISOString().split('T')[0];
        }

        // Reset all selects to first option
        form.querySelectorAll('select').forEach(select => {
            select.selectedIndex = 0;
        });

        currentPage = 1;
    }

    /**
     * Load a page of projects via AJAX
     */
    function loadPage(page) {
        currentPage = page;
        const filters = getFilters();
        const contentContainer = document.getElementById(config.contentId);

        if (!contentContainer) {
            console.error('Project content container not found');
            return;
        }

        const requestData = {
            page: page,
            per_page: config.perPage,
            ...filters
        };

        loadContent(config.apiUrl, contentContainer, 'POST', {
            requestData: requestData,
            replaceMode: 'outerHTML',
            loadingStyle: 'dim',
            onSuccess: function() {
                // Update URL with current state (for browser history)
                updateUrl(page, filters);
            }
        });
    }

    /**
     * Update browser URL without page reload
     */
    function updateUrl(page, filters) {
        const params = new URLSearchParams();
        if (page > 1) {
            params.set('page', page);
        }
        for (const [key, value] of Object.entries(filters)) {
            if (value) {
                params.set(key, value);
            }
        }

        const newUrl = params.toString()
            ? `${window.location.pathname}?${params.toString()}`
            : window.location.pathname;

        window.history.pushState({ page, filters }, '', newUrl);
    }

    /**
     * Open create modal
     */
    function openCreateModal() {
        const form = document.getElementById('project-form');
        const modalTitle = document.getElementById('projectModalLabel');

        if (form) {
            form.reset();
            document.getElementById('project-id').value = '';
            // Set default date to today
            document.getElementById('project-desired-date').value = new Date().toISOString().split('T')[0];
        }

        if (modalTitle) {
            modalTitle.textContent = 'Add Project';
        }

        if (projectModal) {
            projectModal.show();
        }
    }

    /**
     * Open edit modal and load project data
     */
    function openEditModal(id) {
        const modalTitle = document.getElementById('projectModalLabel');

        if (modalTitle) {
            modalTitle.textContent = 'Edit Project';
        }

        // Fetch project data
        fetch(`${config.apiUrl}/${id}`)
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    populateForm(result.data);
                    if (projectModal) {
                        projectModal.show();
                    }
                } else {
                    alert('Failed to load project: ' + (result.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error loading project:', error);
                alert('Failed to load project');
            });
    }

    /**
     * Populate the form with project data
     */
    function populateForm(data) {
        const setVal = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.value = value;
        };

        setVal('project-id', data.id || '');
        setVal('project-client', data.client_id || '');
        setVal('project-type', data.type || 'tandem_hc');
        setVal('project-videographer', data.videographer_id || '');
        setVal('project-desired-date', data.desired_date || '');
        setVal('project-video', data.video || 'maybe');
        setVal('project-photo', data.photo || 'maybe');
    }

    /**
     * Save project (create or update)
     */
    function saveProject() {
        const form = document.getElementById('project-form');
        const id = document.getElementById('project-id').value;
        const isEdit = !!id;

        // Gather form data
        const getVal = (id) => {
            const el = document.getElementById(id);
            return el ? el.value : '';
        };

        const data = {
            client_id: getVal('project-client') || null,
            type: getVal('project-type') || 'tandem_hc',
            videographer_id: getVal('project-videographer') || null,
            desired_date: getVal('project-desired-date'),
            video: getVal('project-video'),
            photo: getVal('project-photo')
        };

        // Validate
        if (!data.client_id) {
            alert('Client is required');
            return;
        }

        if (!data.type) {
            alert('Type is required');
            return;
        }

        // Determine URL and method
        const url = isEdit ? `${config.apiUrl}/${id}` : `${config.apiUrl}/create`;
        const method = isEdit ? 'PUT' : 'POST';

        // Submit
        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    if (projectModal) {
                        projectModal.hide();
                    }
                    loadPage(currentPage);
                } else {
                    alert('Failed to save project: ' + (result.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error saving project:', error);
                alert('Failed to save project');
            });
    }

    /**
     * Open delete confirmation modal
     */
    function openDeleteModal(id) {
        deleteProjectId = id;
        if (deleteModal) {
            deleteModal.show();
        }
    }

    /**
     * Confirm and execute delete
     */
    function confirmDelete() {
        if (!deleteProjectId) return;

        fetch(`${config.apiUrl}/${deleteProjectId}`, {
            method: 'DELETE'
        })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    if (deleteModal) {
                        deleteModal.hide();
                    }
                    deleteProjectId = null;
                    loadPage(currentPage);
                } else {
                    alert('Failed to delete project: ' + (result.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error deleting project:', error);
                alert('Failed to delete project');
            });
    }

    /**
     * Open QR code modal and display QR image
     */
    function openQrModal(qrBase64, uuid) {
        console.log('Opening QR modal');
        console.log('QR Base64 length:', qrBase64 ? qrBase64.length : 0);
        console.log('UUID:', uuid);

        const qrImage = document.getElementById('qr-code-image');
        const qrUuid = document.getElementById('qr-uuid');

        if (qrImage && qrBase64) {
            const dataUrl = 'data:image/png;base64,' + qrBase64;
            console.log('Setting image src, data URL length:', dataUrl.length);
            qrImage.src = dataUrl;
        }

        if (qrUuid && uuid) {
            qrUuid.textContent = uuid;
        }

        if (qrModal) {
            qrModal.show();
        }
    }

    // Handle browser back/forward
    window.addEventListener('popstate', function(e) {
        if (e.state) {
            currentPage = e.state.page || 1;
            // Restore filters to form
            if (e.state.filters) {
                const form = document.getElementById(config.filterFormId);
                if (form) {
                    for (const [key, value] of Object.entries(e.state.filters)) {
                        const input = form.querySelector(`[name="${key}"]`);
                        if (input) {
                            input.value = value;
                        }
                    }
                }
            }
            loadPage(currentPage);
        }
    });

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
