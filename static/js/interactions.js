// Interactive features for portfolio projects
document.addEventListener('DOMContentLoaded', function() {
    // Like functionality
    const likeButtons = document.querySelectorAll('.like-btn');
    likeButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (!this.dataset.projectId) return;
            
            const projectId = this.dataset.projectId;
            const icon = this.querySelector('i');
            const countEl = this.querySelector('.like-count');
            
            // Check if user is authenticated
            if (!document.body.dataset.userAuthenticated) {
                window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
                return;
            }
            
            // Optimistic UI update
            const isLiked = this.classList.contains('liked');
            if (isLiked) {
                this.classList.remove('liked');
                icon.className = 'fas fa-heart';
                if (countEl) {
                    countEl.textContent = parseInt(countEl.textContent) - 1;
                }
            } else {
                this.classList.add('liked');
                icon.className = 'fas fa-heart text-danger';
                if (countEl) {
                    countEl.textContent = parseInt(countEl.textContent) + 1;
                }
                // Add animation
                icon.classList.add('animate__animated', 'animate__pulse');
                setTimeout(() => icon.classList.remove('animate__animated', 'animate__pulse'), 1000);
            }
            
            // Send request to server
            fetch(`/project/${projectId}/like`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    // Revert on error
                    if (isLiked) {
                        this.classList.add('liked');
                        icon.className = 'fas fa-heart text-danger';
                        if (countEl) {
                            countEl.textContent = parseInt(countEl.textContent) + 1;
                        }
                    } else {
                        this.classList.remove('liked');
                        icon.className = 'fas fa-heart';
                        if (countEl) {
                            countEl.textContent = parseInt(countEl.textContent) - 1;
                        }
                    }
                    portfolioUtils.showToast(data.message || 'Error processing like', 'error');
                } else {
                    // Update with server data
                    if (countEl) {
                        countEl.textContent = data.like_count;
                    }
                    portfolioUtils.showToast(data.message, 'success');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Revert on error
                if (isLiked) {
                    this.classList.add('liked');
                    icon.className = 'fas fa-heart text-danger';
                    if (countEl) {
                        countEl.textContent = parseInt(countEl.textContent) + 1;
                    }
                } else {
                    this.classList.remove('liked');
                    icon.className = 'fas fa-heart';
                    if (countEl) {
                        countEl.textContent = parseInt(countEl.textContent) - 1;
                    }
                }
                portfolioUtils.showToast('Error processing like', 'error');
            });
        });
    });

    // Comment form submission
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            const textarea = this.querySelector('textarea[name="content"]');
            
            // Disable form while submitting
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Posting...';
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Reset form
                    textarea.value = '';
                    portfolioUtils.showToast('Comment posted successfully!', 'success');
                    
                    // Add new comment to the list
                    if (data.comment_html) {
                        const commentsContainer = document.getElementById('comments-container');
                        if (commentsContainer) {
                            commentsContainer.insertAdjacentHTML('afterbegin', data.comment_html);
                        }
                    }
                    
                    // Update comment count
                    const commentCount = document.querySelector('.comment-count');
                    if (commentCount) {
                        commentCount.textContent = parseInt(commentCount.textContent) + 1;
                    }
                } else {
                    portfolioUtils.showToast(data.message || 'Error posting comment', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                portfolioUtils.showToast('Error posting comment', 'error');
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Post Comment';
            });
        });
    }

    // Share functionality
    const shareButtons = document.querySelectorAll('.share-btn');
    shareButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const url = window.location.href;
            const title = document.title;
            const text = document.querySelector('meta[name="description"]')?.getAttribute('content') || title;
            
            // Check if Web Share API is supported
            if (navigator.share) {
                navigator.share({
                    title: title,
                    text: text,
                    url: url
                }).then(() => {
                    portfolioUtils.showToast('Project shared successfully!', 'success');
                }).catch((error) => {
                    console.error('Error sharing:', error);
                    fallbackShare(url, title);
                });
            } else {
                fallbackShare(url, title);
            }
        });
    });
    
    function fallbackShare(url, title) {
        // Copy URL to clipboard as fallback
        navigator.clipboard.writeText(url).then(() => {
            portfolioUtils.showToast('Project URL copied to clipboard!', 'info');
        }).catch(() => {
            // Create modal with sharing options
            showShareModal(url, title);
        });
    }
    
    function showShareModal(url, title) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Share Project</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <p class="mb-3">Share this project:</p>
                        <div class="d-grid gap-2">
                            <a href="https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}" 
                               target="_blank" class="btn btn-primary">
                                <i class="fab fa-linkedin me-2"></i>Share on LinkedIn
                            </a>
                            <a href="https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}" 
                               target="_blank" class="btn btn-info">
                                <i class="fab fa-twitter me-2"></i>Share on Twitter
                            </a>
                            <button class="btn btn-secondary" onclick="copyToClipboard('${url}')">
                                <i class="fas fa-copy me-2"></i>Copy Link
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }
    
    // Global function to copy to clipboard
    window.copyToClipboard = function(text) {
        navigator.clipboard.writeText(text).then(() => {
            portfolioUtils.showToast('Link copied to clipboard!', 'success');
        });
    };

    // Smooth scrolling to comments section
    const commentLinks = document.querySelectorAll('a[href="#comments"]');
    commentLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const commentsSection = document.getElementById('comments');
            if (commentsSection) {
                commentsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                // Focus on comment form
                const textarea = commentsSection.querySelector('textarea');
                if (textarea) {
                    setTimeout(() => textarea.focus(), 500);
                }
            }
        });
    });

    // Real-time character counter for comment textarea
    const commentTextarea = document.querySelector('#comment-form textarea[name="content"]');
    if (commentTextarea) {
        const maxLength = 500;
        const counter = document.createElement('small');
        counter.className = 'text-muted form-text';
        commentTextarea.parentNode.appendChild(counter);
        
        function updateCounter() {
            const remaining = maxLength - commentTextarea.value.length;
            counter.textContent = `${remaining} characters remaining`;
            counter.className = `form-text ${remaining < 50 ? 'text-warning' : remaining < 20 ? 'text-danger' : 'text-muted'}`;
        }
        
        commentTextarea.addEventListener('input', updateCounter);
        updateCounter();
    }
});

// Animation utilities
function animateElement(element, animation) {
    element.classList.add('animate__animated', `animate__${animation}`);
    element.addEventListener('animationend', function() {
        element.classList.remove('animate__animated', `animate__${animation}`);
    }, { once: true });
}

// Export for use in other scripts
window.portfolioInteractions = {
    animateElement
};