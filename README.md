# Philosophical Dialogues Through Literary Voices

A sophisticated local web application that orchestrates AI-generated philosophical dialogues where classic philosophers speak through the literary styles of renowned fiction authors. Designed specifically for Mac Studio's unified memory architecture.

## 🎭 Overview

This application creates automated conversations between two philosopher-author pairings on any topic you choose. Each philosopher's ideas are translated through a specific author's literary voice, making timeless wisdom accessible through familiar narrative styles.

## 🚀 Quick Start

1. **Download all files** to a new directory:
   - `dialogue_backend.py` - Flask server
   - `dialogue_app.html` - Web interface  
   - `setup.sh` - Setup script
   - `requirements.txt` - Python dependencies

2. **Make the setup script executable:**
   ```bash
   chmod +x setup.sh
   ```

3. **Run the setup script:**
   ```bash
   ./setup.sh
   ```

4. **Open your browser** to http://localhost:5000

The setup script will automatically:
- Check for Python and Ollama
- Create a virtual environment
- Install dependencies
- Download required models (first run only)
- Start the server

## 💻 System Requirements

- **Mac Studio** (or Mac with Apple Silicon)
- **Memory:** 16GB minimum, 32GB+ recommended
- **Storage:** ~15GB for models
- **macOS:** 11.0 or later
- **Python:** 3.9 or higher
- **Ollama:** Latest version

## 📦 Manual Installation

If you prefer manual setup:

1. **Install Ollama:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Download models:**
   ```bash
   ollama pull llama3.2:3b
   ollama pull mistral:7b
   ollama pull qwen2.5:7b
   ollama pull gemma2:9b
   ```

3. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Python packages:**
   ```bash
   pip install flask flask-cors ollama aiofiles python-dotenv
   ```

5. **Run the server:**
   ```bash
   python3 dialogue_backend.py
   ```

## 🎨 Features

### Philosophers Available

**Ancient & Classical:**
- Socrates, Plato, Aristotle
- Marcus Aurelius, Epicurus
- Confucius, Lao Tzu, Buddha

**Modern Western:**
- Descartes, Spinoza, Hume, Kant
- Kierkegaard, Nietzsche
- Wittgenstein, Sartre

**Contemporary:**
- Hannah Arendt, Simone de Beauvoir
- Martha Nussbaum

### Literary Voices

**Classic Authors:**
- Hemingway (sparse, direct)
- Woolf (stream of consciousness)
- Dickens (Victorian elaborate)
- Austen (witty social commentary)

**Modern Masters:**
- García Márquez (magical realism)
- Kafka (surreal anxiety)
- Vonnegut (satirical humanity)
- Morrison (lyrical depth)

**Contemporary Voices:**
- Murakami (dreamlike modern)
- Atwood (sharp dystopian)
- Ishiguro (subtle restraint)

## 🎯 Usage Tips

1. **Topic Selection:** Be specific but open-ended
   - Good: "The nature of consciousness in the age of AI"
   - Too broad: "Life"
   - Too narrow: "Should I buy a Tesla?"

2. **Pairing Strategy:**
   - Contrast philosophies (Stoic vs Existentialist)
   - Match complexity (Kant + Joyce for depth)
   - Balance accessibility (Socrates + Hemingway for clarity)

3. **Model Selection:**
   - **Llama 3.2 3B:** Fast responses, good for quick exploration
   - **Mistral 7B:** Balanced performance and quality
   - **Qwen 2.5 7B:** Strong on philosophical reasoning
   - **Gemma 2 9B:** Best quality, slower generation

## 🔊 Speechify Integration

The interface is optimized for the Speechify Chrome extension:

1. Install Speechify from Chrome Web Store
2. Let dialogue generate
3. Click Speechify extension icon
4. Select text or use full-page reading
5. Adjust voice and speed as desired

The semantic HTML structure ensures proper reading order and emphasis.

## 🛠 Troubleshooting

### "Ollama not found"
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
```

### "Model not found"
```bash
# Download missing model
ollama pull model_name
```

### Server won't start
```bash
# Check if port 5000 is in use
lsof -i:5000
# Kill existing process or use different port
```

### Slow generation
- Ensure no other heavy applications running
- Use smaller models (3B instead of 9B)
- Close unnecessary browser tabs
- Check Activity Monitor for memory pressure

## 🎮 Advanced Configuration

### Change Port
Edit `dialogue_backend.py` line at bottom:
```python
app.run(host='0.0.0.0', port=8080)  # Change 5000 to 8080
```

### Add Custom Models
Edit the HTML file's model dropdowns:
```html
<option value="your-model:tag">Your Model Name</option>
```

### Adjust Generation Length
In `dialogue_backend.py`, modify:
```python
'max_tokens': 500,  # Increase for longer responses
'temperature': 0.8,  # Decrease for more focused responses
```

## 📊 Performance Expectations

On Mac Studio M2 Ultra (96GB):
- **First response:** 5-10 seconds
- **Subsequent responses:** 3-7 seconds  
- **Tokens/second:** 15-30 depending on model
- **Concurrent models:** 2-4 comfortably

## 🔒 Privacy & Security

- **100% Local:** No data leaves your machine
- **No Analytics:** Zero tracking or telemetry
- **No Account Required:** Completely standalone
- **Your Topics:** Private and never logged

## 🐛 Known Limitations

1. DeepSeek R1 models require manual installation
2. First model load takes 10-30 seconds
3. Browser refresh loses conversation history
4. Maximum 10 exchanges before potential context issues

## 📝 License

MIT License - Free for personal and commercial use

## 🤝 Contributing

This is a demonstration project. Feel free to fork and modify for your needs.

## 📧 Support

This is provided as-is for educational purposes. For Ollama issues, see: https://github.com/ollama/ollama

---

*Built with Flask, Ollama, and the unified memory architecture of Apple Silicon*