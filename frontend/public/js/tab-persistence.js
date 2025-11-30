/**
 * Tab Persistence - Remembers active tab via URL hash (Bootstrap 5)
 *
 * Usage: Include this script on any page with Bootstrap 5 tabs.
 * Tabs must have href="#tabId" or data-bs-target="#tabId" attributes.
 */
(function() {
    'use strict';

    /**
     * Get the tab identifier from a tab element
     */
    function getTabId(tabEl) {
        return tabEl.getAttribute('data-bs-target') || tabEl.getAttribute('href');
    }

    /**
     * Save active tab to URL hash
     */
    function saveTabState(tabId) {
        if (tabId && tabId.startsWith('#')) {
            history.replaceState(null, null, tabId);
        }
    }

    /**
     * Restore active tab from URL hash
     */
    function restoreTabState() {
        const hash = window.location.hash;
        if (!hash) return;

        // Find tab button/link that targets this hash
        const tabEl = document.querySelector(
            `[data-bs-toggle="tab"][data-bs-target="${hash}"], ` +
            `[data-bs-toggle="tab"][href="${hash}"]`
        );

        if (tabEl) {
            const tab = bootstrap.Tab.getOrCreateInstance(tabEl);
            tab.show();
        }
    }

    /**
     * Initialize tab persistence
     */
    function init() {
        // Listen for tab changes (event delegation)
        document.addEventListener('shown.bs.tab', function(e) {
            const tabId = getTabId(e.target);
            saveTabState(tabId);
        });

        // Restore tab from hash on page load
        restoreTabState();
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
