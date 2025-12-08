/**
 * AJAX Content Loader - Generic utility for loading content via AJAX
 *
 * Provides reusable function for fetching and injecting content from API endpoints.
 * Can be used for tabs, pagination, filters, modals, infinite scroll, etc.
 *
 * Usage:
 * // Simple GET request
 * loadContent('/api/endpoint', document.getElementById('container'));
 *
 * // POST with custom data
 * loadContent('/api/endpoint', container, 'POST', {
 *     requestData: { page: 1, filter: 'active' },
 *     replaceMode: 'outerHTML',
 *     loadingStyle: 'dim',
 *     onSuccess: (html) => console.log('Loaded!'),
 *     onError: (error) => console.error('Failed:', error)
 * });
 */

/**
 * Load content via AJAX and inject into target container
 *
 * @param {string} apiUrl - API endpoint to call
 * @param {HTMLElement} contentContainer - DOM element to inject content into
 * @param {string} method - HTTP method (GET, POST, PUT, PATCH, DELETE, default: GET)
 * @param {Object|null} options - Options object
 * @param {Object} options.requestData - Custom JSON data to send
 * @param {string} options.replaceMode - 'innerHTML' (default) or 'outerHTML'
 * @param {string} options.loadingStyle - 'replace' (default) or 'dim' (opacity)
 * @param {Function} options.onSuccess - Callback after successful load (receives html string)
 * @param {Function} options.onError - Callback on error (receives error object)
 * @returns {Promise<void>}
 */
function loadContent(apiUrl, contentContainer, method = 'GET', options = null) {
    // Validate parameters
    if (!apiUrl || typeof apiUrl !== 'string') {
        console.error('AJAX Content Loader: Invalid apiUrl parameter', apiUrl);
        return Promise.reject(new Error('Invalid API URL'));
    }

    if (!contentContainer || !(contentContainer instanceof HTMLElement)) {
        console.error('AJAX Content Loader: Invalid contentContainer parameter', contentContainer);
        return Promise.reject(new Error('Invalid content container'));
    }

    // Normalize method
    method = (method || 'GET').toUpperCase();

    // Parse options
    options = options || {};
    const {
        requestData = null,
        replaceMode = 'innerHTML',
        loadingStyle = 'replace',
        onSuccess = null,
        onError = null
    } = options;

    // Show loading state
    const originalOpacity = contentContainer.style.opacity;
    const originalPointerEvents = contentContainer.style.pointerEvents;

    if (loadingStyle === 'dim') {
        // Dim existing content (for pagination use case)
        contentContainer.style.opacity = '0.5';
        contentContainer.style.pointerEvents = 'none';
    } else {
        // Replace content with loading HTML
        contentContainer.innerHTML = `
            <div class="text-center text-muted py-5">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading content...</p>
            </div>
        `;
    }

    // Prepare fetch options
    const fetchOptions = {
        method: method,
        headers: {}
    };

    // Handle request body
    if (method !== 'GET' && method !== 'HEAD') {
        if (requestData) {
            fetchOptions.headers['Content-Type'] = 'application/json';
            fetchOptions.body = JSON.stringify(requestData);
        }
    }

    // Make API request
    return fetch(apiUrl, fetchOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.text();
        })
        .then(html => {
            // Restore loading state if dimmed
            if (loadingStyle === 'dim') {
                contentContainer.style.opacity = originalOpacity;
                contentContainer.style.pointerEvents = originalPointerEvents;
            }

            // Inject content based on replace mode
            if (replaceMode === 'outerHTML') {
                // Replace entire element (for pagination)
                contentContainer.outerHTML = html;
            } else {
                // Replace inner content (default)
                contentContainer.innerHTML = html;
            }

            // Call success callback if provided
            if (onSuccess && typeof onSuccess === 'function') {
                onSuccess(html);
            }
        })
        .catch(error => {
            console.error('AJAX Content Loader: Error loading content:', error);

            // Restore state if dimmed
            if (loadingStyle === 'dim') {
                contentContainer.style.opacity = originalOpacity;
                contentContainer.style.pointerEvents = originalPointerEvents;
            }

            // Show error message
            contentContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    <strong>Failed to load content.</strong>
                    <p class="mb-0">${error.message}</p>
                    <button class="btn btn-sm btn-outline-danger mt-2" onclick="location.reload()">
                        <i class="bi bi-arrow-clockwise me-1"></i>Reload Page
                    </button>
                </div>
            `;

            // Call error callback if provided
            if (onError && typeof onError === 'function') {
                onError(error);
            }

            throw error; // Re-throw for caller to handle if needed
        });
}
