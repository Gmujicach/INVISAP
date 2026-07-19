/**
 * GESTIÓN DE NOTIFICACIONES ELEGANTES
 * Transforma alertas estáticas y flash-toast en notificaciones modernas con auto-cierre.
 */
document.addEventListener('DOMContentLoaded', function() {
    // Manejar elementos .alert-to-toast existentes
    const alerts = document.querySelectorAll('.alert-to-toast');
    alerts.forEach(alert => {
        const message = alert.textContent.trim();
        const type = alert.dataset.type === 'danger' ? 'error' : (alert.dataset.type || 'success');
        createToastNotification(message, type);
        alert.remove();
    });
    
    // Manejar toast-custom renderizados desde Flask (flash messages)
    const existingToasts = document.querySelectorAll('.toast-custom');
    if (existingToasts.length > 0) {
        existingToasts.forEach((toast, index) => {
            // Agregar evento click al botón cerrar
            const closeBtn = toast.querySelector('.toast-close');
            if (closeBtn) {
                closeBtn.onclick = (e) => {
                    e.stopPropagation();
                    toast.classList.remove('show');
                    toast.classList.add('hide');
                    setTimeout(() => {
                        if (toast.parentNode) {
                            toast.parentNode.removeChild(toast);
                        }
                    }, 400);
                };
            }
            
            const delay = 5000;
            setTimeout(() => {
                toast.classList.add('show');
            }, 100 + (index * 100));
            setTimeout(() => {
                toast.classList.remove('show');
                toast.classList.add('hide');
                setTimeout(() => {
                    if (toast.parentNode) {
                        toast.parentNode.removeChild(toast);
                    }
                }, 400);
            }, delay + 100 + (index * 100));
        });
    }
});

function createToastNotification(message, type) {
    let container = document.querySelector('.notification-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'notification-container';
        document.body.appendChild(container);
    }

    const icons = {
        'success': 'bi-check-circle-fill',
        'error': 'bi-exclamation-triangle-fill',
        'warning': 'bi-exclamation-circle-fill',
        'info': 'bi-info-circle-fill'
    };

    const toast = document.createElement('div');
    toast.className = `toast-custom ${type}`;
    const progressColor = type === 'error' ? '#ff3e1d' : type === 'warning' ? '#ffab00' : type === 'info' ? '#03c3ec' : '#08b324';
    
    toast.innerHTML = `
        <div class="toast-content">
            <div class="toast-icon" style="color: ${progressColor}">
                <i class="bi ${icons[type] || icons.success}"></i>
            </div>
            <span class="toast-message">${message}</span>
        </div>
        <button class="toast-close">&times;</button>
        <div class="toast-progress" style="color: ${progressColor}"></div>
    `;

    container.appendChild(toast);

    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.onclick = () => {
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 500);
    };

    setTimeout(() => {
        if (!toast.parentNode) return;
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}
