/**
 * Client Management JavaScript
 * Handles CRUD operations, filtering, and pagination for clients
 */

(function() {
    'use strict';

    // Configuration
    const config = {
        apiUrl: '/api/clients',
        contentId: 'clients_content',
        filterFormId: 'client-filter-form',
        perPage: 20
    };

    // Current state
    let currentPage = 1;
    let deleteClientId = null;

    // Bootstrap modals
    let clientModal = null;
    let deleteModal = null;

    /**
     * Initialize the module
     */
    function init() {
        // Initialize Bootstrap modals
        const clientModalEl = document.getElementById('clientModal');
        const deleteModalEl = document.getElementById('deleteModal');

        if (clientModalEl) {
            clientModal = new bootstrap.Modal(clientModalEl);
        }
        if (deleteModalEl) {
            deleteModal = new bootstrap.Modal(deleteModalEl);
        }

        // Bind event handlers
        bindEventHandlers();

        // Load initial data
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

        // Add client button
        const addBtn = document.getElementById('client-add-btn');
        if (addBtn) {
            addBtn.addEventListener('click', function() {
                openCreateModal();
            });
        }

        // Save client button
        const saveBtn = document.getElementById('client-save-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', function() {
                saveClient();
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
            if (e.target.closest('.client-edit-btn')) {
                const row = e.target.closest('tr');
                if (row) {
                    openEditModal(row.dataset.id);
                }
            }

            // Delete button
            if (e.target.closest('.client-delete-btn')) {
                const row = e.target.closest('tr');
                if (row) {
                    openDeleteModal(row.dataset.id);
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

        // Clear name input
        const nameInput = form.querySelector('#filter-name');
        if (nameInput) {
            nameInput.value = '';
        }

        // Reset all selects to first option
        form.querySelectorAll('select').forEach(select => {
            select.selectedIndex = 0;
        });

        currentPage = 1;
    }

    /**
     * Load a page of clients via AJAX
     */
    function loadPage(page) {
        currentPage = page;
        const filters = getFilters();
        const contentContainer = document.getElementById(config.contentId);

        if (!contentContainer) {
            console.error('Client content container not found');
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
        const form = document.getElementById('client-form');
        const modalTitle = document.getElementById('clientModalLabel');

        if (form) {
            form.reset();
            document.getElementById('client-id').value = '';
        }

        if (modalTitle) {
            modalTitle.textContent = 'Add Client';
        }

        if (clientModal) {
            clientModal.show();
        }
    }

    /**
     * Open edit modal and load client data
     */
    function openEditModal(id) {
        const modalTitle = document.getElementById('clientModalLabel');

        if (modalTitle) {
            modalTitle.textContent = 'Edit Client';
        }

        // Fetch client data
        fetch(`${config.apiUrl}/${id}`)
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    populateForm(result.data);
                    if (clientModal) {
                        clientModal.show();
                    }
                } else {
                    alert('Failed to load client: ' + (result.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error loading client:', error);
                alert('Failed to load client');
            });
    }

    /**
     * Populate the form with client data
     */
    function populateForm(data) {
        const setVal = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.value = value;
        };
        const setChecked = (id, checked) => {
            const el = document.getElementById(id);
            if (el) el.checked = checked;
        };

        setVal('client-id', data.id || '');
        setVal('client-name', data.name || '');
        setVal('client-email', data.email || '');
        setVal('client-phone', data.phone || '');
        setChecked('client-marketing', data.marketing_flag || false);
    }

    /**
     * Save client (create or update)
     */
    function saveClient() {
        const id = document.getElementById('client-id').value;
        const isEdit = !!id;

        // Gather form data
        const getVal = (id) => {
            const el = document.getElementById(id);
            return el ? el.value : '';
        };
        const getChecked = (id) => {
            const el = document.getElementById(id);
            return el ? el.checked : false;
        };

        const data = {
            name: getVal('client-name').trim(),
            email: getVal('client-email').trim() || null,
            phone: getVal('client-phone').trim() || null,
            marketing_flag: getChecked('client-marketing')
        };

        // Validate
        if (!data.name) {
            alert('Name is required');
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
                    if (clientModal) {
                        clientModal.hide();
                    }
                    loadPage(currentPage);
                } else {
                    alert('Failed to save client: ' + (result.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error saving client:', error);
                alert('Failed to save client');
            });
    }

    /**
     * Open delete confirmation modal
     */
    function openDeleteModal(id) {
        deleteClientId = id;
        if (deleteModal) {
            deleteModal.show();
        }
    }

    /**
     * Confirm and execute delete
     */
    function confirmDelete() {
        if (!deleteClientId) return;

        fetch(`${config.apiUrl}/${deleteClientId}`, {
            method: 'DELETE'
        })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    if (deleteModal) {
                        deleteModal.hide();
                    }
                    deleteClientId = null;
                    loadPage(currentPage);
                } else {
                    alert('Failed to delete client: ' + (result.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error deleting client:', error);
                alert('Failed to delete client');
            });
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
