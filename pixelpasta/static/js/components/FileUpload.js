class FileUpload {
    constructor(container, callback) {
        this.container = container;
        this.callback = callback;
        this.allowedExtensions = ['.cube', '.CUBE'];
        this.maxFileSize = 10 * 1024 * 1024; // 10MB
        
        this.init();
    }

    init() {
        this.fileInput = document.createElement('input');
        this.fileInput.type = 'file';
        this.fileInput.accept = '.cube,.CUBE';
        this.fileInput.style.display = 'none';
        
        this.uploadButton = document.createElement('button');
        this.uploadButton.className = 'btn btn-upload';
        this.uploadButton.textContent = 'Wybierz plik .CUBE';
        
        this.fileInfo = document.createElement('div');
        this.fileInfo.className = 'file-info';
        
        this.errorMessage = document.createElement('div');
        this.errorMessage.className = 'error-message';
        this.errorMessage.style.color = '#dc3545';
        this.errorMessage.style.marginTop = '0.5rem';
        
        this.container.appendChild(this.fileInput);
        this.container.appendChild(this.uploadButton);
        this.container.appendChild(this.fileInfo);
        this.container.appendChild(this.errorMessage);
        
        this.setupEvents();
    }

    setupEvents() {
        this.uploadButton.addEventListener('click', () => {
            this.fileInput.click();
        });
        
        this.fileInput.addEventListener('change', (e) => {
            this.errorMessage.textContent = '';
            const file = e.target.files[0];
            
            if (!file) {
                this.callback(null, 'Nie wybrano pliku');
                return;
            }
            
            // Walidacja rozszerzenia
            const fileExt = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
            if (!this.allowedExtensions.includes(fileExt)) {
                this.errorMessage.textContent = 'Nieprawidłowy format pliku. Wymagany format: .CUBE';
                this.callback(null, 'Nieprawidłowy format pliku');
                return;
            }
            
            // Walidacja rozmiaru
            if (file.size > this.maxFileSize) {
                this.errorMessage.textContent = 'Plik jest zbyt duży. Maksymalny rozmiar: 10MB';
                this.callback(null, 'Plik jest zbyt duży');
                return;
            }
            
            this.fileInfo.textContent = `Wybrano: ${file.name}`;
            this.callback(file, null);
        });
    }
}

// Aby komponent był dostępny globalnie lub do importu jako moduł ES6
// window.FileUpload = FileUpload; // Dla globalnego dostępu
// export default FileUpload; // Dla modułów ES6, jeśli skonfigurujemy odpowiednio projekt 