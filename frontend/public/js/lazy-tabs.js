/**
 * Lazy Tabs - AJAX loading for Bootstrap 5 tab content with URL hash persistence
 *
 * Usage: Add data attributes to tab elements:
 * - data-tab-api-url: API endpoint that returns HTML content
 * - data-tab-content-id: ID of the container to load content into
 * - data-tab-api-method: HTTP method (default: GET)
 *
 * Example:
 * <a class="nav-link" data-bs-toggle="tab" href="#content-fonts"
 *    data-tab-api-url="/api/splashscreens/tab/fonts"
 *    data-tab-content-id="fonts-content">
 *    Fonts
 * </a>
 */
(function() {
    'use strict';

    // Track which tabs have been loaded (prevents duplicate loads)
    const loadedTabs = new Map();

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
     * Load content for a lazy tab
     */
    function loadTabContent(tabElement) {
        const apiUrl = tabElement.getAttribute('data-tab-api-url');
        const contentId = tabElement.getAttribute('data-tab-content-id');
        const method = tabElement.getAttribute('data-tab-api-method') || 'GET';

        if (!apiUrl || !contentId) {
            return Promise.resolve();
        }

        const contentContainer = document.getElementById(contentId);
        if (!contentContainer) {
            console.warn(`Lazy Tabs: Content container #${contentId} not found`);
            return Promise.reject(new Error('Container not found'));
        }

        // Check load state
        const loadState = loadedTabs.get(tabElement);
        if (loadState === true || loadState === 'loading') {
            return Promise.resolve();
        }

        // Mark as loading
        loadedTabs.set(tabElement, 'loading');

        // Show loading indicator
        contentContainer.innerHTML = `
            <div class="text-center text-muted py-5">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading...</p>
            </div>
        `;

        // Fetch content
        return fetch(apiUrl, { method: method })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                return response.text();
            })
            .then(html => {
                contentContainer.innerHTML = html;
                loadedTabs.set(tabElement, true);

                // Dispatch event for other scripts to know content was loaded
                document.dispatchEvent(new CustomEvent('lazyTabLoaded', {
                    detail: { tabElement, contentId, contentContainer }
                }));
            })
            .catch(error => {
                loadedTabs.set(tabElement, false);
                contentContainer.innerHTML = `
                    <div class="alert alert-danger m-3">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        Failed to load content: ${error.message}
                    </div>
                `;
                console.error('Lazy Tabs: Failed to load content', error);
            });
    }

    /**
     * Initialize lazy loading for a tab
     */
    function initializeLazyTab(tabElement) {
        const apiUrl = tabElement.getAttribute('data-tab-api-url');
        if (!apiUrl) return;

        loadedTabs.set(tabElement, false);
    }

    /**
     * Restore active tab from URL hash, or activate first tab
     */
    function restoreActiveTabFromHash() {
        const hash = window.location.hash;

        // Find matching tab
        let tabEl = null;
        if (hash) {
            tabEl = document.querySelector(
                `[data-bs-toggle="tab"][data-bs-target="${hash}"], ` +
                `[data-bs-toggle="tab"][href="${hash}"]`
            );
        }

        // Fall back to first tab
        if (!tabEl) {
            tabEl = document.querySelector('[data-bs-toggle="tab"]');
        }

        if (tabEl) {
            const tab = bootstrap.Tab.getOrCreateInstance(tabEl);
            tab.show();
        }
    }

    /**
     * Initialize
     */
    function init() {
        // Initialize all lazy tabs
        document.querySelectorAll('[data-tab-api-url]').forEach(initializeLazyTab);

        // Listen for tab show events
        document.addEventListener('shown.bs.tab', function(e) {
            const tabId = getTabId(e.target);
            saveTabState(tabId);

            // Load content if this is a lazy tab
            if (e.target.hasAttribute('data-tab-api-url')) {
                loadTabContent(e.target);
            }
        });

        // Restore tab from hash on page load
        restoreActiveTabFromHash();
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose for manual reload if needed
    window.LazyTabs = {
        reload: function(tabElement) {
            loadedTabs.set(tabElement, false);
            loadTabContent(tabElement);
        }
    };
})();
