/**
 * BookTracker - Profile Page JavaScript
 * Loads and displays user stats and reading sessions
 */

document.addEventListener('DOMContentLoaded', async () => {
    // Check auth
    if (!BookTracker.requireAuth()) return;

    // Load user info
    await loadUserInfo();

    // Load reading stats
    await loadReadingStats();

    // Load recent sessions
    await loadRecentSessions();

    // Setup logout
    document.getElementById('logout-btn').onclick = () => BookTracker.logout();
});

async function loadUserInfo() {
    try {
        const user = await BookTracker.api.getCurrentUser();

        // Update display
        document.getElementById('user-name').textContent = user.name || 'Reader';
        document.getElementById('user-email').textContent = user.email;
        document.getElementById('user-avatar').textContent = (user.name?.charAt(0) || '?').toUpperCase();
        document.getElementById('stat-streak').textContent = user.current_streak || 0;

        // Format join date
        if (user.created_at) {
            const joinDate = new Date(user.created_at);
            document.getElementById('user-since').textContent = joinDate.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long'
            });
        }

        // Update localStorage
        localStorage.setItem('book_tracker_user', JSON.stringify(user));
    } catch (error) {
        console.error('Failed to load user info:', error);
        // Use cached data
        const cached = BookTracker.getUser();
        if (cached) {
            document.getElementById('user-name').textContent = cached.name || 'Reader';
            document.getElementById('user-email').textContent = cached.email || '';
            document.getElementById('user-avatar').textContent = (cached.name?.charAt(0) || '?').toUpperCase();
        }
    }
}

async function loadReadingStats() {
    try {
        const stats = await BookTracker.api.getReadingStats('week');

        // Update stats if available
        if (stats.total_sessions !== undefined) {
            document.getElementById('stat-sessions').textContent = stats.total_sessions;
        }

        if (stats.total_duration_minutes !== undefined) {
            const hours = Math.floor(stats.total_duration_minutes / 60);
            const mins = stats.total_duration_minutes % 60;
            document.getElementById('stat-hours').textContent = hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
        }

        // Get marked books count as "books read"
        const markedBooks = await BookTracker.api.getMyMarkedBooks({ limit: 100 });
        document.getElementById('stat-books').textContent = markedBooks.length;

    } catch (error) {
        console.error('Failed to load reading stats:', error);
    }
}

async function loadRecentSessions() {
    const container = document.getElementById('sessions-list');

    try {
        const sessions = await BookTracker.api.getMyReadingSessions({ limit: 10 });

        if (!sessions || sessions.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p style="font-size: 2rem; margin-bottom: 12px;">📚</p>
                    <p>No reading sessions yet.</p>
                    <p style="margin-top: 8px;"><a href="dashboard.html" style="color: var(--primary-red);">Browse books to start reading!</a></p>
                </div>
            `;
            return;
        }

        container.innerHTML = '';

        for (const session of sessions) {
            // Fetch book info
            let book = { title: 'Unknown Book', author_name: 'Unknown Author', cover_url: null };
            try {
                book = await BookTracker.api.getBook(session.book_id);
            } catch (e) {
                console.warn('Could not fetch book:', session.book_id);
            }

            // Calculate duration
            let duration = '-';
            if (session.start_time && session.end_time) {
                const start = new Date(session.start_time);
                const end = new Date(session.end_time);
                const mins = Math.round((end - start) / 60000);
                duration = mins >= 60 ? `${Math.floor(mins / 60)}h ${mins % 60}m` : `${mins}m`;
            }

            // Format date
            const sessionDate = new Date(session.start_time);
            const dateStr = sessionDate.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });

            const coverUrl = BookTracker.getBookCoverUrl(book.cover_url);

            const sessionEl = document.createElement('div');
            sessionEl.className = 'session-item';
            sessionEl.innerHTML = `
                <img src="${coverUrl}" alt="${book.title}" class="session-book-cover" onerror="this.src='https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=100'">
                <div class="session-info">
                    <h4>${book.title}</h4>
                    <p>${book.author_name} • ${dateStr}</p>
                </div>
                <span class="session-duration">${duration}</span>
            `;
            container.appendChild(sessionEl);
        }

    } catch (error) {
        console.error('Failed to load sessions:', error);
        container.innerHTML = `
            <div class="empty-state">
                <p>Failed to load sessions. Please try again.</p>
            </div>
        `;
    }
}
