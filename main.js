class VisitorTracker {
    constructor(apiBaseUrl = 'http://localhost:8000') {
        this.apiBaseUrl = apiBaseUrl;
    }

    async updateVisitorCount(pageUrl) {
        try {
            const response = await fetch(
                `${this.apiBaseUrl}/update?url=${encodeURIComponent(pageUrl)}`,
                { method: 'GET' }
            );
            return await response.json();
        } catch (error) {
            console.error('Failed to update visitor count:', error);
        }
    }

    async getVisitorCount(pageUrl = null) {
        try {
            const url = pageUrl 
                ? `${this.apiBaseUrl}/count?url=${encodeURIComponent(pageUrl)}`
                : `${this.apiBaseUrl}/count`;
            
            const response = await fetch(url, { method: 'GET' });
            return await response.json();
        } catch (error) {
            console.error('Failed to retrieve visitor count:', error);
        }
    }
}

// Example usage in browser
document.addEventListener('DOMContentLoaded', () => {
    const tracker = new VisitorTracker();
    tracker.updateVisitorCount(window.location.href);
});
