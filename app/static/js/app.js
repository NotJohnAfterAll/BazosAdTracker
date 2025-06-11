// Bazos Ad Tracker App JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Connect to Socket.IO with Cloudflare-compatible settings
    const socket = io({
        // Cloudflare WebSocket configuration - start with polling only
        transports: ['polling'], // Use polling only, disable websockets for Cloudflare compatibility
        upgrade: false, // Don't upgrade to websockets automatically
        rememberUpgrade: false,
        timeout: 30000, // Increased timeout for Cloudflare
        forceNew: true,
        // Cloudflare-friendly options
        pingTimeout: 120000, // Increased for Cloudflare
        pingInterval: 60000, // Increased for Cloudflare
        // Retry configuration
        reconnection: true,
        reconnectionAttempts: 10, // More attempts for Cloudflare
        reconnectionDelay: 2000,
        reconnectionDelayMax: 10000,
        maxReconnectionAttempts: 10,
        // Additional Cloudflare settings
        autoConnect: true,
        withCredentials: false
    });
    
    // DOM elements
    const newKeywordInput = document.getElementById('new-keyword');
    const addKeywordBtn = document.getElementById('add-keyword');
    const keywordsList = document.getElementById('keywords-list');
    const keywordFilter = document.getElementById('keyword-filter');
    const keywordTitle = document.getElementById('keyword-title');
    const keywordAds = document.getElementById('keyword-ads');
    const recentAds = document.getElementById('recent-ads');
    const changesList = document.getElementById('changes-list');    const statusBanner = document.getElementById('status-banner');
    const statusMessage = document.getElementById('status-message');    const statusIcon = document.getElementById('status-icon');
    const notificationSound = document.getElementById('notification-sound');
    const themeToggleBtn = document.getElementById('theme-toggle');
    const adSearch = document.getElementById('ad-search');
    const clearSearch = document.getElementById('clear-search');
    const noResults = document.getElementById('no-results');
    const resultsCount = document.getElementById('results-count');
    const manualCheckBtn = document.getElementById('manual-check-btn');
    
    // Settings modal elements
    const settingsModal = document.getElementById('settings-modal');
    const settingsBtn = document.getElementById('settings-btn');
    const closeSettingsBtn = document.getElementById('close-settings-btn');
    const closeSettings = document.getElementById('close-settings');
    const notificationPermissionBtn = document.getElementById('notification-permission-btn');
    const notificationsToggle = document.getElementById('notifications-toggle');
    const soundToggle = document.getElementById('sound-toggle');
      // Store current ads for filtering
    let currentKeywordAds = [];
    let filteredAds = [];
    
    // Pagination
    const adsPerPage = 15; // Increased from 9 to 15 ads per page
    let currentPage = 1;
    
    // Favorites
    let favoriteAds = JSON.parse(localStorage.getItem('favoriteAds') || '{}');
    
    // Tabs
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Pagination buttons
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    
    // Change filters
    const newAdsFilterBtn = document.getElementById('new-ads-filter');
    const deletedAdsFilterBtn = document.getElementById('deleted-ads-filter');
    const allChangesFilterBtn = document.getElementById('all-changes-filter');
      // State
    let keywords = [];
    let allAds = {};
    let changesLog = [];
    let changesFilter = 'all'; // 'new', 'deleted', 'all'
    
    // Theme
    let isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (isDarkMode) {
        document.documentElement.classList.add('dark');
    }
    
    // Initialize settings if available
    if (notificationsToggle && notificationManager) {
        notificationsToggle.checked = notificationManager.notificationsEnabled;
    }
    
    if (soundToggle && notificationManager) {
        soundToggle.checked = notificationManager.soundEnabled;
    }
      // Initial data loading
    fetchKeywords();
    fetchRecentAds();
    fetchSystemStats();
    
    // Initialize dataset for new ad IDs
    if (keywordAds) {
        keywordAds.dataset.newAdIds = JSON.stringify([]);
    }
    
    // Socket.IO events
    socket.on('connect', () => {
        showStatus('Connected to server', 'success');
    });
    
    socket.on('disconnect', () => {
        showStatus('Disconnected from server', 'error');
    });    socket.on('ads_update', (data) => {
        // Add to changes log
        const timestamp = data.timestamp || new Date().toLocaleString();        let newAdIds = [];
        
        if (data.new_ads && data.new_ads.length > 0) {
            // Play notification sound
            playNotification();
            
            // Collect new ad IDs for highlighting
            newAdIds = data.new_ads.map(item => item.ad.id);
            
            // Add new ads to changes log
            data.new_ads.forEach(item => {
                changesLog.unshift({
                    type: 'new',
                    keyword: item.keyword,
                    ad: item.ad,
                    timestamp
                });
            });
            
            showStatus(`${data.new_ads.length} new advertisement(s) found!`, 'success');
        }
        
        if (data.deleted_ads && data.deleted_ads.length > 0) {
            // Add deleted ads to changes log
            data.deleted_ads.forEach(item => {
                changesLog.unshift({
                    type: 'deleted',
                    keyword: item.keyword,
                    ad: item.ad,
                    timestamp
                });
            });
            
            showStatus(`${data.deleted_ads.length} advertisement(s) have been removed.`, 'info');
        }
        
        // Update stats
        fetchSystemStats();
        
        // Keep changes log at a reasonable size
        if (changesLog.length > 100) {
            changesLog = changesLog.slice(0, 100);
        }
          // Auto-refresh data based on which tab is currently active
        const activeTab = document.querySelector('.tab.active');
        const activeTabId = activeTab ? activeTab.getAttribute('data-tab') : 'recent';
        
        // Refresh data based on active tab and whether there are changes
        if (data.new_ads && data.new_ads.length > 0 || data.deleted_ads && data.deleted_ads.length > 0) {
            if (activeTabId === 'recent') {
                // Only refresh recent ads with highlighting if we're on the recent tab
                fetchRecentAdsWithHighlight(newAdIds);
            } else {
                // For other tabs, refresh recent ads without highlighting (for background data)
                fetchRecentAds();
            }
        }
        
        // Update changes log
        updateChangesLog();
        
        // If keywords tab is active and the current keyword has changes, refresh its ads
        const currentKeyword = keywordFilter.value;
        if (
            activeTabId === 'keywords' && 
            currentKeyword && 
            data.keywords_with_changes && 
            data.keywords_with_changes.includes(currentKeyword)
        ) {
            fetchKeywordAdsWithHighlight(currentKeyword, newAdIds);
        }
        
        // If favorites tab is active, refresh favorites in case any new ads were favorited
        if (activeTabId === 'favorites') {
            displayFavorites();
        }
        
        // Refresh keywords list in case new keywords were added
        fetchKeywords();
    });
      // Event listeners
    if (addKeywordBtn) {
        addKeywordBtn.addEventListener('click', addKeyword);
    }
    
    if (newKeywordInput) {
        newKeywordInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                addKeyword();
            }
        });
    }
    
    // Manual check button
    if (manualCheckBtn) {
        manualCheckBtn.addEventListener('click', performManualCheck);
    }
    
    if (keywordFilter) {
        keywordFilter.addEventListener('change', () => {
            const keyword = keywordFilter.value;
            if (keyword) {
                keywordTitle.textContent = `Advertisements for: "${keyword}"`;
                fetchKeywordAds(keyword);
            } else {
                keywordTitle.textContent = 'Select a keyword above';
                keywordAds.innerHTML = '';
            }
        });
    }
    
    if (adSearch) {
        adSearch.addEventListener('input', () => {
            const query = adSearch.value.trim().toLowerCase();
            
            clearSearch.classList.toggle('hidden', !query);
            
            // Filter ads by title, description, or price
            filteredAds = currentKeywordAds.filter(ad => {
                const titleMatch = ad.title?.toLowerCase().includes(query) || false;
                const descriptionMatch = ad.description?.toLowerCase().includes(query) || false;
                const priceMatch = ad.price?.toString().includes(query) || false;
                
                return titleMatch || descriptionMatch || priceMatch;
            });
            
            // Reset to first page
            currentPage = 1;
            
            // Update results count
            resultsCount.textContent = `${filteredAds.length} result${filteredAds.length !== 1 ? 's' : ''}`;
            
            // Show or hide no results message
            noResults.classList.toggle('hidden', filteredAds.length > 0);
            
            // Render page and update pagination
            if (filteredAds.length > 0) {
                renderCurrentPage();
                updatePaginationControls();
            } else {
                keywordAds.innerHTML = '';
                document.getElementById('pagination-controls').classList.add('hidden');
            }
        });
    }
    
    if (clearSearch) {
        clearSearch.addEventListener('click', () => {
            adSearch.value = '';
            adSearch.dispatchEvent(new Event('input'));
        });
    }
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabId = tab.getAttribute('data-tab');
            
            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Show active tab content
            tabContents.forEach(tc => {
                tc.classList.add('hidden');
                if (tc.id === `${tabId}-tab`) {
                    tc.classList.remove('hidden');
                }
            });
            
            // If selecting keywords tab and we have keywords, load ads for first keyword
            if (tabId === 'keywords' && keywords.length > 0 && !keywordFilter.value) {
                keywordFilter.value = keywords[0];
                keywordTitle.textContent = `Advertisements for: "${keywords[0]}"`;
                fetchKeywordAds(keywords[0]);
            }
            
            // If selecting favorites tab, update the display
            if (tabId === 'favorites') {
                displayFavorites();
            }
            
            // If selecting changes tab, update the log
            if (tabId === 'changes') {
                updateChangesLog();
            }
        });
    });
    
    // Pagination event listeners
    if (prevPageBtn) {
        prevPageBtn.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                renderCurrentPage();
                updatePaginationControls();
                // Scroll to top of ads container
                keywordAds.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
    
    if (nextPageBtn) {
        nextPageBtn.addEventListener('click', () => {
            const totalPages = Math.ceil(filteredAds.length / adsPerPage);
            if (currentPage < totalPages) {
                currentPage++;
                renderCurrentPage();
                updatePaginationControls();
                // Scroll to top of ads container
                keywordAds.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
    
    // Change filters
    if (newAdsFilterBtn) {
        newAdsFilterBtn.addEventListener('click', () => {
            setChangesFilter('new');
        });
    }
    
    if (deletedAdsFilterBtn) {
        deletedAdsFilterBtn.addEventListener('click', () => {
            setChangesFilter('deleted');
        });
    }
    
    if (allChangesFilterBtn) {
        allChangesFilterBtn.addEventListener('click', () => {
            setChangesFilter('all');
        });
    }
      // Theme toggle
    if (themeToggleBtn) {
        // Initialize button text based on current theme
        if (isDarkMode) {
            themeToggleBtn.innerHTML = '<i class="fas fa-sun mr-2"></i><span>Theme</span>';
        } else {
            themeToggleBtn.innerHTML = '<i class="fas fa-moon mr-2"></i><span>Theme</span>';
        }
          themeToggleBtn.addEventListener('click', () => {
            isDarkMode = !isDarkMode;
            console.log('Theme toggle clicked, isDarkMode:', isDarkMode);
            
            if (isDarkMode) {
                document.documentElement.classList.add('dark');
                themeToggleBtn.innerHTML = '<i class="fas fa-sun mr-2"></i><span>Theme</span>';
                console.log('Switched to dark mode');
            } else {
                document.documentElement.classList.remove('dark');
                themeToggleBtn.innerHTML = '<i class="fas fa-moon mr-2"></i><span>Theme</span>';
                console.log('Switched to light mode');
            }
            
            localStorage.setItem('darkMode', isDarkMode);
        });
    }
    
    // Settings modal
    if (settingsBtn) {
        settingsBtn.addEventListener('click', () => {
            settingsModal.classList.add('active');
            fetchSystemStats(); // Update stats when opening settings
        });
    }
    
    // Close settings modal
    if (closeSettingsBtn && closeSettings) {
        [closeSettingsBtn, closeSettings].forEach(el => {
            el.addEventListener('click', () => {
                settingsModal.classList.remove('active');
            });
        });
    }
    
    // Settings modal should close when clicking outside
    if (settingsModal) {
        settingsModal.addEventListener('click', (e) => {
            if (e.target === settingsModal) {
                settingsModal.classList.remove('active');
            }
        });
    }
    
    // Request notification permission
    if (notificationPermissionBtn) {
        notificationPermissionBtn.addEventListener('click', () => {
            notificationManager.requestPermission();
        });
    }
    
    // Toggle notifications
    if (notificationsToggle) {
        notificationsToggle.addEventListener('change', () => {
            const enabled = notificationManager.toggleNotifications();
            notificationsToggle.checked = enabled;
        });
    }
    
    // Toggle sound
    if (soundToggle) {
        soundToggle.addEventListener('change', () => {
            const enabled = notificationManager.toggleSound();
            soundToggle.checked = enabled;
        });
    }
      // Update stats every 10 seconds for better real-time feedback
    setInterval(fetchSystemStats, 10000);
    
    // Functions
    function fetchKeywords() {
        fetch('/api/keywords')
            .then(response => response.json())
            .then(data => {
                keywords = data.keywords || [];
                updateKeywordsList();
                updateKeywordFilter();
            })
            .catch(error => {
                showStatus('Error fetching keywords: ' + error.message, 'error');
            });
    }
      function fetchRecentAds() {
        fetchRecentAdsWithHighlight([]);
    }
    
    function fetchRecentAdsWithHighlight(newAdIds = []) {
        fetch('/api/recent-ads')
            .then(response => response.json())
            .then(data => {
                displayRecentAds(data.ads || [], newAdIds);
            })
            .catch(error => {
                showStatus('Error fetching recent ads: ' + error.message, 'error');
            });
    }
    
    function fetchKeywordAds(keyword) {
        fetchKeywordAdsWithHighlight(keyword, []);
    }
    
    function fetchKeywordAdsWithHighlight(keyword, newAdIds = []) {
        keywordAds.innerHTML = getSkeletonLoading(3);
        
        fetch(`/api/ads?keyword=${encodeURIComponent(keyword)}`)
            .then(response => response.json())
            .then(data => {
                displayKeywordAds(data.ads || [], newAdIds);
            })
            .catch(error => {
                showStatus('Error fetching ads: ' + error.message, 'error');
            });
    }
      function fetchSystemStats() {
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                console.log('Stats data received:', data);
                
                // Update stats in UI
                if (document.getElementById('stats-total-checks')) {
                    const element = document.getElementById('stats-total-checks');
                    console.log('Updating stats-total-checks from', element.textContent, 'to', data.checks.total);
                    element.textContent = data.checks.total;
                }
                if (document.getElementById('stats-avg-duration')) {
                    document.getElementById('stats-avg-duration').textContent = data.checks.avg_duration_ms + ' ms';
                }
                if (document.getElementById('stats-total-ads')) {
                    const element = document.getElementById('stats-total-ads');
                    console.log('Updating stats-total-ads from', element.textContent, 'to', data.ads.total_found);
                    element.textContent = data.ads.total_found;
                }
                if (document.getElementById('stats-uptime')) {
                    const uptime = Math.floor(data.system.uptime_seconds / 60);
                    const element = document.getElementById('stats-uptime');
                    console.log('Updating stats-uptime from', element.textContent, 'to', uptime + ' minutes');
                    element.textContent = uptime + ' minutes';
                }
                
                // Update detailed stats in modal
                if (document.getElementById('stats-total-checks-detail')) {
                    document.getElementById('stats-total-checks-detail').textContent = data.checks.total;
                }
                if (document.getElementById('stats-total-ads-detail')) {
                    document.getElementById('stats-total-ads-detail').textContent = data.ads.total_found;
                }
                if (document.getElementById('stats-uptime-detail')) {
                    const uptime = Math.floor(data.system.uptime_seconds / 60);
                    document.getElementById('stats-uptime-detail').textContent = uptime + ' minutes';
                }
            })
            .catch(error => {
                console.error('Error fetching system stats:', error);
            });
    }
      function addKeyword() {
        const keyword = newKeywordInput.value.trim();
        
        if (!keyword) {
            showStatus('Please enter a keyword', 'error');
            return;
        }
        
        if (keywords.includes(keyword)) {
            showStatus('This keyword is already being tracked', 'error');
            return;
        }
        
        fetch('/api/keywords', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ keyword })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    newKeywordInput.value = '';
                    showStatus('Keyword added successfully', 'success');
                    fetchKeywords();
                } else {
                    showStatus(data.error || 'Failed to add keyword', 'error');
                }
            })
            .catch(error => {
                showStatus('Error: ' + error.message, 'error');
            });
    }
    
    function performManualCheck() {
        console.log('Manual check button clicked');
        
        // Disable button and show loading state
        manualCheckBtn.disabled = true;
        const originalContent = manualCheckBtn.innerHTML;
        manualCheckBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i><span>Checking...</span>';
        
        showStatus('Checking for new ads...', 'info');
        
        console.log('Sending manual check request...');
        fetch('/api/manual-check')
            .then(response => {
                console.log('Manual check response received:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('Manual check data:', data);
                if (data.status === 'success') {
                    showStatus('Manual check completed successfully', 'success');
                    // Refresh the data
                    fetchRecentAds();
                    fetchSystemStats();
                } else {
                    showStatus(data.message || 'Manual check failed', 'error');
                }
            })
            .catch(error => {
                console.error('Manual check error:', error);
                showStatus('Error during manual check: ' + error.message, 'error');
            })
            .finally(() => {
                console.log('Manual check request completed');
                // Re-enable button and restore original content
                manualCheckBtn.disabled = false;
                manualCheckBtn.innerHTML = originalContent;
            });
    }
    
    function deleteKeyword(keyword) {
        if (!confirm(`Are you sure you want to stop tracking "${keyword}"?`)) {
            return;
        }
        
        fetch(`/api/keywords/${encodeURIComponent(keyword)}`, {
            method: 'DELETE'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showStatus('Keyword removed successfully', 'success');
                    fetchKeywords();
                } else {
                    showStatus(data.error || 'Failed to remove keyword', 'error');
                }
            })
            .catch(error => {
                showStatus('Error: ' + error.message, 'error');
            });
    }
    
    function updateKeywordsList() {
        if (!keywordsList) return;
        
        keywordsList.innerHTML = '';
        
        if (keywords.length === 0) {
            const emptyEl = document.createElement('p');
            emptyEl.className = 'text-sm text-gray-500';
            emptyEl.textContent = 'No keywords added yet';
            keywordsList.appendChild(emptyEl);
            return;
        }
        
        keywords.forEach(keyword => {
            const keywordEl = document.createElement('div');
            keywordEl.className = 'bg-secondary text-secondary-foreground py-1 px-3 rounded-full flex items-center text-sm';
            
            const textEl = document.createElement('span');
            textEl.textContent = keyword;
            keywordEl.appendChild(textEl);
            
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'ml-2 text-gray-500 hover:text-destructive';
            deleteBtn.innerHTML = '<i class="fas fa-times"></i>';
            deleteBtn.addEventListener('click', () => deleteKeyword(keyword));
            keywordEl.appendChild(deleteBtn);
            
            keywordsList.appendChild(keywordEl);
        });
    }
    
    function updateKeywordFilter() {
        if (!keywordFilter) return;
        
        keywordFilter.innerHTML = '';
        
        if (keywords.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'No keywords available';
            keywordFilter.appendChild(option);
            return;
        }
        
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Select a keyword';
        keywordFilter.appendChild(defaultOption);
        
        keywords.forEach(keyword => {
            const option = document.createElement('option');
            option.value = keyword;
            option.textContent = keyword;
            keywordFilter.appendChild(option);
        });
    }    function displayRecentAds(ads, newAdIds = []) {
        if (!recentAds) return;
        
        console.log('displayRecentAds called with newAdIds:', newAdIds);
        
        if (!ads || ads.length === 0) {
            recentAds.innerHTML = '<p class="col-span-full text-center text-gray-500">No recent ads found</p>';
            return;
        }
        
        recentAds.innerHTML = '';
        
        ads.forEach(item => {
            const isNewAd = newAdIds.includes(item.ad.id);
            console.log(`Ad ${item.ad.id}: isNewAd = ${isNewAd}`);
            const adCard = createAdCard(item.ad, item.keyword, isNewAd);
            recentAds.appendChild(adCard);
        });
    }
    
    function displayKeywordAds(ads, newAdIds = []) {
        if (!keywordAds) return;
        
        // Store current ads for search filtering
        currentKeywordAds = ads || [];
        filteredAds = currentKeywordAds;
        currentPage = 1;
        
        // Reset search
        if (adSearch) adSearch.value = '';
        if (clearSearch) clearSearch.classList.add('hidden');
        if (noResults) noResults.classList.add('hidden');
        
        if (!filteredAds || filteredAds.length === 0) {
            keywordAds.innerHTML = '<p class="col-span-full text-center text-gray-500">No ads found for this keyword</p>';
            if (resultsCount) resultsCount.textContent = '0 results';
            if (document.getElementById('pagination-controls')) {
                document.getElementById('pagination-controls').classList.add('hidden');
            }
            return;
        }
        
        // Store new ad IDs for highlighting during pagination
        keywordAds.dataset.newAdIds = JSON.stringify(newAdIds);
        
        // Update results count
        if (resultsCount) {
            resultsCount.textContent = `${filteredAds.length} results`;
        }
        
        // Render current page
        renderCurrentPage();
        
        // Update pagination controls
        updatePaginationControls();
    }
      function renderCurrentPage() {
        if (!keywordAds) return;
        
        // Calculate slice indices for current page
        const startIndex = (currentPage - 1) * adsPerPage;
        const endIndex = startIndex + adsPerPage;
        const adsToShow = filteredAds.slice(startIndex, endIndex);
        
        // Get new ad IDs from data attribute
        const newAdIds = JSON.parse(keywordAds.dataset.newAdIds || '[]');
        
        keywordAds.innerHTML = '';
        
        if (adsToShow.length === 0) {
            keywordAds.innerHTML = '<p class="col-span-full text-center text-gray-500">No ads to show on this page</p>';
            return;
        }
        
        adsToShow.forEach(ad => {
            const isNewAd = newAdIds.includes(ad.id);
            const adCard = createAdCard(ad, null, isNewAd);
            keywordAds.appendChild(adCard);
        });
    }
    
    function updatePaginationControls() {
        const paginationControls = document.getElementById('pagination-controls');
        if (!paginationControls) return;
        
        const totalPages = Math.ceil(filteredAds.length / adsPerPage);
        const currentPageEl = document.getElementById('current-page');
        const totalPagesEl = document.getElementById('total-pages');
        
        // Show pagination only if we need more than one page
        if (totalPages <= 1) {
            paginationControls.classList.add('hidden');
            return;
        }
        
        paginationControls.classList.remove('hidden');
        if (currentPageEl) currentPageEl.textContent = currentPage;
        if (totalPagesEl) totalPagesEl.textContent = totalPages;
        
        // Enable/disable prev/next buttons
        if (prevPageBtn) {
            prevPageBtn.disabled = currentPage === 1;
            prevPageBtn.className = currentPage === 1 
                ? 'btn btn-secondary opacity-50 cursor-not-allowed' 
                : 'btn btn-secondary';
        }
        
        if (nextPageBtn) {
            nextPageBtn.disabled = currentPage === totalPages;
            nextPageBtn.className = currentPage === totalPages 
                ? 'btn btn-secondary opacity-50 cursor-not-allowed' 
                : 'btn btn-secondary';
        }
    }
      function createAdCard(ad, keywordLabel = null, isNewAd = false) {
        if (!ad) return document.createElement('div');
        
        const card = document.createElement('div');
        card.className = 'card transition-all hover:shadow-md';
        card.setAttribute('data-ad-id', ad.id);        // Add pulsating effect for new ads (check both isNewAd parameter and ad.isNew property)
        if (isNewAd || ad.isNew) {
            card.classList.add('new-item-pulse');
            // Remove the effect after animation completes (10 seconds)
            setTimeout(() => {
                card.classList.remove('new-item-pulse');
            }, 10000);
        }
          const imageContainer = document.createElement('div');
        imageContainer.className = 'h-48 bg-gray-100 relative overflow-hidden';
        
        // NEW tag overlay (positioned over image)
        if (isNewAd || ad.isNew) {
            const newTag = document.createElement('div');
            newTag.className = 'absolute top-2 left-2 z-20 bg-red-500 text-white px-2 py-1 text-xs font-bold uppercase rounded shadow-lg';
            newTag.textContent = 'NEW';
            imageContainer.appendChild(newTag);
        }
        
        // Favorite button
        const favoriteBtn = document.createElement('button');
        favoriteBtn.className = 'favorite-btn absolute justify-center items-center flex w-10 h-10 top-2 right-2 z-10 text-xl p-2 bg-white bg-opacity-70 rounded-full hover:bg-opacity-100 transition-all';
        
        // Check if this ad is favorited
        const isFavorite = favoriteAds[ad.id];
        
        favoriteBtn.innerHTML = isFavorite 
            ? '<i class="fas fa-star text-yellow-500"></i>' 
            : '<i class="far fa-star text-gray-500"></i>';
        
        favoriteBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent card click event
            toggleFavorite(ad);
            
            // Update this button
            favoriteBtn.innerHTML = favoriteAds[ad.id] 
                ? '<i class="fas fa-star text-yellow-500"></i>' 
                : '<i class="far fa-star text-gray-500"></i>';
        });
        
        imageContainer.appendChild(favoriteBtn);
        
        if (ad.image_url) {
            const img = document.createElement('img');
            img.className = 'w-full h-full object-cover';
            img.src = ad.image_url;
            img.alt = ad.title || 'Advertisement image';
            img.onerror = function() {
                this.onerror = null;
                this.src = 'https://via.placeholder.com/300x200?text=No+Image';
            };
            imageContainer.appendChild(img);
        } else {
            const placeholder = document.createElement('div');
            placeholder.className = 'w-full h-full flex items-center justify-center text-gray-400';
            placeholder.innerHTML = '<i class="fas fa-image fa-3x"></i>';
            imageContainer.appendChild(placeholder);
        }
        
        card.appendChild(imageContainer);
        
        const content = document.createElement('div');
        content.className = 'p-4';        // Title and price
        const titleRow = document.createElement('div');
        titleRow.className = 'flex justify-between items-start mb-2';
          const title = document.createElement('h3');
        title.className = 'font-medium text-lg truncate flex-1';
        
        // Clean up and display title
        const cleanTitle = ad.title || '';
        // Try to extract a meaningful title from various sources
        let displayTitle = 'Bazos Advertisement';
        
        if (cleanTitle && cleanTitle !== "No title" && cleanTitle !== "Bazos.cz Advertisement") {
            displayTitle = cleanTitle;
        } else if (ad.description) {
            // If no title but we have a description, use first few words
            const firstWords = ad.description.split(' ').slice(0, 5).join(' ');
            if (firstWords.length > 0) {
                displayTitle = firstWords + '...';
            }
        }
        
        title.textContent = displayTitle;
        titleRow.appendChild(title);
        
        const price = document.createElement('div');
        price.className = 'font-bold text-primary whitespace-nowrap ml-2';
        price.textContent = ad.price || 'Price not listed';
        titleRow.appendChild(price);
          content.appendChild(titleRow);
          // Badges container for keyword badge
        const badgesContainer = document.createElement('div');
        badgesContainer.className = 'flex gap-2 mb-2';
        
        // Keyword badge if provided
        if (keywordLabel) {
            const badge = document.createElement('div');
            badge.className = 'badge bg-secondary text-secondary-foreground inline-block';
            badge.textContent = keywordLabel;
            badgesContainer.appendChild(badge);
        }
        
        // Only add badges container if it has content
        if (badgesContainer.children.length > 0) {
            content.appendChild(badgesContainer);
        }
        
        // Description
        const description = document.createElement('p');
        description.className = 'text-gray-600 text-sm mb-3 line-clamp-3';
        description.textContent = ad.description || 'No description available';
        content.appendChild(description);
          // Seller info
        const sellerInfo = document.createElement('div');
        sellerInfo.className = 'flex items-center justify-between text-xs text-gray-500 mt-3';        const dateAdded = document.createElement('div');
        // Use date_added field instead of seller_name
        let dateAddedText = ad.date_added || 'N/A';
        dateAdded.innerHTML = `<i class="fas fa-calendar mr-1"></i> ${dateAddedText}`;
        sellerInfo.appendChild(dateAdded);        
        // Note: location field has been removed as requested
        
        content.appendChild(sellerInfo);
        
        // Action row
        const actionRow = document.createElement('div');
        actionRow.className = 'mt-4 flex justify-end';
          // View button
        const viewBtn = document.createElement('a');
        viewBtn.className = 'btn btn-primary text-xs';
          // Ensure the link is properly formatted
        let adLink = ad.link || '#';
          // Fix various URL issues
        if (adLink !== '#') {
            // Fix double domain prefixes (bazos.czbazos.cz/...) but preserve subdomains
            if (adLink.includes('bazos.cz') && adLink.indexOf('bazos.cz') !== adLink.lastIndexOf('bazos.cz')) {
                // Check if it's a malformed URL with duplicate domains
                const bazosMatches = adLink.match(/([a-zA-Z0-9-]*\.)?bazos\.cz/g);
                if (bazosMatches && bazosMatches.length > 1) {
                    // Find the last occurrence that might include a subdomain
                    const lastBazosIndex = adLink.lastIndexOf('bazos.cz');
                    let startIndex = lastBazosIndex;
                    
                    // Look for subdomain before the last bazos.cz
                    const beforeBazos = adLink.substring(0, lastBazosIndex);
                    const subdomainMatch = beforeBazos.match(/([a-zA-Z0-9-]+)\.$/);
                    if (subdomainMatch) {
                        startIndex = lastBazosIndex - subdomainMatch[1].length - 1;
                    }
                    
                    adLink = 'https://' + adLink.substring(startIndex);
                }
            }
            
            // Fix URLs missing protocol (bazos.cz/...)
            if (!adLink.startsWith('http://') && !adLink.startsWith('https://')) {
                adLink = 'https://' + adLink.replace(/^\/\//, '');
            }
            
            // Clean any malformed URLs but preserve subdomains
            adLink = adLink.replace(/bazos\.cz(http|https):\/\//, 'bazos.cz/');
        }
        
        viewBtn.href = adLink;
        viewBtn.target = '_blank';
        viewBtn.rel = 'noopener noreferrer';
        viewBtn.innerHTML = '<i class="fas fa-external-link-alt mr-1"></i> View Ad';
        actionRow.appendChild(viewBtn);
        
        content.appendChild(actionRow);
        card.appendChild(content);
        
        return card;
    }
    
    function updateFavoriteButton(btn, ad) {
        if (!btn) return;
        
        const isFavorite = favoriteAds[ad.id];
        btn.innerHTML = isFavorite 
            ? '<i class="fas fa-star text-yellow-500"></i>' 
            : '<i class="far fa-star text-gray-500"></i>';
    }
    
    function updateChangesLog() {
        if (!changesList) return;
        
        if (changesLog.length === 0) {
            changesList.innerHTML = '<p class="text-sm text-gray-500">No changes detected yet. Changes will appear here when new ads are found or old ones are removed.</p>';
            return;
        }
        
        changesList.innerHTML = '';
        
        const filteredChanges = changesFilter === 'all' 
            ? changesLog 
            : changesLog.filter(change => change.type === changesFilter);
        
        if (filteredChanges.length === 0) {
            const message = changesFilter === 'new' 
                ? 'No new ads found yet.' 
                : 'No deleted ads detected yet.';
            changesList.innerHTML = `<p class="text-sm text-gray-500">${message}</p>`;
            return;
        }
        
        filteredChanges.forEach(change => {
            const changeItem = document.createElement('div');
            changeItem.className = `card p-4 transition-all ${change.type === 'new' ? 'border-l-4 border-green-500' : 'border-l-4 border-red-500'}`;
            
            const header = document.createElement('div');
            header.className = 'flex items-center justify-between mb-2';
            
            const typeIcon = change.type === 'new' 
                ? '<i class="fas fa-plus-circle text-green-500 mr-2"></i>' 
                : '<i class="fas fa-minus-circle text-red-500 mr-2"></i>';
            
            const action = change.type === 'new' ? 'New ad found' : 'Ad removed';
            
            header.innerHTML = `
                <div class="flex items-center">
                    ${typeIcon}
                    <span class="font-medium">${action} for keyword "${change.keyword}"</span>
                </div>
                <div class="text-xs text-gray-500">${change.timestamp}</div>
            `;
            
            changeItem.appendChild(header);
            
            // Ad summary
            const adSummary = document.createElement('div');
            adSummary.className = 'flex items-center mt-2 p-2 bg-gray-50 rounded';
            
            // Add small thumbnail if available
            if (change.ad && change.ad.image_url) {
                const img = document.createElement('img');
                img.className = 'w-16 h-16 object-cover rounded mr-3';
                img.src = change.ad.image_url;
                img.alt = change.ad.title || 'Advertisement image';
                img.onerror = function() {
                    this.onerror = null;
                    this.src = 'https://via.placeholder.com/80?text=No+Image';
                };
                adSummary.appendChild(img);
            } else {
                const imgPlaceholder = document.createElement('div');
                imgPlaceholder.className = 'w-16 h-16 bg-gray-200 rounded mr-3 flex items-center justify-center text-gray-400';
                imgPlaceholder.innerHTML = '<i class="fas fa-image"></i>';
                adSummary.appendChild(imgPlaceholder);
            }
            
            // Ad info
            const adInfo = document.createElement('div');
            adInfo.className = 'flex-1 min-w-0';
            
            if (change.ad) {
                const titlePrice = document.createElement('div');
                titlePrice.className = 'flex justify-between items-start';
                
                const title = document.createElement('h4');
                title.className = 'font-medium truncate';
                title.textContent = change.ad.title || 'Untitled';
                titlePrice.appendChild(title);
                
                const price = document.createElement('span');
                price.className = 'whitespace-nowrap font-bold text-primary ml-2';
                price.textContent = change.ad.price || 'Price not listed';
                titlePrice.appendChild(price);
                
                adInfo.appendChild(titlePrice);
                
                const description = document.createElement('p');
                description.className = 'text-sm text-gray-600 truncate';
                description.textContent = change.ad.description || 'No description available';
                adInfo.appendChild(description);
            }
            
            adSummary.appendChild(adInfo);
            
            // View button
            if (change.ad && change.ad.link) {
                const viewBtn = document.createElement('a');
                viewBtn.className = 'btn btn-secondary text-xs whitespace-nowrap ml-2';
                viewBtn.href = change.ad.link;
                viewBtn.target = '_blank';
                viewBtn.rel = 'noopener noreferrer';
                viewBtn.innerHTML = '<i class="fas fa-external-link-alt"></i>';
                adSummary.appendChild(viewBtn);
            }
            
            changeItem.appendChild(adSummary);
            changesList.appendChild(changeItem);
        });
    }
    
    function setChangesFilter(type) {
        changesFilter = type;
        
        // Update UI
        if (newAdsFilterBtn && deletedAdsFilterBtn && allChangesFilterBtn) {
            [newAdsFilterBtn, deletedAdsFilterBtn, allChangesFilterBtn].forEach(btn => {
                btn.className = 'btn btn-secondary';
            });
            
            if (type === 'new') {
                newAdsFilterBtn.className = 'btn btn-primary';
            } else if (type === 'deleted') {
                deletedAdsFilterBtn.className = 'btn btn-primary';
            } else {
                allChangesFilterBtn.className = 'btn btn-primary';
            }
        }
        
        updateChangesLog();
    }
    
    function showStatus(message, type = 'info') {
        if (!statusMessage || !statusBanner || !statusIcon) return;
        
        statusMessage.textContent = message;
        statusBanner.classList.remove('hidden');
        
        // Set appropriate colors based on type
        statusBanner.className = 'p-4 mb-4 border-l-4';
        
        if (type === 'success') {
            statusBanner.classList.add('bg-green-100', 'border-green-500');
            statusMessage.className = 'text-sm text-green-700';
            statusIcon.className = 'fas fa-info-circle text-green-500';
        } else if (type === 'error') {
            statusBanner.classList.add('bg-red-100', 'border-red-500');
            statusMessage.className = 'text-sm text-red-700';
            statusIcon.className = 'fas fa-info-circle text-red-500';
        } else {
            statusBanner.classList.add('bg-blue-100', 'border-blue-500');
            statusMessage.className = 'text-sm text-blue-700';
            statusIcon.className = 'fas fa-info-circle text-blue-500';
        }
        
        // Auto hide after 5 seconds
        setTimeout(() => {
            statusBanner.classList.add('hidden');
        }, 5000);
    }
    
    function playNotification() {
        if (!notificationManager) return;
        
        // Sound notification
        notificationManager.playSound();
        
        // Browser notification
        notificationManager.sendNotification('Bazos Ad Tracker', {
            body: 'New advertisements found!',
            icon: '/static/img/favicon.png'
        });
    }
    
    function getSkeletonLoading(count = 2) {
        let html = '';
        
        for (let i = 0; i < count; i++) {
            html += `
                <div class="card">
                    <div class="skeleton h-48 w-full"></div>
                    <div class="p-4">
                        <div class="skeleton h-6 w-3/4 mb-2"></div>
                        <div class="skeleton h-4 w-1/2 mb-4"></div>
                        <div class="skeleton h-20 w-full mb-4"></div>
                        <div class="skeleton h-6 w-1/3"></div>
                    </div>
                </div>
            `;
        }
        
        return html;
    }
    
    function toggleFavorite(ad) {
        if (!ad) return;
        
        // If the ad is already in favorites, remove it
        if (favoriteAds[ad.id]) {
            delete favoriteAds[ad.id];
            showStatus(`Removed "${ad.title}" from favorites`, 'info');
        } else {
            // Otherwise add it
            favoriteAds[ad.id] = {
                ad: ad,
                addedAt: new Date().toISOString()
            };
            showStatus(`Added "${ad.title}" to favorites`, 'success');
        }
        
        // Save to localStorage
        localStorage.setItem('favoriteAds', JSON.stringify(favoriteAds));
        
        // Update favorites tab if it's visible
        if (document.getElementById('favorites-tab').classList.contains('active')) {
            displayFavorites();
        }
        
        // Update any existing cards
        const existingCards = document.querySelectorAll(`[data-ad-id="${ad.id}"]`);
        existingCards.forEach(card => {
            const favBtn = card.querySelector('.favorite-btn');
            if (favBtn) {
                favBtn.innerHTML = favoriteAds[ad.id] 
                    ? '<i class="fas fa-star text-yellow-500"></i>' 
                    : '<i class="far fa-star text-gray-500"></i>';
            }
        });
    }
      function displayFavorites() {
        const favoritesContainer = document.getElementById('favorites-container');
        const noFavoritesMsg = document.getElementById('no-favorites');
        
        if (!favoritesContainer || !noFavoritesMsg) return;
        
        // Convert object to array and sort by addedAt
        const favoritesList = Object.values(favoriteAds)
            .sort((a, b) => new Date(b.addedAt) - new Date(a.addedAt));
        
        if (favoritesList.length === 0) {
            favoritesContainer.innerHTML = '';
            noFavoritesMsg.classList.remove('hidden');
            return;
        }
        
        noFavoritesMsg.classList.add('hidden');
        favoritesContainer.innerHTML = '';
        
        favoritesList.forEach(item => {
            const adCard = createAdCard(item.ad, null, false);
            favoritesContainer.appendChild(adCard);
        });
    }
});
