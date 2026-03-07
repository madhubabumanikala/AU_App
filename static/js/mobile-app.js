/**
 * AU Event System - Mobile App JavaScript
 */

class MobileApp {
    constructor() {
        this.isOnline = navigator.onLine;
        this.currentView = 'dashboard';
        this.swipeThreshold = 100;
        this.init();
    }

    init() {
        this.setupServiceWorker();
        this.setupNavigation();
        this.setupSwipeGestures();
        this.setupPullToRefresh();
        this.setupFormHandling();
        this.setupOfflineHandling();
        this.setupNotifications();
    }

    // Service Worker Registration
    async setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/static/js/service-worker.js');
                console.log('ServiceWorker registered:', registration);
                
                // Check for updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            this.showUpdateNotification();
                        }
                    });
                });
            } catch (error) {
                console.log('ServiceWorker registration failed:', error);
            }
        }
    }

    showUpdateNotification() {
        const notification = document.createElement('div');
        notification.className = 'mobile-alert mobile-alert-info';
        notification.innerHTML = `
            <i class="fas fa-download"></i>
            <span>New version available! Refresh to update.</span>
            <button onclick="window.location.reload()" class="mobile-btn-small">Update</button>
        `;
        document.body.insertBefore(notification, document.body.firstChild);
    }

    // Navigation Management
    setupNavigation() {
        // Bottom navigation
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('nav-btn')) {
                this.navigateToView(e.target.dataset.view);
                this.updateActiveNav(e.target);
            }
        });

        // Tab navigation
        document.addEventListener('click', (e) => {
            if (e.target.closest('.nav-tabs a')) {
                e.preventDefault();
                const tab = e.target.closest('a');
                this.switchTab(tab);
            }
        });

        // Back button handling
        window.addEventListener('popstate', (e) => {
            if (e.state && e.state.view) {
                this.navigateToView(e.state.view, false);
            }
        });
    }

    navigateToView(view, updateHistory = true) {
        this.currentView = view;
        
        if (updateHistory) {
            history.pushState({ view: view }, '', `/${view}`);
        }

        // Update UI
        this.showLoading();
        
        // Simulate navigation or make AJAX call
        setTimeout(() => {
            this.hideLoading();
            this.updateViewContent(view);
        }, 500);
    }

    updateActiveNav(activeBtn) {
        document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
        activeBtn.classList.add('active');
    }

    switchTab(activeTab) {
        const tabContainer = activeTab.closest('.nav-tabs');
        tabContainer.querySelectorAll('a').forEach(tab => tab.classList.remove('active'));
        activeTab.classList.add('active');
    }

    updateViewContent(view) {
        // This would typically make an AJAX request to get new content
        console.log(`Navigating to view: ${view}`);
    }

    // Swipe Gestures
    setupSwipeGestures() {
        let startX = 0;
        let startY = 0;
        let currentX = 0;
        let currentY = 0;

        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });

        document.addEventListener('touchmove', (e) => {
            if (!startX || !startY) return;
            
            currentX = e.touches[0].clientX;
            currentY = e.touches[0].clientY;
        });

        document.addEventListener('touchend', (e) => {
            if (!startX || !startY) return;

            const diffX = startX - currentX;
            const diffY = startY - currentY;

            if (Math.abs(diffX) > Math.abs(diffY)) {
                // Horizontal swipe
                if (Math.abs(diffX) > this.swipeThreshold) {
                    if (diffX > 0) {
                        this.handleSwipeLeft();
                    } else {
                        this.handleSwipeRight();
                    }
                }
            } else {
                // Vertical swipe
                if (Math.abs(diffY) > this.swipeThreshold) {
                    if (diffY > 0) {
                        this.handleSwipeUp();
                    } else {
                        this.handleSwipeDown();
                    }
                }
            }

            startX = 0;
            startY = 0;
        });
    }

    handleSwipeLeft() {
        // Navigate to next view or show side menu
        console.log('Swiped left');
    }

    handleSwipeRight() {
        // Navigate to previous view or go back
        console.log('Swiped right');
        if (window.history.length > 1) {
            window.history.back();
        }
    }

    handleSwipeUp() {
        console.log('Swiped up');
    }

    handleSwipeDown() {
        // Pull to refresh
        this.triggerPullToRefresh();
    }

    // Pull to Refresh
    setupPullToRefresh() {
        let startY = 0;
        let pullDistance = 0;
        const pullThreshold = 80;
        let isPulling = false;

        const content = document.querySelector('.mobile-content');
        if (!content) return;

        content.addEventListener('touchstart', (e) => {
            if (content.scrollTop === 0) {
                startY = e.touches[0].clientY;
                isPulling = true;
            }
        });

        content.addEventListener('touchmove', (e) => {
            if (!isPulling) return;

            const currentY = e.touches[0].clientY;
            pullDistance = currentY - startY;

            if (pullDistance > 0 && pullDistance < pullThreshold * 2) {
                e.preventDefault();
                this.updatePullIndicator(pullDistance, pullThreshold);
            }
        });

        content.addEventListener('touchend', () => {
            if (isPulling && pullDistance > pullThreshold) {
                this.triggerPullToRefresh();
            }
            this.resetPullIndicator();
            isPulling = false;
            pullDistance = 0;
        });
    }

    updatePullIndicator(distance, threshold) {
        let indicator = document.querySelector('.pull-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'pull-indicator';
            indicator.innerHTML = '<i class="fas fa-arrow-down"></i>';
            document.querySelector('.mobile-content').insertBefore(indicator, document.querySelector('.mobile-content').firstChild);
        }

        const progress = Math.min(distance / threshold, 1);
        indicator.style.transform = `translateY(${distance - 60}px) rotate(${progress * 180}deg)`;
        indicator.style.opacity = progress;
    }

    resetPullIndicator() {
        const indicator = document.querySelector('.pull-indicator');
        if (indicator) {
            indicator.style.transform = 'translateY(-60px) rotate(0deg)';
            indicator.style.opacity = '0';
        }
    }

    triggerPullToRefresh() {
        this.showRefreshLoader();
        
        // Simulate refresh
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    }

    showRefreshLoader() {
        const loader = document.createElement('div');
        loader.className = 'refresh-loader';
        loader.innerHTML = '<div class="spinner"></div>';
        document.body.appendChild(loader);
    }

    // Form Handling
    setupFormHandling() {
        document.addEventListener('submit', (e) => {
            if (e.target.classList.contains('mobile-form')) {
                this.handleMobileFormSubmit(e);
            }
        });

        // Auto-save functionality
        document.addEventListener('input', (e) => {
            if (e.target.closest('.mobile-form')) {
                this.autoSaveForm(e.target.closest('.mobile-form'));
            }
        });
    }

    handleMobileFormSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const submitBtn = form.querySelector('[type="submit"]');
        
        // Show loading state
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
            submitBtn.disabled = true;
        }

        // Get form data
        const formData = new FormData(form);
        
        // Submit via fetch
        fetch(form.action, {
            method: form.method,
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showToast('Success!', 'success');
                if (data.redirect) {
                    window.location.href = data.redirect;
                }
            } else {
                this.showToast(data.message || 'Error occurred', 'error');
            }
        })
        .catch(error => {
            this.showToast('Network error', 'error');
            console.error('Form submit error:', error);
        })
        .finally(() => {
            if (submitBtn) {
                submitBtn.innerHTML = submitBtn.dataset.originalText || 'Submit';
                submitBtn.disabled = false;
            }
        });
    }

    autoSaveForm(form) {
        if (form.dataset.autoSave !== 'true') return;

        clearTimeout(this.autoSaveTimeout);
        this.autoSaveTimeout = setTimeout(() => {
            const formData = new FormData(form);
            localStorage.setItem(`form_${form.id}`, JSON.stringify(Object.fromEntries(formData)));
        }, 1000);
    }

    // Offline Handling
    setupOfflineHandling() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.hideOfflineIndicator();
            this.syncOfflineActions();
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showOfflineIndicator();
        });
    }

    showOfflineIndicator() {
        let indicator = document.querySelector('.offline-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'offline-indicator mobile-alert mobile-alert-warning';
            indicator.innerHTML = '<i class="fas fa-wifi"></i> You are offline';
            document.body.insertBefore(indicator, document.body.firstChild);
        }
    }

    hideOfflineIndicator() {
        const indicator = document.querySelector('.offline-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    syncOfflineActions() {
        // Sync any offline actions when back online
        const offlineActions = JSON.parse(localStorage.getItem('offlineActions') || '[]');
        
        offlineActions.forEach(action => {
            // Process each offline action
            console.log('Syncing offline action:', action);
        });

        localStorage.removeItem('offlineActions');
    }

    // Notifications
    setupNotifications() {
        if ('Notification' in window && 'serviceWorker' in navigator) {
            this.requestNotificationPermission();
        }
    }

    async requestNotificationPermission() {
        if (Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                this.showToast('Notifications enabled!', 'success');
            }
        }
    }

    showNotification(title, message, icon = '/static/images/icon-192.png') {
        if ('serviceWorker' in navigator && Notification.permission === 'granted') {
            navigator.serviceWorker.ready.then(registration => {
                registration.showNotification(title, {
                    body: message,
                    icon: icon,
                    badge: icon,
                    vibrate: [100, 50, 100]
                });
            });
        }
    }

    // UI Helpers
    showLoading() {
        let loader = document.querySelector('.mobile-loader');
        if (!loader) {
            loader = document.createElement('div');
            loader.className = 'mobile-loader';
            loader.innerHTML = '<div class="spinner"></div>';
            document.body.appendChild(loader);
        }
        loader.style.display = 'flex';
    }

    hideLoading() {
        const loader = document.querySelector('.mobile-loader');
        if (loader) {
            loader.style.display = 'none';
        }
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `mobile-toast mobile-toast-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${this.getToastIcon(type)}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 100);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || icons.info;
    }

    // Utility Methods
    vibrate(pattern = [100]) {
        if ('vibrate' in navigator) {
            navigator.vibrate(pattern);
        }
    }

    shareContent(title, text, url) {
        if (navigator.share) {
            navigator.share({
                title: title,
                text: text,
                url: url
            });
        } else {
            // Fallback to clipboard
            navigator.clipboard.writeText(url).then(() => {
                this.showToast('Link copied to clipboard!', 'success');
            });
        }
    }
}

// Initialize mobile app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.mobileApp = new MobileApp();
});

// Mobile-specific event handlers
function toggleNotifications() {
    // Toggle notifications panel
    const panel = document.querySelector('.notifications-panel');
    if (panel) {
        panel.classList.toggle('active');
    }
}

function toggleProfile() {
    // Toggle profile menu
    const menu = document.querySelector('.profile-menu');
    if (menu) {
        menu.classList.toggle('active');
    }
}

function showLogin() {
    window.location.href = '/auth/login';
}

// Event Registration Functions
function registerForEvent(eventId) {
    if (!window.mobileApp.isOnline) {
        window.mobileApp.showToast('You are offline. Try again when connected.', 'warning');
        return;
    }

    fetch(`/events/${eventId}/register`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.mobileApp.showToast('Successfully registered!', 'success');
            window.mobileApp.vibrate([100, 50, 100]);
            // Update UI
            location.reload();
        } else {
            window.mobileApp.showToast(data.message || 'Registration failed', 'error');
        }
    })
    .catch(error => {
        window.mobileApp.showToast('Network error. Please try again.', 'error');
    });
}

function unregisterFromEvent(eventId) {
    if (!confirm('Are you sure you want to unregister from this event?')) return;

    fetch(`/events/${eventId}/unregister`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.mobileApp.showToast('Successfully unregistered', 'success');
            location.reload();
        } else {
            window.mobileApp.showToast(data.message || 'Unregistration failed', 'error');
        }
    })
    .catch(error => {
        window.mobileApp.showToast('Network error. Please try again.', 'error');
    });
}

// QR Code Scanner (if camera is available)
async function scanQRCode() {
    if ('mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: 'environment' } 
            });
            
            // Show camera interface
            showCameraInterface(stream);
            
        } catch (error) {
            window.mobileApp.showToast('Camera access denied', 'error');
        }
    } else {
        window.mobileApp.showToast('Camera not supported', 'warning');
    }
}

function showCameraInterface(stream) {
    const modal = document.createElement('div');
    modal.className = 'camera-modal';
    modal.innerHTML = `
        <div class="camera-container">
            <video autoplay playsinline></video>
            <div class="camera-overlay">
                <div class="scan-frame"></div>
            </div>
            <button onclick="closeCameraInterface()" class="close-btn">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const video = modal.querySelector('video');
    video.srcObject = stream;
    
    // QR code detection would go here
    // This is a placeholder for QR code scanning library integration
}

function closeCameraInterface() {
    const modal = document.querySelector('.camera-modal');
    if (modal) {
        const video = modal.querySelector('video');
        if (video.srcObject) {
            video.srcObject.getTracks().forEach(track => track.stop());
        }
        modal.remove();
    }
}
