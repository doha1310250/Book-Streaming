/**
 * Book Streaming - Enterprise Application
 * Main JavaScript file for frontend functionality
 */

// ============================================
// Configuration
// ============================================
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    STORAGE_KEYS: {
        TOKEN: 'book_streaming_token',
        USER: 'book_streaming_user'
    }
};

// ============================================
// API Service
// ============================================
class APIService {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        const token = localStorage.getItem(CONFIG.STORAGE_KEYS.TOKEN);
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        return headers;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.getHeaders(),
                ...options.headers
            }
        };

        try {
            console.log(`[API] ${config.method} ${url}`, config);
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                let errorMessage = 'An error occurred';
                if (data.detail) {
                    if (typeof data.detail === 'string') {
                        errorMessage = data.detail;
                    } else if (Array.isArray(data.detail)) {
                        // Handle Pydantic validation errors
                        errorMessage = data.detail.map(err => err.msg || JSON.stringify(err)).join('. ');
                    } else if (typeof data.detail === 'object') {
                        errorMessage = JSON.stringify(data.detail);
                    }
                }
                throw new Error(errorMessage);
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    async post(endpoint, body) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(body)
        });
    }

    async put(endpoint, body) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(body)
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // Auth endpoints
    async login(email, password) {
        return this.post('/auth/login', { email, password });
    }

    async register(name, email, password) {
        return this.post('/auth/register', { name, email, password });
    }

    async getCurrentUser() {
        return this.get('/users/me');
    }

    // Book endpoints
    async getBooks(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.get(`/books${queryString ? `?${queryString}` : ''}`);
    }

    async getBook(bookId) {
        return this.get(`/books/${bookId}`);
    }

    // Reading session endpoints
    async getReadingStats(period = 'week') {
        return this.get(`/reading-sessions/stats?period=${period}`);
    }

    async createReadingSession(bookId) {
        return this.post(`/books/${bookId}/reading-sessions`, {
            start_time: new Date().toISOString()
        });
    }

    async endReadingSession(sessionId) {
        // Pass end_time as query parameter as expected by the backend
        const endTime = new Date().toISOString();
        return this.put(`/reading-sessions/${sessionId}?end_time=${endTime}`, {});
    }

    async getMyReadingSessions(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.get(`/users/me/reading-sessions${queryString ? `?${queryString}` : ''}`);
    }

    // Mark endpoints
    async markBook(bookId) {
        return this.post(`/books/${bookId}/mark`, {});
    }

    async unmarkBook(bookId) {
        return this.delete(`/books/${bookId}/mark`);
    }

    async getMyMarkedBooks(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        // Fixed endpoint: backend uses /users/me/marks
        return this.get(`/users/me/marks${queryString ? `?${queryString}` : ''}`);
    }

    async isBookMarked(bookId) {
        return this.get(`/books/${bookId}/is-marked`);
    }

    // Review endpoints
    async createReview(bookId, reviewData) {
        return this.post(`/books/${bookId}/reviews`, reviewData);
    }

    async getBookReviews(bookId, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.get(`/books/${bookId}/reviews${queryString ? `?${queryString}` : ''}`);
    }

    // Follower endpoints
    async followUser(userId) {
        return this.post(`/users/${userId}/follow`, {});
    }

    async unfollowUser(userId) {
        return this.delete(`/users/${userId}/follow`);
    }

    async getFollowingActivity(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.get(`/users/me/following/activity${queryString ? `?${queryString}` : ''}`);
    }

    // Health check
    async healthCheck() {
        return this.get('/health');
    }
}

const api = new APIService(CONFIG.API_BASE_URL);

// ============================================
// State Management
// ============================================
const state = {
    user: null,
    isAuthenticated: false,
    books: [],
    isLoading: false
};

function updateState(updates) {
    Object.assign(state, updates);
    onStateChange();
}

function onStateChange() {
    updateAuthUI();
}

// ============================================
// DOM Elements
// ============================================
const elements = {
    navbar: document.getElementById('navbar'),
    navMenu: document.getElementById('nav-menu'),
    navToggle: document.getElementById('nav-toggle'),
    loginBtn: document.getElementById('login-btn'),
    signupBtn: document.getElementById('signup-btn'),
    heroStartBtn: document.getElementById('hero-start-btn'),
    ctaSignupBtn: document.getElementById('cta-signup-btn'),
    authModal: document.getElementById('auth-modal'),
    modalClose: document.getElementById('modal-close'),
    modalTabs: document.querySelectorAll('.modal-tab'),
    loginForm: document.getElementById('login-form'),
    registerForm: document.getElementById('register-form'),
    switchAuthLinks: document.querySelectorAll('.switch-auth'),
    contactForm: document.getElementById('contact-form'),
    booksGrid: document.getElementById('books-grid'),
    filterBtns: document.querySelectorAll('.filter-btn'),
    loadMoreBtn: document.getElementById('load-more-books'),
    toastContainer: document.getElementById('toast-container'),
    loadingOverlay: document.getElementById('loading-overlay'),
    passwordStrength: document.getElementById('password-strength'),
    registerPassword: document.getElementById('register-password')
};

// ============================================
// Toast Notifications
// ============================================
function showToast(message, type = 'default', duration = 4000) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span>${message}</span>
        <span class="toast-close" onclick="this.parentElement.remove()">✕</span>
    `;

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'toast-in 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ============================================
// Loading State
// ============================================
function showLoading() {
    elements.loadingOverlay?.classList.add('active');
}

function hideLoading() {
    elements.loadingOverlay?.classList.remove('active');
}

// ============================================
// Navigation
// ============================================
function initNavigation() {
    // Scroll handling
    let lastScrollY = window.scrollY;

    window.addEventListener('scroll', () => {
        const navbar = elements.navbar;
        if (!navbar) return;

        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        lastScrollY = window.scrollY;
    });

    // Mobile menu toggle
    elements.navToggle?.addEventListener('click', () => {
        elements.navMenu?.classList.toggle('active');
        elements.navToggle.classList.toggle('active');
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });

                // Close mobile menu if open
                elements.navMenu?.classList.remove('active');
            }
        });
    });

    // Active nav link on scroll
    const sections = document.querySelectorAll('section[id]');

    window.addEventListener('scroll', () => {
        const scrollY = window.pageYOffset;

        sections.forEach(section => {
            const sectionHeight = section.offsetHeight;
            const sectionTop = section.offsetTop - 100;
            const sectionId = section.getAttribute('id');
            const navLink = document.querySelector(`.nav-link[href="#${sectionId}"]`);

            if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
                navLink?.classList.add('active');
            } else {
                navLink?.classList.remove('active');
            }
        });
    });
}

// ============================================
// Authentication
// ============================================
function initAuth() {
    // Check for existing session
    const token = localStorage.getItem(CONFIG.STORAGE_KEYS.TOKEN);
    const user = localStorage.getItem(CONFIG.STORAGE_KEYS.USER);

    if (token && user) {
        updateState({
            isAuthenticated: true,
            user: JSON.parse(user)
        });
    }

    // Open modal buttons
    [elements.loginBtn, elements.signupBtn, elements.heroStartBtn, elements.ctaSignupBtn].forEach(btn => {
        btn?.addEventListener('click', () => {
            openAuthModal(btn === elements.signupBtn || btn === elements.heroStartBtn || btn === elements.ctaSignupBtn ? 'register' : 'login');
        });
    });

    // Close modal
    elements.modalClose?.addEventListener('click', closeAuthModal);
    elements.authModal?.addEventListener('click', (e) => {
        if (e.target === elements.authModal) {
            closeAuthModal();
        }
    });

    // Tab switching
    elements.modalTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            switchAuthTab(tab.dataset.tab);
        });
    });

    // Switch auth links
    elements.switchAuthLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            switchAuthTab(link.dataset.target);
        });
    });

    // Form submissions
    elements.loginForm?.addEventListener('submit', handleLogin);
    elements.registerForm?.addEventListener('submit', handleRegister);

    // Password strength indicator
    elements.registerPassword?.addEventListener('input', (e) => {
        updatePasswordStrength(e.target.value);
    });
}

function openAuthModal(tab = 'login') {
    elements.authModal?.classList.add('active');
    switchAuthTab(tab);
    document.body.style.overflow = 'hidden';
}

function closeAuthModal() {
    elements.authModal?.classList.remove('active');
    document.body.style.overflow = '';
    // Reset forms
    elements.loginForm?.reset();
    elements.registerForm?.reset();
}

function switchAuthTab(tab) {
    elements.modalTabs.forEach(t => {
        t.classList.toggle('active', t.dataset.tab === tab);
    });

    if (tab === 'login') {
        elements.loginForm?.classList.remove('hidden');
        elements.registerForm?.classList.add('hidden');
    } else {
        elements.loginForm?.classList.add('hidden');
        elements.registerForm?.classList.remove('hidden');
    }
}

async function handleLogin(e) {
    e.preventDefault();

    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        showLoading();
        const response = await api.login(email, password);

        localStorage.setItem(CONFIG.STORAGE_KEYS.TOKEN, response.access_token);
        localStorage.setItem(CONFIG.STORAGE_KEYS.USER, JSON.stringify(response.user));

        updateState({
            isAuthenticated: true,
            user: response.user
        });

        closeAuthModal();
        showToast('Welcome back! 👋', 'success');
    } catch (error) {
        showToast(error.message || 'Login failed. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function handleRegister(e) {
    e.preventDefault();

    const name = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    try {
        showLoading();
        const response = await api.register(name, email, password);

        localStorage.setItem(CONFIG.STORAGE_KEYS.TOKEN, response.access_token);
        localStorage.setItem(CONFIG.STORAGE_KEYS.USER, JSON.stringify(response.user));

        updateState({
            isAuthenticated: true,
            user: response.user
        });

        closeAuthModal();
        showToast('Account created successfully! 🎉', 'success');
    } catch (error) {
        showToast(error.message || 'Registration failed. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function updatePasswordStrength(password) {
    const strength = elements.passwordStrength;
    if (!strength) return;

    let score = 0;
    if (password.length >= 8) score++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[^a-zA-Z\d]/.test(password)) score++;

    strength.classList.remove('weak', 'medium', 'strong');

    const strengthText = strength.querySelector('.strength-text');

    if (password.length === 0) {
        strengthText.textContent = '';
    } else if (score <= 1) {
        strength.classList.add('weak');
        strengthText.textContent = 'Weak password';
    } else if (score <= 2) {
        strength.classList.add('medium');
        strengthText.textContent = 'Medium strength';
    } else {
        strength.classList.add('strong');
        strengthText.textContent = 'Strong password';
    }
}

function updateAuthUI() {
    const { isAuthenticated, user } = state;

    if (isAuthenticated && user) {
        // Update nav actions
        const navActions = document.querySelector('.nav-actions');
        if (navActions) {
            navActions.innerHTML = `
                <span class="user-greeting">Hi, ${user.name.split(' ')[0]}!</span>
                <button class="btn btn-ghost btn-sm" id="logout-btn">Log Out</button>
            `;

            document.getElementById('logout-btn')?.addEventListener('click', logout);
        }
    }
}

function logout() {
    localStorage.removeItem(CONFIG.STORAGE_KEYS.TOKEN);
    localStorage.removeItem(CONFIG.STORAGE_KEYS.USER);

    updateState({
        isAuthenticated: false,
        user: null
    });

    // Reload to reset UI
    window.location.reload();
}

// ============================================
// Books
// ============================================
async function loadBooks(filter = 'all') {
    const grid = elements.booksGrid;
    if (!grid) return;

    // Show skeletons
    grid.innerHTML = `
        <div class="book-skeleton"></div>
        <div class="book-skeleton"></div>
        <div class="book-skeleton"></div>
        <div class="book-skeleton"></div>
    `;

    try {
        const params = {};
        if (filter === 'verified') {
            params.verified = true;
        }
        params.limit = 8;

        const response = await api.getBooks(params);
        const books = response.items || response;

        if (books.length === 0) {
            grid.innerHTML = `
                <div class="empty-state" style="grid-column: 1/-1; text-align: center; padding: 4rem;">
                    <p style="color: var(--gray-500);">No books found. Check back later!</p>
                </div>
            `;
            return;
        }

        renderBooks(books);
        updateState({ books });
    } catch (error) {
        console.error('Failed to load books:', error);
        // Show demo books if API fails
        renderDemoBooks();
    }
}

function renderBooks(books) {
    const grid = elements.booksGrid;
    if (!grid) return;

    grid.innerHTML = books.map(book => `
        <div class="book-card" data-book-id="${book.book_id}">
            <div class="book-card-cover">
                ${book.cover_url
            ? `<img src="${CONFIG.API_BASE_URL}${book.cover_url}" alt="${book.title}">`
            : '📚'}
                ${book.is_verified ? '<div class="book-card-verified">✓</div>' : ''}
            </div>
            <h4 class="book-card-title">${book.title}</h4>
            <p class="book-card-author">${book.author_name}</p>
            <div class="book-card-rating">
                <span class="stars">★★★★☆</span>
                <span class="count">(${Math.floor(Math.random() * 100) + 1})</span>
            </div>
        </div>
    `).join('');

    // Add click handlers
    grid.querySelectorAll('.book-card').forEach(card => {
        card.addEventListener('click', () => {
            const bookId = card.dataset.bookId;
            openBookModal(bookId);
        });
    });
}

function renderDemoBooks() {
    const demoBooks = [
        { book_id: '1', title: 'The Great Gatsby', author_name: 'F. Scott Fitzgerald', is_verified: true },
        { book_id: '2', title: '1984', author_name: 'George Orwell', is_verified: true },
        { book_id: '3', title: 'Pride and Prejudice', author_name: 'Jane Austen', is_verified: true },
        { book_id: '4', title: 'To Kill a Mockingbird', author_name: 'Harper Lee', is_verified: false },
        { book_id: '5', title: 'The Catcher in the Rye', author_name: 'J.D. Salinger', is_verified: true },
        { book_id: '6', title: 'One Hundred Years of Solitude', author_name: 'Gabriel García Márquez', is_verified: false },
        { book_id: '7', title: 'Brave New World', author_name: 'Aldous Huxley', is_verified: true },
        { book_id: '8', title: 'The Lord of the Rings', author_name: 'J.R.R. Tolkien', is_verified: true }
    ];

    renderBooks(demoBooks);
}

function initBooks() {
    // Load initial books
    loadBooks();

    // Filter buttons
    elements.filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            elements.filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadBooks(btn.dataset.filter);
        });
    });

    // Load more button
    elements.loadMoreBtn?.addEventListener('click', () => {
        showToast('Loading more books...', 'default');
    });
}

// ============================================
// Contact Form
// ============================================
function initContactForm() {
    elements.contactForm?.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);

        try {
            showLoading();
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1000));

            showToast('Message sent successfully! We\'ll get back to you soon. 📬', 'success');
            e.target.reset();
        } catch (error) {
            showToast('Failed to send message. Please try again.', 'error');
        } finally {
            hideLoading();
        }
    });
}

// ============================================
// Book Modal
// ============================================
let currentBookId = null;
let currentSessionId = null;

function initBookModal() {
    const modal = document.getElementById('book-modal');
    const closeBtn = document.getElementById('book-modal-close');
    const tabs = document.querySelectorAll('.book-modal-tabs .tab-btn');

    if (!modal) return;

    // Close handlers
    closeBtn?.addEventListener('click', () => {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    });

    // Tab switching
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Activate tab button
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Activate content
            const targetId = `tab-${tab.dataset.tab}`;
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(targetId)?.classList.add('active');
        });
    });

    // Action Buttons
    document.getElementById('btn-start-reading')?.addEventListener('click', async (e) => {
        if (!checkAuthForAction()) return;

        const btn = e.currentTarget;
        const btnText = btn.querySelector('span');

        try {
            showLoading();

            if (currentSessionId) {
                // End session
                await api.endReadingSession(currentSessionId);
                currentSessionId = null;
                btnText.textContent = 'Start Reading';
                btn.classList.remove('btn-danger'); // Assuming danger class for stop
                btn.classList.add('btn-primary');
                showToast('Reading session ended. Great work! 🎉', 'success');

                // Refresh stats if on dashboard
                if (window.location.pathname.includes('dashboard')) {
                    if (window.loadDashboardData) window.loadDashboardData();
                }
            } else {
                // Start session
                const session = await api.createReadingSession(currentBookId);
                currentSessionId = session.id;
                btnText.textContent = 'End Reading';
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-danger'); // Add a red style class for stop button if available, or just keep primary
                showToast('Reading session started! 📖', 'success');
            }
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            hideLoading();
        }
    });

    document.getElementById('btn-mark-book')?.addEventListener('click', async (e) => {
        if (!checkAuthForAction()) return;

        const btn = e.currentTarget;
        const isMarked = btn.classList.contains('active');

        try {
            if (isMarked) {
                await api.unmarkBook(currentBookId);
                btn.classList.remove('active', 'btn-primary');
                btn.classList.add('btn-outline');
                btn.querySelector('span').textContent = 'Bookmark';
                showToast('Bookmark removed', 'default');
            } else {
                await api.markBook(currentBookId);
                btn.classList.add('active', 'btn-primary');
                btn.classList.remove('btn-outline');
                btn.querySelector('span').textContent = 'Bookmarked';
                showToast('Book added to library! 📚', 'success');
            }
        } catch (error) {
            showToast(error.message, 'error');
        }
    });

    // Reviews
    document.getElementById('btn-write-review')?.addEventListener('click', () => {
        if (!checkAuthForAction()) return;
        document.getElementById('review-form')?.classList.remove('hidden');
    });

    document.getElementById('btn-cancel-review')?.addEventListener('click', () => {
        document.getElementById('review-form')?.classList.add('hidden');
    });

    document.getElementById('review-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();

        const rating = parseInt(document.getElementById('review-rating').value);
        const comment = document.getElementById('review-comment').value;

        try {
            showLoading();
            await api.createReview(currentBookId, { rating, review_comment: comment });
            showToast('Review posted successfully!', 'success');
            document.getElementById('review-form').reset();
            document.getElementById('review-form').classList.add('hidden');
            loadBookReviews(currentBookId); // Refresh reviews
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            hideLoading();
        }
    });
}

function checkAuthForAction() {
    if (!state.isAuthenticated) {
        openAuthModal();
        showToast('Please log in to continue', 'default');
        return false;
    }
    return true;
}

async function openBookModal(bookId) {
    currentBookId = bookId;
    const modal = document.getElementById('book-modal');
    if (!modal) return;

    showLoading();

    try {
        const [book, sessions] = await Promise.all([
            api.getBook(bookId),
            state.isAuthenticated ? api.getMyReadingSessions({ book_id: bookId, limit: 1 }) : []
        ]);

        // Check for active session (no end_time)
        // Check for active session (no end_time)
        const activeSession = sessions.find(s => !s.end_time) || null;
        currentSessionId = activeSession ? activeSession.id : null;

        // Update button state
        const startBtn = document.getElementById('btn-start-reading');
        if (startBtn) {
            const btnText = startBtn.querySelector('span');
            if (currentSessionId) {
                btnText.textContent = 'End Reading';
                startBtn.classList.remove('btn-primary');
                startBtn.classList.add('btn-danger'); // Use error color for stop action
            } else {
                btnText.textContent = 'Start Reading';
                startBtn.classList.remove('btn-danger');
                startBtn.classList.add('btn-primary');
            }
        }

        // Populate specific fields
        document.getElementById('modal-book-title').textContent = book.title;
        document.getElementById('modal-book-author').textContent = book.author_name;
        document.getElementById('modal-book-date').textContent = new Date(book.created_at).getFullYear();
        document.getElementById('modal-book-verified').style.display = book.is_verified ? 'inline-block' : 'none';

        const coverEl = document.getElementById('modal-book-cover');
        if (book.cover_url) {
            coverEl.style.backgroundImage = `url(${CONFIG.API_BASE_URL}${book.cover_url})`;
        } else {
            coverEl.style.backgroundImage = 'none';
            coverEl.style.backgroundColor = 'var(--primary-100)';
        }

        // Check markup status if logged in
        if (state.isAuthenticated) {
            try {
                const markStatus = await api.isBookMarked(bookId);
                const markBtn = document.getElementById('btn-mark-book');
                if (markStatus.is_marked) {
                    markBtn.classList.add('active', 'btn-primary');
                    markBtn.classList.remove('btn-outline');
                    markBtn.querySelector('span').textContent = 'Bookmarked';
                } else {
                    markBtn.classList.remove('active', 'btn-primary');
                    markBtn.classList.add('btn-outline');
                    markBtn.querySelector('span').textContent = 'Bookmark';
                }
            } catch (ignore) { }
        }

        // Load reviews
        loadBookReviews(bookId);

        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    } catch (error) {
        showToast('Failed to load book details', 'error');
        console.error(error);
    } finally {
        hideLoading();
    }
}

async function loadBookReviews(bookId) {
    const container = document.getElementById('modal-reviews-list');
    try {
        const response = await api.getBookReviews(bookId, { limit: 5 });
        const reviews = response.items || response;

        if (reviews.length === 0) {
            container.innerHTML = '<p class="empty-state">No reviews yet. Be the first!</p>';
            return;
        }

        container.innerHTML = reviews.map(review => `
            <div class="review-item">
                <div class="review-header">
                    <span class="review-author">${review.user_name || 'Reader'}</span>
                    <span class="review-date">${new Date(review.created_at).toLocaleDateString()}</span>
                </div>
                <div class="review-rating">${'★'.repeat(review.rating)}${'☆'.repeat(5 - review.rating)}</div>
                <p class="review-text">${review.review_comment}</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load reviews', error);
        container.innerHTML = '<p class="empty-state">Could not load reviews.</p>';
    }
}

// ============================================
// Animations
// ============================================
function initAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('aos-animate');
            }
        });
    }, observerOptions);

    document.querySelectorAll('[data-aos]').forEach(el => {
        observer.observe(el);
    });

    // Animated counters
    const counters = document.querySelectorAll('.stat-number[data-count]');

    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => counterObserver.observe(counter));
}

function animateCounter(element) {
    const target = parseInt(element.dataset.count);
    const duration = 2000;
    const step = target / (duration / 16);
    let current = 0;

    const updateCounter = () => {
        current += step;
        if (current < target) {
            element.textContent = formatNumber(Math.floor(current));
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = formatNumber(target);
        }
    };

    requestAnimationFrame(updateCounter);
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(0) + 'K';
    }
    return num.toLocaleString();
}

// ============================================
// Keyboard Navigation
// ============================================
function initKeyboard() {
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeAuthModal();
        }
    });
}

// ============================================
// Initialize Application
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initAuth();
    initBookModal();
    initBooks();
    initContactForm();
    initAnimations();
    initKeyboard();

    // Check API health
    api.healthCheck()
        .then(() => console.log('✅ API is healthy'))
        .catch(() => console.log('⚠️ API is not available, using demo mode'));

    console.log('📚 Book Streaming App initialized');
});

// ============================================
// Export for external use
// ============================================
window.BookStreaming = {
    api,
    state,
    showToast,
    openAuthModal,
    closeAuthModal,
    loadBooks
};
