class FileUpload {
    constructor(targetElement, onFileSelectCallback) {
        this.targetElement = targetElement; // Element DOM, w którym komponent ma się wyrenderować
        this.onFileSelect = onFileSelectCallback; // Funkcja zwrotna wywoływana po wybraniu pliku

        this.render();
        this.attachEventListeners();
    }

    render() {
        // Stworzenie podstawowej struktury HTML dla komponentu
        // np. <input type="file"> i obszar do drag & drop
        this.targetElement.innerHTML = `
            <div class="file-upload-container">
                <div class="file-upload-input-area">
                    <input type="file" id="lut-file-input" accept=".cube" style="display: none;">
                    <label for="lut-file-input" class="file-upload-label btn btn-secondary">
                        Wybierz plik .CUBE
                    </label>
                    <span class="file-upload-or">lub</span>
                    <div class="file-upload-drop-area" id="lut-drop-area">
                        <p>Przeciągnij i upuść plik .CUBE tutaj</p>
                    </div>
                </div>
                <div class="file-upload-info" id="lut-file-info">
                    <!-- Informacje o wybranym pliku lub błędy -->
                </div>
            </div>
        `;
        this.fileInput = this.targetElement.querySelector('#lut-file-input');
        this.dropArea = this.targetElement.querySelector('#lut-drop-area');
        this.fileInfo = this.targetElement.querySelector('#lut-file-info');
    }

    attachEventListeners() {
        // Dodanie obsługi zdarzeń dla inputu i drag & drop
        this.fileInput.addEventListener('change', (event) => this.handleFileSelect(event.target.files));

        this.dropArea.addEventListener('dragover', (event) => {
            event.preventDefault();
            this.dropArea.classList.add('dragover');
        });

        this.dropArea.addEventListener('dragleave', () => {
            this.dropArea.classList.remove('dragover');
        });

        this.dropArea.addEventListener('drop', (event) => {
            event.preventDefault();
            this.dropArea.classList.remove('dragover');
            this.handleFileSelect(event.dataTransfer.files);
        });
    }

    handleFileSelect(files) {
        if (files.length === 0) {
            this.displayFileInfo('', 'error');
            return;
        }

        const file = files[0];
        if (!file.name.toLowerCase().endsWith('.cube')) {
            this.displayFileInfo('Nieprawidłowy format pliku. Akceptowane są tylko pliki .CUBE.', 'error');
            if (this.onFileSelect) {
                this.onFileSelect(null, 'Nieprawidłowy format pliku. Akceptowane są tylko pliki .CUBE.');
            }
            return;
        }

        this.displayFileInfo(`Wybrano plik: ${file.name}`, 'success');
        if (this.onFileSelect) {
            this.onFileSelect(file, null);
        }
    }

    displayFileInfo(message, type = 'info') {
        this.fileInfo.textContent = message;
        this.fileInfo.className = `file-upload-info ${type}`; // Można dodać klasy CSS dla różnych typów wiadomości
    }
}

// Aby komponent był dostępny globalnie lub do importu jako moduł ES6
// window.FileUpload = FileUpload; // Dla globalnego dostępu
// export default FileUpload; // Dla modułów ES6, jeśli skonfigurujemy odpowiednio projekt 