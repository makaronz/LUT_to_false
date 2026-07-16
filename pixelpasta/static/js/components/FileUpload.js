class FileUpload {
    constructor(container, callback) {
        this.container = container;
        this.callback = callback;
        this.allowedExtensions = ['.cube', '.CUBE'];
        this.maxFileSize = 10 * 1024 * 1024; // 10MB
        this.selectedFile = null;
        
        this.init();
    }

    init() {
        this.container.innerHTML = ''; // Clear container
        
        this.fileInput = document.createElement('input');
        this.fileInput.type = 'file';
        this.fileInput.accept = '.cube,.CUBE';
        this.fileInput.style.display = 'none';
        
        // Create drop area
        this.dropArea = document.createElement('div');
        this.dropArea.className = 'file-upload-drop-area';
        
        // SVG Upload Icon
        const uploadIcon = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        uploadIcon.setAttribute('viewBox', '0 0 24 24');
        uploadIcon.setAttribute('fill', 'none');
        uploadIcon.setAttribute('stroke', 'currentColor');
        uploadIcon.setAttribute('stroke-width', '2');
        uploadIcon.setAttribute('stroke-linecap', 'round');
        uploadIcon.setAttribute('stroke-linejoin', 'round');
        uploadIcon.innerHTML = '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line>';
        
        const dropText = document.createElement('p');
        dropText.textContent = 'Przeciągnij i upuść plik .CUBE tutaj';
        
        const orText = document.createElement('div');
        orText.className = 'file-upload-or';
        orText.textContent = 'lub';
        
        this.uploadButton = document.createElement('button');
        this.uploadButton.type = 'button';
        this.uploadButton.className = 'btn-upload';
        this.uploadButton.textContent = 'Wybierz plik';
        
        this.dropArea.appendChild(uploadIcon);
        this.dropArea.appendChild(dropText);
        this.dropArea.appendChild(orText);
        this.dropArea.appendChild(this.uploadButton);
        
        this.fileInfo = document.createElement('div');
        this.fileInfo.className = 'file-info';
        
        this.errorMessage = document.createElement('div');
        this.errorMessage.className = 'error-message';
        
        this.container.appendChild(this.fileInput);
        this.container.appendChild(this.dropArea);
        this.container.appendChild(this.fileInfo);
        this.container.appendChild(this.errorMessage);
        
        this.setupEvents();
    }

    setupEvents() {
        // Trigger file input click on button click
        this.uploadButton.addEventListener('click', (e) => {
            e.stopPropagation();
            this.fileInput.click();
        });
        
        // Trigger file input click on clicking drop area
        this.dropArea.addEventListener('click', () => {
            this.fileInput.click();
        });
        
        // Drag & Drop events
        const preventDefaults = (e) => {
            e.preventDefault();
            e.stopPropagation();
        };

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.dropArea.addEventListener(eventName, preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            this.dropArea.addEventListener(eventName, () => {
                this.dropArea.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.dropArea.addEventListener(eventName, () => {
                this.dropArea.classList.remove('dragover');
            }, false);
        });

        this.dropArea.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                this.handleFile(files[0]);
            }
        });

        this.fileInput.addEventListener('change', (e) => {
            const files = e.target.files;
            if (files.length > 0) {
                this.handleFile(files[0]);
            }
        });
    }

    handleFile(file) {
        this.errorMessage.textContent = '';
        this.fileInfo.innerHTML = '';
        
        if (!file) {
            this.callback(null, 'Nie wybrano pliku');
            return;
        }
        
        // Validate extension
        const fileExt = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
        if (!this.allowedExtensions.includes(fileExt)) {
            this.errorMessage.textContent = 'Nieprawidłowy format pliku. Wymagany format: .CUBE';
            this.callback(null, 'Nieprawidłowy format pliku');
            return;
        }
        
        // Validate size
        if (file.size > this.maxFileSize) {
            this.errorMessage.textContent = 'Plik jest zbyt duży. Maksymalny rozmiar: 10MB';
            this.callback(null, 'Plik jest zbyt duży');
            return;
        }
        
        // Show success file info
        const checkIcon = '<svg style="width:1.25rem;height:1.25rem;stroke:currentColor;fill:none;stroke-width:2" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"></polyline></svg>';
        this.fileInfo.innerHTML = `${checkIcon} Wybrano plik: ${file.name}`;
        
        this.selectedFile = file;
        this.callback(file, null);
    }
}

// Export to global scope
window.FileUpload = FileUpload;
export default FileUpload;