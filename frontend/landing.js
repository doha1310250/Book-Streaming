/**
 * BookTracker - Landing Page JavaScript
 * Animated counters, parallax, and interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initMobileMenu();
    initAnimatedCounters();
    initParallax();
});

// ============================================
// Navbar Scroll Effect
// ============================================
function initNavbar() {
    const navbar = document.getElementById('navbar');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        lastScroll = currentScroll;
    });
}

// ============================================
// Mobile Menu Toggle
// ============================================
function initMobileMenu() {
    const toggle = document.getElementById('nav-toggle');
    const menu = document.getElementById('mobile-menu');

    toggle?.addEventListener('click', () => {
        menu.classList.toggle('active');
        toggle.classList.toggle('active');
    });

    // Close menu when clicking a link
    document.querySelectorAll('.mobile-link').forEach(link => {
        link.addEventListener('click', () => {
            menu.classList.remove('active');
            toggle.classList.remove('active');
        });
    });
}

// ============================================
// Animated Counters
// ============================================
function initAnimatedCounters() {
    const counters = document.querySelectorAll('.metric-value');

    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    counters.forEach(counter => observer.observe(counter));
}

function animateCounter(element) {
    const target = parseInt(element.dataset.target) || 0;
    const prefix = element.dataset.prefix || '';
    const duration = 2000;
    const start = performance.now();

    // Format number for display
    function formatNumber(num) {
        if (num >= 1000000000) {
            return (num / 1000000000).toFixed(1) + 'B';
        }
        if (num >= 1000000) {
            return (num / 1000000).toFixed(0) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(0) + 'K';
        }
        return num.toString();
    }

    function easeOutQuart(t) {
        return 1 - Math.pow(1 - t, 4);
    }

    function update(currentTime) {
        const elapsed = currentTime - start;
        const progress = Math.min(elapsed / duration, 1);
        const easedProgress = easeOutQuart(progress);
        const currentValue = Math.floor(easedProgress * target);

        element.textContent = prefix + formatNumber(currentValue);

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = prefix + formatNumber(target);
        }
    }

    requestAnimationFrame(update);
}

// ============================================
// Parallax Effect for Hero Cards
// ============================================
function initParallax() {
    const heroVisual = document.querySelector('.hero-visual');
    const cards = document.querySelectorAll('.hero-card');

    if (!heroVisual || cards.length === 0) return;

    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const rate = scrolled * 0.15;

        cards.forEach((card, index) => {
            const direction = index % 2 === 0 ? 1 : -1;
            const offset = rate * direction * (0.5 + index * 0.2);
            card.style.transform = `translateY(${offset}px)`;
        });
    });

    // Mouse parallax
    heroVisual.addEventListener('mousemove', (e) => {
        const rect = heroVisual.getBoundingClientRect();
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const mouseX = e.clientX - rect.left - centerX;
        const mouseY = e.clientY - rect.top - centerY;

        cards.forEach((card, index) => {
            const factor = 0.02 * (index + 1);
            const x = mouseX * factor;
            const y = mouseY * factor;
            card.style.transform = `translate(${x}px, ${y}px)`;
        });
    });

    heroVisual.addEventListener('mouseleave', () => {
        cards.forEach(card => {
            card.style.transform = 'translate(0, 0)';
        });
    });
}

// ============================================
// Smooth scroll for anchor links
// ============================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});