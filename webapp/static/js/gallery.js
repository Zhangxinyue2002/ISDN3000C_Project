/**
 * Gallery JavaScript
 * Handles image loading, filtering, and display
 */

let currentFilters = {
    category: '',
    limit: 50,
    offset: 0,
    order: 'desc'
};

// Auto-refresh settings
let autoRefreshEnabled = true;
let autoRefreshInterval = null;
let lastImageCount = 0;

/**
 * Start auto-refresh
 */
function startAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    // Refresh every 3 seconds
    autoRefreshInterval = setInterval(function() {
        if (autoRefreshEnabled) {
            checkForNewImages();
        }
    }, 3000);
}

/**
 * Stop auto-refresh
 */
function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

/**
 * Toggle auto-refresh
 */
function toggleAutoRefresh() {
    autoRefreshEnabled = !autoRefreshEnabled;
    const btn = $('#autoRefreshBtn');
    
    if (autoRefreshEnabled) {
        btn.removeClass('btn-outline-secondary').addClass('btn-success');
        btn.html('<i class="bi bi-arrow-clockwise"></i> Auto-Refresh ON');
    } else {
        btn.removeClass('btn-success').addClass('btn-outline-secondary');
        btn.html('<i class="bi bi-arrow-clockwise"></i> Auto-Refresh OFF');
    }
}

/**
 * Check for new images without full reload
 */
function checkForNewImages() {
    $.get('/api/images?limit=1&order=desc')
        .done(function(response) {
            if (response.success && response.count > 0) {
                const currentCount = response.count;
                
                // If count changed, reload gallery
                if (lastImageCount > 0 && currentCount !== lastImageCount) {
                    loadGallery();
                    updateStatistics();
                }
                
                lastImageCount = currentCount;
            }
        })
        .fail(function() {
            // Silent fail for auto-refresh check
        });
}

/**
 * Load gallery with current filters
 */
function loadGallery() {
    $('#loading').show();
    $('#imageGrid').hide();
    $('#noImages').hide();
    
    const params = new URLSearchParams(currentFilters);
    
    $.get('/api/images?' + params.toString())
        .done(function(response) {
            $('#loading').hide();
            
            if (response.success && response.images.length > 0) {
                displayImages(response.images);
                $('#imageGrid').show();
            } else {
                $('#noImages').show();
            }
        })
        .fail(function(xhr) {
            $('#loading').hide();
            $('#noImages').show();
            // Silent fail on initial load - don't show error popup
            console.error('Failed to load images:', xhr);
        });
}

/**
 * Display images in grid
 */
function displayImages(images) {
    const grid = $('#imageGrid');
    grid.empty();
    
    images.forEach(function(image) {
        const col = $('<div>')
            .addClass('col-12 col-sm-6 col-md-4 col-lg-3 col-xl-2 mb-3');
        
        const item = $('<div>')
            .addClass('gallery-item')
            .attr('onclick', `showImageModal(${image.id})`);
        
        // Use lazy loading for images
        const img = $('<img>')
            .attr('data-src', `/api/image/${image.id}`)
            .attr('alt', image.filename)
            .addClass('img-fluid lazy-load')
            .css('background', '#f0f0f0');
        
        // Load image immediately for first 20, lazy load rest
        const imageIndex = images.indexOf(image);
        if (imageIndex < 20) {
            img.attr('src', `/api/image/${image.id}`);
        }
        
        // Add badge for fall/emergency
        let badge = '';
        if (image.fall_detected) {
            badge = '<span class="badge bg-danger gallery-badge">FALL</span>';
        } else if (image.emergency_triggered) {
            badge = '<span class="badge bg-warning gallery-badge">EMERGENCY</span>';
        }
        
        // Add timestamp
        const timestamp = new Date(image.timestamp).toLocaleString();
        const timestampDiv = $('<div>')
            .addClass('gallery-timestamp')
            .text(timestamp);
        
        item.append(img);
        if (badge) {
            item.append(badge);
        }
        item.append(timestampDiv);
        
        col.append(item);
        grid.append(col);
    });
    
    // Implement lazy loading for images
    lazyLoadImages();
}

/**
 * Show image in modal
 */
function showImageModal(imageId) {
    $.get('/api/images')
        .done(function(response) {
            if (response.success) {
                const image = response.images.find(img => img.id === imageId);
                
                if (image) {
                    $('#modalImage').attr('src', `/api/image/${imageId}`);
                    $('#imageModalTitle').text(image.filename);
                    
                    // Build details
                    let details = `
                        <table class="table table-sm">
                            <tr><th>Filename:</th><td>${image.filename}</td></tr>
                            <tr><th>Timestamp:</th><td>${new Date(image.timestamp).toLocaleString()}</td></tr>
                            <tr><th>Category:</th><td>${image.category}</td></tr>
                            <tr><th>Fall Detected:</th><td>${image.fall_detected ? 'Yes' : 'No'}</td></tr>
                    `;
                    
                    if (image.confidence !== null) {
                        details += `<tr><th>Confidence:</th><td>${(image.confidence * 100).toFixed(1)}%</td></tr>`;
                    }
                    
                    if (image.breathing_detected !== null) {
                        details += `<tr><th>Breathing:</th><td>${image.breathing_detected ? 'Yes' : 'No'}</td></tr>`;
                    }
                    
                    details += '</table>';
                    
                    $('#imageDetails').html(details);
                    
                    // Show modal
                    const modal = new bootstrap.Modal(document.getElementById('imageModal'));
                    modal.show();
                }
            }
        });
}

/**
 * Apply filters
 */
function applyFilters() {
    currentFilters.category = $('#categoryFilter').val();
    currentFilters.limit = parseInt($('#limitSelect').val());
    currentFilters.order = $('#sortOrder').val();
    currentFilters.offset = 0;
    
    loadGallery();
}

/**
 * Confirm and reset filters
 */
function confirmReset() {
    showConfirm(
        'Are you sure you want to reset all filters to default values?',
        'Reset Filters',
        resetFilters
    );
}

/**
 * Reset filters
 */
function resetFilters() {
    $('#categoryFilter').val('');
    $('#sortOrder').val('desc');
    $('#limitSelect').val('50');
    
    currentFilters = {
        category: '',
        limit: 50,
        offset: 0,
        order: 'desc'
    };
    
    loadGallery();
}

/**
 * Refresh gallery
 */
function refreshGallery() {
    loadGallery();
    updateStatistics();
}

/**
 * Confirm and download all images
 */
function confirmDownload() {
    // Check if there are images first
    $.get('/api/images?limit=1')
        .done(function(response) {
            if (response.success && response.images.length > 0) {
                showConfirm(
                    'Download all captured images as a ZIP file?',
                    'Download Images',
                    downloadAllImages
                );
            } else {
                showWarning(
                    'There are no images to download yet.<br><br>' +
                    '<strong>What you can do:</strong><br>' +
                    '• Make sure the camera is connected and working<br>' +
                    '• Wait for the system to capture images automatically<br>' +
                    '• Check that the detection system is running',
                    'No Images to Download'
                );
            }
        })
        .fail(function(xhr) {
            showError(
                'Cannot check images right now. Please try again later.',
                'System Error'
            );
            console.error('Download check failed:', xhr);
        });
}

/**
 * Download all images
 */
function downloadAllImages() {
    const btn = event.target || document.activeElement;
    const originalText = btn.innerHTML;
    
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Preparing...';
    btn.disabled = true;
    
    // Trigger download
    window.location.href = '/api/download_all';
    
    // Reset button after 3 seconds
    setTimeout(function() {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }, 3000);
}

/**
 * Update statistics
 */
function updateStatistics() {
    $.get('/api/statistics')
        .done(function(response) {
            if (response.success) {
                const stats = response.statistics;
                
                $('#totalImages').text(stats.total_images || 0);
                $('#fallsDetected').text(stats.falls_detected || 0);
                $('#emergencies').text(stats.emergencies_triggered || 0);
                $('#storageSize').text((stats.total_size_mb || 0).toFixed(1) + ' MB');
            }
        })
        .fail(function(xhr) {
            console.error('Failed to load statistics:', xhr);
            // Only show error if it's not a 404 (no stats yet) and user actively needs this info
            // Silent fail for statistics as it's not critical for user operation
        });
}

/**
 * Format timestamp
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    // Less than 1 minute
    if (diff < 60000) {
        return 'Just now';
    }
    
    // Less than 1 hour
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    }
    
    // Less than 24 hours
    if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    }
    
    // Default to full date
    return date.toLocaleString();
}

/**
 * Format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Lazy load images
 */
function lazyLoadImages() {
    const lazyImages = document.querySelectorAll('img.lazy-load');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy-load');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(function(img) {
            imageObserver.observe(img);
        });
    } else {
        // Fallback for older browsers
        lazyImages.forEach(function(img) {
            img.src = img.dataset.src;
            img.classList.remove('lazy-load');
        });
    }
}

// Initialize on page load
$(document).ready(function() {
    loadGallery();
    updateStatistics();
    startAutoRefresh();
    
    // Update statistics every 10 seconds
    setInterval(updateStatistics, 10000);
});
