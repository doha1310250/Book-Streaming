/**
 * BookTracker - Main Application JavaScript
 * API Service and Shared Utilities
 */

// ============================================
// Configuration
// ============================================
const CONFIG = {
    API_BASE_URL: window.location.origin,
    STORAGE_KEYS: {
        TOKEN: 'book_tracker_token',
        USER: 'book_tracker_user',
        CURRENT_BOOK: 'book_tracker_current_book',
        SESSION: 'book_tracker_session'
    }
};

// ============================================
// API Service
// ============================================
const APIService = {
    baseURL: CONFIG.API_BASE_URL,

    getHeaders() {
        const headers = { 'Content-Type': 'application/json' };
        const token = localStorage.getItem(CONFIG.STORAGE_KEYS.TOKEN);
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        return headers;
    },

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: { ...this.getHeaders(), ...options.headers }
        };

        try {
            const response = await fetch(url, config);

            // Try to parse as JSON, fallback to text
            let data;
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                const text = await response.text();
                data = { detail: text || 'Server error' };
            }

            if (!response.ok) {
                const errorMsg = typeof data.detail === 'string'
                    ? data.detail
                    : (Array.isArray(data.detail) ? data.detail.map(e => e.msg).join(', ') : 'An error occurred');
                throw new Error(errorMsg);
            }
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    // Auth endpoints
    async login(email, password) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
    },

    async register(name, email, password) {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ name, email, password })
        });
    },

    // User endpoints
    async getCurrentUser() {
        return this.request('/users/me');
    },

    async updateUser(data) {
        return this.request('/users/me', {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    // Books endpoints
    async getBookStats() {
        return this.request('/books/stats');
    },

    async getBooks(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/books${query ? '?' + query : ''}`);
    },

    async getBook(bookId) {
        return this.request(`/books/${bookId}`);
    },

    async createBook(formData) {
        // FormData for file upload
        const token = localStorage.getItem(CONFIG.STORAGE_KEYS.TOKEN);
        return fetch(`${this.baseURL}/books`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        }).then(r => r.json());
    },

    // Marks/Bookmarks endpoints
    async markBook(bookId) {
        return this.request(`/books/${bookId}/mark`, { method: 'POST' });
    },

    async unmarkBook(bookId) {
        return this.request(`/books/${bookId}/mark`, { method: 'DELETE' });
    },

    async getMyMarkedBooks(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/users/me/marks${query ? '?' + query : ''}`);
    },

    async isBookMarked(bookId) {
        return this.request(`/books/${bookId}/is-marked`);
    },

    // Reading Sessions endpoints
    async startReadingSession(bookId) {
        return this.request(`/books/${bookId}/reading-sessions`, {
            method: 'POST',
            body: JSON.stringify({
                start_time: new Date().toISOString()
            })
        });
    },

    async endReadingSession(sessionId, endTime = new Date().toISOString()) {
        return this.request(`/reading-sessions/${sessionId}?end_time=${encodeURIComponent(endTime)}`, {
            method: 'PUT'
        });
    },

    async getMyReadingSessions(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/users/me/reading-sessions${query ? '?' + query : ''}`);
    },

    async getReadingStats(period = 'week') {
        return this.request(`/users/me/reading-stats?period=${period}`);
    },

    // Reviews endpoints
    async getBookReviews(bookId, params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/books/${bookId}/reviews${query ? '?' + query : ''}`);
    },

    async createReview(bookId, rating, comment) {
        return this.request(`/books/${bookId}/reviews`, {
            method: 'POST',
            body: JSON.stringify({ rating, review_comment: comment })
        });
    },

    async getBookReviewsSummary(bookId) {
        return this.request(`/books/${bookId}/reviews/summary`);
    },

    // Social endpoints
    async getFollowing(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/users/me/following${query ? '?' + query : ''}`);
    },

    async getFollowers(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/users/me/followers${query ? '?' + query : ''}`);
    },

    async followUser(userId) {
        return this.request(`/users/${userId}/follow`, {
            method: 'POST'
        });
    },

    async unfollowUser(userId) {
        return this.request(`/users/${userId}/follow`, {
            method: 'DELETE'
        });
    },

    async getFollowStatus(userId) {
        return this.request(`/users/${userId}/follow-status`);
    },

    async getFollowingActivity(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/users/me/following/activity${query ? '?' + query : ''}`);
    },

    // User profile endpoints
    async searchUsers(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/users${query ? '?' + query : ''}`);
    },

    async getUserProfile(userId) {
        return this.request(`/users/${userId}/profile`);
    },

    async getUserReadingSessions(userId, params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/users/${userId}/reading-sessions${query ? '?' + query : ''}`);
    },

    // Health check
    async healthCheck() {
        return this.request('/health');
    }
};

// ============================================
// UI Utilities
// ============================================
function showToast(message, type = 'default') {
    const container = document.getElementById('toast-container') || createToastContainer();

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span>${message}</span>
        <span class="toast-close" onclick="this.parentElement.remove()">✕</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.add('active');
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.remove('active');
}

// ============================================
// Auth Utilities
// ============================================
function isLoggedIn() {
    return !!localStorage.getItem(CONFIG.STORAGE_KEYS.TOKEN);
}

function getUser() {
    const userData = localStorage.getItem(CONFIG.STORAGE_KEYS.USER);
    return userData ? JSON.parse(userData) : null;
}

function logout() {
    localStorage.removeItem(CONFIG.STORAGE_KEYS.TOKEN);
    localStorage.removeItem(CONFIG.STORAGE_KEYS.USER);
    localStorage.removeItem(CONFIG.STORAGE_KEYS.CURRENT_BOOK);
    localStorage.removeItem(CONFIG.STORAGE_KEYS.SESSION);
    window.location.href = 'index.html';
}

function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

// ============================================
// Book Cover URL Helper
// ============================================
function getBookCoverUrl(coverUrl) {
    if (!coverUrl) return 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=400';
    if (coverUrl.startsWith('http')) return coverUrl;
    return `${CONFIG.API_BASE_URL}${coverUrl}`;
}

// ============================================
// Export for global use
// ============================================
window.BookTracker = {
    api: APIService,
    config: CONFIG,
    showToast,
    showLoading,
    hideLoading,
    isLoggedIn,
    getUser,
    logout,
    requireAuth,
    getBookCoverUrl,
    toggleTheme,
    getTheme,
    initTheme
};

// ============================================
// Theme Management (Dark Mode)
// ============================================
function getTheme() {
    return localStorage.getItem('book_tracker_theme') || 'light';
}

function setTheme(theme) {
    localStorage.setItem('book_tracker_theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
    updateThemeToggle(theme);
}

function toggleTheme() {
    const current = getTheme();
    const newTheme = current === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    return newTheme;
}

function updateThemeToggle(theme) {
    const toggles = document.querySelectorAll('.theme-toggle');
    toggles.forEach(toggle => {
        toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
        toggle.title = theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
    });
}

function initTheme() {
    const theme = getTheme();
    document.documentElement.setAttribute('data-theme', theme);
    updateThemeToggle(theme);
}

// Check API health on load and init theme
document.addEventListener('DOMContentLoaded', () => {
    initTheme();

    APIService.healthCheck()
        .then(() => console.log('✅ API connected'))
        .catch(() => console.warn('⚠️ API not available'));
});
