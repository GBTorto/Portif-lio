// Global utilities and functions
const portfolioUtils = {
    showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }

        // Create toast
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white border-0';
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        // Set background color based on type
        const bgClass = {
            'success': 'bg-success',
            'error': 'bg-danger',
            'warning': 'bg-warning',
            'info': 'bg-primary'
        }[type] || 'bg-primary';
        
        toast.classList.add(bgClass);
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Show toast
        const bootstrapToast = new bootstrap.Toast(toast);
        bootstrapToast.show();
        
        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    smoothScrollTo(element, offset = 0) {
        const targetPosition = element.offsetTop - offset;
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    },

    debounce(func, wait, immediate) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func.apply(this, args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(this, args);
        };
    }
};

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    portfolioUtils.initializeTooltips();

    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            if (href && href !== '#') {
                const target = document.querySelector(href);
                if (target) {
                    portfolioUtils.smoothScrollTo(target, 100);
                }
            }
        });
    });

    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert:not(.alert-permanent)');
    flashMessages.forEach(function(alert) {
        setTimeout(function() {
            const bootstrapAlert = new bootstrap.Alert(alert);
            bootstrapAlert.close();
        }, 5000);
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Enhanced search functionality
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        const debouncedSearch = portfolioUtils.debounce(function() {
            // Optional: Add real-time search suggestions here
            console.log('Search term:', searchInput.value);
        }, 300);
        
        searchInput.addEventListener('input', debouncedSearch);
    }

    // Lazy loading for images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
});



// Social Network Management
const socialNetworkManager = {
    confirmationDialog: null,
    
    addNetwork() {
        const form = document.getElementById('social-network-form');
        const formData = new FormData(form);
        
        fetch('/add_social_network', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('meta[name=csrf-token]').getAttribute('content')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                portfolioUtils.showToast(data.message, 'success');
                this.refreshSocialNetworks();
                form.reset();
            } else {
                portfolioUtils.showToast(data.message, 'error');
            }
        })
        .catch(error => {
            portfolioUtils.showToast('An error occurred', 'error');
            console.error('Error:', error);
        });
    },
    
    removeNetwork(networkId, showConfirmation = true) {
        if (showConfirmation && !this.checkSkipConfirmation()) {
            this.showConfirmationDialog(networkId);
            return;
        }
        
        fetch(`/remove_social_network/${networkId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': document.querySelector('meta[name=csrf-token]').getAttribute('content')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                portfolioUtils.showToast(data.message, 'success');
                this.refreshSocialNetworks();
            } else {
                portfolioUtils.showToast(data.message, 'error');
            }
        })
        .catch(error => {
            portfolioUtils.showToast('An error occurred', 'error');
            console.error('Error:', error);
        });
    },
    
    showConfirmationDialog(networkId) {
        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'confirmation-overlay';
        
        // Create dialog
        const dialog = document.createElement('div');
        dialog.className = 'confirmation-dialog';
        dialog.innerHTML = `
            <h5 class="mb-3">Confirm Deletion</h5>
            <p class="mb-4">Are you sure you want to remove this social network?</p>
            <div class="form-check mb-3">
                <input class="form-check-input" type="checkbox" id="dontAskAgain">
                <label class="form-check-label" for="dontAskAgain">
                    Don't ask again
                </label>
            </div>
            <div class="d-flex gap-2 justify-content-end">
                <button class="btn btn-secondary" onclick="socialNetworkManager.closeConfirmationDialog()">Cancel</button>
                <button class="btn btn-outline-danger" onclick="socialNetworkManager.confirmRemove(${networkId})">Confirm</button>
            </div>
        `;
        
        this.confirmationDialog = { overlay, dialog };
        document.body.appendChild(overlay);
        document.body.appendChild(dialog);
        
        // Close on overlay click
        overlay.addEventListener('click', () => this.closeConfirmationDialog());
    },
    
    closeConfirmationDialog() {
        if (this.confirmationDialog) {
            document.body.removeChild(this.confirmationDialog.overlay);
            document.body.removeChild(this.confirmationDialog.dialog);
            this.confirmationDialog = null;
        }
    },
    
    confirmRemove(networkId) {
        const dontAskAgain = document.getElementById('dontAskAgain').checked;
        if (dontAskAgain) {
            localStorage.setItem('skipSocialNetworkConfirmation', 'true');
        }
        
        this.closeConfirmationDialog();
        this.removeNetwork(networkId, false);
    },
    
    checkSkipConfirmation() {
        return localStorage.getItem('skipSocialNetworkConfirmation') === 'true';
    },
    
    refreshSocialNetworks() {
        // Reload the social networks section
        window.location.reload();
    }
};

// Make functions globally available
window.socialNetworkManager = socialNetworkManager;
window.portfolioUtils = portfolioUtils;