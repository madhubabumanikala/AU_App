// AU Event Information System - Main JavaScript

// Document Ready Function
$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Initialize date pickers
    if($('.date-picker').length) {
        $('.date-picker').flatpickr({
            dateFormat: 'Y-m-d',
            minDate: 'today'
        });
    }

    // Initialize time pickers
    if($('.time-picker').length) {
        $('.time-picker').flatpickr({
            enableTime: true,
            noCalendar: true,
            dateFormat: 'H:i',
            time_24hr: true
        });
    }

    // Handle event registration
    $('.register-event-btn').click(function(e) {
        e.preventDefault();
        var eventId = $(this).data('event-id');
        var btn = $(this);
        
        btn.prop('disabled', true);
        btn.html('<span class="loading-spinner"></span> Registering...');
        
        $.ajax({
            url: '/events/' + eventId + '/register',
            method: 'POST',
            success: function(response) {
                if(response.success) {
                    btn.removeClass('btn-primary').addClass('btn-success');
                    btn.html('<i class="fas fa-check"></i> Registered');
                    btn.prop('disabled', true);
                    
                    // Update registration status
                    $('.registration-status').removeClass('not-registered').addClass('registered').text('Registered');
                    
                    // Show success message
                    showAlert('success', response.message);
                    
                    // Update registered count
                    var countElement = $('.registered-count');
                    var currentCount = parseInt(countElement.text());
                    countElement.text(currentCount + 1);
                } else {
                    showAlert('error', response.error);
                    btn.prop('disabled', false);
                    btn.html('<i class="fas fa-user-plus"></i> Register');
                }
            },
            error: function(xhr) {
                var error = xhr.responseJSON ? xhr.responseJSON.error : 'Registration failed';
                showAlert('error', error);
                btn.prop('disabled', false);
                btn.html('<i class="fas fa-user-plus"></i> Register');
            }
        });
    });

    // Handle event unregistration
    $('.unregister-event-btn').click(function(e) {
        e.preventDefault();
        var eventId = $(this).data('event-id');
        var btn = $(this);
        
        if(!confirm('Are you sure you want to unregister from this event?')) {
            return;
        }
        
        btn.prop('disabled', true);
        btn.html('<span class="loading-spinner"></span> Unregistering...');
        
        $.ajax({
            url: '/events/' + eventId + '/unregister',
            method: 'POST',
            success: function(response) {
                if(response.success) {
                    btn.removeClass('btn-warning').addClass('btn-primary');
                    btn.html('<i class="fas fa-user-plus"></i> Register');
                    btn.removeClass('unregister-event-btn').addClass('register-event-btn');
                    
                    // Update registration status
                    $('.registration-status').removeClass('registered').addClass('not-registered').text('Not Registered');
                    
                    // Show success message
                    showAlert('success', response.message);
                    
                    // Update registered count
                    var countElement = $('.registered-count');
                    var currentCount = parseInt(countElement.text());
                    countElement.text(currentCount - 1);
                } else {
                    showAlert('error', response.error);
                    btn.prop('disabled', false);
                    btn.html('<i class="fas fa-user-minus"></i> Unregister');
                }
            },
            error: function(xhr) {
                var error = xhr.responseJSON ? xhr.responseJSON.error : 'Unregistration failed';
                showAlert('error', error);
                btn.prop('disabled', false);
                btn.html('<i class="fas fa-user-minus"></i> Unregister');
            }
        });
    });

    // Handle notification marking as read
    $('.mark-notification-read').click(function(e) {
        e.preventDefault();
        var notificationId = $(this).data('notification-id');
        var element = $(this).closest('.notification-item');
        
        $.ajax({
            url: '/notifications/' + notificationId + '/read',
            method: 'POST',
            success: function(response) {
                if(response.success) {
                    element.removeClass('unread').addClass('read');
                    element.find('.notification-badge').remove();
                    
                    // Update notification count
                    var countElement = $('.notification-count');
                    var currentCount = parseInt(countElement.text());
                    if(currentCount > 0) {
                        countElement.text(currentCount - 1);
                        if(currentCount - 1 === 0) {
                            countElement.hide();
                        }
                    }
                }
            }
        });
    });

    // Handle search functionality
    $('#search-form').submit(function(e) {
        e.preventDefault();
        var query = $('#search-input').val().trim();
        
        if(query) {
            window.location.href = '/events/search?q=' + encodeURIComponent(query);
        }
    });

    // Handle filter functionality
    $('#filter-form select').change(function() {
        $('#filter-form').submit();
    });

    // Handle calendar navigation
    $('.calendar-nav').click(function(e) {
        e.preventDefault();
        var year = $(this).data('year');
        var month = $(this).data('month');
        
        window.location.href = '/calendar?year=' + year + '&month=' + month;
    });

    // Handle attendance marking
    $('.mark-attendance').change(function() {
        var registrationId = $(this).data('registration-id');
        var attendanceStatus = $(this).is(':checked');
        var element = $(this).closest('tr');
        
        $.ajax({
            url: '/admin/attendance/' + registrationId + '/mark',
            method: 'POST',
            data: {
                registration_id: registrationId,
                attendance_status: attendanceStatus
            },
            success: function(response) {
                if(response.success) {
                    if(attendanceStatus) {
                        element.addClass('table-success');
                        element.find('.attendance-status').text('Present').removeClass('text-danger').addClass('text-success');
                    } else {
                        element.removeClass('table-success');
                        element.find('.attendance-status').text('Absent').removeClass('text-success').addClass('text-danger');
                    }
                    showAlert('success', 'Attendance updated successfully');
                } else {
                    showAlert('error', response.error);
                    $(this).prop('checked', !attendanceStatus);
                }
            }.bind(this),
            error: function() {
                showAlert('error', 'Failed to update attendance');
                $(this).prop('checked', !attendanceStatus);
            }.bind(this)
        });
    });

    // Handle image preview for file uploads
    $('.poster-upload').change(function(e) {
        var file = e.target.files[0];
        var reader = new FileReader();
        
        reader.onload = function(e) {
            $('#poster-preview').attr('src', e.target.result).show();
        };
        
        if(file) {
            reader.readAsDataURL(file);
        }
    });

    // Handle form validation
    $('form').submit(function(e) {
        var form = $(this);
        var isValid = true;
        
        form.find('.form-control[required]').each(function() {
            if(!$(this).val().trim()) {
                $(this).addClass('is-invalid');
                isValid = false;
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        
        if(!isValid) {
            e.preventDefault();
            showAlert('error', 'Please fill in all required fields');
        }
    });

    // Clear validation on input
    $('.form-control').on('input', function() {
        $(this).removeClass('is-invalid');
    });

    // Handle dynamic content loading
    $('.load-more').click(function(e) {
        e.preventDefault();
        var btn = $(this);
        var page = btn.data('page') + 1;
        var url = btn.data('url') + '?page=' + page;
        
        btn.prop('disabled', true);
        btn.html('<span class="loading-spinner"></span> Loading...');
        
        $.get(url, function(data) {
            var content = $(data).find('.dynamic-content').html();
            $('.dynamic-content').append(content);
            
            btn.data('page', page);
            btn.prop('disabled', false);
            btn.html('Load More');
            
            // Hide button if no more content
            if($(data).find('.load-more').length === 0) {
                btn.hide();
            }
        });
    });

    // Handle real-time notifications (if WebSocket is available)
    if(typeof io !== 'undefined') {
        var socket = io();
        
        socket.on('connect', function() {
            // WebSocket connected successfully
        });
        
        socket.on('notification', function(data) {
            showNotification(data.title, data.message, data.type);
            
            // Update notification count
            var countElement = $('.notification-count');
            var currentCount = parseInt(countElement.text());
            countElement.text(currentCount + 1).show();
        });
        
        socket.on('event_update', function(data) {
            if(window.location.pathname.includes('/events/')) {
                // Refresh event details if on event page
                location.reload();
            }
        });
    }
});

// Utility Functions
function showAlert(type, message) {
    var alertClass = type === 'error' ? 'danger' : type;
    var alert = '<div class="alert alert-' + alertClass + ' alert-dismissible fade show" role="alert">' +
                message +
                '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
                '</div>';
    
    $('.alert-container').html(alert);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
}

function showNotification(title, message, type) {
    if('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, {
            body: message,
            icon: '/static/images/logo.png'
        });
    }
}

function confirmAction(message, callback) {
    if(confirm(message)) {
        callback();
    }
}

function formatDateTime(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Search with debouncing
var debouncedSearch = debounce(function(query) {
    if(query.length >= 3) {
        $.get('/api/search/events?q=' + encodeURIComponent(query), function(data) {
            if(data.success) {
                // Update search results
                updateSearchResults(data.events);
            }
        });
    }
}, 300);

$('#search-input').on('input', function() {
    var query = $(this).val();
    debouncedSearch(query);
});

function updateSearchResults(events) {
    var resultsContainer = $('#search-results');
    resultsContainer.empty();
    
    if(events.length === 0) {
        resultsContainer.html('<p class="text-muted">No events found</p>');
        return;
    }
    
    events.forEach(function(event) {
        var eventCard = '<div class="col-md-6 col-lg-4 mb-3">' +
            '<div class="card event-card">' +
            '<div class="card-body">' +
            '<h6 class="card-title">' + event.title + '</h6>' +
            '<p class="card-text">' + event.description.substring(0, 100) + '...</p>' +
            '<p class="text-muted"><i class="fas fa-calendar"></i> ' + event.date + '</p>' +
            '<p class="text-muted"><i class="fas fa-clock"></i> ' + event.time + '</p>' +
            '<p class="text-muted"><i class="fas fa-map-marker-alt"></i> ' + event.location + '</p>' +
            '<a href="/events/' + event.id + '" class="btn btn-primary btn-sm">View Details</a>' +
            '</div>' +
            '</div>' +
            '</div>';
        
        resultsContainer.append(eventCard);
    });
}

// Request notification permission
if('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}
