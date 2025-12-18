/**
 * BookTracker - Dashboard Page JavaScript
 * Fortune 500 Edition
 */

// State
let libraryBooks = [];
let markedBookIds = new Set();
let currentActiveBook = null;
let currentFilter = 'all';

// ============================================
// Initialize
// ============================================
document.addEventListener('DOMContentLoaded', async () => {
    if (!BookTracker.requireAuth()) return;

    initSidebar();
    initUserInfo();
    initSearch();
    initModal();
    initMobileMenu();
    initAddBookModal();

    await loadBooks();
    await loadMarkedBooks();
    await loadStats();
});

// ============================================
// User Info & Sidebar
// ============================================
function initUserInfo() {
    const user = BookTracker.getUser();
    if (user) {
        document.getElementById('user-name').textContent = user.name || 'Reader';
        document.getElementById('user-email').textContent = user.email || '';
        document.getElementById('user-avatar').textContent = (user.name?.charAt(0) || '?').toUpperCase();
        document.getElementById('streak-value').textContent = user.current_streak || 0;
    }

    document.getElementById('logout-btn').onclick = () => BookTracker.logout();
}

function initSidebar() {
    document.querySelectorAll('.nav-item[data-filter]').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();

            document.querySelector('.nav-item.active')?.classList.remove('active');
            item.classList.add('active');

            currentFilter = item.dataset.filter;
            document.getElementById('page-title').textContent = item.textContent.trim();

            renderBooks();
        });
    });
}

function initMobileMenu() {
    const btn = document.getElementById('mobile-menu-btn');
    const sidebar = document.getElementById('sidebar');

    btn?.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });
}

// ============================================
// Load Data
// ============================================
async function loadBooks() {
    try {
        // Show skeleton loaders while loading
        showBookSkeletons();

        libraryBooks = await BookTracker.api.getBooks();
        renderBooks();
    } catch (error) {
        console.error('Failed to load books:', error);
        showEmptyState('Failed to load books.');
    }
}

function showBookSkeletons() {
    const grid = document.getElementById('book-grid');
    grid.innerHTML = '';

    for (let i = 0; i < 8; i++) {
        const skeleton = document.createElement('div');
        skeleton.className = 'book-card skeleton-book-card';
        skeleton.innerHTML = `
            <div class="book-cover skeleton skeleton-cover"></div>
            <div class="book-info">
                <div class="skeleton skeleton-text" style="width: 80%"></div>
                <div class="skeleton skeleton-text-sm"></div>
            </div>
        `;
        grid.appendChild(skeleton);
    }
}

async function loadMarkedBooks() {
    try {
        const marked = await BookTracker.api.getMyMarkedBooks();
        markedBookIds = new Set(marked.map(b => b.book_id));
        document.getElementById('stat-favorites').textContent = marked.length;
        renderBooks();
    } catch (error) {
        console.error('Failed to load marked books:', error);
    }
}

async function loadStats() {
    try {
        document.getElementById('stat-books').textContent = libraryBooks.length;

        const sessions = await BookTracker.api.getMyReadingSessions({ limit: 100 });
        document.getElementById('stat-sessions').textContent = sessions.length;
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// ============================================
// Render Books
// ============================================
function renderBooks() {
    const grid = document.getElementById('book-grid');
    grid.innerHTML = '';

    let filtered = [...libraryBooks];

    // Apply filter
    if (currentFilter === 'favorites') {
        filtered = filtered.filter(book => markedBookIds.has(book.book_id));
    } else if (currentFilter === 'verified') {
        filtered = filtered.filter(book => book.is_verified);
    }

    // Apply search
    const searchTerm = document.getElementById('book-search')?.value?.toLowerCase() || '';
    if (searchTerm) {
        filtered = filtered.filter(book =>
            book.title.toLowerCase().includes(searchTerm) ||
            book.author_name.toLowerCase().includes(searchTerm)
        );
    }

    if (filtered.length === 0) {
        showEmptyState(currentFilter === 'favorites'
            ? 'No favorites yet. Add some books!'
            : 'No books found.');
        return;
    }

    filtered.forEach(book => {
        const isFavorite = markedBookIds.has(book.book_id);
        const coverUrl = BookTracker.getBookCoverUrl(book.cover_url);

        const card = document.createElement('div');
        card.className = 'book-card';
        card.innerHTML = `
            <div class="book-cover">
                <img src="${coverUrl}" alt="${book.title}" onerror="this.src='https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=400'">
                <div class="book-badges">
                    ${book.is_verified ? '<span class="book-verified">✓</span>' : '<span></span>'}
                    ${isFavorite ? '<span class="book-favorite">♥</span>' : '<span></span>'}
                </div>
            </div>
            <div class="book-info">
                <div class="book-title">${book.title}</div>
                <div class="book-author">${book.author_name}</div>
            </div>
        `;
        card.onclick = () => openModal(book);
        grid.appendChild(card);
    });
}

function showBookSkeleton() {
    const grid = document.getElementById('book-grid');
    grid.innerHTML = '';
    for (let i = 0; i < 8; i++) {
        const skeleton = document.createElement('div');
        skeleton.className = 'skeleton-card';
        skeleton.innerHTML = `
            <div class="skeleton-cover"></div>
            <div class="skeleton-text"></div>
            <div class="skeleton-text short"></div>
        `;
        grid.appendChild(skeleton);
    }
}

function showEmptyState(message) {
    const grid = document.getElementById('book-grid');
    grid.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
            <div class="empty-state-icon">📚</div>
            <p>${message}</p>
        </div>
    `;
}

// ============================================
// Search
// ============================================
function initSearch() {
    let debounce;
    document.getElementById('book-search')?.addEventListener('input', () => {
        clearTimeout(debounce);
        debounce = setTimeout(() => renderBooks(), 300);
    });
}

// ============================================
// Modal
// ============================================
function initModal() {
    const modal = document.getElementById('book-modal');
    const closeBtn = document.getElementById('modal-close');
    const readBtn = document.getElementById('modal-read-btn');
    const favBtn = document.getElementById('modal-fav-btn');

    closeBtn.onclick = () => modal.classList.add('hidden');
    modal.onclick = (e) => {
        if (e.target === modal) modal.classList.add('hidden');
    };

    readBtn.onclick = () => {
        if (currentActiveBook) {
            localStorage.setItem('book_tracker_current_book', JSON.stringify(currentActiveBook));
            window.location.href = 'timer.html';
        }
    };

    favBtn.onclick = async () => {
        if (!currentActiveBook) return;

        const bookId = currentActiveBook.book_id;
        const isFavorite = markedBookIds.has(bookId);

        try {
            if (isFavorite) {
                await BookTracker.api.unmarkBook(bookId);
                markedBookIds.delete(bookId);
                favBtn.textContent = 'Add to Favorites';
                BookTracker.showToast('Removed from favorites', 'default');
            } else {
                await BookTracker.api.markBook(bookId);
                markedBookIds.add(bookId);
                favBtn.textContent = 'Remove from Favorites';
                BookTracker.showToast('Added to favorites!', 'success');
            }
            document.getElementById('stat-favorites').textContent = markedBookIds.size;
            renderBooks();
        } catch (error) {
            BookTracker.showToast(error.message || 'Action failed', 'error');
        }
    };
}

function openModal(book) {
    currentActiveBook = book;
    const modal = document.getElementById('book-modal');
    const isFavorite = markedBookIds.has(book.book_id);
    const coverUrl = BookTracker.getBookCoverUrl(book.cover_url);

    document.getElementById('modal-cover').src = coverUrl;
    document.getElementById('modal-title').textContent = book.title;
    document.getElementById('modal-author').textContent = book.author_name;
    document.getElementById('modal-desc').textContent = `Published: ${book.publish_date || 'Unknown'}`;

    const badge = document.getElementById('modal-badge');
    badge.textContent = book.is_verified ? 'Verified' : 'Community';
    badge.className = book.is_verified ? 'badge badge-success' : 'badge';

    document.getElementById('modal-fav-btn').textContent = isFavorite ? 'Remove from Favorites' : 'Add to Favorites';

    modal.classList.remove('hidden');
}

// ============================================
// Add Book Logic
// ============================================
function initAddBookModal() {
    const modal = document.getElementById('add-book-modal');
    const openBtn = document.getElementById('add-book-btn');
    const closeBtn = document.getElementById('add-book-close');
    const cancelBtn = document.getElementById('add-book-cancel');
    const form = document.getElementById('add-book-form');

    const closeModal = () => {
        modal.classList.add('hidden');
        form.reset();
    };

    openBtn.addEventListener('click', () => {
        modal.classList.remove('hidden');
    });

    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);

    // Close on click outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // Handle Form Submit
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitBtn = document.getElementById('add-book-submit');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Adding...';

        try {
            const formData = new FormData();
            formData.append('title', document.getElementById('add-book-title').value);
            formData.append('author_name', document.getElementById('add-book-author').value);

            const date = document.getElementById('add-book-date').value;
            if (date) formData.append('publish_date', date);

            const coverFile = document.getElementById('add-book-cover').files[0];
            if (coverFile) {
                formData.append('cover_image', coverFile);
            }

            await BookTracker.api.createBook(formData);

            BookTracker.showToast('Book added successfully!', 'success');
            closeModal();
            await loadBooks(); // Refresh list

        } catch (error) {
            console.error('Failed to add book:', error);
            BookTracker.showToast(error.message || 'Failed to add book', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });
}