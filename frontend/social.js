/**
 * BookTracker - Social Page JavaScript
 * Fortune 500 Edition
 */

document.addEventListener('DOMContentLoaded', async () => {
    if (!BookTracker.requireAuth()) return;

    initUserInfo();
    initTabs();
    initMobileMenu();

    await loadSocialStats();
    await loadActivityFeed();
    await loadFollowing();
    await loadFollowers();

    document.getElementById('logout-btn').onclick = () => BookTracker.logout();
});

function initUserInfo() {
    const user = BookTracker.getUser();
    if (user) {
        document.getElementById('user-name').textContent = user.name || 'Reader';
        document.getElementById('user-email').textContent = user.email || '';
        document.getElementById('user-avatar').textContent = (user.name?.charAt(0) || '?').toUpperCase();
    }
}

function initMobileMenu() {
    const btn = document.getElementById('mobile-menu-btn');
    const sidebar = document.getElementById('sidebar');

    btn?.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });
}

function initTabs() {
    const tabs = document.querySelectorAll('.user-tab');
    const followingList = document.getElementById('following-list');
    const followersList = document.getElementById('followers-list');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            if (tab.dataset.tab === 'following') {
                followingList.classList.remove('hidden');
                followersList.classList.add('hidden');
            } else {
                followingList.classList.add('hidden');
                followersList.classList.remove('hidden');
            }
        });
    });
}

// ============================================
// Load Data
// ============================================
async function loadSocialStats() {
    try {
        const [following, followers] = await Promise.all([
            BookTracker.api.getFollowing({ limit: 100 }),
            BookTracker.api.getFollowers({ limit: 100 })
        ]);

        document.getElementById('following-count').textContent = following.total || following.following?.length || 0;
        document.getElementById('followers-count').textContent = followers.total || followers.followers?.length || 0;
    } catch (error) {
        console.error('Failed to load social stats:', error);
    }
}

async function loadActivityFeed() {
    const container = document.getElementById('activity-feed');

    try {
        const activities = await BookTracker.api.getFollowingActivity({ limit: 20 });

        if (!activities || activities.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📰</div>
                    <p>No activity yet. Follow some readers to see their updates!</p>
                </div>
            `;
            return;
        }

        container.innerHTML = '';

        activities.forEach(activity => {
            const coverUrl = BookTracker.getBookCoverUrl(activity.cover_url);
            const userName = activity.user_name || activity.name || 'A reader';
            const initial = userName.charAt(0).toUpperCase();
            const timeAgo = formatTimeAgo(activity.created_at);

            const item = document.createElement('div');
            item.className = 'feed-item';
            item.innerHTML = `
                <div class="feed-avatar">${initial}</div>
                <div class="feed-content">
                    <p>
                        <span class="feed-user">${userName}</span>
                        <span class="feed-action">added a new book</span>
                    </p>
                    <div class="feed-book">
                        <div class="feed-book-cover">
                            <img src="${coverUrl}" alt="${activity.title}" onerror="this.src='https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=100'">
                        </div>
                        <div class="feed-book-info">
                            <div class="feed-book-title">${activity.title}</div>
                            <div class="feed-book-author">${activity.author_name}</div>
                        </div>
                    </div>
                    <div class="feed-time">${timeAgo}</div>
                </div>
            `;
            container.appendChild(item);
        });
    } catch (error) {
        console.error('Failed to load activity feed:', error);
        container.innerHTML = `
            <div class="empty-state">
                <p>Failed to load activity feed.</p>
            </div>
        `;
    }
}

async function loadFollowing() {
    const container = document.getElementById('following-list');

    try {
        const response = await BookTracker.api.getFollowing({ limit: 50 });
        const users = response.following || [];

        if (users.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>You're not following anyone yet.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = '';

        users.forEach(user => {
            const initial = (user.name?.charAt(0) || user.email?.charAt(0) || '?').toUpperCase();
            const item = document.createElement('div');
            item.className = 'user-item';
            item.innerHTML = `
                <a href="user-profile.html?id=${user.user_id}" class="user-item-avatar clickable">${initial}</a>
                <a href="user-profile.html?id=${user.user_id}" class="user-item-info clickable">
                    <div class="user-item-name">${user.name || 'Unnamed'}</div>
                    <div class="user-item-email">${user.email || ''}</div>
                </a>
                <button class="btn btn-secondary btn-follow btn-unfollow" data-user-id="${user.user_id}">
                    Unfollow
                </button>
            `;
            container.appendChild(item);
        });

        // Add unfollow handlers
        container.querySelectorAll('.btn-unfollow').forEach(btn => {
            btn.addEventListener('click', async () => {
                const userId = btn.dataset.userId;
                try {
                    btn.disabled = true;
                    btn.textContent = '...';
                    await BookTracker.api.unfollowUser(userId);
                    btn.closest('.user-item').remove();
                    BookTracker.showToast('Unfollowed', 'default');
                    await loadSocialStats();
                } catch (error) {
                    BookTracker.showToast(error.message || 'Failed to unfollow', 'error');
                    btn.disabled = false;
                    btn.textContent = 'Unfollow';
                }
            });
        });
    } catch (error) {
        console.error('Failed to load following:', error);
        container.innerHTML = `
            <div class="empty-state">
                <p>Failed to load following list.</p>
            </div>
        `;
    }
}

async function loadFollowers() {
    const container = document.getElementById('followers-list');

    try {
        const response = await BookTracker.api.getFollowers({ limit: 50 });
        const users = response.followers || [];

        if (users.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>No followers yet. Keep reading!</p>
                </div>
            `;
            return;
        }

        container.innerHTML = '';

        // Get my following to check if I follow back
        const followingResponse = await BookTracker.api.getFollowing({ limit: 100 });
        const followingIds = new Set((followingResponse.following || []).map(u => u.user_id));

        users.forEach(user => {
            const initial = (user.name?.charAt(0) || user.email?.charAt(0) || '?').toUpperCase();
            const isFollowing = followingIds.has(user.user_id);

            const item = document.createElement('div');
            item.className = 'user-item';
            item.innerHTML = `
                <a href="user-profile.html?id=${user.user_id}" class="user-item-avatar clickable">${initial}</a>
                <a href="user-profile.html?id=${user.user_id}" class="user-item-info clickable">
                    <div class="user-item-name">${user.name || 'Unnamed'}</div>
                    <div class="user-item-email">${user.email || ''}</div>
                </a>
                ${isFollowing
                    ? `<button class="btn btn-secondary btn-follow btn-unfollow" data-user-id="${user.user_id}">Following</button>`
                    : `<button class="btn btn-primary btn-follow" data-user-id="${user.user_id}">Follow</button>`
                }
            `;
            container.appendChild(item);
        });

        // Add follow/unfollow handlers
        container.querySelectorAll('.btn-follow').forEach(btn => {
            btn.addEventListener('click', async () => {
                const userId = btn.dataset.userId;
                const isUnfollow = btn.classList.contains('btn-unfollow');

                try {
                    btn.disabled = true;
                    btn.textContent = '...';

                    if (isUnfollow) {
                        await BookTracker.api.unfollowUser(userId);
                        btn.classList.remove('btn-unfollow', 'btn-secondary');
                        btn.classList.add('btn-primary');
                        btn.textContent = 'Follow';
                        BookTracker.showToast('Unfollowed', 'default');
                    } else {
                        await BookTracker.api.followUser(userId);
                        btn.classList.add('btn-unfollow', 'btn-secondary');
                        btn.classList.remove('btn-primary');
                        btn.textContent = 'Following';
                        BookTracker.showToast('Following!', 'success');
                    }

                    btn.disabled = false;
                    await loadSocialStats();
                } catch (error) {
                    BookTracker.showToast(error.message || 'Action failed', 'error');
                    btn.disabled = false;
                    btn.textContent = isUnfollow ? 'Following' : 'Follow';
                }
            });
        });
    } catch (error) {
        console.error('Failed to load followers:', error);
        container.innerHTML = `
            <div class="empty-state">
                <p>Failed to load followers list.</p>
            </div>
        `;
    }
}

// ============================================
// Utilities
// ============================================
function formatTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;

    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}
