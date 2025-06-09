// Notification manager for Bazos Ad Tracker

class NotificationManager {
    constructor() {
        this.notificationSound = document.getElementById('notification-sound');
        this.notificationPermission = 'default';
        this.notificationsEnabled = true;
        this.soundEnabled = true;
        
        // Check if browser supports notifications
        if ('Notification' in window) {
            this.notificationPermission = Notification.permission;
            
            if (this.notificationPermission !== 'granted' && this.notificationPermission !== 'denied') {
                document.getElementById('notification-permission-btn').classList.remove('hidden');
            }
        }
        
        // Initialize settings from localStorage
        this.loadSettings();
    }
    
    // Request permission to show notifications
    requestPermission() {
        if ('Notification' in window) {
            Notification.requestPermission().then(permission => {
                this.notificationPermission = permission;
                
                if (permission === 'granted') {
                    document.getElementById('notification-permission-btn').classList.add('hidden');
                    this.sendTestNotification();
                }
            });
        }
    }
    
    // Send a browser notification
    sendNotification(title, options = {}) {
        if (!this.notificationsEnabled) return;
        
        if (this.notificationPermission === 'granted') {
            const defaultOptions = {
                icon: '/static/img/favicon.png',
                badge: '/static/img/favicon.png',
                vibrate: [100, 50, 100],
                timestamp: Date.now()
            };
            
            const notification = new Notification(title, { ...defaultOptions, ...options });
            
            notification.onclick = function() {
                window.focus();
                this.close();
            };
        }
    }
    
    // Play notification sound
    playSound() {
        if (!this.soundEnabled) return;
        
        try {
            this.notificationSound.currentTime = 0;
            this.notificationSound.play().catch(err => {
                console.error('Error playing notification sound:', err);
            });
        } catch (err) {
            console.error('Error playing notification sound:', err);
        }
    }
    
    // Send a test notification
    sendTestNotification() {
        this.sendNotification('Bazos Ad Tracker', {
            body: 'Notifications are now enabled!'
        });
    }
    
    // Toggle notifications
    toggleNotifications() {
        this.notificationsEnabled = !this.notificationsEnabled;
        this.saveSettings();
        return this.notificationsEnabled;
    }
    
    // Toggle sound
    toggleSound() {
        this.soundEnabled = !this.soundEnabled;
        this.saveSettings();
        return this.soundEnabled;
    }
    
    // Save settings to localStorage
    saveSettings() {
        localStorage.setItem('notificationsEnabled', JSON.stringify(this.notificationsEnabled));
        localStorage.setItem('soundEnabled', JSON.stringify(this.soundEnabled));
    }
    
    // Load settings from localStorage
    loadSettings() {
        try {
            const notificationsEnabled = localStorage.getItem('notificationsEnabled');
            const soundEnabled = localStorage.getItem('soundEnabled');
            
            if (notificationsEnabled !== null) {
                this.notificationsEnabled = JSON.parse(notificationsEnabled);
            }
            
            if (soundEnabled !== null) {
                this.soundEnabled = JSON.parse(soundEnabled);
            }
        } catch (err) {
            console.error('Error loading notification settings:', err);
        }
    }
}

// Export notification manager
window.notificationManager = new NotificationManager();
