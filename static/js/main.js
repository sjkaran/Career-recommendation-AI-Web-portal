/**
 * AI Career Platform - Main JavaScript
 * Common functionality and utilities
 */

// Global app object
window.CareerPlatform = {
    // Configuration
    config: {
        apiBaseUrl: '/api',
        debounceDelay: 300,
        animationDuration: 300,
        supportedLanguages: ['en', 'or']
    },
    
    // Utility functions
    utils: {
        // Debounce function for search inputs
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        // Format date for display
        formatDate: function(dateString) {
            const options = { year: 'numeric', month: 'short', day: 'numeric' };
            return new Date(dateString).toLocaleDateString('en-US', options);
        },
        
        // Show loading spinner
        showLoading: function(element) {
            const spinner = '<span class="loading-spinner me-2"></span>';
            element.innerHTML = spinner + element.textContent;
            element.disabled = true;
        },
        
        // Hide loading spinner
        hideLoading: function(element, originalText) {
            element.innerHTML = originalText;
            element.disabled = false;
        },
        
        // Show toast notification
        showToast: function(message, type = 'info') {
            const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
            const toast = this.createToast(message, type);
            toastContainer.appendChild(toast);
            
            // Show toast
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
            
            // Remove from DOM after hiding
            toast.addEventListener('hidden.bs.toast', () => {
                toast.remove();
            });
        },
        
        // Create toast container if it doesn't exist
        createToastContainer: function() {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1055';
            document.body.appendChild(container);
            return container;
        },
        
        // Create toast element
        createToast: function(message, type) {
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.setAttribute('role', 'alert');
            
            const iconMap = {
                success: 'bi-check-circle-fill text-success',
                error: 'bi-exclamation-triangle-fill text-danger',
                warning: 'bi-exclamation-triangle-fill text-warning',
                info: 'bi-info-circle-fill text-info'
            };
            
            toast.innerHTML = `
                <div class="toast-header">
                    <i class="bi ${iconMap[type] || iconMap.info} me-2"></i>
                    <strong class="me-auto">Notification</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            `;
            
            return toast;
        },
        
        // Validate email format
        isValidEmail: function(email) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(email);
        },
        
        // Validate phone number format
        isValidPhone: function(phone) {
            const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
            return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
        },
        
        // Get current language from localStorage or default
        getCurrentLanguage: function() {
            return localStorage.getItem('preferred_language') || 'en';
        },
        
        // Set language preference
        setLanguagePreference: function(languageCode) {
            if (CareerPlatform.config.supportedLanguages.includes(languageCode)) {
                localStorage.setItem('preferred_language', languageCode);
                return true;
            }
            return false;
        },
        
        // Detect browser language
        detectBrowserLanguage: function() {
            const browserLang = navigator.language || navigator.userLanguage;
            const langCode = browserLang.split('-')[0].toLowerCase();
            return CareerPlatform.config.supportedLanguages.includes(langCode) ? langCode : 'en';
        }
    },
    
    // Language management
    language: {
        // Initialize language detection and persistence
        init: function() {
            // Check if user has a stored preference
            let preferredLang = CareerPlatform.utils.getCurrentLanguage();
            
            // If no preference stored, detect from browser
            if (!localStorage.getItem('preferred_language')) {
                preferredLang = CareerPlatform.utils.detectBrowserLanguage();
                CareerPlatform.utils.setLanguagePreference(preferredLang);
            }
            
            // Update HTML lang attribute
            document.documentElement.lang = preferredLang;
        },
        
        // Switch language
        switchLanguage: function(languageCode) {
            if (CareerPlatform.utils.setLanguagePreference(languageCode)) {
                // Show loading indicator
                const currentLangElement = document.querySelector('.navbar-nav .dropdown-toggle');
                if (currentLangElement) {
                    CareerPlatform.utils.showLoading(currentLangElement);
                }
                
                // Redirect to set language endpoint
                window.location.href = `/set-language/${languageCode}`;
                return true;
            }
            return false;
        },
        
        // Get language display name
        getLanguageName: function(languageCode) {
            const languageNames = {
                'en': 'English',
                'or': 'ଓଡ଼ିଆ'
            };
            return languageNames[languageCode] || languageCode;
        }
    },
    
    // API helper functions
    api: {
        // Generic API request function
        request: async function(endpoint, options = {}) {
            const url = `${CareerPlatform.config.apiBaseUrl}${endpoint}`;
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json',
                },
            };
            
            // Add auth token if available
            const token = localStorage.getItem('authToken');
            if (token) {
                defaultOptions.headers['Authorization'] = `Bearer ${token}`;
            }
            
            const config = { ...defaultOptions, ...options };
            
            try {
                const response = await fetch(url, config);
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.message || 'API request failed');
                }
                
                return data;
            } catch (error) {
                console.error('API Error:', error);
                CareerPlatform.utils.showToast(error.message, 'error');
                throw error;
            }
        },
        
        // GET request
        get: function(endpoint) {
            return this.request(endpoint, { method: 'GET' });
        },
        
        // POST request
        post: function(endpoint, data) {
            return this.request(endpoint, {
                method: 'POST',
                body: JSON.stringify(data)
            });
        },
        
        // PUT request
        put: function(endpoint, data) {
            return this.request(endpoint, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
        },
        
        // DELETE request
        delete: function(endpoint) {
            return this.request(endpoint, { method: 'DELETE' });
        }
    },
    
    // Form validation
    validation: {
        // Validate form fields
        validateForm: function(form) {
            const fields = form.querySelectorAll('[required]');
            let isValid = true;
            
            fields.forEach(field => {
                if (!this.validateField(field)) {
                    isValid = false;
                }
            });
            
            return isValid;
        },
        
        // Validate individual field
        validateField: function(field) {
            const value = field.value.trim();
            const type = field.type;
            let isValid = true;
            let message = '';
            
            // Check if required field is empty
            if (field.hasAttribute('required') && !value) {
                isValid = false;
                message = 'This field is required';
            }
            // Email validation
            else if (type === 'email' && value && !CareerPlatform.utils.isValidEmail(value)) {
                isValid = false;
                message = 'Please enter a valid email address';
            }
            // Phone validation
            else if (field.name === 'phone' && value && !CareerPlatform.utils.isValidPhone(value)) {
                isValid = false;
                message = 'Please enter a valid phone number';
            }
            // Password strength (minimum 8 characters)
            else if (type === 'password' && value && value.length < 8) {
                isValid = false;
                message = 'Password must be at least 8 characters long';
            }
            
            // Show/hide validation feedback
            this.showFieldValidation(field, isValid, message);
            
            return isValid;
        },
        
        // Show field validation feedback
        showFieldValidation: function(field, isValid, message) {
            // Remove existing feedback
            const existingFeedback = field.parentNode.querySelector('.invalid-feedback');
            if (existingFeedback) {
                existingFeedback.remove();
            }
            
            // Update field classes
            field.classList.remove('is-valid', 'is-invalid');
            
            if (!isValid && message) {
                field.classList.add('is-invalid');
                
                // Add feedback message
                const feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                feedback.textContent = message;
                field.parentNode.appendChild(feedback);
            } else if (isValid && field.value.trim()) {
                field.classList.add('is-valid');
            }
        }
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize language support
    CareerPlatform.language.init();
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add real-time validation to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const fields = form.querySelectorAll('input, select, textarea');
        fields.forEach(field => {
            field.addEventListener('blur', function() {
                CareerPlatform.validation.validateField(this);
            });
            
            // Real-time validation for certain field types
            if (field.type === 'email' || field.name === 'phone') {
                field.addEventListener('input', CareerPlatform.utils.debounce(function() {
                    CareerPlatform.validation.validateField(field);
                }, CareerPlatform.config.debounceDelay));
            }
        });
        
        // Form submission validation
        form.addEventListener('submit', function(e) {
            if (!CareerPlatform.validation.validateForm(this)) {
                e.preventDefault();
                e.stopPropagation();
                CareerPlatform.utils.showToast('Please fix the errors in the form', 'error');
            }
        });
    });
    
    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card, .dashboard-card, .job-card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, { threshold: 0.1 });
    
    cards.forEach(card => {
        observer.observe(card);
    });
    
    // Mobile-specific optimizations
    CareerPlatform.mobile.init();
});

// Mobile optimization module
CareerPlatform.mobile = {
    // Initialize mobile optimizations
    init: function() {
        this.setupTouchOptimizations();
        this.setupViewportOptimizations();
        this.setupPerformanceOptimizations();
    },
    
    // Setup touch-friendly interactions
    setupTouchOptimizations: function() {
        // Add touch feedback to buttons
        const buttons = document.querySelectorAll('.btn, .card, .dropdown-item');
        buttons.forEach(button => {
            button.addEventListener('touchstart', function() {
                this.style.transform = 'scale(0.98)';
            });
            
            button.addEventListener('touchend', function() {
                this.style.transform = 'scale(1)';
            });
        });
        
        // Improve dropdown behavior on touch devices
        const dropdowns = document.querySelectorAll('.dropdown-toggle');
        dropdowns.forEach(dropdown => {
            dropdown.addEventListener('touchstart', function(e) {
                // Prevent double-tap zoom on dropdown toggles
                e.preventDefault();
                this.click();
            });
        });
        
        // Add swipe gesture support for cards
        this.addSwipeSupport();
    },
    
    // Setup viewport optimizations
    setupViewportOptimizations: function() {
        // Prevent zoom on input focus (iOS)
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.type !== 'range' && input.type !== 'checkbox' && input.type !== 'radio') {
                input.style.fontSize = '16px'; // Prevents zoom on iOS
            }
        });
        
        // Handle orientation changes
        window.addEventListener('orientationchange', function() {
            setTimeout(() => {
                // Recalculate layout after orientation change
                window.scrollTo(0, 0);
                
                // Trigger resize event for charts and other components
                window.dispatchEvent(new Event('resize'));
            }, 100);
        });
    },
    
    // Setup performance optimizations for mobile
    setupPerformanceOptimizations: function() {
        // Lazy load images
        const images = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
        
        // Debounce scroll events for better performance
        let scrollTimeout;
        window.addEventListener('scroll', function() {
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }
            scrollTimeout = setTimeout(() => {
                // Handle scroll-based animations or updates
                document.body.classList.toggle('scrolled', window.scrollY > 100);
            }, 16); // ~60fps
        });
        
        // Optimize animations for mobile
        if (window.matchMedia('(max-width: 768px)').matches) {
            // Reduce animation duration on mobile
            document.documentElement.style.setProperty('--animation-duration', '0.2s');
        }
    },
    
    // Add swipe gesture support
    addSwipeSupport: function() {
        let startX, startY, distX, distY;
        const threshold = 100; // Minimum distance for swipe
        
        document.addEventListener('touchstart', function(e) {
            const touch = e.touches[0];
            startX = touch.clientX;
            startY = touch.clientY;
        });
        
        document.addEventListener('touchmove', function(e) {
            if (!startX || !startY) return;
            
            const touch = e.touches[0];
            distX = touch.clientX - startX;
            distY = touch.clientY - startY;
        });
        
        document.addEventListener('touchend', function(e) {
            if (!startX || !startY) return;
            
            // Check if it's a horizontal swipe
            if (Math.abs(distX) > Math.abs(distY) && Math.abs(distX) > threshold) {
                const target = e.target.closest('.swipeable');
                if (target) {
                    if (distX > 0) {
                        // Swipe right
                        target.dispatchEvent(new CustomEvent('swiperight'));
                    } else {
                        // Swipe left
                        target.dispatchEvent(new CustomEvent('swipeleft'));
                    }
                }
            }
            
            // Reset values
            startX = startY = distX = distY = null;
        });
    },
    
    // Check if device is mobile
    isMobile: function() {
        return window.matchMedia('(max-width: 768px)').matches;
    },
    
    // Check if device supports touch
    isTouch: function() {
        return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    }
};

// Export for use in other scripts
window.CP = window.CareerPlatform;