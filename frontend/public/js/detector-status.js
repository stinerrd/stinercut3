/**
 * Detector Status Widget
 *
 * Displays detector daemon status and provides toggle control for device monitoring.
 * Uses WebSocket for all communication - both commands and real-time updates.
 */
(function() {
    'use strict';

    // DOM element references
    let els = {};
    let isToggling = false;

    /**
     * Initialize the widget on DOM ready.
     */
    function init() {
        els = {
            card: document.getElementById('detector-status-card'),
            serviceStatus: document.getElementById('detector-service-status'),
            listenerToggle: document.getElementById('detector-listener-toggle'),
            listenerLabel: document.getElementById('detector-listener-label'),
            refreshIndicator: document.getElementById('detector-refresh-indicator'),
            errorContainer: document.getElementById('detector-error')
        };

        // Exit if widget not on page
        if (!els.card) return;

        // Bind toggle event
        els.listenerToggle.addEventListener('change', handleToggle);

        // Subscribe to WebSocket events for real-time updates
        if (window.App && window.App.ws) {
            window.App.ws.on('detector.status', function(data) {
                console.log('[Detector] Received status update:', data);
                updateUI(data);
                hideError();
                showRefreshIndicator(false);
            });

            // Request initial status once WebSocket connects
            window.App.ws.onConnect(fetchStatus);
        }
    }

    /**
     * Request detector status via WebSocket.
     */
    function fetchStatus() {
        if (isToggling) return;

        console.log('[Detector] Requesting status via WebSocket');
        showRefreshIndicator(true);

        if (window.App && window.App.ws) {
            var sent = window.App.ws.send('detector:status');
            if (!sent) {
                // WebSocket not connected yet, retry after a short delay
                setTimeout(fetchStatus, 1000);
            }
        }
    }

    /**
     * Handle toggle switch change.
     */
    function handleToggle(e) {
        const enable = e.target.checked;
        const command = enable ? 'detector:enable' : 'detector:disable';

        isToggling = true;
        els.listenerToggle.disabled = true;

        console.log('[Detector] Sending command:', command);

        if (window.App && window.App.ws) {
            var sent = window.App.ws.send(command);
            if (sent) {
                // Optimistic UI update
                els.listenerLabel.textContent = enable ? 'Enabled' : 'Disabled';
                showToast('Device listener ' + (enable ? 'enabled' : 'disabled'), 'success');
                hideError();
            } else {
                // WebSocket not connected
                els.listenerToggle.checked = !enable;
                showToast('WebSocket not connected', 'danger');
                showError('WebSocket not connected');
            }
        }

        els.listenerToggle.disabled = false;
        isToggling = false;
    }

    /**
     * Update UI based on status data.
     */
    function updateUI(data) {
        console.log('[Detector] updateUI called with:', data);

        // Update service status badge
        if (data.running) {
            els.serviceStatus.textContent = 'Running';
            els.serviceStatus.className = 'badge bg-success';
        } else if (data.error) {
            els.serviceStatus.textContent = 'Offline';
            els.serviceStatus.className = 'badge bg-danger';
        } else {
            els.serviceStatus.textContent = 'Stopped';
            els.serviceStatus.className = 'badge bg-warning';
        }

        // Update listener toggle
        const isEnabled = data.monitoring_enabled || false;
        els.listenerToggle.checked = isEnabled;
        els.listenerToggle.disabled = !data.running;
        els.listenerLabel.textContent = isEnabled ? 'Enabled' : 'Disabled';
    }

    /**
     * Set UI to offline state.
     */
    function setOfflineState() {
        els.serviceStatus.textContent = 'Unreachable';
        els.serviceStatus.className = 'badge bg-danger';
        els.listenerToggle.disabled = true;
        els.listenerLabel.textContent = 'Unavailable';
    }

    /**
     * Show/hide refresh indicator.
     */
    function showRefreshIndicator(show) {
        if (els.refreshIndicator) {
            els.refreshIndicator.style.display = show ? 'inline' : 'none';
        }
    }

    /**
     * Show error message in card.
     */
    function showError(message) {
        if (els.errorContainer) {
            els.errorContainer.textContent = message;
            els.errorContainer.style.display = 'block';
        }
    }

    /**
     * Hide error message.
     */
    function hideError() {
        if (els.errorContainer) {
            els.errorContainer.style.display = 'none';
        }
    }

    /**
     * Show Bootstrap toast notification.
     */
    function showToast(message, type) {
        type = type || 'info';

        // Get or create toast container
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1100';
            document.body.appendChild(container);
        }

        // Create toast element
        const toastEl = document.createElement('div');
        toastEl.className = 'toast align-items-center text-bg-' + type + ' border-0';
        toastEl.setAttribute('role', 'alert');
        toastEl.innerHTML =
            '<div class="d-flex">' +
                '<div class="toast-body">' + message + '</div>' +
                '<button type="button" class="btn-close btn-close-white me-2 m-auto" ' +
                        'data-bs-dismiss="toast"></button>' +
            '</div>';

        container.appendChild(toastEl);

        // Show toast using Bootstrap
        const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
        toast.show();

        // Remove element after hidden
        toastEl.addEventListener('hidden.bs.toast', function() {
            toastEl.remove();
        });
    }

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', init);
})();
