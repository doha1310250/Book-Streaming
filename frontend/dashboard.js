/**
 * Dashboard Page JavaScript
 */

// Check authentication on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    initDashboard();
});

function checkAuth() {
    const token = localStorage.getItem('book_streaming_token');
    const user = localStorage.getItem('book_streaming_user');

    if (!token || !user) {
        // Redirect to home page if not authenticated
        window.location.href = 'index.html';
        return;
    }

    // Update UI with user info
    try {
        const userData = JSON.parse(user);
        updateUserInfo(userData);
    } catch (e) {
        // Invalid user data
        localStorage.removeItem('book_streaming_token');
        window.location.href = 'index.html';
    }
}

function updateUserInfo(user) {
    const welcomeName = document.getElementById('welcome-name');
    const userName = document.getElementById('user-name');
    const userAvatar = document.getElementById('user-avatar');
    const currentStreak = document.getElementById('current-streak');

    if (welcomeName) welcomeName.textContent = user.name.split(' ')[0];
    if (userName) userName.textContent = user.name;
    if (userAvatar) userAvatar.textContent = user.name.charAt(0).toUpperCase();
    if (currentStreak) currentStreak.textContent = user.current_streak || 0;
}

function initDashboard() {
    initSidebar();
    initLogout();
    loadDashboardData();
}

function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('sidebar-toggle');

    toggle?.addEventListener('click', () => {
        sidebar?.classList.toggle('active');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 1024) {
            if (!sidebar?.contains(e.target) && !toggle?.contains(e.target)) {
                sidebar?.classList.remove('active');
            }
        }
    });
}

function initLogout() {
    const logoutBtn = document.getElementById('logout-btn');

    logoutBtn?.addEventListener('click', () => {
        localStorage.removeItem('book_streaming_token');
        localStorage.removeItem('book_streaming_user');
        window.location.href = 'index.html';
    });
}

async function loadDashboardData() {
    // Load all data in parallel
    await Promise.allSettled([
        loadStats(),
        loadMarkedBooks(),
        loadReadingActivity(),
        loadFollowingActivity()
    ]);
}

async function loadStats() {
    try {
        const user = await BookStreaming.api.getCurrentUser();
        updateUserInfo(user); // Refresh user info/streak

        // Update local storage with fresh user data
        localStorage.setItem('book_streaming_user', JSON.stringify(user));

        // Note: The stats-grid currently shows placeholders or requires additional endpoints
        // For example, total reviews can be fetched:
        // const reviews = await BookStreaming.api.getMyReviews({ limit: 0 }); // Just for count
        // document.getElementById('total-reviews').textContent = reviews.length; 

        // For now we keep placeholders or implement specific count endpoints if prioritized
    } catch (error) {
        console.error('Failed to load stats:', error);
        BookStreaming.showToast('Failed to refresh user stats', 'error');
    }
}

async function loadMarkedBooks() {
    try {
        const markedBooks = await BookStreaming.api.getMyMarkedBooks({ limit: 5 });
        renderBookmarkedBooks(markedBooks);
    } catch (error) {
        console.error('Failed to load marked books:', error);
        const container = document.getElementById('bookmarked-list');
        if (container) container.innerHTML = '<div class="empty-state" style="padding: 1rem; text-align: center; color: var(--gray-500);">Could not load marked books</div>';
    }
}

async function loadReadingActivity() {
    const period = document.getElementById('activity-period')?.value || 'week';

    try {
        const data = await BookStreaming.api.getReadingStats(period);
        renderActivityChart(data);
    } catch (error) {
        console.error('Failed to load activity:', error);
    }
}

async function loadFollowingActivity() {
    try {
        const activities = await BookStreaming.api.getFollowingActivity({ limit: 10 });
        renderActivityList(activities);
    } catch (error) {
        console.error('Failed to load following activity:', error);
        const list = document.getElementById('activity-list');
        if (list) list.innerHTML = '<div class="empty-state" style="padding: 1rem; text-align: center; color: var(--gray-500);">Could not load activity</div>';
    }
}

function renderActivityList(activities) {
    const list = document.getElementById('activity-list');
    if (!list) return;

    if (!activities || activities.length === 0) {
        list.innerHTML = '<div class="empty-state" style="padding: 2rem; text-align: center; color: var(--gray-500);">Follow users to see their activity here!</div>';
        return;
    }

    list.innerHTML = activities.map(activity => {
        let text = '';
        let icon = '';
        const user = activity.user_name || 'Someone';
        const title = activity.title;

        if (activity.activity_type === 'book_added') {
            icon = '📚';
            text = `<strong>${user}</strong> added <strong>${title}</strong> to their library`;
        } else if (activity.activity_type === 'review_added') {
            icon = '✍️';
            text = `<strong>${user}</strong> reviewed <strong>${title}</strong>`;
        } else if (activity.activity_type === 'reading_session') {
            icon = '📖';
            const duration = activity.duration_min ? `${activity.duration_min} mins` : 'just now';
            text = `<strong>${user}</strong> read <strong>${title}</strong> for ${duration}`;
        }

        return `
            <div class="activity-item">
                <div class="activity-icon">${icon}</div>
                <div class="activity-content">
                    <p>${text}</p>
                    <small class="activity-time">${new Date(activity.activity_time).toLocaleString()}</small>
                </div>
            </div>
        `;
    }).join('');
}

function renderBookmarkedBooks(books) {
    const container = document.getElementById('bookmarked-list');
    if (!container) return;

    if (books.length === 0) {
        container.innerHTML = '<div class="empty-state" style="padding: 1rem; text-align: center; color: var(--gray-500);">No books marked yet</div>';
        return;
    }

    container.innerHTML = books.map(book => `
        <div class="mini-book-card" onclick="window.location.href='index.html#books'">
            <div class="mini-book-cover" style="${book.cover_url ? `background-image: url(http://localhost:8000${book.cover_url}); background-size: cover;` : ''}"></div>
            <div class="mini-book-info">
                <span class="mini-book-title">${book.title}</span>
                <span class="mini-book-author">${book.author_name}</span>
            </div>
        </div>
    `).join('');
}

function renderActivityChart(data) {
    // Update chart bars based on data
    const bars = document.querySelectorAll('.chart-bar');
    if (!data.daily_stats) return;

    bars.forEach((bar, index) => {
        const dayData = data.daily_stats[index];
        if (dayData) {
            const maxMinutes = 120; // 2 hours max reference
            const percentage = Math.min((dayData.minutes / maxMinutes) * 100, 100);
            bar.style.setProperty('--height', `${percentage}%`);
            // Add tooltip or label if needed
        }
    });
}

// Period change handler
document.getElementById('activity-period')?.addEventListener('change', () => {
    loadReadingActivity();
});
