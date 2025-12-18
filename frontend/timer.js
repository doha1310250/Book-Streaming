/**
 * BookTracker - Timer Page JavaScript
 * Reading session timer with API integration
 */

// State
let seconds = 0;
let timerId = null;
let currentSession = null;
let currentBook = null;
const dailyGoalMinutes = 30;

// DOM Elements
const display = document.getElementById('display');
const progressBar = document.getElementById('progress-bar');
const startBtn = document.getElementById('start-btn');
const finishBtn = document.getElementById('finish-btn');
const logModal = document.getElementById('log-modal');
const saveLogBtn = document.getElementById('save-log-btn');
const summaryTime = document.getElementById('summary-time');

// Progress Circle Calculation
const circumference = 130 * 2 * Math.PI;
progressBar.style.strokeDasharray = `${circumference} ${circumference}`;
progressBar.style.strokeDashoffset = circumference;

// ============================================
// Initialize Timer Page
// ============================================
document.addEventListener('DOMContentLoaded', async () => {
    // Check auth
    if (!BookTracker.requireAuth()) return;

    // Load current book from localStorage
    const bookData = localStorage.getItem('book_tracker_current_book');
    if (bookData) {
        currentBook = JSON.parse(bookData);
        updateBookDisplay(currentBook);
    }

    // Check for existing active session
    const sessionData = localStorage.getItem('book_tracker_session');
    if (sessionData) {
        const session = JSON.parse(sessionData);
        // Calculate elapsed time if session was started
        if (session.startTime) {
            const elapsed = Math.floor((Date.now() - session.startTime) / 1000);
            seconds = elapsed;
            currentSession = session;
            display.textContent = formatTime(seconds);
            updateProgress();

            // Resume timer
            startTimer();
            startBtn.disabled = true;
            startBtn.textContent = 'Session in Progress...';
            startBtn.style.opacity = '0.7';
        }
    }

    // Load user stats
    loadUserStats();
});

function updateBookDisplay(book) {
    const coverUrl = BookTracker.getBookCoverUrl(book.cover_url);

    document.querySelector('.book-info h1').textContent = book.title;
    document.querySelector('.book-info p').textContent = book.author_name;
    document.querySelector('.book-artwork img').src = coverUrl;
}

async function loadUserStats() {
    try {
        const user = BookTracker.getUser();
        if (user) {
            // Update streak in modal
            const streakEl = document.querySelector('.stats-grid .stat-card:nth-child(2) .stat-value');
            if (streakEl) {
                streakEl.textContent = user.current_streak || 0;
            }
        }
    } catch (error) {
        console.error('Failed to load user stats:', error);
    }
}

// ============================================
// Timer Functions
// ============================================
function formatTime(s) {
    const h = Math.floor(s / 3600).toString().padStart(2, '0');
    const m = Math.floor((s % 3600) / 60).toString().padStart(2, '0');
    const sec = (s % 60).toString().padStart(2, '0');
    return `${h}:${m}:${sec}`;
}

function updateProgress() {
    const totalGoalSeconds = dailyGoalMinutes * 60;
    const progress = Math.min(seconds / totalGoalSeconds, 1);
    const offset = circumference - (progress * circumference);
    progressBar.style.strokeDashoffset = offset;
}

function startTimer() {
    if (timerId) return;

    timerId = setInterval(() => {
        seconds++;
        display.textContent = formatTime(seconds);
        updateProgress();
    }, 1000);
}

// ============================================
// Start Session
// ============================================
startBtn.addEventListener('click', async () => {
    if (timerId) return;

    if (!currentBook) {
        BookTracker.showToast('Please select a book first', 'error');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1000);
        return;
    }

    try {
        startBtn.disabled = true;
        startBtn.textContent = 'Starting...';

        // Create session via API
        const response = await BookTracker.api.startReadingSession(currentBook.book_id);
        currentSession = {
            id: response.id,
            bookId: currentBook.book_id,
            startTime: Date.now()
        };

        // Save session to localStorage for persistence
        localStorage.setItem('book_tracker_session', JSON.stringify(currentSession));

        // Start the timer
        startTimer();

        startBtn.textContent = 'Session in Progress...';
        startBtn.style.opacity = '0.7';
        startBtn.style.cursor = 'default';

        BookTracker.showToast('Reading session started! 📖', 'success');

    } catch (error) {
        console.error('Failed to start session:', error);
        BookTracker.showToast(error.message || 'Failed to start session', 'error');
        startBtn.disabled = false;
        startBtn.textContent = 'Start Session';
    }
});

// ============================================
// Finish Session
// ============================================
finishBtn.addEventListener('click', async () => {
    // Stop timer
    if (timerId) {
        clearInterval(timerId);
        timerId = null;
    }

    const minsRead = Math.floor(seconds / 60);
    summaryTime.textContent = minsRead + 'm';

    // Show modal
    logModal.classList.remove('hidden');
});

// ============================================
// Save Log (End Session)
// ============================================
saveLogBtn.addEventListener('click', async () => {
    const pageNum = document.getElementById('end-page').value;

    try {
        saveLogBtn.disabled = true;
        saveLogBtn.textContent = 'Saving...';

        // End session via API
        if (currentSession?.id) {
            await BookTracker.api.endReadingSession(currentSession.id);
        }

        // Clear session from localStorage
        localStorage.removeItem('book_tracker_session');

        const minsRead = Math.floor(seconds / 60);
        BookTracker.showToast(`Great session! You read for ${minsRead} minutes 🎉`, 'success');

        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1000);

    } catch (error) {
        console.error('Failed to save session:', error);
        BookTracker.showToast(error.message || 'Failed to save session', 'error');
        saveLogBtn.disabled = false;
        saveLogBtn.textContent = 'Save to Library';
    }
});

// Close modal if clicking outside
logModal.addEventListener('click', (e) => {
    if (e.target === logModal) {
        logModal.classList.add('hidden');
        // Resume timer if not finished
        if (seconds > 0 && !currentSession?.ended) {
            startTimer();
        }
    }
});

// Add toast container styles if not present
if (!document.querySelector('.toast-styles')) {
    const style = document.createElement('style');
    style.className = 'toast-styles';
    style.textContent = `
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
}