/**
 * Landing Page Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    initButtons();
});

function initButtons() {
    // Select all signup/login triggers
    const authButtons = document.querySelectorAll('.btn-signup, #nav-login');

    authButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // For now, redirect to a hypothetical login page
            // Replace 'login.html' with your actual auth page name later
            redirectToAuth();
        });
    });
}

function redirectToAuth() {
    // In a functional app, this would point to your Login/Sign-up page
    console.log("Redirecting to Login/Sign-up...");
    
    // Smooth transition effect (optional)
    document.body.style.opacity = '0';
    setTimeout(() => {
        window.location.href = 'login.html'; 
    }, 300);
}

// Simple scroll effect for navbar
window.addEventListener('scroll', () => {
    const nav = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        nav.style.background = 'rgba(253, 250, 246, 0.95)';
        nav.style.backdropFilter = 'blur(10px)';
        nav.style.boxShadow = '0 2px 10px rgba(0,0,0,0.05)';
    } else {
        nav.style.background = 'transparent';
        nav.style.boxShadow = 'none';
    }
});