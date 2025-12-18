/**
 * BookTracker - Timer Page JavaScript
 * Fortune 500 Edition
 */

// State
let seconds = 0;
let timerId = null;
let currentSession = null;
let currentBook = null;
const dailyGoalMinutes = 30;

// Elements
const timerDisplay = document.getElementById('timer-display');
const timerProgress = document.getElementById('timer-progress');
const startBtn = document.getElementById('start-btn');
const finishBtn = document.getElementById('finish-btn');
const completeModal = document.getElementById('complete-modal');
const saveBtn = document.getElementById('save-btn');

// Timer ring circumference
const circumference = 140 * 2 * Math.PI;
timerProgress.style.strokeDasharray = circumference;
timerProgress.style.strokeDashoffset = circumference;

// ============================================
// Initialize
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    if (!BookTracker.requireAuth()) return;

    loadBook();
    loadUserInfo();
    initControls();

    // Resume session if exists
    const savedSession = localStorage.getItem('book_tracker_session');
    if (savedSession) {
        const session = JSON.parse(savedSession);
        if (session.startTime) {
            seconds = Math.floor((Date.now() - session.startTime) / 1000);
            currentSession = session;
            updateDisplay();
            startTimer();
            startBtn.textContent = 'Session Active';
            startBtn.disabled = true;
        }
    }
});

function loadBook() {
    const bookData = localStorage.getItem('book_tracker_current_book');
    if (bookData) {
        currentBook = JSON.parse(bookData);
        document.getElementById('book-title').textContent = currentBook.title;
        document.getElementById('book-author').textContent = currentBook.author_name;
        document.getElementById('book-cover').src = BookTracker.getBookCoverUrl(currentBook.cover_url);
    }
}

function loadUserInfo() {
    const user = BookTracker.getUser();
    if (user) {
        document.getElementById('summary-streak').textContent = user.current_streak || 0;
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

function updateDisplay() {
    timerDisplay.textContent = formatTime(seconds);

    // Update progress ring
    const totalGoalSeconds = dailyGoalMinutes * 60;
    const progress = Math.min(seconds / totalGoalSeconds, 1);
    const offset = circumference - (progress * circumference);
    timerProgress.style.strokeDashoffset = offset;
}

function startTimer() {
    if (timerId) return;

    timerId = setInterval(() => {
        seconds++;
        updateDisplay();
    }, 1000);
}

function stopTimer() {
    if (timerId) {
        clearInterval(timerId);
        timerId = null;
    }
}

// ============================================
// Controls
// ============================================
function initControls() {
    // Start button
    startBtn.addEventListener('click', async () => {
        if (timerId) return;

        if (!currentBook) {
            BookTracker.showToast('Please select a book first', 'error');
            setTimeout(() => window.location.href = 'dashboard.html', 1000);
            return;
        }

        startBtn.disabled = true;
        startBtn.textContent = 'Starting...';

        try {
            const response = await BookTracker.api.startReadingSession(currentBook.book_id);
            currentSession = {
                id: response.id,
                bookId: currentBook.book_id,
                startTime: Date.now()
            };

            localStorage.setItem('book_tracker_session', JSON.stringify(currentSession));
            startTimer();

            startBtn.textContent = 'Session Active';
            BookTracker.showToast('Session started!', 'success');

        } catch (error) {
            console.error('Failed to start session:', error);
            BookTracker.showToast(error.message || 'Failed to start', 'error');
            startBtn.disabled = false;
            startBtn.textContent = 'Start Session';
        }
    });

    // Finish button
    finishBtn.addEventListener('click', () => {
        stopTimer();
        const mins = Math.floor(seconds / 60);
        document.getElementById('summary-time').textContent = mins + 'm';
        completeModal.classList.remove('hidden');
    });

    // Save button
    saveBtn.addEventListener('click', async () => {
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';

        try {
            if (currentSession?.id) {
                await BookTracker.api.endReadingSession(currentSession.id);
            }

            localStorage.removeItem('book_tracker_session');

            const mins = Math.floor(seconds / 60);
            BookTracker.showToast(`Great session! ${mins} minutes read.`, 'success');

            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);

        } catch (error) {
            console.error('Failed to save:', error);
            BookTracker.showToast(error.message || 'Failed to save', 'error');
            saveBtn.disabled = false;
            saveBtn.textContent = 'Save & Continue';
        }
    });
}