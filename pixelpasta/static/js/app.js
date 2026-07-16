import Toast from './components/Toast.js';
import FileUpload from './components/FileUpload.js';
import ComparisonTable from './components/ComparisonTable.js';

console.log('PixelPasta App Initialized');

let curveChartInstance = null;
let lastAnalysisData = null; // Store last analysis data to re-render chart on theme change

// Helper to check if dark theme is active
function isDarkTheme() {
    return document.body.classList.contains('dark-theme');
}

// Get chart colors based on active theme
function getChartColors(isDark) {
    return {
        text: isDark ? '#fafafa' : '#09090b',
        grid: isDark ? '#1e1e24' : '#e4e4e7',
        tooltipBg: isDark ? 'rgba(12, 12, 15, 0.95)' : 'rgba(255, 255, 255, 0.95)',
        tooltipBorder: isDark ? '#1e1e24' : '#e4e4e7',
        tooltipText: isDark ? '#fafafa' : '#09090b'
    };
}

function renderCurveChart(data) {
    const ctx = document.getElementById('curve-chart').getContext('2d');
    if (curveChartInstance) {
        curveChartInstance.destroy();
    }

    const isDark = isDarkTheme();
    const colors = getChartColors(isDark);

    const chartData = {
        labels: data.exposure_percentages.map(val => `${val}%`),
        datasets: [
            {
                label: data.log_label || 'Kamera Log',
                data: data.log_percentages,
                borderColor: isDark ? '#60a5fa' : '#2563eb', // Accent blue
                backgroundColor: isDark ? 'rgba(96, 165, 250, 0.1)' : 'rgba(37, 99, 235, 0.1)',
                borderWidth: 2,
                pointRadius: 3,
                pointHoverRadius: 5,
                tension: 0.1
            },
            {
                label: 'Krzywa Rec.709',
                data: data.rec709_percentages,
                borderColor: isDark ? '#34d399' : '#10b981', // green
                backgroundColor: isDark ? 'rgba(52, 211, 153, 0.1)' : 'rgba(16, 185, 129, 0.1)',
                borderWidth: 2,
                pointRadius: 3,
                pointHoverRadius: 5,
                tension: 0.1
            },
            {
                label: 'Twój LUT (Wyjście)',
                data: data.lut_percentages,
                borderColor: isDark ? '#f87171' : '#ef4444', // red
                backgroundColor: isDark ? 'rgba(248, 113, 113, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                borderWidth: 3,
                pointRadius: 3,
                pointHoverRadius: 6,
                tension: 0.1
            }
        ]
    };

    curveChartInstance = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                x: {
                    grid: {
                        color: colors.grid
                    },
                    ticks: {
                        color: colors.text,
                        font: {
                            family: 'JetBrains Mono',
                            size: 11
                        }
                    },
                    title: {
                        display: true,
                        text: 'Ekspozycja wejściowa (Scene Linear)',
                        color: colors.text,
                        font: {
                            family: 'DM Sans',
                            weight: 'bold',
                            size: 13
                        }
                    }
                },
                y: {
                    grid: {
                        color: colors.grid
                    },
                    ticks: {
                        color: colors.text,
                        font: {
                            family: 'JetBrains Mono',
                            size: 11
                        }
                    },
                    title: {
                        display: true,
                        text: 'Wartość wyjściowa luma Y (%)',
                        color: colors.text,
                        font: {
                            family: 'DM Sans',
                            weight: 'bold',
                            size: 13
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: colors.text,
                        font: {
                            family: 'DM Sans',
                            weight: '600',
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: colors.tooltipBg,
                    titleColor: colors.tooltipText,
                    bodyColor: colors.tooltipText,
                    borderColor: colors.tooltipBorder,
                    borderWidth: 1,
                    titleFont: {
                        family: 'DM Sans',
                        weight: 'bold',
                        size: 12
                    },
                    bodyFont: {
                        family: 'JetBrains Mono',
                        size: 11
                    }
                }
            }
        }
    });
}

function displayLutInfo(lutInfo) {
    const infoContainer = document.getElementById('lut-info');
    infoContainer.innerHTML = '';

    const labelMap = {
        'filename': 'Nazwa pliku',
        'lut_type': 'Typ LUT',
        'lut_1d_size': 'Rozmiar 1D LUT',
        'lut_3d_size': 'Rozmiar 3D LUT',
        'color_space': 'Wybrana przestrzeń'
    };

    for (const [key, value] of Object.entries(lutInfo)) {
        const p = document.createElement('p');
        const strong = document.createElement('strong');
        strong.textContent = `${labelMap[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}: `;
        p.appendChild(strong);
        p.append(document.createTextNode(value !== null && value !== undefined ? value : 'Brak danych'));
        infoContainer.appendChild(p);
    }
}

function setupTabs() {
    const tabButtons = document.querySelectorAll('.tabs [role="tab"]');
    const tabPanels = document.querySelectorAll('.tab-content [role="tabpanel"]');

    tabButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            switchTab(button);
        });

        button.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                switchTab(button);
            }

            if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
                const direction = e.key === 'ArrowRight' ? 1 : -1;
                const nextIndex = (Array.from(tabButtons).indexOf(button) + direction + tabButtons.length) % tabButtons.length;
                tabButtons[nextIndex].focus();
            }
        });
    });

    function switchTab(button) {
        const targetId = button.getAttribute('aria-controls');
        
        tabButtons.forEach(btn => {
            btn.setAttribute('aria-selected', 'false');
            btn.setAttribute('tabindex', '-1');
            btn.classList.remove('active');
        });
        
        button.setAttribute('aria-selected', 'true');
        button.setAttribute('tabindex', '0');
        button.classList.add('active');
        
        tabPanels.forEach(panel => {
            panel.classList.remove('active');
            panel.setAttribute('hidden', '');
        });
        
        const targetPanel = document.getElementById(targetId);
        targetPanel.classList.add('active');
        targetPanel.removeAttribute('hidden');
        
        targetPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

function setupTheme() {
    const toggleBtn = document.getElementById('theme-toggle');
    const icon = document.getElementById('theme-toggle-icon');

    // Load initial theme from localStorage
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    const isDark = savedTheme === null ? systemPrefersDark : savedTheme === 'dark';
    
    if (isDark) {
        document.body.classList.add('dark-theme');
    } else {
        document.body.classList.remove('dark-theme');
    }
    updateThemeIcon(isDark);

    toggleBtn.addEventListener('click', () => {
        const darkActive = document.body.classList.toggle('dark-theme');
        localStorage.setItem('theme', darkActive ? 'dark' : 'light');
        updateThemeIcon(darkActive);
        
        // Re-render chart if there is data
        if (lastAnalysisData) {
            renderCurveChart(lastAnalysisData);
        }
    });

    function updateThemeIcon(dark) {
        if (dark) {
            // Render Sun (switching to light)
            icon.innerHTML = `
                <circle cx="12" cy="12" r="4"></circle>
                <path d="M12 2v2"></path>
                <path d="M12 20v2"></path>
                <path d="m4.93 4.93 1.41 1.41"></path>
                <path d="m17.66 17.66 1.41 1.41"></path>
                <path d="M2 12h2"></path>
                <path d="M20 12h2"></path>
                <path d="m6.34 17.66-1.41 1.41"></path>
                <path d="m19.07 4.93-1.41 1.41"></path>
            `;
        } else {
            // Render Moon (switching to dark)
            icon.innerHTML = `
                <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"></path>
            `;
        }
    }
}

// Gemini Chat Interface Controller
function setupChat() {
    const chatToggleBtn = document.getElementById('chat-toggle-btn');
    const chatPanel = document.getElementById('chat-panel');
    const chatCloseBtn = document.getElementById('chat-close-btn');
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatSuggestions = document.getElementById('chat-suggestions');
    
    let chatHistory = [];
    let isChatLoading = false;
    
    const md = window.markdownit ? window.markdownit({ html: false, linkify: true, breaks: true }) : null;

    // Toggle Chat sidebar
    chatToggleBtn.addEventListener('click', () => {
        chatPanel.classList.toggle('active');
        scrollToBottom();
    });

    chatCloseBtn.addEventListener('click', () => {
        chatPanel.classList.remove('active');
    });

    // Auto-resize input textarea
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        const scrollHeight = chatInput.scrollHeight;
        chatInput.style.height = Math.min(scrollHeight, 120) + 'px';
    });

    // Submit with Enter key (without shift)
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.requestSubmit();
        }
    });

    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        if (!text || isChatLoading) return;
        
        chatInput.value = '';
        chatInput.style.height = 'auto';
        handleSend(text);
    });

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function handleSend(textToSend) {
        isChatLoading = true;
        
        // Add User Message
        appendMessage('user', textToSend);
        chatHistory.push({ role: 'user', content: textToSend });
        scrollToBottom();

        // Clear suggestions
        chatSuggestions.innerHTML = '';

        // Add Bot Message Placeholder
        const botMessageEl = document.createElement('div');
        botMessageEl.className = 'chat-message bot';
        
        // Collapsible Thoughts Box container
        const thoughtsBox = document.createElement('div');
        thoughtsBox.className = 'thoughts-box';
        
        const thoughtsHeader = document.createElement('button');
        thoughtsHeader.className = 'thoughts-header';
        thoughtsHeader.innerHTML = `
            <svg class="chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
            <svg class="brain" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1 0-3.12 3 3 0 0 1 0-4.88 2.5 2.5 0 0 1 0-3.12A2.5 2.5 0 0 1 9.5 2Z"></path><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 2.5 2.5 0 0 0 0-3.12 3 3 0 0 0 0-4.88 2.5 2.5 0 0 0 0-3.12A2.5 2.5 0 0 0 14.5 2Z"></path></svg>
            <span class="thoughts-title">Przygotowywanie analizy...</span>
        `;
        
        const thoughtsContent = document.createElement('div');
        thoughtsContent.className = 'thoughts-content';
        
        thoughtsHeader.addEventListener('click', () => {
            const isExpanded = thoughtsBox.classList.toggle('expanded');
            thoughtsHeader.classList.toggle('expanded', isExpanded);
        });
        
        thoughtsBox.appendChild(thoughtsHeader);
        thoughtsBox.appendChild(thoughtsContent);
        botMessageEl.appendChild(thoughtsBox);
        
        // Final response bubble
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        // Loading loader
        const loader = document.createElement('div');
        loader.className = 'message-loader';
        loader.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="2" y2="6"></line><line x1="12" x2="12" y1="18" y2="22"></line><line x1="4.93" x2="7.76" y1="4.93" y2="7.76"></line><line x1="16.24" x2="19.07" y1="16.24" y2="19.07"></line><line x1="2" x2="6" y1="12" y2="12"></line><line x1="18" x2="22" y1="12" y2="12"></line><line x1="4.93" x2="7.76" y1="19.07" y2="16.24"></line><line x1="16.24" x2="19.07" y1="7.76" y2="4.93"></line></svg>
            Ładowanie...
        `;
        
        botMessageEl.appendChild(bubble);
        botMessageEl.appendChild(loader);
        chatMessages.appendChild(botMessageEl);
        scrollToBottom();

        let thinking = '';
        let reply = '';
        let suggestions = [];

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: textToSend,
                    history: chatHistory.slice(0, -1)
                })
            });

            if (!response.ok) {
                throw new Error(`Mismatched API status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            // Hide global loading, start reading stream
            loader.remove();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop(); // save incomplete line for next iteration

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const dataStr = line.replace('data: ', '').trim();
                        if (dataStr === '[DONE]') break;
                        if (dataStr) {
                            try {
                                const parsed = JSON.parse(dataStr);
                                if (parsed.type === 'THOUGHT') {
                                    thinking += (thinking ? '\n' : '') + parsed.content;
                                    thoughtsContent.textContent = thinking;
                                    
                                    // Update title to the very last thought
                                    const thoughtLines = thinking.split('\n');
                                    thoughtsHeader.querySelector('.thoughts-title').textContent = thoughtLines[thoughtLines.length - 1];
                                } else if (parsed.type === 'SUGGESTION') {
                                    suggestions.push(parsed.content);
                                } else {
                                    reply += parsed.content;
                                    bubble.innerHTML = md ? md.render(reply) : reply;
                                }
                                scrollToBottom();
                            } catch (e) {
                                console.error('JSON parse fail:', dataStr, e);
                            }
                        }
                    }
                }
            }
            
            // Clean up thoughts header if no thoughts were generated
            if (!thinking) {
                thoughtsBox.remove();
            } else {
                // Change title to completed
                thoughtsHeader.querySelector('.thoughts-title').textContent = 'Zobacz proces analizy';
            }

            // Save reply to history
            chatHistory.push({ role: 'model', content: reply });

            // Display suggestions
            if (suggestions.length > 0) {
                suggestions.forEach(s => {
                    const btn = document.createElement('button');
                    btn.className = 'chat-suggestion-btn';
                    btn.textContent = s;
                    btn.addEventListener('click', () => {
                        handleSend(s);
                    });
                    chatSuggestions.appendChild(btn);
                });
            }

        } catch (err) {
            console.error('Chat error:', err);
            loader.remove();
            bubble.innerHTML = `<span style="color: var(--error-color)">⚠️ Wystąpił błąd podczas komunikacji z asystentem: ${err.message}</span>`;
        } finally {
            isChatLoading = false;
            scrollToBottom();
        }
    }

    function appendMessage(role, text) {
        const msgEl = document.createElement('div');
        msgEl.className = `chat-message ${role}`;
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = text;
        
        msgEl.appendChild(bubble);
        chatMessages.appendChild(msgEl);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded and parsed');

    setupTheme();
    setupTabs();
    setupChat();

    const fileUploadContainer = document.getElementById('file-upload-component-container');
    const colorSpaceSelect = document.getElementById('color-space');
    const analyzeButton = document.getElementById('analyze-button');
    const resultsSection = document.getElementById('results');
    let selectedFile = null;

    if (fileUploadContainer) {
        new FileUpload(fileUploadContainer, (file, error) => {
            if (error) {
                console.error('Błąd ładowania pliku:', error);
                selectedFile = null;
                analyzeButton.style.display = 'none';
                resultsSection.style.display = 'none';
                if (error !== 'Nie wybrano pliku') {
                    Toast.error(error);
                }
            } else {
                console.log('Wybrany plik:', file.name);
                selectedFile = file;
                resultsSection.style.display = 'none';
                if (colorSpaceSelect.value) {
                    analyzeButton.style.display = 'block';
                }
            }
        });
    } else {
        console.error('Nie znaleziono kontenera dla komponentu FileUpload.');
    }

    colorSpaceSelect.addEventListener('change', () => {
        resultsSection.style.display = 'none';
        if (selectedFile && colorSpaceSelect.value) {
            analyzeButton.style.display = 'block';
        } else {
            analyzeButton.style.display = 'none';
        }
    });

    analyzeButton.addEventListener('click', () => {
        if (!selectedFile) {
            Toast.warning('Proszę najpierw wybrać plik .CUBE.');
            return;
        }
        if (!colorSpaceSelect.value) {
            Toast.warning('Proszę wybrać przestrzeń barwną kamery.');
            return;
        }

        console.log('Rozpoczynanie analizy dla pliku:', selectedFile.name, 'i przestrzeni:', colorSpaceSelect.value);
        analyzeButton.disabled = true;
        analyzeButton.textContent = 'Analizowanie...';

        const formData = new FormData();
        // Match the field names in pixelpasta/app.py (cube-file and color-space)
        formData.append('cube-file', selectedFile);
        formData.append('color-space', colorSpaceSelect.value);

        fetch('/api/analyze', { 
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errData => {
                    throw new Error(errData.error || `Błąd serwera: ${response.status}`);
                }).catch(() => {
                    throw new Error(`Błąd serwera: ${response.status} ${response.statusText}`);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Odpowiedź z serwera:', data);
            if (data.error) {
                Toast.error(`Błąd analizy: ${data.error}`);
                resultsSection.style.display = 'none';
            } else {
                lastAnalysisData = data;
                
                // Render Curve Chart
                renderCurveChart(data);
                
                // Map data for Comparison Table
                const tableData = data.exposure_percentages.map((exp, idx) => ({
                    exposure: exp,
                    log: data.log_percentages[idx],
                    rec709: data.rec709_percentages[idx],
                    lut: data.lut_percentages[idx]
                }));
                
                // Render Comparison Table client-side
                new ComparisonTable('comparison-table-container', tableData, data.log_label);
                
                // Render LUT Info
                displayLutInfo(data.lut_info);
                
                resultsSection.style.display = 'block';
                Toast.success('Analiza zakończona pomyślnie!');
            }
        })
        .catch(error => {
            Toast.error(`Wystąpił błąd: ${error.message}`);
            console.error('Błąd podczas wysyłania żądania analizy:', error);
            resultsSection.style.display = 'none';
        })
        .finally(() => {
            analyzeButton.disabled = false;
            analyzeButton.textContent = 'Analizuj LUT';
        });
    });
});