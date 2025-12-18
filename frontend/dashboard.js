/**
 * BookTracker - Dashboard Page JavaScript
 * Loads and displays books from API with filtering and favorites
 */

// State
let libraryBooks = [];
let markedBookIds = new Set();
let currentActiveBookId = null;
let currentFilter = 'all';

// DOM Elements
const bookGrid = document.getElementById('book-grid');
const bookModal = document.getElementById('book-modal');
const favBtn = document.getElementById('modal-fav-btn');
const searchInput = document.getElementById('book-search');
const categoryTitle = document.getElementById('current-category');

// ============================================
// Initialize Dashboard
// ============================================
document.addEventListener('DOMContentLoaded', async () => {
    // Check auth
    if (!BookTracker.requireAuth()) return;

    // Update user info
    const user = BookTracker.getUser();
    if (user) {
        document.getElementById('user-name').textContent = user.name?.split(' ')[0] || 'Reader';

        // Update streak if available
        const streakEl = document.querySelector('.stat-value');
        if (streakEl && user.current_streak !== undefined) {
            streakEl.textContent = `🔥 ${user.current_streak} Days`;
        }
    }

    // Load books
    await loadBooks();
    await loadMarkedBooks();

    // Setup event listeners
    setupNavigation();
    setupSearch();
    setupModal();
    setupLogout();
});

// ============================================
// Load Books from API
// ============================================
async function loadBooks() {
    try {
        showBookSkeleton();
        const params = {};

        if (currentFilter === 'verified') {
            params.verified = true;
        }

        libraryBooks = await BookTracker.api.getBooks(params);
        renderBooks();
    } catch (error) {
        console.error('Failed to load books:', error);
        showEmptyState('Failed to load books. Please try again.');
    }
}

async function loadMarkedBooks() {
    try {
        const marked = await BookTracker.api.getMyMarkedBooks();
        markedBookIds = new Set(marked.map(b => b.book_id));
        renderBooks(); // Re-render with favorites
    } catch (error) {
        console.error('Failed to load marked books:', error);
    }
}

// ============================================
// Render Books
// ============================================
function renderBooks() {
    bookGrid.innerHTML = '';

    let filteredBooks = [...libraryBooks];

    // Apply filter
    if (currentFilter === 'favorites') {
        filteredBooks = filteredBooks.filter(book => markedBookIds.has(book.book_id));
    } else if (currentFilter === 'verified') {
        filteredBooks = filteredBooks.filter(book => book.is_verified);
    }

    // Apply search
    const searchTerm = searchInput?.value?.toLowerCase() || '';
    if (searchTerm) {
        filteredBooks = filteredBooks.filter(book =>
            book.title.toLowerCase().includes(searchTerm) ||
            book.author_name.toLowerCase().includes(searchTerm)
        );
    }

    if (filteredBooks.length === 0) {
        showEmptyState(currentFilter === 'favorites'
            ? 'No favorite books yet. Click ❤️ on books to add them!'
            : 'No books found.'
        );
        return;
    }

    filteredBooks.forEach(book => {
        const isFavorite = markedBookIds.has(book.book_id);
        const coverUrl = BookTracker.getBookCoverUrl(book.cover_url);

        const bookEl = document.createElement('div');
        bookEl.className = 'book-item';
        bookEl.innerHTML = `
            <div class="book-card-inner">
                <img src="${coverUrl}" alt="${book.title}" onerror="this.src='https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=400'">
                ${isFavorite ? '<span class="fav-icon">❤️</span>' : ''}
                ${book.is_verified ? '<span class="verified-badge">✓</span>' : ''}
                <h3>${book.title}</h3>
                <p>${book.author_name}</p>
            </div>
        `;
        bookEl.onclick = () => openBookDetails(book);
        bookGrid.appendChild(bookEl);
    });
}

function showBookSkeleton() {
    bookGrid.innerHTML = '';
    for (let i = 0; i < 4; i++) {
        const skeleton = document.createElement('div');
        skeleton.className = 'book-item skeleton';
        skeleton.innerHTML = `
            <div class="skeleton-cover"></div>
            <div class="skeleton-text"></div>
            <div class="skeleton-text short"></div>
        `;
        bookGrid.appendChild(skeleton);
    }
}

function showEmptyState(message) {
    bookGrid.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: var(--text-muted);">
            <p style="font-size: 3rem; margin-bottom: 16px;">📚</p>
            <p>${message}</p>
        </div>
    `;
}

// ============================================
// Modal Logic
// ============================================
function openBookDetails(book) {
    currentActiveBookId = book.book_id;
    const isFavorite = markedBookIds.has(book.book_id);
    const coverUrl = BookTracker.getBookCoverUrl(book.cover_url);

    document.getElementById('modal-title').textContent = book.title;
    document.getElementById('modal-author').textContent = book.author_name;
    document.getElementById('modal-cover').src = coverUrl;
    document.getElementById('modal-badge').textContent = book.is_verified ? 'VERIFIED' : 'COMMUNITY';
    document.getElementById('modal-badge').style.background = book.is_verified ? '#10b981' : '#6b5b5b';

    favBtn.textContent = isFavorite ? "Remove from Favorites" : "Add to Favorites";
    favBtn.dataset.isFavorite = isFavorite;

    // Store book for timer page
    localStorage.setItem('book_tracker_current_book', JSON.stringify(book));

    bookModal.classList.remove('hidden');
}

function setupModal() {
    // Close modal
    document.getElementById('close-modal').onclick = () => {
        bookModal.classList.add('hidden');
    };

    // Favorite button
    favBtn.addEventListener('click', async () => {
        if (!currentActiveBookId) return;

        const isFavorite = favBtn.dataset.isFavorite === 'true';

        try {
            if (isFavorite) {
                await BookTracker.api.unmarkBook(currentActiveBookId);
                markedBookIds.delete(currentActiveBookId);
                favBtn.textContent = "Add to Favorites";
                favBtn.dataset.isFavorite = 'false';
                BookTracker.showToast('Removed from favorites', 'default');
            } else {
                await BookTracker.api.markBook(currentActiveBookId);
                markedBookIds.add(currentActiveBookId);
                favBtn.textContent = "Remove from Favorites";
                favBtn.dataset.isFavorite = 'true';
                BookTracker.showToast('Added to favorites! ❤️', 'success');
            }
            renderBooks();
        } catch (error) {
            BookTracker.showToast(error.message || 'Failed to update', 'error');
        }
    });

    // Continue reading button - navigate to timer
    const continueBtn = document.querySelector('.btn-main[onclick*="timer"]');
    if (continueBtn) {
        continueBtn.onclick = () => {
            window.location.href = 'timer.html';
        };
    }
}

// ============================================
// Navigation & Filters
// ============================================
function setupNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            if (item.classList.contains('highlight')) return; // Skip "Start Session" button
            e.preventDefault();

            document.querySelector('.nav-item.active')?.classList.remove('active');
            item.classList.add('active');

            const filter = item.getAttribute('data-filter');
            currentFilter = filter || 'all';

            const filterName = item.innerText.replace(/[^\w\s]/gi, '').trim();
            categoryTitle.textContent = filterName;

            renderBooks();
        });
    });
}

function setupSearch() {
    let debounceTimer;
    searchInput?.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            renderBooks();
        }, 300);
    });
}

function setupLogout() {
    const logoutBtn = document.querySelector('.btn-logout');
    if (logoutBtn) {
        logoutBtn.onclick = () => {
            BookTracker.logout();
        };
    }
}

// Add some skeleton styles dynamically
const style = document.createElement('style');
style.textContent = `
    .skeleton { pointer-events: none; }
    .skeleton-cover {
        width: 100%;
        aspect-ratio: 2/3;
        background: linear-gradient(90deg, #eee3e1 25%, #f5f0ed 50%, #eee3e1 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 12px;
        margin-bottom: 12px;
    }
    .skeleton-text {
        height: 14px;
        background: #eee3e1;
        border-radius: 4px;
        margin-bottom: 8px;
    }
    .skeleton-text.short { width: 60%; }
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    .verified-badge {
        position: absolute;
        top: 10px;
        left: 10px;
        background: #10b981;
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: bold;
    }
    .toast-container {
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    .toast {
        background: white;
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        display: flex;
        align-items: center;
        gap: 12px;
        animation: slideIn 0.3s ease;
        border-left: 4px solid #a63d40;
    }
    .toast.success { border-left-color: #10b981; }
    .toast.error { border-left-color: #ef4444; }
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    .toast-close { cursor: pointer; color: #999; margin-left: 8px; }
`;
document.head.appendChild(style);