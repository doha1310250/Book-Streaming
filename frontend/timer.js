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

// Elements - will be set on DOMContentLoaded
let timerDisplay, timerProgress, startBtn, finishBtn, completeModal, saveBtn, cancelBtn;
let modalInitial, modalSaving, modalSuccess;
let circumference;

// ============================================
// Initialize
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Get elements
    timerDisplay = document.getElementById('timer-display');
    timerProgress = document.getElementById('timer-progress');
    startBtn = document.getElementById('start-btn');
    finishBtn = document.getElementById('finish-btn');
    completeModal = document.getElementById('complete-modal');
    saveBtn = document.getElementById('save-btn');
    cancelBtn = document.getElementById('cancel-btn');
    modalInitial = document.getElementById('modal-initial');
    modalSaving = document.getElementById('modal-saving');
    modalSuccess = document.getElementById('modal-success');

    // Debug: check if elements were found
    console.log('Elements found:', {
        timerDisplay: !!timerDisplay,
        timerProgress: !!timerProgress,
        startBtn: !!startBtn,
        finishBtn: !!finishBtn,
        completeModal: !!completeModal,
        saveBtn: !!saveBtn
    });

    // Timer ring circumference
    if (timerProgress) {
        circumference = 140 * 2 * Math.PI;
        timerProgress.style.strokeDasharray = circumference;
        timerProgress.style.strokeDashoffset = circumference;
    }

    if (!BookTracker.requireAuth()) return;

    loadBook();
    loadUserInfo();
    initControls();

    // Resume session if exists
    const savedSession = localStorage.getItem('book_tracker_session');
    if (savedSession) {
        const session = JSON.parse(savedSession);
        console.log('Found saved session:', session);
        if (session.startTime && session.id) {
            seconds = Math.floor((Date.now() - session.startTime) / 1000);
            currentSession = session;
            updateDisplay();
            startTimer();
            if (startBtn) {
                startBtn.textContent = 'Session Active';
                startBtn.disabled = true;
            }
            console.log('Resumed session with ID:', session.id);
        } else {
            console.warn('Saved session missing startTime or id, clearing');
            localStorage.removeItem('book_tracker_session');
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
    if (timerDisplay) {
        timerDisplay.textContent = formatTime(seconds);
    }

    // Update progress ring
    if (timerProgress && circumference) {
        const totalGoalSeconds = dailyGoalMinutes * 60;
        const progress = Math.min(seconds / totalGoalSeconds, 1);
        const offset = circumference - (progress * circumference);
        timerProgress.style.strokeDashoffset = offset;
    }
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
    if (!startBtn || !finishBtn || !saveBtn) {
        console.error('Required buttons not found!', { startBtn, finishBtn, saveBtn });
        return;
    }

    // Start button
    startBtn.addEventListener('click', async () => {
        console.log('Start button clicked');
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
            console.log('Start session response:', response);

            currentSession = {
                id: response.id,
                bookId: currentBook.book_id,
                startTime: Date.now()
            };
            console.log('Created session:', currentSession);

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

    // Finish button - opens modal
    finishBtn.addEventListener('click', () => {
        console.log('Finish button clicked');
        stopTimer();

        // Format time with seconds for short sessions
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        let timeDisplay;
        if (mins >= 60) {
            timeDisplay = `${Math.floor(mins / 60)}h ${mins % 60}m`;
        } else if (mins > 0) {
            timeDisplay = `${mins}m`;
        } else {
            timeDisplay = `${secs}s`;
        }
        document.getElementById('summary-time').textContent = timeDisplay;

        // Reset modal to initial state
        showModalState('initial');
        completeModal.classList.remove('hidden');
    });

    // Cancel button - close modal and resume timer
    cancelBtn.addEventListener('click', () => {
        console.log('Cancel button clicked');
        completeModal.classList.add('hidden');
        startTimer();
    });

    // Save button - save session with loading states
    saveBtn.addEventListener('click', async () => {
        console.log('Save button clicked');

        // Show saving state
        showModalState('saving');

        try {
            console.log('Current session:', currentSession);

            if (currentSession?.id) {
                console.log('Ending session with ID:', currentSession.id);
                const endTime = new Date().toISOString();

                try {
                    await BookTracker.api.endReadingSession(currentSession.id, endTime);
                    console.log('Session ended successfully');
                } catch (endError) {
                    console.error('End session error:', endError);
                    // Continue anyway
                }
            }

            localStorage.removeItem('book_tracker_session');

            // Show success state
            showModalState('success');

            // Redirect after showing success
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);

        } catch (error) {
            console.error('Failed to save:', error);
            BookTracker.showToast(error.message || 'Failed to save', 'error');
            showModalState('initial');
        }
    });

    console.log('Controls initialized successfully');
}

// Show specific modal state
function showModalState(state) {
    modalInitial?.classList.add('hidden');
    modalSaving?.classList.add('hidden');
    modalSuccess?.classList.add('hidden');

    if (state === 'initial') modalInitial?.classList.remove('hidden');
    if (state === 'saving') modalSaving?.classList.remove('hidden');
    if (state === 'success') modalSuccess?.classList.remove('hidden');
}