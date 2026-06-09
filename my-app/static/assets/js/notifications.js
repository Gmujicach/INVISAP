/**
 * GESTIÓN DE NOTIFICACIONES ELEGANTES
 * Transforma alertas estáticas en Toasts modernos con auto-cierre de 3s.
 */
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert-to-toast');
    
    alerts.forEach(alert => {
        const message = alert.textContent.trim();
        // Mapear 'danger' de Flask a 'error' para consistencia en CSS
        const type = alert.dataset.type === 'danger' ? 'error' : (alert.dataset.type || 'success');
        createToast(message, type);
        alert.remove();
    });
});

function createToast(message, type) {
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
    // Aplicar color de la barra de progreso dinámicamente según el tipo
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

    // Funcionalidad del botón cerrar
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.onclick = () => {
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 500);
    };

    // Auto-eliminar después de 3 segundos
    setTimeout(() => {
        if (!toast.parentNode) return;
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}
