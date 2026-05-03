// WorkVerse - Custom JavaScript

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(function(card, index) {
        card.style.animationDelay = (index * 0.1) + 's';
        card.classList.add('fade-in');
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = button.getAttribute('data-confirm-delete');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Character counter for textareas
    const textareas = document.querySelectorAll('textarea[maxlength]');
    textareas.forEach(function(textarea) {
        const maxLength = textarea.getAttribute('maxlength');
        const counterDiv = document.createElement('div');
        counterDiv.className = 'form-text text-end';
        counterDiv.innerHTML = `<span class="char-count">0</span>/${maxLength} characters`;
        textarea.parentNode.appendChild(counterDiv);

        textarea.addEventListener('input', function() {
            const charCount = textarea.value.length;
            counterDiv.querySelector('.char-count').textContent = charCount;
        });
    });
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// File upload preview
function previewFileName(input) {
    if (input.files && input.files[0]) {
        const fileName = input.files[0].name;
        const fileSize = (input.files[0].size / 1024 / 1024).toFixed(2);
        
        let preview = input.parentNode.querySelector('.file-preview');
        if (!preview) {
            preview = document.createElement('div');
            preview.className = 'file-preview mt-2 small text-muted';
            input.parentNode.appendChild(preview);
        }
        
        preview.innerHTML = `<i class="bi bi-file-earmark"></i> ${fileName} (${fileSize} MB)`;
    }
}

// Add event listeners to file inputs
document.querySelectorAll('input[type="file"]').forEach(function(input) {
    input.addEventListener('change', function() {
        previewFileName(this);
    });
});

// Tooltip initialization
const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
});

// Copy to clipboard functionality
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Copied to clipboard!', 'success');
    }).catch(function(err) {
        console.error('Failed to copy:', err);
    });
}

// Toast notification
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

// Progress bar animation
function animateProgressBar(element, targetValue) {
    let currentValue = 0;
    const increment = targetValue / 50;
    
    const interval = setInterval(function() {
        currentValue += increment;
        if (currentValue >= targetValue) {
            currentValue = targetValue;
            clearInterval(interval);
        }
        element.style.width = currentValue + '%';
        element.setAttribute('aria-valuenow', currentValue);
    }, 20);
}

// Search functionality for tables
function searchTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    
    if (!input || !table) return;
    
    input.addEventListener('keyup', function() {
        const filter = input.value.toUpperCase();
        const rows = table.getElementsByTagName('tr');
        
        for (let i = 1; i < rows.length; i++) {
            let txtValue = rows[i].textContent || rows[i].innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                rows[i].style.display = '';
            } else {
                rows[i].style.display = 'none';
            }
        }
    });
}

// Print certificate
function printCertificate() {
    window.print();
}

// Download as PDF (using browser's print to PDF)
function downloadCertificatePDF() {
    window.print();
}

// Confirmation dialog helper
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Loading spinner
function showLoadingSpinner(button) {
    const originalContent = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    
    return function() {
        button.disabled = false;
        button.innerHTML = originalContent;
    };
}

// Video player helpers
function pauseAllVideos() {
    const videos = document.querySelectorAll('video');
    videos.forEach(video => video.pause());
}

// Scroll to top
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Add scroll to top button
window.addEventListener('scroll', function() {
    const scrollBtn = document.getElementById('scrollTopBtn');
    if (!scrollBtn) return;
    
    if (window.pageYOffset > 300) {
        scrollBtn.style.display = 'block';
    } else {
        scrollBtn.style.display = 'none';
    }
});

// Form auto-save (for long forms)
function enableAutoSave(formId, storageKey) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    // Load saved data
    const savedData = localStorage.getItem(storageKey);
    if (savedData) {
        const data = JSON.parse(savedData);
        Object.keys(data).forEach(key => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) input.value = data[key];
        });
    }
    
    // Save on input
    form.addEventListener('input', function() {
        const formData = {};
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            if (input.name) {
                formData[input.name] = input.value;
            }
        });
        localStorage.setItem(storageKey, JSON.stringify(formData));
    });
    
    // Clear on submit
    form.addEventListener('submit', function() {
        localStorage.removeItem(storageKey);
    });
}

// Lazy loading for images
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
});

// Debounce function for search
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

// Export functions to global scope
window.WorkVerse = {
    showToast,
    copyToClipboard,
    confirmAction,
    showLoadingSpinner,
    scrollToTop,
    printCertificate,
    downloadCertificatePDF,
    searchTable,
    enableAutoSave,
    debounce
};
