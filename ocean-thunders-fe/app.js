class ChatApp {
    constructor() {
        this.websocket = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.audioStream = null;
        this.currentAudioSource = null;

        this.messageInput = document.getElementById('messageInput');
        this.micButton = document.querySelector('.mic-button');
        this.sendButton = document.querySelector('.send-button');
        this.messagesContainer = document.querySelector('.messages-container');
        this.statusDot = document.querySelector('.status-dot');
        this.statusText = document.querySelector('.status-text');

        this.setupEventListeners();
        this.connectWebSocket();
    }

    setupEventListeners() {
        document.querySelector('.chat-input-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        this.messageInput.addEventListener('input', () => {
            this.sendButton.disabled = !this.messageInput.value.trim();
        });

        this.micButton.addEventListener('click', () => {
            if (this.isRecording) {
                this.stopRecording();
            } else {
                this.startRecording();
            }
        });
    }

    connectWebSocket() {
        try {
            this.websocket = new WebSocket('ws://0.0.0.0:12345/message');

            this.websocket.onopen = () => {
                console.log('Connected to WebSocket');
                this.updateConnectionStatus(true);
            };

            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    if (data.type === 'transcription') {
                        this.removeTypingIndicator();
                        this.addMessage(data.content, 'user');
                        this.showTypingIndicator();
                    } else if (data.type === 'assistant') {
                        this.removeTypingIndicator();
                        this.addMessage(data.content, 'assistant');
                    } else if (data.type === 'audio') {
                        this.removeTypingIndicator();
                        this.playAudio(data.content);
                    }
                } catch (err) {
                    console.error('Error parsing WebSocket message:', err);
                }
            };

            this.websocket.onclose = () => {
                console.log('WebSocket connection closed');
                this.updateConnectionStatus(false);
                setTimeout(() => this.connectWebSocket(), 3000);
            };

            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus(false);
            };
        } catch (error) {
            console.error('Error creating WebSocket:', error);
            this.updateConnectionStatus(false);
        }
    }

    updateConnectionStatus(connected) {
        this.statusDot.className = 'status-dot' + (connected ? ' connected' : '');
        this.statusText.textContent = connected ? 'Connected' : 'Disconnected';
    }

    formatTimestamp(date) {
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);
        if (seconds < 60) return 'just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        return date.toLocaleDateString();
    }

    addMessage(text, sender, prepend = false) {
        const welcome = document.querySelector('.welcome-message');
        if (welcome) welcome.remove();

        const el = document.createElement('div');
        el.className = `message ${sender}`;
        el.innerHTML = `
            <div class="message-avatar">${sender === 'assistant' ? 'HC' : 'You'}</div>
            <div class="message-content">
                <div class="message-text">${text}</div>
                <div class="message-timestamp">${this.formatTimestamp(new Date())}</div>
            </div>
        `;

        if (prepend) {
            this.messagesContainer.insertBefore(el, this.messagesContainer.firstChild);
        } else {
            this.messagesContainer.appendChild(el);
        }

        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    sendMessage() {
        const msg = this.messageInput.value.trim();
        if (!msg) return;

        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({ type: 'text', content: msg }));
            this.addMessage(msg, 'user');
            this.messageInput.value = '';
            this.sendButton.disabled = true;
            this.showTypingIndicator();
        }
    }

    async startRecording() {
        try {
            if (!this.audioStream) {
                this.audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            }

            this.mediaRecorder = new MediaRecorder(this.audioStream);
            this.audioChunks = [];
            this.mediaRecorder.ondataavailable = (e) => { if (e.data.size) this.audioChunks.push(e.data); };
            this.mediaRecorder.onstop = () => {
                const blob = new Blob(this.audioChunks, { type: 'audio/wav' });
                const reader = new FileReader();
                reader.onloadend = () => {
                    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                        this.websocket.send(JSON.stringify({ type: 'audio', content: reader.result.split(',')[1] }));
                    }
                };
                reader.readAsDataURL(blob);
            };

            if (this.currentAudioSource) {
                try {
                    this.currentAudioSource.stop();
                } catch (err) {
                    console.warn("Error stopping audio during mic activation:", err);
                }
                this.currentAudioSource = null;
            }

            this.mediaRecorder.start();
            this.isRecording = true;
            this.micButton.classList.add('recording');
            this.messageInput.disabled = true;
        } catch (err) {
            console.error('Mic error:', err);
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.micButton.classList.remove('recording');
            this.messageInput.disabled = false;
            this.showTypingIndicator('user');
        }
    }

    showTypingIndicator(sender = 'assistant') {
        this.removeTypingIndicator();
        const el = document.createElement('div');
        el.className = `message ${sender} typing-indicator`;
        el.id = 'typing-indicator';
        el.innerHTML = `
            <div class="message-avatar">${sender === 'assistant' ? 'HC' : 'You'}</div>
            <div class="typing-dots">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
            </div>
        `;
        this.messagesContainer.appendChild(el);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    removeTypingIndicator() {
        const e = document.getElementById('typing-indicator');
        if (e) e.remove();
    }

    playAudio(base64Data) {
        try {
            const binary = atob(base64Data);
            const byteArray = Uint8Array.from(binary, c => c.charCodeAt(0));
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();

            if (audioContext.state === 'suspended') {
                audioContext.resume();
            }

            audioContext.decodeAudioData(byteArray.buffer)
                .then(audioBuffer => {
                    // Stop previous audio if playing
                    if (this.currentAudioSource) {
                        try {
                            this.currentAudioSource.stop();
                        } catch (err) {
                            console.warn("Failed to stop previous audio:", err);
                        }
                    }

                    const source = audioContext.createBufferSource();
                    source.buffer = audioBuffer;
                    source.connect(audioContext.destination);
                    source.start(0);

                    this.currentAudioSource = source;
                })
                .catch(err => {
                    console.error("Failed to decode audio data:", err);
                });
        } catch (err) {
            console.error('Error decoding or playing audio:', err);
        }
    }
}

// Helper to convert base64 to Blob
function base64ToBlob(base64, mime) {
    const binary = atob(base64);
    const array = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
    array[i] = binary.charCodeAt(i);
    }
    return new Blob([array], { type: mime });
}

document.addEventListener('DOMContentLoaded', () => new ChatApp());
