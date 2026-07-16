class Toast {
  static show(message, type = 'info', duration = 5000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    const toastContainer = document.getElementById('toast-container') || 
      (() => {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
        return container;
        
      })();
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
      toast.classList.add('fade-out');
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }
}

// Typy toastów
Toast.success = (message) => Toast.show(message, 'success');
Toast.error = (message) => Toast.show(message, 'error');
Toast.info = (message) => Toast.show(message, 'info');
Toast.warning = (message) => Toast.show(message, 'warning');

export default Toast;