#!/usr/bin/env python3
"""
Philosophical Dialogue System - Flask/SocketIO Backend
Dual-view synchronized dialogue generation with local LLM inference
"""

import os
import json
import uuid
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from threading import Thread
import traceback

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'philosophical-dialogue-secret-2025'

# Initialize SocketIO with CORS support
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state management
active_conversations: Dict[str, Dict[str, Any]] = {}
client_sessions: Dict[str, Dict[str, Any]] = {}

# Load philosopher and author data
def load_metadata():
    """Load philosopher and author metadata from JSON files"""
    try:
        with open('data/philosophers.json', 'r') as f:
            philosophers = json.load(f)
        with open('data/authors.json', 'r') as f:
            authors = json.load(f)
        return philosophers, authors
    except FileNotFoundError:
        logger.warning("Metadata files not found, using embedded defaults")
        return get_default_philosophers(), get_default_authors()

def get_default_philosophers():
    """Embedded philosopher data as fallback"""
    return {
        "socrates": {
            "name": "Socrates",
            "era": "Ancient Greek (470-399 BCE)",
            "key_concepts": ["know thyself", "examined life", "virtue as knowledge", "dialectical method"],
            "beliefs": "wisdom through acknowledging ignorance, moral virtue, divine inner voice",
            "style": "questioning, ironic, humble yet penetrating"
        },
        "plato": {
            "name": "Plato",
            "era": "Ancient Greek (428-348 BCE)",
            "key_concepts": ["theory of Forms", "ideal state", "philosopher kings", "allegory of the cave"],
            "beliefs": "eternal Forms, tripartite soul, justice as harmony",
            "style": "idealistic, systematic, metaphorical"
        },
        "aristotle": {
            "name": "Aristotle",
            "era": "Ancient Greek (384-322 BCE)",
            "key_concepts": ["golden mean", "eudaimonia", "potentiality and actuality", "four causes"],
            "beliefs": "virtue ethics, teleology, logic as tool for truth",
            "style": "systematic, empirical, categorizing"
        },
        "marcus_aurelius": {
            "name": "Marcus Aurelius",
            "era": "Roman (121-180 CE)",
            "key_concepts": ["stoic virtue", "cosmic perspective", "present moment", "duty"],
            "beliefs": "stoicism, universal reason, acceptance of fate",
            "style": "personal, practical, contemplative"
        },
        "buddha": {
            "name": "Siddhartha Gautama (Buddha)",
            "era": "Ancient Indian (563-483 BCE)",
            "key_concepts": ["four noble truths", "eightfold path", "non-self", "dependent origination"],
            "beliefs": "middle way, liberation from suffering",
            "style": "compassionate, practical, metaphorical"
        },
        "confucius": {
            "name": "Confucius",
            "era": "Ancient Chinese (551-479 BCE)",
            "key_concepts": ["ren", "li", "junzi", "rectification of names"],
            "beliefs": "social harmony, filial piety, moral cultivation",
            "style": "practical, social, virtue-focused"
        },
        "descartes": {
            "name": "René Descartes",
            "era": "17th century (1596-1650)",
            "key_concepts": ["cogito ergo sum", "methodical doubt", "mind-body dualism", "clear and distinct ideas"],
            "beliefs": "rationalism, mathematical certainty in philosophy",
            "style": "methodical, skeptical progressing to certainty"
        },
        "hume": {
            "name": "David Hume",
            "era": "18th century Scottish (1711-1776)",
            "key_concepts": ["impressions and ideas", "bundle theory", "is-ought problem", "miracles critique"],
            "beliefs": "empiricism, sentiment over reason in morality",
            "style": "skeptical, witty, empirical"
        },
        "kant": {
            "name": "Immanuel Kant",
            "era": "18th century German (1724-1804)",
            "key_concepts": ["categorical imperative", "synthetic a priori", "phenomena/noumena", "transcendental idealism"],
            "beliefs": "moral duty, limits of reason, human dignity",
            "style": "systematic, precise, architectonic"
        },
        "kierkegaard": {
            "name": "Søren Kierkegaard",
            "era": "19th century Danish (1813-1855)",
            "key_concepts": ["leap of faith", "anxiety", "stages of life", "subjective truth"],
            "beliefs": "Christian existentialism, individual over system",
            "style": "passionate, paradoxical, literary"
        },
        "nietzsche": {
            "name": "Friedrich Nietzsche",
            "era": "19th century German (1844-1900)",
            "key_concepts": ["will to power", "eternal recurrence", "übermensch", "master/slave morality"],
            "beliefs": "life affirmation, critique of Christianity, perspectivism",
            "style": "aphoristic, provocative, poetic"
        },
        "wittgenstein": {
            "name": "Ludwig Wittgenstein",
            "era": "20th century Austrian-British (1889-1951)",
            "key_concepts": ["language games", "forms of life", "showing vs saying", "private language"],
            "beliefs": "meaning as use, philosophy as therapy",
            "style": "precise, enigmatic, therapeutic"
        },
        "sartre": {
            "name": "Jean-Paul Sartre",
            "era": "20th century French (1905-1980)",
            "key_concepts": ["existence precedes essence", "bad faith", "radical freedom", "the Look"],
            "beliefs": "atheistic existentialism, condemned to freedom",
            "style": "phenomenological, dramatic, engaged"
        },
        "de_beauvoir": {
            "name": "Simone de Beauvoir",
            "era": "20th century French (1908-1986)",
            "key_concepts": ["situated freedom", "ethics of ambiguity", "woman as Other", "bad faith"],
            "beliefs": "existentialist feminism, ethics of liberation",
            "style": "phenomenological, feminist, engaged"
        },
        "arendt": {
            "name": "Hannah Arendt",
            "era": "20th century German-American (1906-1975)",
            "key_concepts": ["banality of evil", "vita activa", "public/private", "plurality"],
            "beliefs": "importance of political action, thinking without banisters",
            "style": "analytical, historical, politically engaged"
        }
    }

def get_default_authors():
    """Embedded author data as fallback"""
    return {
        "austen": {
            "name": "Jane Austen",
            "characteristics": "free indirect discourse, social observation, wit, irony",
            "voice": "satirical, mannered, precise, socially astute"
        },
        "dickens": {
            "name": "Charles Dickens",
            "characteristics": "elaborate descriptions, sentiment, social criticism, memorable characters",
            "voice": "Victorian, expansive, moralistic, humorous"
        },
        "wilde": {
            "name": "Oscar Wilde",
            "characteristics": "epigrams, paradoxes, aestheticism, wit",
            "voice": "witty, decadent, paradoxical, sophisticated"
        },
        "hemingway": {
            "name": "Ernest Hemingway",
            "characteristics": "short sentences, simple words, concrete imagery, iceberg theory",
            "voice": "direct, understated, masculine, journalistic"
        },
        "woolf": {
            "name": "Virginia Woolf",
            "characteristics": "stream of consciousness, long flowing sentences, interior monologue, time fluidity",
            "voice": "lyrical, introspective, modernist, feminist"
        },
        "joyce": {
            "name": "James Joyce",
            "characteristics": "stream of consciousness, experimental, mythic parallels, language play",
            "voice": "modernist, Irish, complex, revolutionary"
        },
        "kafka": {
            "name": "Franz Kafka",
            "characteristics": "surreal situations, bureaucratic nightmares, alienation, ambiguity",
            "voice": "anxious, precise, dreamlike, oppressive"
        },
        "tolkien": {
            "name": "J.R.R. Tolkien",
            "characteristics": "elevated language, world-building detail, mythic scope, linguistic richness",
            "voice": "epic, archaic touches, moral clarity, eucatastrophe"
        },
        "vonnegut": {
            "name": "Kurt Vonnegut",
            "characteristics": "simple syntax, dark humor, science fiction elements, fatalism",
            "voice": "sardonic, humane, anti-war, accessible"
        },
        "borges": {
            "name": "Jorge Luis Borges",
            "characteristics": "labyrinths, mirrors, infinite recursion, scholarly tone",
            "voice": "erudite, metaphysical, playful, mysterious"
        },
        "marquez": {
            "name": "Gabriel García Márquez",
            "characteristics": "magical realism, cyclical time, lush descriptions, myth blending",
            "voice": "sensual, fantastical, political, Latin American"
        },
        "baldwin": {
            "name": "James Baldwin",
            "characteristics": "passionate rhetoric, long sentences, biblical cadence, moral urgency",
            "voice": "prophetic, eloquent, confrontational, compassionate"
        },
        "calvino": {
            "name": "Italo Calvino",
            "characteristics": "lightness, multiplicity, metafiction, combinatorial",
            "voice": "playful, philosophical, fantastical, precise"
        },
        "morrison": {
            "name": "Toni Morrison",
            "characteristics": "lyrical prose, nonlinear narrative, African American experience, memory",
            "voice": "poetic, haunting, politically engaged, spiritual"
        },
        "le_guin": {
            "name": "Ursula K. Le Guin",
            "characteristics": "anthropological depth, gender exploration, ecological themes, clarity",
            "voice": "wise, speculative, feminist, Taoist-influenced"
        },
        "murakami": {
            "name": "Haruki Murakami",
            "characteristics": "surreal elements, parallel worlds, jazz references, alienation",
            "voice": "dreamlike, contemporary, Japanese-Western fusion"
        },
        "ishiguro": {
            "name": "Kazuo Ishiguro",
            "characteristics": "unreliable narrators, emotional restraint, memory, subtle reveals",
            "voice": "understated, melancholic, precise, haunting"
        },
        "atwood": {
            "name": "Margaret Atwood",
            "characteristics": "dystopian elements, feminist themes, environmental concerns, sharp prose",
            "voice": "incisive, speculative, Canadian, politically aware"
        },
        "butler": {
            "name": "Octavia Butler",
            "characteristics": "Afrofuturism, power dynamics, biological themes, survival",
            "voice": "visionary, grounded, African American, transformative"
        },
        "pynchon": {
            "name": "Thomas Pynchon",
            "characteristics": "paranoia, encyclopedic, conspiracy, entropy",
            "voice": "complex, paranoid, satirical, postmodern"
        }
    }

# Load metadata on startup
PHILOSOPHERS, AUTHORS = load_metadata()

class DialogueGenerator:
    """Handles dialogue generation with Ollama integration"""
    
    def __init__(self):
        host = os.getenv("OLLAMA_HOST")
        if host:
            # if the env var doesn’t start with http:// or https://, prepend http://
            if not host.startswith(("http://", "https://")):
                host = f"http://{host}"
            self.ollama_url = host
        else:
            self.ollama_url = "http://localhost:11434"

# def create_prompt(self, philosopher: str, author: str, topic: str,
#                   history: List[Dict], is_response: bool = False) -> str:
#     phil = PHILOSOPHERS.get(philosopher, {})
#     auth = AUTHORS.get(author, {})

#     key_concepts = ', '.join(phil.get('key_concepts', []))
#     beliefs = phil.get('beliefs', '')
#     style = auth.get('characteristics', '')
#     voice = auth.get('voice', '')

#     if is_response and history:
#         last_message = history[-1] if history else None
#         last_content = last_message.get('content', '')[:500] if last_message else ''
#         prompt = (
#             f"Adopt the philosophical stance defined by these ideas: {beliefs}, focusing on concepts such as {key_concepts}. "
#             f"Respond to the following statement in one to three sentences, using a narrative style characterized by {style} "
#             f"with a {voice} voice. Avoid naming any philosopher or author and do not reference the author's personal beliefs "
#             f"or values. Directly answer the previous point and pose a related question or segue to keep the dialogue flowing.\n\n"
#             f'Previous message: \"{last_content}\"\n'
#             f'Topic: \"{topic}\"'
#         )
#     else:
#         prompt = (
#             f"Assume a philosophical stance defined by these ideas: {beliefs}, focusing on concepts such as {key_concepts}. "
#             f"Use a narrative style described as {style} with a {voice} voice to introduce your perspective on the topic "
#             f"\"{topic}\" in one to three sentences. Avoid naming any philosopher or author and do not reference the author's "
#             f"personal beliefs or values. Pose a thoughtful question to invite your dialogue partner to respond."
#         )
#     return prompt

# Your philosophical position includes:
# - Key concepts: {', '.join(phil.get('key_concepts', []))}
# - Core beliefs: {phil.get('beliefs', '')}

# Writing style characteristics: {auth.get('characteristics', '')}
# Literary voice: {auth.get('voice', '')}


    def create_prompt(self, philosopher: str, author: str, topic: str, 
                     history: List[Dict], is_response: bool = False) -> str:
        """Create specialized prompt for dialogue generation"""
        
        phil = PHILOSOPHERS.get(philosopher, {})
        auth = AUTHORS.get(author, {})
        
        if is_response and history:
            # Response template
            last_message = history[-1] if history else None
            last_content = last_message.get('content', '')[:500] if last_message else ''
            
            front_matter = """Never mention the name of the philospher. You are not describing
their views, instead you are embodying them.

Never mention the name of the author. You are not describing
their views, instead you are embodying them.

Note that of greatest importance is to distingusih that your task is to embody
    the ideas/stance/arguments/beliefs/values of the philosopher (or likely ideas on the topic)
    NOT their writing/communication style at all!

Note that of greatest importance is to distingusih that your task is to embody
    the writing/communication/dialogue style of the author (acting as a character in one of their books might)
    NOT their ideas/stance/arguments/beliefs/values at all!

Separate components, the philosopher speaking through the author.
The author studying the philosopher thoroughly and creating a character in one of their novels portraying them covertly.

There is no commentary around the writing, only the content itself. The dialogue is not quoted. There is no narrator or descriptions of setting other than what naturally flows from the conversation.

This is conversational. Brief bursts of dialogue. One to three sentences. Posing questions to each other. Answering the others questions and moving on with a believable and interesting segue.
"""

            prompt = f"""You are {phil.get('name', philosopher)}, the {phil.get('era', '')} philosopher.
Express your philosophical ideas through the author {auth.get('name', author)}'s literary style.

{front_matter}

Previous statement to respond to:
"{last_content}"

Topic: "{topic}"

Respond in 2-3 sentences that:
1. Engage directly with the previous philosophical position
2. Present your perspective using {auth.get('name', author)}'s narrative techniques
3. Use literary style to make philosophical concepts accessible
4. Advance the dialogue while maintaining philosophical authenticity

Write in a style both philosophically authentic and literarily engaging."""
        else:
            # Opening statement template
            prompt = f"""You are {phil.get('name', philosopher)}, the {phil.get('era', '')} philosopher.
Express your philosophical ideas through {auth.get('name', author)}'s literary style.

{front_matter}

Topic for discussion: "{topic}"

Craft an opening statement (2-3 sentences) that:
1. Introduces your philosophical perspective on this topic
2. Uses {auth.get('name', author)}'s narrative techniques to engage modern readers  
3. Poses questions or observations inviting deeper exploration
4. Makes classical wisdom immediately relevant

Write in a style both philosophically authentic and literarily engaging."""
        
        return prompt
    
    def generate_stream(self, model: str, prompt: str, conversation_id: str, 
                       speaker: int, callback):
        """Generate response with streaming to clients"""
        
        try:
            # Notify generation start
            socketio.emit('generation_start', {
                'speaker': speaker,
                'philosopher': conversation_id
            }, room=conversation_id)
            
            # Call Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "temperature": 0.8,
                        "top_p": 0.9,
                        "top_k": 40
                    }
                },
                stream=True
            )
            
            full_content = ""
            
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if 'response' in chunk:
                            content = chunk['response']
                            full_content += content
                            
                            # Emit chunk to clients
                            socketio.emit('message_chunk', {
                                'speaker': speaker,
                                'content': content,
                                'conversation_id': conversation_id
                            }, room=conversation_id)
                            
                            # Small delay for smooth streaming
                            time.sleep(0.02)
                            
                    except json.JSONDecodeError:
                        continue
            
            # Store complete message
            if conversation_id in active_conversations:
                active_conversations[conversation_id]['history'].append({
                    'speaker': speaker,
                    'content': full_content,
                    'timestamp': datetime.now().isoformat()
                })
            
            # Notify completion
            socketio.emit('generation_complete', {
                'speaker': speaker,
                'message': {
                    'speaker': speaker,
                    'content': full_content
                }
            }, room=conversation_id)
            
            return full_content
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            logger.error(traceback.format_exc())
            socketio.emit('generation_error', {
                'error': str(e)
            }, room=conversation_id)
            return None

generator = DialogueGenerator()

# Flask routes
@app.route('/')
def index():
    """Render control panel"""
    return render_template('control_panel.html')

@app.route('/philosopher/<int:philosopher_id>')
def philosopher_view(philosopher_id):
    """Render philosopher view"""
    conversation_id = request.args.get('conversation_id', '')
    return render_template('philosopher_view.html', 
                         philosopher_id=philosopher_id,
                         conversation_id=conversation_id)

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    client_id = request.sid
    client_sessions[client_id] = {
        'connected_at': datetime.now().isoformat()
    }
    logger.info(f"Client connected: {client_id}")
    emit('connected', {'client_id': client_id})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    client_id = request.sid
    if client_id in client_sessions:
        del client_sessions[client_id]
    logger.info(f"Client disconnected: {client_id}")

@socketio.on('join_conversation')
def handle_join(data):
    """Handle client joining conversation room"""
    conversation_id = data.get('conversation_id')
    client_type = data.get('client_type')
    client_id = request.sid
    
    if conversation_id and conversation_id in active_conversations:
        join_room(conversation_id)
        
        # Send current state to joining client
        conversation = active_conversations[conversation_id]
        emit('conversation_state', {
            'conversation': conversation,
            'client_type': client_type
        })
        
        logger.info(f"Client {client_id} joined conversation {conversation_id} as {client_type}")

@socketio.on('start_dialogue')
def handle_start_dialogue(data):
    """Initialize new dialogue"""
    try:
        # Create conversation ID
        conversation_id = str(uuid.uuid4())
        
        # Store conversation configuration
        active_conversations[conversation_id] = {
            'id': conversation_id,
            'config': data,
            'history': [],
            'created_at': datetime.now().isoformat(),
            'exchange_count': 0
        }
        
        # Notify control panel
        emit('dialogue_started', {
            'conversation_id': conversation_id,
            'config': data
        })
        
        logger.info(f"Started dialogue {conversation_id}")
        
        # Start generation in background thread
        def generate_opening():
            # Generate first philosopher's opening
            prompt1 = generator.create_prompt(
                data['philosopher1'],
                data['author1'],
                data['topic'],
                [],
                is_response=False
            )
            
            generator.generate_stream(
                data['model1'],
                prompt1,
                conversation_id,
                1,
                None
            )
            
            # Brief pause between speakers
            time.sleep(2)
            
            # Generate second philosopher's response
            history = active_conversations[conversation_id]['history']
            prompt2 = generator.create_prompt(
                data['philosopher2'],
                data['author2'],
                data['topic'],
                history,
                is_response=True
            )
            
            generator.generate_stream(
                data['model2'],
                prompt2,
                conversation_id,
                2,
                None
            )
            
            # Update exchange count
            active_conversations[conversation_id]['exchange_count'] = 1
        
        # Run generation in background
        thread = Thread(target=generate_opening)
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        logger.error(f"Error starting dialogue: {e}")
        emit('generation_error', {'error': str(e)})

@socketio.on('continue_dialogue')
def handle_continue_dialogue(data):
    """Continue existing dialogue"""
    try:
        conversation_id = data.get('conversation_id')
        
        if conversation_id not in active_conversations:
            emit('generation_error', {'error': 'Conversation not found'})
            return
        
        conversation = active_conversations[conversation_id]
        config = conversation['config']
        history = conversation['history']
        
        # Check exchange limit
        # if conversation['exchange_count'] >= 20:
        #     emit('generation_error', {'error': 'Maximum exchanges reached'})
        #     return
        
        def generate_continuation():
            # Generate two more exchanges
            for i in range(2):
                # Determine speaker
                speaker = 1 if len(history) % 2 == 0 else 2
                philosopher = config['philosopher1'] if speaker == 1 else config['philosopher2']
                author = config['author1'] if speaker == 1 else config['author2']
                model = config['model1'] if speaker == 1 else config['model2']
                
                # Create prompt
                prompt = generator.create_prompt(
                    philosopher,
                    author,
                    config['topic'],
                    history,
                    is_response=True
                )
                
                # Generate response
                generator.generate_stream(
                    model,
                    prompt,
                    conversation_id,
                    speaker,
                    None
                )
                
                # Update history reference
                history = active_conversations[conversation_id]['history']
                
                # Brief pause between speakers
                if i == 0:
                    time.sleep(2)
            
            # Update exchange count
            active_conversations[conversation_id]['exchange_count'] += 1
        
        # Run generation in background
        thread = Thread(target=generate_continuation)
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        logger.error(f"Error continuing dialogue: {e}")
        emit('generation_error', {'error': str(e)})

@socketio.on('get_conversation_history')
def handle_get_history(data):
    """Send conversation history to client"""
    conversation_id = data.get('conversation_id')
    
    if conversation_id in active_conversations:
        conversation = active_conversations[conversation_id]
        emit('conversation_history', {
            'history': conversation['history'],
            'config': conversation['config']
        })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check Ollama connectivity
        response = requests.get(f"{generator.ollama_url}/api/tags", timeout=5)
        models = response.json().get('models', [])
        
        return {
            'status': 'healthy',
            'ollama': 'connected',
            'conversations': len(active_conversations),
            'clients': len(client_sessions),
            'models': [m['name'] for m in models]
        }
    except:
        return {
            'status': 'unhealthy',
            'ollama': 'disconnected',
            'conversations': len(active_conversations),
            'clients': len(client_sessions)
        }, 500

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   Philosophical Dialogue System - Dual View               ║
    ║   Server starting on http://localhost:5001               ║
    ╠══════════════════════════════════════════════════════════╣
    ║   Ensure Ollama is running with required models:         ║
    ║   - ollama pull llama3.2:3b                              ║
    ║   - ollama pull mistral:7b                               ║
    ║   - ollama pull qwen2.5:7b                               ║
    ║   - ollama pull gemma2:9b                                ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    socketio.run(app, host='0.0.0.0', port=5001, debug=False)