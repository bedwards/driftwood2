#!/usr/bin/env python3
"""
Philosophical Dialogue Generator Backend
Runs locally on Mac Studio with Ollama for LLM inference
"""

import json
import asyncio
from flask import Flask, render_template_string, request, Response, stream_with_context
from flask_cors import CORS
import ollama
from datetime import datetime
import logging
from typing import Dict, List, Optional
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Philosopher characteristics and philosophical positions
PHILOSOPHER_PROFILES = {
    'socrates': {
        'era': 'Ancient Greek',
        'key_concepts': ['know thyself', 'examined life', 'virtue as knowledge', 'dialectical method'],
        'style': 'questioning, ironic, humble yet penetrating',
        'beliefs': 'wisdom through acknowledging ignorance, moral virtue, divine inner voice'
    },
    'plato': {
        'era': 'Ancient Greek',
        'key_concepts': ['theory of Forms', 'ideal state', 'philosopher kings', 'allegory of the cave'],
        'style': 'idealistic, systematic, metaphorical',
        'beliefs': 'eternal Forms, tripartite soul, justice as harmony'
    },
    'aristotle': {
        'era': 'Ancient Greek', 
        'key_concepts': ['golden mean', 'eudaimonia', 'potentiality and actuality', 'four causes'],
        'style': 'systematic, empirical, categorizing',
        'beliefs': 'virtue ethics, teleology, logic as tool for truth'
    },
    'marcus_aurelius': {
        'era': 'Roman',
        'key_concepts': ['stoic virtue', 'cosmic perspective', 'present moment', 'duty'],
        'style': 'personal, practical, contemplative',
        'beliefs': 'stoicism, universal reason, acceptance of fate'
    },
    'epicurus': {
        'era': 'Hellenistic Greek',
        'key_concepts': ['ataraxia', 'absence of pain', 'friendship', 'atomic theory'],
        'style': 'gentle, reassuring, practical',
        'beliefs': 'pleasure as absence of suffering, mortality acceptance'
    },
    'spinoza': {
        'era': '17th century',
        'key_concepts': ['substance monism', 'God or Nature', 'emotions as confused ideas', 'necessity'],
        'style': 'geometric, rigorous, systematic',
        'beliefs': 'determinism, intellectual love of God, freedom through understanding'
    },
    'descartes': {
        'era': '17th century',
        'key_concepts': ['cogito ergo sum', 'methodical doubt', 'mind-body dualism', 'clear and distinct ideas'],
        'style': 'methodical, skeptical progressing to certainty',
        'beliefs': 'rationalism, mathematical certainty in philosophy'
    },
    'hume': {
        'era': '18th century Scottish',
        'key_concepts': ['impressions and ideas', 'bundle theory', 'is-ought problem', 'miracles critique'],
        'style': 'skeptical, witty, empirical',
        'beliefs': 'empiricism, sentiment over reason in morality'
    },
    'kant': {
        'era': '18th century German',
        'key_concepts': ['categorical imperative', 'synthetic a priori', 'phenomena/noumena', 'transcendental idealism'],
        'style': 'systematic, precise, architectonic',
        'beliefs': 'moral duty, limits of reason, human dignity'
    },
    'kierkegaard': {
        'era': '19th century Danish',
        'key_concepts': ['leap of faith', 'anxiety', 'stages of life', 'subjective truth'],
        'style': 'passionate, paradoxical, literary',
        'beliefs': 'Christian existentialism, individual over system'
    },
    'nietzsche': {
        'era': '19th century German',
        'key_concepts': ['will to power', 'eternal recurrence', 'übermensch', 'master/slave morality'],
        'style': 'aphoristic, provocative, poetic',
        'beliefs': 'life affirmation, critique of Christianity, perspectivism'
    },
    'sartre': {
        'era': '20th century French',
        'key_concepts': ['existence precedes essence', 'bad faith', 'radical freedom', 'the Look'],
        'style': 'phenomenological, dramatic, engaged',
        'beliefs': 'atheistic existentialism, condemned to freedom'
    },
    'wittgenstein': {
        'era': '20th century Austrian-British',
        'key_concepts': ['language games', 'forms of life', 'showing vs saying', 'private language'],
        'style': 'precise, enigmatic, therapeutic',
        'beliefs': 'meaning as use, philosophy as therapy'
    },
    'hannah_arendt': {
        'era': '20th century German-American',
        'key_concepts': ['banality of evil', 'vita activa', 'public/private', 'plurality'],
        'style': 'analytical, historical, politically engaged',
        'beliefs': 'importance of political action, thinking without banisters'
    },
    'simone_de_beauvoir': {
        'era': '20th century French',
        'key_concepts': ['situated freedom', 'ethics of ambiguity', 'woman as Other', 'bad faith'],
        'style': 'phenomenological, feminist, engaged',
        'beliefs': 'existentialist feminism, ethics of liberation'
    },
    'buddha': {
        'era': 'Ancient Indian',
        'key_concepts': ['four noble truths', 'eightfold path', 'non-self', 'dependent origination'],
        'style': 'compassionate, practical, metaphorical',
        'beliefs': 'middle way, liberation from suffering'
    },
    'confucius': {
        'era': 'Ancient Chinese',
        'key_concepts': ['ren', 'li', 'junzi', 'rectification of names'],
        'style': 'practical, social, virtue-focused',
        'beliefs': 'social harmony, filial piety, moral cultivation'
    },
    'lao_tzu': {
        'era': 'Ancient Chinese',
        'key_concepts': ['dao', 'wu wei', 'yin yang', 'simplicity'],
        'style': 'paradoxical, poetic, mystical',
        'beliefs': 'natural way, non-action, return to simplicity'
    },
    'rumi': {
        'era': '13th century Persian',
        'key_concepts': ['divine love', 'whirling', 'unity', 'spiritual intoxication'],
        'style': 'ecstatic, poetic, mystical',
        'beliefs': 'Sufi mysticism, love as path to divine'
    },
    'martha_nussbaum': {
        'era': 'Contemporary American',
        'key_concepts': ['capabilities approach', 'fragility of goodness', 'political emotions', 'cosmopolitanism'],
        'style': 'analytical, humanistic, interdisciplinary',
        'beliefs': 'human dignity, emotions in ethics, global justice'
    }
}

# Author writing styles
AUTHOR_STYLES = {
    'hemingway': {
        'characteristics': 'short sentences, simple words, concrete imagery, iceberg theory',
        'voice': 'direct, understated, masculine, journalistic'
    },
    'woolf': {
        'characteristics': 'stream of consciousness, long flowing sentences, interior monologue, time fluidity',
        'voice': 'lyrical, introspective, modernist, feminist'
    },
    'tolkien': {
        'characteristics': 'elevated language, world-building detail, mythic scope, linguistic richness',
        'voice': 'epic, archaic touches, moral clarity, eucatastrophe'
    },
    'austen': {
        'characteristics': 'free indirect discourse, social observation, wit, irony',
        'voice': 'satirical, mannered, precise, socially astute'
    },
    'dickens': {
        'characteristics': 'elaborate descriptions, sentiment, social criticism, memorable characters',
        'voice': 'Victorian, expansive, moralistic, humorous'
    },
    'kafka': {
        'characteristics': 'surreal situations, bureaucratic nightmares, alienation, ambiguity',
        'voice': 'anxious, precise, dreamlike, oppressive'
    },
    'garcia_marquez': {
        'characteristics': 'magical realism, cyclical time, lush descriptions, myth blending',
        'voice': 'sensual, fantastical, political, Latin American'
    },
    'vonnegut': {
        'characteristics': 'simple syntax, dark humor, science fiction elements, fatalism',
        'voice': 'sardonic, humane, anti-war, accessible'
    },
    'wilde': {
        'characteristics': 'epigrams, paradoxes, aestheticism, wit',
        'voice': 'witty, decadent, paradoxical, sophisticated'
    },
    'joyce': {
        'characteristics': 'stream of consciousness, experimental, mythic parallels, language play',
        'voice': 'modernist, Irish, complex, revolutionary'
    },
    'morrison': {
        'characteristics': 'lyrical prose, nonlinear narrative, African American experience, memory',
        'voice': 'poetic, haunting, politically engaged, spiritual'
    },
    'baldwin': {
        'characteristics': 'passionate rhetoric, long sentences, biblical cadence, moral urgency',
        'voice': 'prophetic, eloquent, confrontational, compassionate'
    },
    'borges': {
        'characteristics': 'labyrinths, mirrors, infinite recursion, scholarly tone',
        'voice': 'erudite, metaphysical, playful, mysterious'
    },
    'calvino': {
        'characteristics': 'lightness, multiplicity, metafiction, combinatorial',
        'voice': 'playful, philosophical, fantastical, precise'
    },
    'leguin': {
        'characteristics': 'anthropological depth, gender exploration, ecological themes, clarity',
        'voice': 'wise, speculative, feminist, Taoist-influenced'
    },
    'ishiguro': {
        'characteristics': 'unreliable narrators, emotional restraint, memory, subtle reveals',
        'voice': 'understated, melancholic, precise, haunting'
    },
    'murakami': {
        'characteristics': 'surreal elements, parallel worlds, jazz references, alienation',
        'voice': 'dreamlike, contemporary, Japanese-Western fusion'
    },
    'pynchon': {
        'characteristics': 'paranoia, encyclopedic, conspiracy, entropy',
        'voice': 'complex, paranoid, satirical, postmodern'
    },
    'atwood': {
        'characteristics': 'dystopian elements, feminist themes, environmental concerns, sharp prose',
        'voice': 'incisive, speculative, Canadian, politically aware'
    },
    'butler': {
        'characteristics': 'Afrofuturism, power dynamics, biological themes, survival',
        'voice': 'visionary, grounded, African American, transformative'
    }
}

class DialogueGenerator:
    def __init__(self):
        self.client = ollama.Client()
        
    def create_philosopher_prompt(self, philosopher: str, author: str, topic: str, 
                                 history: List[Dict], is_response: bool = False,
                                 other_philosopher: str = None) -> str:
        """Create a prompt for a philosopher speaking through an author's voice"""
        
        phil_profile = PHILOSOPHER_PROFILES.get(philosopher, {})
        author_style = AUTHOR_STYLES.get(author, {})
        
        # Build the context
        prompt_parts = []
        
        # System instruction
        prompt_parts.append(f"""You are {philosopher.replace('_', ' ').title()}, the {phil_profile.get('era', '')} philosopher, 
but you must express your philosophical ideas through the literary voice and style of {author.replace('_', ' ').title()}.

Your philosophical position includes:
- Key concepts: {', '.join(phil_profile.get('key_concepts', []))}
- Core beliefs: {phil_profile.get('beliefs', '')}
- Philosophical style: {phil_profile.get('style', '')}

You must express these ideas using:
- Writing characteristics: {author_style.get('characteristics', '')}
- Literary voice: {author_style.get('voice', '')}

The discussion topic is: "{topic}"
""")

        # Add conversation history context
        if history:
            prompt_parts.append("\nPrevious exchange:")
            for entry in history[-4:]:  # Last 4 exchanges for context
                speaker_name = PHILOSOPHER_PROFILES.get(entry['philosopher'], {}).get('era', '')
                prompt_parts.append(f"\n{entry['philosopher'].title()} ({speaker_name}): {entry['content'][:500]}...")
        
        # Specific instruction for this turn
        if is_response and other_philosopher:
            other_profile = PHILOSOPHER_PROFILES.get(other_philosopher, {})
            prompt_parts.append(f"""
Now respond to {other_philosopher.replace('_', ' ').title()}'s points while:
1. Maintaining your philosophical position as {philosopher.replace('_', ' ').title()}
2. Using {author.replace('_', ' ').title()}'s literary style to make your ideas accessible
3. Engaging directly with their argument about {topic}
4. Making your classical philosophy relevant to modern readers

Write 2-3 paragraphs that blend philosophical depth with literary artistry.""")
        else:
            prompt_parts.append(f"""
Begin the dialogue about "{topic}" by:
1. Presenting your philosophical perspective as {philosopher.replace('_', ' ').title()}
2. Using {author.replace('_', ' ').title()}'s literary style to engage modern readers
3. Raising questions or observations that invite philosophical exploration
4. Making ancient wisdom feel immediate and relevant

Write 2-3 paragraphs that blend philosophical insight with literary craft.""")
        
        return '\n'.join(prompt_parts)
    
    async def generate_response(self, philosopher: str, author: str, model: str, 
                               topic: str, history: List[Dict], 
                               is_response: bool = False, other_philosopher: str = None) -> str:
        """Generate a response from a philosopher through an author's voice"""
        
        prompt = self.create_philosopher_prompt(
            philosopher, author, topic, history, is_response, other_philosopher
        )
        
        try:
            # Use Ollama to generate response
            response = self.client.generate(
                model=model,
                prompt=prompt,
                options={
                    'temperature': 0.8,
                    'top_p': 0.9,
                    'max_tokens': 500,
                    'stop': ['</dialogue>', '\n\n\n']
                }
            )
            
            # Extract and clean the response
            content = response['response'].strip()
            
            # Convert to HTML paragraphs
            paragraphs = content.split('\n\n')
            html_content = ''.join([f'<p>{p.strip()}</p>' for p in paragraphs if p.strip()])
            
            return html_content
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

generator = DialogueGenerator()

@app.route('/')
def index():
    """Serve the main HTML page"""
    with open('dialogue_app.html', 'r') as f:
        return f.read()

@app.route('/generate', methods=['POST'])
def generate_dialogue():
    """Generate dialogue exchanges using SSE"""
    
    def generate():
        try:
            data = request.json
            history = data.get('history', [])
            is_start = data.get('isStart', True)
            
            # Determine the number of exchanges (2 per round = 1 from each pairing)
            num_exchanges = 2
            
            for i in range(num_exchanges):
                # Alternate between pairings
                if (len(history) + i) % 2 == 0:
                    # Pairing 1 speaks
                    philosopher = data['philosopher1']
                    author = data['author1']
                    model = data['model1']
                    pairing = 1
                    other_philosopher = data['philosopher2'] if len(history) > 0 else None
                else:
                    # Pairing 2 speaks
                    philosopher = data['philosopher2']
                    author = data['author2'] 
                    model = data['model2']
                    pairing = 2
                    other_philosopher = data['philosopher1']
                
                # Generate response synchronously (we're in a generator)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    content = loop.run_until_complete(
                        generator.generate_response(
                            philosopher=philosopher,
                            author=author,
                            model=model,
                            topic=data['topic'],
                            history=history,
                            is_response=(len(history) > 0),
                            other_philosopher=other_philosopher
                        )
                    )
                finally:
                    loop.close()
                
                # Create message object
                message = {
                    'type': 'message',
                    'philosopher': philosopher,
                    'author': author,
                    'pairing': pairing,
                    'content': content,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Send via SSE
                yield f"data: {json.dumps(message)}\n\n"
                
                # Add to history for context
                history.append(message)
                
                # Small delay between speakers
                if i < num_exchanges - 1:
                    import time
                    time.sleep(1)
        
        except Exception as e:
            logger.error(f"Error in dialogue generation: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype="text/event-stream")

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Check if Ollama is running
        models = ollama.list()
        return json.dumps({
            'status': 'healthy',
            'ollama': 'connected',
            'models': [m['name'] for m in models['models']]
        })
    except Exception as e:
        return json.dumps({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║   Philosophical Dialogues Through Literary Voices              ║
    ║   Ready to run on http://localhost:5000                       ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║   Ensure Ollama is running with required models:              ║
    ║   - ollama pull llama3.2:3b                                   ║
    ║   - ollama pull mistral:7b                                    ║
    ║   - ollama pull deepseek-r1:7b                               ║
    ║   - ollama pull qwen2.5:7b                                    ║
    ║   - ollama pull gemma2:9b                                     ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
