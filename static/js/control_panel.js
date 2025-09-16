/**
 * Control Panel JavaScript
 * Manages dialogue configuration and initialization
 */

class ControlPanel {
    constructor() {
        this.socket = null;
        this.conversationId = null;
        this.philosopher1Window = null;
        this.philosopher2Window = null;
        
        this.initializeSocket();
        this.initializeElements();
        this.attachEventListeners();
        this.loadSavedConfig();
    }
    
    initializeElements() {
        // Form elements
        this.philosopher1Select = document.getElementById('philosopher1');
        this.author1Select = document.getElementById('author1');
        this.model1Select = document.getElementById('model1');
        
        this.philosopher2Select = document.getElementById('philosopher2');
        this.author2Select = document.getElementById('author2');
        this.model2Select = document.getElementById('model2');
        
        this.topicInput = document.getElementById('topic');
        
        // Buttons
        this.beginButton = document.getElementById('beginDialogue');
        this.continueButton = document.getElementById('continueDialogue');
        
        // Status elements
        this.statusSection = document.getElementById('statusSection');
        this.conversationIdSpan = document.getElementById('conversationId');
        this.exchangeCountSpan = document.getElementById('exchangeCount');
    }
    
    initializeSocket() {
        this.socket = io('http://localhost:5001');
        
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.updateConnectionStatus(true);
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.updateConnectionStatus(false);
        });
        
        this.socket.on('dialogue_started', (data) => {
            this.handleDialogueStarted(data);
        });
        
        this.socket.on('generation_start', (data) => {
            this.updateStatus('generating', `${data.philosopher} is contemplating...`);
        });
        
        this.socket.on('generation_complete', (data) => {
            this.updateStatus('idle', 'Ready');
            this.updateExchangeCount(data.message);
        });
        
        this.socket.on('generation_error', (data) => {
            this.updateStatus('error', `Error: ${data.error}`);
            alert(`Generation error: ${data.error}`);
        });
    }
    
    attachEventListeners() {
        // Form validation on change
        const validateForm = () => this.validateForm();
        
        this.philosopher1Select.addEventListener('change', validateForm);
        this.author1Select.addEventListener('change', validateForm);
        this.philosopher2Select.addEventListener('change', validateForm);
        this.author2Select.addEventListener('change', validateForm);
        this.topicInput.addEventListener('input', validateForm);
        
        // Button handlers
        this.beginButton.addEventListener('click', () => this.beginDialogue());
        this.continueButton.addEventListener('click', () => this.continueDialogue());
        
        // Save config on change
        const saveConfig = () => this.saveConfig();
        this.philosopher1Select.addEventListener('change', saveConfig);
        this.author1Select.addEventListener('change', saveConfig);
        this.model1Select.addEventListener('change', saveConfig);
        this.philosopher2Select.addEventListener('change', saveConfig);
        this.author2Select.addEventListener('change', saveConfig);
        this.model2Select.addEventListener('change', saveConfig);
        
        // Prevent selecting same philosopher twice
        this.philosopher1Select.addEventListener('change', () => {
            if (this.philosopher1Select.value === this.philosopher2Select.value && 
                this.philosopher1Select.value !== '') {
                alert('Please select different philosophers for each voice');
                this.philosopher1Select.value = '';
                this.validateForm();
            }
        });
        
        this.philosopher2Select.addEventListener('change', () => {
            if (this.philosopher2Select.value === this.philosopher1Select.value && 
                this.philosopher2Select.value !== '') {
                alert('Please select different philosophers for each voice');
                this.philosopher2Select.value = '';
                this.validateForm();
            }
        });
    }
    
    validateForm() {
        const isValid = 
            this.philosopher1Select.value !== '' &&
            this.author1Select.value !== '' &&
            this.philosopher2Select.value !== '' &&
            this.author2Select.value !== '' &&
            this.topicInput.value.trim().length >= 5 &&
            this.topicInput.value.trim().length <= 200 &&
            this.philosopher1Select.value !== this.philosopher2Select.value;
        
        this.beginButton.disabled = !isValid;
        
        return isValid;
    }
    
    saveConfig() {
        const config = {
            philosopher1: this.philosopher1Select.value,
            author1: this.author1Select.value,
            model1: this.model1Select.value,
            philosopher2: this.philosopher2Select.value,
            author2: this.author2Select.value,
            model2: this.model2Select.value
        };
        
        localStorage.setItem('philosophicalDialogueConfig', JSON.stringify(config));
    }
    
    loadSavedConfig() {
        const saved = localStorage.getItem('philosophicalDialogueConfig');
        
        if (saved) {
            try {
                const config = JSON.parse(saved);
                
                this.philosopher1Select.value = config.philosopher1 || '';
                this.author1Select.value = config.author1 || '';
                this.model1Select.value = config.model1 || 'mistral:7b';
                this.philosopher2Select.value = config.philosopher2 || '';
                this.author2Select.value = config.author2 || '';
                this.model2Select.value = config.model2 || 'mistral:7b';
                
                this.validateForm();
            } catch (e) {
                console.error('Error loading saved config:', e);
            }
        }
    }
    
    beginDialogue() {
        if (!this.validateForm()) {
            alert('Please complete all fields before beginning dialogue');
            return;
        }
        
        const config = {
            philosopher1: this.philosopher1Select.value,
            author1: this.author1Select.value,
            model1: this.model1Select.value,
            philosopher2: this.philosopher2Select.value,
            author2: this.author2Select.value,
            model2: this.model2Select.value,
            topic: this.topicInput.value.trim()
        };
        
        // Disable button during initialization
        this.beginButton.disabled = true;
        this.beginButton.textContent = 'Initializing...';
        
        // Send configuration to server
        this.socket.emit('start_dialogue', config);
    }
    
    handleDialogueStarted(data) {
        this.conversationId = data.conversation_id;
        this.conversationIdSpan.textContent = this.conversationId.substring(0, 8);
        
        // Show status section
        this.statusSection.style.display = 'block';
        
        // Reset button
        this.beginButton.textContent = 'Begin Dialogue';
        this.beginButton.disabled = false;
        
        // Enable continue button
        this.continueButton.disabled = false;
        
        // Join conversation room
        this.socket.emit('join_conversation', {
            conversation_id: this.conversationId,
            client_type: 'control'
        });
        
        // Open philosopher windows
        this.openPhilosopherWindows();
        
        // Update status
        this.updateStatus('generating', 'Dialogue beginning...');
    }
    
    openPhilosopherWindows() {
        // Calculate window positions
        const screenWidth = window.screen.availWidth;
        const screenHeight = window.screen.availHeight;
        const windowWidth = Math.floor(screenWidth / 2) - 20;
        const windowHeight = screenHeight - 100;
        
        // Open philosopher 1 window (left side)
        this.philosopher1Window = window.open(
            `/philosopher/1?conversation_id=${this.conversationId}`,
            `philosopher1_${this.conversationId}`,
            `width=${windowWidth},height=${windowHeight},left=0,top=50,popup=no`
        );
        
        // Open philosopher 2 window (right side)
        this.philosopher2Window = window.open(
            `/philosopher/2?conversation_id=${this.conversationId}`,
            `philosopher2_${this.conversationId}`,
            `width=${windowWidth},height=${windowHeight},left=${windowWidth + 40},top=50,popup=no`
        );
        
        // Check if windows were blocked
        if (!this.philosopher1Window || !this.philosopher2Window) {
            alert('Please allow pop-ups for this site to open philosopher windows');
        }
    }
    
    continueDialogue() {
        if (!this.conversationId) {
            alert('No active conversation to continue');
            return;
        }
        
        this.continueButton.disabled = true;
        this.continueButton.textContent = 'Generating...';
        
        this.socket.emit('continue_dialogue', {
            conversation_id: this.conversationId
        });
        
        setTimeout(() => {
            this.continueButton.disabled = false;
            this.continueButton.textContent = 'Continue Conversation';
        }, 3000);
    }
    
    updateStatus(status, message) {
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.querySelector('.status-text');
        
        if (statusDot && statusText) {
            statusText.textContent = message;
            
            // Update dot color based on status
            switch(status) {
                case 'generating':
                    statusDot.style.background = '#f6ad55'; // Orange
                    break;
                case 'idle':
                    statusDot.style.background = '#48bb78'; // Green
                    break;
                case 'error':
                    statusDot.style.background = '#fc8181'; // Red
                    break;
            }
        }
    }
    
    updateExchangeCount(message) {
        // Count exchanges from the conversation
        if (this.exchangeCountSpan) {
            const currentCount = parseInt(this.exchangeCountSpan.textContent) || 0;
            if (message && message.speaker === 2) {
                this.exchangeCountSpan.textContent = currentCount + 1;
            }
        }
    }
    
    updateConnectionStatus(connected) {
        const statusDot = document.querySelector('.connection-dot');
        if (statusDot) {
            statusDot.style.background = connected ? '#48bb78' : '#fc8181';
        }
    }
}

// Initialize control panel when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const controlPanel = new ControlPanel();
    
    // Make control panel accessible globally for debugging
    window.controlPanel = controlPanel;
    
    console.log('Control Panel initialized');
});