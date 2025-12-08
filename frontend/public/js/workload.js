/**
 * Workload Management JavaScript
 * Handles CRUD operations, filtering, and pagination for workloads
 */

(function() {
    'use strict';

    // Configuration from window.App (injected by controller)
    const config = {
        apiUrl: '/api/workloads',
        contentId: 'workloads_content',
        filterFormId: 'workload-filter-form',
        perPage: 20
    };

    // Current state
    let currentPage = 1;
    let deleteWorkloadId = null;

    // Bootstrap modals
    let workloadModal = null;
    let deleteModal = null;
    let qrModal = null;

    /**
     * Initialize the module
     */
    function init() {
        // Initialize Bootstrap modals
        const workloadModalEl = document.getElementById('workloadModal');
        const deleteModalEl = document.getElementById('deleteModal');
        const qrModalEl = document.getElementById('qrModal');

        if (workloadModalEl) {
            workloadModal = new bootstrap.Modal(workloadModalEl);
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

        // Add workload button
        const addBtn = document.getElementById('workload-add-btn');
        if (addBtn) {
            addBtn.addEventListener('click', function() {
                openCreateModal();
            });
        }

        // Save workload button
        const saveBtn = document.getElementById('workload-save-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', function() {
                saveWorkload();
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
            if (e.target.closest('.workload-edit-btn')) {
                const row = e.target.closest('tr');
                if (row) {
                    openEditModal(row.dataset.id);
                }
            }

            // Delete button
            if (e.target.closest('.workload-delete-btn')) {
                const row = e.target.closest('tr');
                if (row) {
                    openDeleteModal(row.dataset.id);
                }
            }

            // QR code button
            if (e.target.closest('.workload-qr-btn')) {
                const btn = e.target.closest('.workload-qr-btn');
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
     * Load a page of workloads via AJAX
     */
    function loadPage(page) {
        currentPage = page;
        const filters = getFilters();
        const contentContainer = document.getElementById(config.contentId);

        if (!contentContainer) {
            console.error('Workload content container not found');
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
        const form = document.getElementById('workload-form');
        const modalTitle = document.getElementById('workloadModalLabel');

        if (form) {
            form.reset();
            document.getElementById('workload-id').value = '';
            // Set default date to today
            document.getElementById('workload-desired-date').value = new Date().toISOString().split('T')[0];
        }

        if (modalTitle) {
            modalTitle.textContent = 'Add Workload';
        }

        if (workloadModal) {
            workloadModal.show();
        }
    }

    /**
     * Open edit modal and load workload data
     */
    function openEditModal(id) {
        const modalTitle = document.getElementById('workloadModalLabel');

        if (modalTitle) {
            modalTitle.textContent = 'Edit Workload';
        }

        // Fetch workload data
        fetch(`${config.apiUrl}/${id}`)
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    populateForm(result.data);
                    if (workloadModal) {
                        workloadModal.show();
                    }
                } else {
                    alert('Failed to load workload: ' + (result.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error loading workload:', error);
                alert('Failed to load workload');
            });
    }

    /**
     * Populate the form with workload data
     */
    function populateForm(data) {
        const setVal = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.value = value;
        };

        setVal('workload-id', data.id || '');
        setVal('workload-client', data.client_id || '');
        setVal('workload-type', data.type || 'tandem_hc');
        setVal('workload-videographer', data.videographer_id || '');
        setVal('workload-desired-date', data.desired_date || '');
        setVal('workload-video', data.video || 'maybe');
        setVal('workload-photo', data.photo || 'maybe');
    }

    /**
     * Save workload (create or update)
     */
    function saveWorkload() {
        const form = document.getElementById('workload-form');
        const id = document.getElementById('workload-id').value;
        const isEdit = !!id;

        // Gather form data
        const getVal = (id) => {
            const el = document.getElementById(id);
            return el ? el.value : '';
        };

        const data = {
            client_id: getVal('workload-client') || null,
            type: getVal('workload-type') || 'tandem_hc',
            videographer_id: getVal('workload-videographer') || null,
            desired_date: getVal('workload-desired-date'),
            video: getVal('workload-video'),
            photo: getVal('workload-photo')
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
                    if (workloadModal) {
                        workloadModal.hide();
                    }
                    loadPage(currentPage);
                } else {
                    alert('Failed to save workload: ' + (result.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error saving workload:', error);
                alert('Failed to save workload');
            });
    }

    /**
     * Open delete confirmation modal
     */
    function openDeleteModal(id) {
        deleteWorkloadId = id;
        if (deleteModal) {
            deleteModal.show();
        }
    }

    /**
     * Confirm and execute delete
     */
    function confirmDelete() {
        if (!deleteWorkloadId) return;

        fetch(`${config.apiUrl}/${deleteWorkloadId}`, {
            method: 'DELETE'
        })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    if (deleteModal) {
                        deleteModal.hide();
                    }
                    deleteWorkloadId = null;
                    loadPage(currentPage);
                } else {
                    alert('Failed to delete workload: ' + (result.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error deleting workload:', error);
                alert('Failed to delete workload');
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
