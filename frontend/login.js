/**
 * BookTracker - Login Page JavaScript
 * Handles login/signup with API integration
 */

document.addEventListener('DOMContentLoaded', () => {
    // Check if already logged in
    if (localStorage.getItem('book_tracker_token')) {
        window.location.href = 'dashboard.html';
        return;
    }

    initTabs();
    initForms();
});

// ============================================
// Tab Switching
// ============================================
function initTabs() {
    const tabs = document.querySelectorAll('.auth-tab');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const authTitle = document.getElementById('auth-title');
    const authSubtitle = document.getElementById('auth-subtitle');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;

            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            if (tabName === 'login') {
                loginForm.classList.remove('hidden');
                signupForm.classList.add('hidden');
                authTitle.textContent = 'Sign in';
                authSubtitle.textContent = 'Enter your credentials to access your account';
            } else {
                loginForm.classList.add('hidden');
                signupForm.classList.remove('hidden');
                authTitle.textContent = 'Create account';
                authSubtitle.textContent = 'Get started with your free account today';
            }
        });
    });
}

// ============================================
// Form Submission
// ============================================
function initForms() {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');

    // Login
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value;
        const btn = document.getElementById('login-btn');

        if (!email || !password) {
            showToast('Please fill in all fields', 'error');
            return;
        }

        btn.disabled = true;
        btn.textContent = 'Signing in...';

        try {
            const response = await BookTracker.api.login(email, password);

            localStorage.setItem('book_tracker_token', response.access_token);
            localStorage.setItem('book_tracker_user', JSON.stringify(response.user));

            showToast('Welcome back!', 'success');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 500);
        } catch (error) {
            showToast(error.message || 'Login failed', 'error');
            btn.disabled = false;
            btn.textContent = 'Sign In';
        }
    });

    // Signup
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('signup-name').value.trim();
        const email = document.getElementById('signup-email').value.trim();
        const password = document.getElementById('signup-password').value;
        const btn = document.getElementById('signup-btn');

        if (!name || !email || !password) {
            showToast('Please fill in all fields', 'error');
            return;
        }

        btn.disabled = true;
        btn.textContent = 'Creating account...';

        try {
            await BookTracker.api.register(name, email, password);

            // Auto-login
            const loginResponse = await BookTracker.api.login(email, password);
            localStorage.setItem('book_tracker_token', loginResponse.access_token);
            localStorage.setItem('book_tracker_user', JSON.stringify(loginResponse.user));

            showToast('Account created!', 'success');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 500);
        } catch (error) {
            showToast(error.message || 'Registration failed', 'error');
            btn.disabled = false;
            btn.textContent = 'Create Account';
        }
    });
}

// ============================================
// Toast Helper
// ============================================
function showToast(message, type = 'default') {
    if (window.BookTracker?.showToast) {
        window.BookTracker.showToast(message, type);
        return;
    }

    // Fallback
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${message}</span><span class="toast-close" onclick="this.parentElement.remove()">✕</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}