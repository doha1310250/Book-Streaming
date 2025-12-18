/**
 * BookTracker - User Profile Page JavaScript
 * View other users' profiles and reading sessions
 */

let currentUserId = null;
let isFollowing = false;

document.addEventListener('DOMContentLoaded', async () => {
    if (!BookTracker.requireAuth()) return;

    // Get user ID from URL
    const params = new URLSearchParams(window.location.search);
    currentUserId = params.get('id');

    if (!currentUserId) {
        BookTracker.showToast('No user specified', 'error');
        setTimeout(() => window.location.href = 'social.html', 1000);
        return;
    }

    await loadUserProfile();
    await loadFollowStatus();
    await loadStreakCalendar();
    await loadReadingSessions();

    initFollowButton();
});

async function loadUserProfile() {
    try {
        const profile = await BookTracker.api.getUserProfile(currentUserId);

        document.getElementById('user-name').textContent = profile.name || 'Unknown User';
        document.getElementById('user-email').textContent = profile.email || '';
        document.getElementById('user-avatar').textContent = (profile.name?.charAt(0) || '?').toUpperCase();

        // Stats
        document.getElementById('stat-streak').textContent = profile.current_streak || 0;
        document.getElementById('stat-books').textContent = profile.books_read || 0;
        document.getElementById('stat-sessions').textContent = profile.total_sessions || 0;
        document.getElementById('stat-followers').textContent = profile.followers_count || 0;
        document.getElementById('stat-following').textContent = profile.following_count || 0;

        // Total time
        const totalMinutes = profile.total_minutes || 0;
        const hours = Math.floor(totalMinutes / 60);
        const mins = totalMinutes % 60;
        document.getElementById('stat-time').textContent = hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;

        // Join date
        if (profile.created_at) {
            const date = new Date(profile.created_at);
            document.getElementById('user-joined').textContent = date.toLocaleDateString('en-US', {
                month: 'long',
                year: 'numeric'
            });
        }

        document.title = `${profile.name} | BookTracker`;
    } catch (error) {
        console.error('Failed to load profile:', error);
        BookTracker.showToast('Failed to load profile', 'error');
    }
}

async function loadFollowStatus() {
    try {
        const status = await BookTracker.api.getFollowStatus(currentUserId);
        isFollowing = status.is_following;
        updateFollowButton();
    } catch (error) {
        console.error('Failed to load follow status:', error);
    }
}

async function loadStreakCalendar() {
    const container = document.getElementById('streak-calendar');
    if (!container) return;

    try {
        // Get reading sessions for this user
        const sessions = await BookTracker.api.getUserReadingSessions(currentUserId, { limit: 100 });

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

async function loadReadingSessions() {
    const container = document.getElementById('sessions-list');

    try {
        const sessions = await BookTracker.api.getUserReadingSessions(currentUserId, { limit: 20 });

        if (!sessions || sessions.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>No reading sessions yet.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = '';

        sessions.forEach(session => {
            const coverUrl = BookTracker.getBookCoverUrl(session.cover_url);

            // Duration
            let duration = '-';
            if (session.duration_min && session.duration_min > 0) {
                const mins = session.duration_min;
                duration = mins >= 60 ? `${Math.floor(mins / 60)}h ${mins % 60}m` : `${mins}m`;
            } else if (session.start_time && session.end_time) {
                // Calculate seconds for very short sessions
                const totalSeconds = Math.round((new Date(session.end_time) - new Date(session.start_time)) / 1000);
                if (totalSeconds < 60) {
                    duration = `${totalSeconds}s`;
                } else {
                    duration = `${Math.floor(totalSeconds / 60)}m`;
                }
            }

            // Date
            const date = new Date(session.start_time);
            const dateStr = date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            });

            const item = document.createElement('div');
            item.className = 'session-item';
            item.innerHTML = `
                <div class="session-cover">
                    <img src="${coverUrl}" alt="${session.title}" onerror="this.src='https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=100'">
                </div>
                <div class="session-info">
                    <div class="session-title">${session.title}</div>
                    <div class="session-author">${session.author_name}</div>
                    <div class="session-time">${dateStr}</div>
                </div>
                <div class="session-duration">${duration}</div>
            `;
            container.appendChild(item);
        });
    } catch (error) {
        console.error('Failed to load sessions:', error);
        container.innerHTML = `
            <div class="empty-state">
                <p>Failed to load reading sessions.</p>
            </div>
        `;
    }
}

function initFollowButton() {
    const btn = document.getElementById('follow-btn');

    btn.addEventListener('click', async () => {
        btn.disabled = true;
        btn.textContent = '...';

        try {
            if (isFollowing) {
                await BookTracker.api.unfollowUser(currentUserId);
                isFollowing = false;
                BookTracker.showToast('Unfollowed', 'default');
            } else {
                await BookTracker.api.followUser(currentUserId);
                isFollowing = true;
                BookTracker.showToast('Following!', 'success');
            }

            updateFollowButton();
            await loadUserProfile(); // Refresh follower count
        } catch (error) {
            BookTracker.showToast(error.message || 'Action failed', 'error');
        }

        btn.disabled = false;
    });
}

function updateFollowButton() {
    const btn = document.getElementById('follow-btn');

    if (isFollowing) {
        btn.textContent = 'Following';
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-secondary', 'btn-following');
    } else {
        btn.textContent = 'Follow';
        btn.classList.add('btn-primary');
        btn.classList.remove('btn-secondary', 'btn-following');
    }
}
