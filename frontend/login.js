/**
 * BookTracker - Login Page JavaScript
 * Handles login/signup form submission with API integration
 */

document.addEventListener('DOMContentLoaded', () => {
    // Check if already logged in
    if (localStorage.getItem('book_tracker_token')) {
        window.location.href = 'dashboard.html';
        return;
    }

    const authTitle = document.getElementById('auth-title');
    const authSubtitle = document.getElementById('auth-subtitle');
    const nameGroup = document.getElementById('name-group');
    const submitBtn = document.getElementById('submit-btn');
    const toggleWrapper = document.getElementById('toggle-wrapper');
    const authForm = document.getElementById('auth-form');

    // Get form inputs
    const emailInput = authForm.querySelector('input[type="email"]');
    const passwordInput = authForm.querySelector('input[type="password"]');
    const nameInput = document.getElementById('user-fullname');

    let isLogin = true;

    // Toggle between login and signup
    toggleWrapper.addEventListener('click', (e) => {
        if (e.target.id === 'toggle-auth') {
            e.preventDefault();
            isLogin = !isLogin;

            if (isLogin) {
                authTitle.textContent = "Welcome Back";
                authSubtitle.textContent = "Log in to continue your reading journey.";
                nameGroup.classList.add('hidden');
                submitBtn.textContent = "Continue";
                toggleWrapper.innerHTML = `New here? <a href="#" id="toggle-auth">Create Account</a>`;
            } else {
                authTitle.textContent = "Create Account";
                authSubtitle.textContent = "Join the community of cozy readers today.";
                nameGroup.classList.remove('hidden');
                submitBtn.textContent = "Create Account";
                toggleWrapper.innerHTML = `Already have an account? <a href="#" id="toggle-auth">Log In</a>`;
            }
        }
    });

    // Form submission
    authForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = emailInput.value.trim();
        const password = passwordInput.value;

        if (!email || !password) {
            showToast('Please fill in all fields', 'error');
            return;
        }

        // Disable button during request
        submitBtn.disabled = true;
        submitBtn.textContent = isLogin ? 'Signing in...' : 'Creating account...';

        try {
            if (isLogin) {
                // Login
                const response = await BookTracker.api.login(email, password);

                localStorage.setItem('book_tracker_token', response.access_token);
                localStorage.setItem('book_tracker_user', JSON.stringify(response.user));

                showToast('Welcome back! 👋', 'success');
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 500);
            } else {
                // Signup
                const name = nameInput.value.trim();
                if (!name) {
                    showToast('Please enter your name', 'error');
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Create Account';
                    return;
                }

                await BookTracker.api.register(name, email, password);

                // Auto-login after registration
                const loginResponse = await BookTracker.api.login(email, password);
                localStorage.setItem('book_tracker_token', loginResponse.access_token);
                localStorage.setItem('book_tracker_user', JSON.stringify(loginResponse.user));

                showToast('Account created! 🎉', 'success');
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 500);
            }
        } catch (error) {
            showToast(error.message || 'Something went wrong', 'error');
            submitBtn.disabled = false;
            submitBtn.textContent = isLogin ? 'Continue' : 'Create Account';
        }
    });

    // Simple toast function (fallback if app.js not loaded)
    function showToast(message, type = 'default') {
        if (window.BookTracker?.showToast) {
            window.BookTracker.showToast(message, type);
            return;
        }

        // Fallback toast
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed; bottom: 20px; right: 20px; padding: 16px 24px;
            background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#333'};
            color: white; border-radius: 8px; z-index: 9999; font-size: 14px;
        `;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }
});