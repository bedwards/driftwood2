/**
 * Dialogue Client JavaScript
 * Manages real-time philosophical dialogue display
 */

class DialogueClient {
    constructor() {
        // Get philosopher ID and conversation ID from DOM
        this.philosopherId = parseInt(document.body.dataset.philosopherId);
        this.conversationId = document.body.dataset.conversationId || null;
        
        // Socket connection
        this.socket = null;
        
        // UI elements
        this.dialogueContent = document.getElementById('dialogueContent');
        this.philosopherName = document.getElementById('philosopherName');
        this.authorVoice = document.getElementById('authorVoice');
        this.exchangeCount = document.getElementById('exchangeCount');
        this.timestamp = document.getElementById('timestamp');
        this.connectionText = document.getElementById('connectionText');
        this.thinkingIndicator = document.querySelector('.thinking-indicator');
        
        // Conversation state
        this.currentConfig = null;
        this.messageHistory = [];
        this.isGenerating = false;
        
        // Initialize
        this.initializeSocket();
        this.setupSpeechifyNotice();
    }
    
    initializeSocket() {
        this.socket = io('http://localhost:5000');
        
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.updateConnectionStatus(true);
            
            // Join conversation if ID exists
            if (this.conversationId) {
                this.joinConversation();
            }
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.updateConnectionStatus(false);
        });
        
        // Handle conversation state
        this.socket.on('conversation_state', (data) => {
            this.handleConversationState(data);
        });
        
        // Handle message chunks
        this.socket.on('message_chunk', (data) => {
            this.handleMessageChunk(data);
        });
        
        // Handle generation events
        this.socket.on('generation_start', (data) => {
            this.handleGenerationStart(data);
        });
        
        this.socket.on('generation_complete', (data) => {
            this.handleGenerationComplete(data);
        });
        
        // Handle errors
        this.socket.on('generation_error', (data) => {
            console.error('Generation error:', data.error);
            this.showError(data.error);
        });
        
        // Handle conversation history
        this.socket.on('conversation_history', (data) => {
            this.loadConversationHistory(data);
        });
    }
    
    joinConversation() {
        const clientType = `philosopher${this.philosopherId}`;
        
        this.socket.emit('join_conversation', {
            conversation_id: this.conversationId,
            client_type: clientType
        });
        
        // Request conversation history
        this.socket.emit('get_conversation_history', {
            conversation_id: this.conversationId
        });
    }
    
    handleConversationState(data) {
        const { conversation, client_type } = data;
        
        if (conversation && conversation.config) {
            this.currentConfig = conversation.config;
            this.updatePhilosopherInfo();
            
            // Load existing history
            if (conversation.history && conversation.history.length > 0) {
                this.loadMessages(conversation.history);
            }
        }
    }
    
    updatePhilosopherInfo() {
        if (!this.currentConfig) return;
        
        const isPhil1 = this.philosopherId === 1;
        const philosopher = isPhil1 ? this.currentConfig.philosopher1 : this.currentConfig.philosopher2;
        const author = isPhil1 ? this.currentConfig.author1 : this.currentConfig.author2;
        
        // Get philosopher and author names from config or use fallback
        const philosopherName = this.getPhilosopherName(philosopher);
        const authorName = this.getAuthorName(author);
        
        this.philosopherName.textContent = philosopherName;
        this.authorVoice.textContent = `through ${authorName}'s voice`;
        
        // Update page title
        document.title = `${philosopherName} - Philosophical Dialogue`;
    }
    
    getPhilosopherName(key) {
        const philosophers = {
            'socrates': 'Socrates',
            'plato': 'Plato',
            'aristotle': 'Aristotle',
            'marcus_aurelius': 'Marcus Aurelius',
            'buddha': 'Siddhartha Gautama (Buddha)',
            'confucius': 'Confucius',
            'descartes': 'René Descartes',
            'hume': 'David Hume',
            'kant': 'Immanuel Kant',
            'nietzsche': 'Friedrich Nietzsche',
            'kierkegaard': 'Søren Kierkegaard',
            'wittgenstein': 'Ludwig Wittgenstein',
            'sartre': 'Jean-Paul Sartre',
            'de_beauvoir': 'Simone de Beauvoir',
            'arendt': 'Hannah Arendt'
        };
        return philosophers[key] || key;
    }
    
    getAuthorName(key) {
        const authors = {
            'austen': 'Jane Austen',
            'dickens': 'Charles Dickens',
            'wilde': 'Oscar Wilde',
            'hemingway': 'Ernest Hemingway',
            'woolf': 'Virginia Woolf',
            'joyce': 'James Joyce',
            'kafka': 'Franz Kafka',
            'tolkien': 'J.R.R. Tolkien',
            'vonnegut': 'Kurt Vonnegut',
            'borges': 'Jorge Luis Borges',
            'marquez': 'Gabriel García Márquez',
            'morrison': 'Toni Morrison',
            'le_guin': 'Ursula K. Le Guin',
            'murakami': 'Haruki Murakami',
            'ishiguro': 'Kazuo Ishiguro',
            'atwood': 'Margaret Atwood',
            'baldwin': 'James Baldwin',
            'calvino': 'Italo Calvino',
            'butler': 'Octavia Butler',
            'pynchon': 'Thomas Pynchon'
        };
        return authors[key] || key;
    }
    
    handleMessageChunk(data) {
        // Only display chunks for this philosopher
        if (data.speaker !== this.philosopherId) {
            // Show thinking indicator for other philosopher
            this.showThinkingIndicator(true);
            return;
        }
        
        // Hide thinking indicator when receiving own content
        this.showThinkingIndicator(false);
        
        // Get or create current message container
        let currentMessage = document.querySelector('.dialogue-entry.generating');
        
        if (!currentMessage) {
            currentMessage = this.createMessageContainer();
            this.dialogueContent.appendChild(currentMessage);
            
            // Clear welcome message if present
            const welcomeMessage = this.dialogueContent.querySelector('.welcome-message');
            if (welcomeMessage) {
                welcomeMessage.remove();
            }
        }
        
        // Append chunk to content
        const contentDiv = currentMessage.querySelector('.dialogue-content');
        const existingText = contentDiv.textContent;
        
        // If this is the first chunk, wrap in paragraph
        if (existingText === '') {
            const paragraph = document.createElement('p');
            paragraph.textContent = data.content;
            contentDiv.appendChild(paragraph);
        } else {
            // Add to existing paragraph or create new one if needed
            const paragraphs = contentDiv.querySelectorAll('p');
            const lastParagraph = paragraphs[paragraphs.length - 1];
            
            // Check if content contains paragraph break
            if (data.content.includes('\n\n')) {
                const parts = data.content.split('\n\n');
                lastParagraph.textContent += parts[0];
                
                for (let i = 1; i < parts.length; i++) {
                    if (parts[i].trim()) {
                        const newParagraph = document.createElement('p');
                        newParagraph.textContent = parts[i];
                        contentDiv.appendChild(newParagraph);
                    }
                }
            } else {
                lastParagraph.textContent += data.content;
            }
        }
        
        // Auto-scroll to bottom
        this.scrollToBottom();
    }
    
    handleGenerationStart(data) {
        if (data.speaker === this.philosopherId) {
            this.isGenerating = true;
            this.showThinkingIndicator(false);
        } else {
            this.showThinkingIndicator(true);
        }
    }
    
    handleGenerationComplete(data) {
        if (data.speaker === this.philosopherId) {
            this.isGenerating = false;
            
            // Mark message as complete
            const generatingMessage = document.querySelector('.dialogue-entry.generating');
            if (generatingMessage) {
                generatingMessage.classList.remove('generating');
                
                // Add timestamp
                const timestamp = this.createTimestamp();
                generatingMessage.appendChild(timestamp);
            }
            
            // Update exchange count
            this.updateExchangeCount();
        }
        
        this.showThinkingIndicator(false);
    }
    
    createMessageContainer() {
        const entry = document.createElement('article');
        entry.className = 'dialogue-entry generating';
        entry.setAttribute('role', 'article');
        entry.setAttribute('aria-label', 'Philosophical statement');
        
        // Create header
        const header = document.createElement('header');
        
        const philosopherLabel = document.createElement('h2');
        philosopherLabel.className = 'philosopher-label';
        philosopherLabel.textContent = this.philosopherName.textContent;
        
        const authorStyle = document.createElement('p');
        authorStyle.className = 'author-style';
        authorStyle.textContent = this.authorVoice.textContent;
        
        header.appendChild(philosopherLabel);
        header.appendChild(authorStyle);
        
        // Create content container
        const content = document.createElement('div');
        content.className = 'dialogue-content';
        content.setAttribute('lang', 'en');
        
        entry.appendChild(header);
        entry.appendChild(content);
        
        return entry;
    }
    
    createTimestamp() {
        const timestamp = document.createElement('div');
        timestamp.className = 'entry-timestamp';
        
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        timestamp.textContent = timeString;
        this.timestamp.textContent = `Last update: ${timeString}`;
        
        return timestamp;
    }
    
    loadMessages(history) {
        // Clear existing content
        this.dialogueContent.innerHTML = '';
        
        // Filter and display messages for this philosopher
        const myMessages = history.filter(msg => msg.speaker === this.philosopherId);
        
        myMessages.forEach(message => {
            const entry = this.createMessageContainer();
            entry.classList.remove('generating');
            
            const content = entry.querySelector('.dialogue-content');
            
            // Split content into paragraphs
            const paragraphs = message.content.split('\n\n');
            paragraphs.forEach(para => {
                if (para.trim()) {
                    const p = document.createElement('p');
                    p.textContent = para.trim();
                    content.appendChild(p);
                }
            });
            
            // Add timestamp
            const timestamp = this.createTimestamp();
            entry.appendChild(timestamp);
            
            this.dialogueContent.appendChild(entry);
        });
        
        // Update exchange count
        this.exchangeCount.textContent = Math.floor(history.length / 2);
        
        this.scrollToBottom();
    }
    
    loadConversationHistory(data) {
        if (data.history && data.history.length > 0) {
            this.loadMessages(data.history);
        }
        
        if (data.config) {
            this.currentConfig = data.config;
            this.updatePhilosopherInfo();
        }
    }
    
    updateExchangeCount() {
        const currentCount = parseInt(this.exchangeCount.textContent) || 0;
        this.exchangeCount.textContent = currentCount + 1;
    }
    
    showThinkingIndicator(show) {
        if (this.thinkingIndicator) {
            this.thinkingIndicator.style.display = show ? 'inline-flex' : 'none';
        }
    }
    
    scrollToBottom() {
        this.dialogueContent.scrollTop = this.dialogueContent.scrollHeight;
    }
    
    updateConnectionStatus(connected) {
        const dot = document.querySelector('.connection-dot');
        if (dot) {
            dot.style.background = connected ? '#48bb78' : '#fc8181';
        }
        
        if (this.connectionText) {
            this.connectionText.textContent = connected ? 'Connected' : 'Disconnected';
        }
    }
    
    showError(error) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.cssText = `
            background: #fc8181;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 20px;
            text-align: center;
        `;
        errorDiv.textContent = `Error: ${error}`;
        
        this.dialogueContent.appendChild(errorDiv);
        this.scrollToBottom();
        
        // Remove after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
    
    setupSpeechifyNotice() {
        // Show Speechify notice on first load
        if (!localStorage.getItem('speechifyNoticeShown')) {
            const notice = document.querySelector('.speechify-notice');
            if (notice) {
                notice.style.display = 'block';
                
                setTimeout(() => {
                    notice.style.display = 'none';
                    localStorage.setItem('speechifyNoticeShown', 'true');
                }, 10000);
            }
        }
    }
}

// Initialize dialogue client when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const client = new DialogueClient();
    
    // Make client accessible globally for debugging
    window.dialogueClient = client;
    
    console.log(`Dialogue Client initialized for Philosopher ${client.philosopherId}`);
});