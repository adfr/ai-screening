// Load stats on page load
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    checkHealth();
});

async function loadStats() {
    try {
        const response = await fetch('/stats');
        if (response.ok) {
            const data = await response.json();
            updateNavStats(data);
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

async function checkHealth() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        if (data.api_status === 'unreachable') {
            showNotification('API server is unreachable. Please ensure the API is running on port 8000.', 'error');
        }
    } catch (error) {
        console.error('Health check failed:', error);
    }
}

function updateNavStats(stats) {
    const navStats = document.getElementById('nav-stats');
    if (stats.error) {
        navStats.innerHTML = '<span class="stat-item">Stats unavailable</span>';
        return;
    }
    
    navStats.innerHTML = `
        <span class="stat-item">
            <strong>Individuals:</strong> ${stats.individuals_count?.toLocaleString() || 0}
        </span>
        <span class="stat-item">
            <strong>Entities:</strong> ${stats.entities_count?.toLocaleString() || 0}
        </span>
        <span class="stat-item">
            <strong>Programs:</strong> ${stats.programs_count || 0}
        </span>
    `;
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background-color: ${type === 'error' ? '#fee2e2' : '#d1fae5'};
        color: ${type === 'error' ? '#dc2626' : '#059669'};
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);