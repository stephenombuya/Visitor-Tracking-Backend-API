class VisitorTracker {
    /**
     * Initializes the VisitorTracker with the base API URL and optional fetch options.
     * @param {string} apiBaseUrl - The base URL for the API.
     * @param {Object} fetchOptions - Default options for fetch requests (e.g., headers).
     */
    constructor(apiBaseUrl = 'http://localhost:8000', fetchOptions = {}) {
        this.apiBaseUrl = apiBaseUrl;
        this.defaultFetchOptions = fetchOptions;
    }

    /**
     * Sends a GET request to the specified endpoint with query parameters.
     * @param {string} endpoint - The API endpoint (e.g., '/update').
     * @param {Object} params - Query parameters as key-value pairs.
     * @returns {Promise<Object>} - The parsed JSON response.
     */
    async sendGetRequest(endpoint, params = {}) {
        const url = new URL(`${this.apiBaseUrl}${endpoint}`);
        Object.entries(params).forEach(([key, value]) =>
            url.searchParams.append(key, value)
        );

        try {
            const response = await fetch(url.toString(), {
                method: 'GET',
                ...this.defaultFetchOptions,
            });

            if (!response.ok) {
                throw new Error(
                    `HTTP error! status: ${response.status}, message: ${response.statusText}`
                );
            }

            return await response.json();
        } catch (error) {
            console.error(`Error during GET request to ${url}:`, error);
            throw error;
        }
    }

    /**
     * Updates the visitor count for a given page URL.
     * @param {string} pageUrl - The URL of the page to track.
     * @returns {Promise<Object>} - The API response containing updated visitor data.
     */
    async updateVisitorCount(pageUrl) {
        if (!pageUrl) {
            console.error('Invalid page URL provided for visitor count update.');
            return null;
        }

        try {
            return await this.sendGetRequest('/update', { url: pageUrl });
        } catch (error) {
            console.error('Failed to update visitor count:', error);
            return null;
        }
    }

    /**
     * Retrieves the visitor count for a specific page or all pages.
     * @param {string|null} pageUrl - The URL of the page to query (optional).
     * @returns {Promise<Object|Array>} - The API response containing visitor data.
     */
    async getVisitorCount(pageUrl = null) {
        try {
            const params = pageUrl ? { url: pageUrl } : {};
            return await this.sendGetRequest('/count', params);
        } catch (error) {
            console.error('Failed to retrieve visitor count:', error);
            return null;
        }
    }
}

// Example usage in the browser
document.addEventListener('DOMContentLoaded', () => {
    const tracker = new VisitorTracker('http://localhost:8000', {
        headers: {
            'Content-Type': 'application/json',
        },
    });

    // Automatically update visitor count for the current page
    tracker.updateVisitorCount(window.location.href).then((data) => {
        console.log('Visitor count updated:', data);
    });

    // Retrieve visitor count for a specific page (optional example)
    // tracker.getVisitorCount('http://example.com/some-page').then(data => {
    //     console.log('Visitor count for page:', data);
    // });
});
