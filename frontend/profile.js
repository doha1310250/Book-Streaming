/**
 * BookTracker - Profile Page JavaScript
 * Fortune 500 Edition
 */

document.addEventListener('DOMContentLoaded', async () => {
    if (!BookTracker.requireAuth()) return;

    initMobileMenu();
    await loadUserInfo();
    await loadStats();
    await loadStreakCalendar();
    await loadRecentSessions();

    document.getElementById('logout-btn').onclick = () => BookTracker.logout();
});

function initMobileMenu() {
    const btn = document.getElementById('mobile-menu-btn');
    const sidebar = document.getElementById('sidebar');

    btn?.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });
}

async function loadUserInfo() {
    try {
        const user = await BookTracker.api.getCurrentUser();

        // Update sidebar
        document.getElementById('sidebar-user-name').textContent = user.name || 'Reader';
        document.getElementById('sidebar-user-email').textContent = user.email || '';
        document.getElementById('user-avatar').textContent = (user.name?.charAt(0) || '?').toUpperCase();

        // Update profile card
        document.getElementById('profile-name').textContent = user.name || 'Reader';
        document.getElementById('profile-email').textContent = user.email || '';
        document.getElementById('profile-avatar').textContent = (user.name?.charAt(0) || '?').toUpperCase();

        // Streak
        document.getElementById('stat-streak').textContent = user.current_streak || 0;

        // Join date
        if (user.created_at) {
            const date = new Date(user.created_at);
            document.getElementById('profile-joined').textContent = date.toLocaleDateString('en-US', {
                month: 'long',
                year: 'numeric'
            });
        }

        localStorage.setItem('book_tracker_user', JSON.stringify(user));
    } catch (error) {
        console.error('Failed to load user:', error);
        const cached = BookTracker.getUser();
        if (cached) {
            document.getElementById('profile-name').textContent = cached.name || 'Reader';
            document.getElementById('profile-email').textContent = cached.email || '';
        }
    }
}

async function loadStats() {
    try {
        // Get marked books
        const marked = await BookTracker.api.getMyMarkedBooks({ limit: 100 });
        document.getElementById('stat-books').textContent = marked.length;

        // Get reading stats
        const stats = await BookTracker.api.getReadingStats('week');
        if (stats.total_sessions !== undefined) {
            document.getElementById('stat-sessions').textContent = stats.total_sessions;
        }
        if (stats.total_minutes !== undefined) {
            const hours = Math.floor(stats.total_minutes / 60);
            const mins = stats.total_minutes % 60;
            document.getElementById('stat-hours').textContent = hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

async function loadStreakCalendar() {
    const container = document.getElementById('streak-calendar');
    if (!container) return;

    try {
        // Get reading sessions for the past 84 days (12 weeks)
        const sessions = await BookTracker.api.getMyReadingSessions({ limit: 100 });

        // Create a map of dates to reading minutes
        const readingByDate = {};
        sessions.forEach(session => {
            if (session.start_time) {
                const date = new Date(session.start_time).toISOString().split('T')[0];
                const duration = session.duration_min || 0;
                readingByDate[date] = (readingByDate[date] || 0) + duration;
            }
        });

        // Generate 84 days (12 weeks)
        container.innerHTML = '';
        const today = new Date();

        for (let i = 83; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            const dateStr = date.toISOString().split('T')[0];
            const minutes = readingByDate[dateStr] || 0;

            // Calculate level based on reading time
            let level = 0;
            if (minutes > 0 && minutes < 15) level = 1;
            else if (minutes >= 15 && minutes < 30) level = 2;
            else if (minutes >= 30 && minutes < 60) level = 3;
            else if (minutes >= 60) level = 4;

            const day = document.createElement('div');
            day.className = `streak-day level-${level}`;
            day.setAttribute('data-tooltip', `${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}: ${minutes > 0 ? minutes + ' min' : 'No reading'}`);
            container.appendChild(day);
        }
    } catch (error) {
        console.error('Failed to load streak calendar:', error);
        container.innerHTML = '<div class="empty-state"><p>Could not load activity</p></div>';
    }
}

async function loadRecentSessions() {
    const container = document.getElementById('sessions-list');

    try {
        const sessions = await BookTracker.api.getMyReadingSessions({ limit: 10 });

        if (!sessions || sessions.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>No reading sessions yet.</p>
                    <a href="dashboard.html" style="color: var(--color-accent);">Start reading!</a>
                </div>
            `;
            return;
        }

        container.innerHTML = '';

        for (const session of sessions) {
            let book = { title: 'Unknown Book', author_name: 'Unknown', cover_url: null };
            try {
                book = await BookTracker.api.getBook(session.book_id);
            } catch (e) {
                console.warn('Could not fetch book:', session.book_id);
            }

            // Duration
            let duration = '-';
            if (session.start_time && session.end_time) {
                const totalSeconds = Math.round((new Date(session.end_time) - new Date(session.start_time)) / 1000);
                const mins = Math.floor(totalSeconds / 60);
                const secs = totalSeconds % 60;
                if (mins >= 60) {
                    duration = `${Math.floor(mins / 60)}h ${mins % 60}m`;
                } else if (mins > 0) {
                    duration = `${mins}m`;
                } else {
                    duration = `${secs}s`;
                }
            }

            // Date
            const date = new Date(session.start_time);
            const dateStr = date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });

            const coverUrl = BookTracker.getBookCoverUrl(book.cover_url);

            const item = document.createElement('div');
            item.className = 'session-item';
            item.innerHTML = `
                <div class="session-cover">
                    <img src="${coverUrl}" alt="${book.title}" onerror="this.src='https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=100'">
                </div>
                <div class="session-info">
                    <div class="session-title">${book.title}</div>
                    <div class="session-meta">${book.author_name} • ${dateStr}</div>
                </div>
                <div class="session-duration">${duration}</div>
            `;
            container.appendChild(item);
        }
    } catch (error) {
        console.error('Failed to load sessions:', error);
        container.innerHTML = `
            <div class="empty-state">
                <p>Failed to load sessions.</p>
            </div>
        `;
    }
}
