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
    initReviewForm();

    await loadBooks();
    await loadMarkedBooks();
    await loadStats();

    // Poll for stats updates every 10 seconds
    setInterval(loadStats, 10000);
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
        // Fetch accurate stats from backend
        try {
            const stats = await BookTracker.api.getBookStats();
            document.getElementById('stat-books').textContent = stats.total_books;
        } catch (e) {
            console.warn('Stats endpoint unavailable, falling back to loaded count');
            document.getElementById('stat-books').textContent = libraryBooks.length;
        }

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

    // Load reviews for this book
    loadBookReviews(book.book_id);
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

// ============================================
// Reviews Functionality
// ============================================

let selectedRating = 0;
let currentUserReview = null;

function initReviewForm() {
    const starInput = document.getElementById('star-input');
    const submitBtn = document.getElementById('submit-review-btn');

    // Star rating interaction
    starInput.addEventListener('click', (e) => {
        if (e.target.classList.contains('star')) {
            selectedRating = parseInt(e.target.dataset.value);
            updateStarDisplay(selectedRating);
        }
    });

    // Hover effect for stars
    starInput.addEventListener('mouseover', (e) => {
        if (e.target.classList.contains('star')) {
            const hoverValue = parseInt(e.target.dataset.value);
            highlightStars(hoverValue);
        }
    });

    starInput.addEventListener('mouseout', () => {
        highlightStars(selectedRating);
    });

    // Submit review
    submitBtn.addEventListener('click', async () => {
        if (selectedRating === 0) {
            BookTracker.showToast('Please select a rating', 'error');
            return;
        }

        if (!currentActiveBook) return;

        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';

        try {
            const comment = document.getElementById('review-comment').value.trim();
            await BookTracker.api.createReview(currentActiveBook.book_id, selectedRating, comment);
            BookTracker.showToast('Review submitted!', 'success');

            // Reload reviews
            await loadBookReviews(currentActiveBook.book_id);

            // Reset form
            selectedRating = 0;
            updateStarDisplay(0);
            document.getElementById('review-comment').value = '';
        } catch (error) {
            BookTracker.showToast(error.message || 'Failed to submit review', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Review';
        }
    });
}

function updateStarDisplay(rating) {
    const stars = document.querySelectorAll('#star-input .star');
    stars.forEach((star, index) => {
        star.classList.toggle('active', index < rating);
        star.textContent = index < rating ? '★' : '☆';
    });
}

function highlightStars(rating) {
    const stars = document.querySelectorAll('#star-input .star');
    stars.forEach((star, index) => {
        const isActive = index < rating;
        star.style.color = isActive ? '#fbbf24' : '';
        star.textContent = isActive ? '★' : '☆';
    });
}

async function loadBookReviews(bookId) {
    const reviewsList = document.getElementById('reviews-list');
    const reviewForm = document.getElementById('review-form');

    reviewsList.innerHTML = '<div class="reviews-loading">Loading reviews...</div>';
    selectedRating = 0;
    updateStarDisplay(0);
    currentUserReview = null;

    try {
        // Load reviews and summary in parallel
        const [reviewsData, summaryData] = await Promise.all([
            BookTracker.api.getBookReviews(bookId),
            BookTracker.api.getBookReviewsSummary(bookId).catch(() => ({ average_rating: 0, total_reviews: 0 }))
        ]);

        // Update summary
        const avgRating = summaryData.average_rating || 0;
        const totalReviews = summaryData.total_reviews || 0;

        document.getElementById('avg-rating-value').textContent = avgRating.toFixed(1);
        document.getElementById('avg-stars').textContent = renderStars(avgRating);
        document.getElementById('review-count').textContent = `${totalReviews} review${totalReviews !== 1 ? 's' : ''}`;

        // Get reviews items
        const reviews = reviewsData.items || reviewsData || [];

        // Check if current user already reviewed
        const currentUser = BookTracker.getUser();
        currentUserReview = reviews.find(r => r.user_id === currentUser?.user_id);

        // Show/hide review form based on whether user already reviewed
        if (currentUserReview) {
            reviewForm.innerHTML = `<div class="already-reviewed">✓ You've already reviewed this book (${currentUserReview.rating}★)</div>`;
        } else {
            // Reset form to default state
            reviewForm.innerHTML = `
                <div class="star-input" id="star-input">
                    <span class="star" data-value="1">☆</span>
                    <span class="star" data-value="2">☆</span>
                    <span class="star" data-value="3">☆</span>
                    <span class="star" data-value="4">☆</span>
                    <span class="star" data-value="5">☆</span>
                </div>
                <textarea class="review-input" id="review-comment" placeholder="Write your review (optional)..." rows="2"></textarea>
                <button class="btn btn-primary btn-sm" id="submit-review-btn">Submit Review</button>
            `;
            initReviewForm();
        }

        // Render reviews list
        if (reviews.length === 0) {
            reviewsList.innerHTML = '<div class="reviews-empty">No reviews yet. Be the first to review!</div>';
        } else {
            reviewsList.innerHTML = reviews.map(review => `
                <div class="review-item">
                    <div class="review-item-header">
                        <div class="review-user">
                            <div class="review-avatar">${(review.user_name?.charAt(0) || '?').toUpperCase()}</div>
                            <div>
                                <div class="review-user-name">${review.user_name || 'Anonymous'}</div>
                                <div class="review-date">${formatDate(review.created_at)}</div>
                            </div>
                        </div>
                        <div class="review-rating">${renderStars(review.rating)}</div>
                    </div>
                    ${review.review_comment ? `<div class="review-comment">${escapeHtml(review.review_comment)}</div>` : ''}
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Failed to load reviews:', error);
        reviewsList.innerHTML = '<div class="reviews-empty">Failed to load reviews</div>';
    }
}

function renderStars(rating) {
    const fullStars = Math.floor(rating);
    const halfStar = rating % 1 >= 0.5 ? 1 : 0;
    const emptyStars = 5 - fullStars - halfStar;
    return '★'.repeat(fullStars) + (halfStar ? '½' : '') + '☆'.repeat(emptyStars);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}