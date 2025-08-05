"""
Base NPC Class for Rogue City with conversation capabilities.

Extends the existing NPC system with structured personality types,
conversation abilities, and behavioral patterns.
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from abc import ABC, abstractmethod
from areas.npc_system import NPC, NPCType, NPCReaction
from core.alignment_system import Alignment


class NPCPersonality(Enum):
    """Personality types that affect NPC behavior and dialogue."""
    FRIENDLY = "friendly"          # Helpful, cheerful, approachable
    CAUTIOUS = "cautious"          # Careful, suspicious, reserved
    GRUFF = "gruff"                # Rough, blunt, no-nonsense
    SCHOLARLY = "scholarly"        # Intellectual, verbose, knowledgeable
    GREEDY = "greedy"              # Money-focused, opportunistic
    NOBLE = "noble"                # Dignified, proper, aristocratic
    MYSTERIOUS = "mysterious"      # Secretive, cryptic, enigmatic
    CHEERFUL = "cheerful"          # Upbeat, optimistic, energetic
    STERN = "stern"                # Serious, disciplined, authoritative
    ECCENTRIC = "eccentric"        # Quirky, unusual, unpredictable


class NPCMood(Enum):
    """Current mood states that can change based on interactions."""
    CONTENT = "content"            # Default peaceful state
    HAPPY = "happy"                # Pleased, satisfied
    ANNOYED = "annoyed"            # Mildly irritated
    ANGRY = "angry"                # Actively hostile
    EXCITED = "excited"            # Enthusiastic, eager
    WORRIED = "worried"            # Concerned, anxious
    SUSPICIOUS = "suspicious"      # Distrustful, watchful
    GRATEFUL = "grateful"          # Appreciative, thankful


class BaseNPC(NPC):
    """
    Enhanced NPC with conversation capabilities, personality, and dynamic behavior.
    
    Extends the basic NPC system with:
    - Structured personality traits
    - Dynamic mood states
    - Conversation memory
    - Behavioral patterns
    - Service offerings
    """
    
    def __init__(self, npc_id: str, name: str, npc_type: NPCType, alignment: Alignment,
                 faction: str, personality: NPCPersonality, description: str = "",
                 base_reaction: int = 0):
        """
        Initialize enhanced NPC with personality and conversation systems.
        
        Args:
            npc_id: Unique identifier for this NPC
            name: Display name
            npc_type: Type of NPC (merchant, guard, etc.)
            alignment: Moral alignment
            faction: Faction membership
            personality: Core personality type
            description: Physical/background description
            base_reaction: Base reaction modifier
        """
        super().__init__(name, npc_type, alignment, faction, base_reaction)
        
        self.npc_id = npc_id
        self.personality = personality
        self.description = description
        self.current_mood = NPCMood.CONTENT
        
        # Conversation system
        self.conversation_memory: Dict[str, List[str]] = {}  # character_name -> topics discussed
        self.last_interaction: Dict[str, float] = {}         # character_name -> timestamp
        self.conversation_cooldowns: Dict[str, float] = {}   # topic -> cooldown end time
        
        # Services and capabilities
        self.services_offered: List[str] = []
        self.special_knowledge: List[str] = []
        self.quest_hooks: List[str] = []
        
        # Behavioral parameters
        self.chattiness = 0.5        # How much the NPC likes to talk (0-1)
        self.memory_span = 10        # How many conversation topics to remember
        self.mood_volatility = 0.3   # How easily mood changes (0-1)
        
        # Initialize personality-specific traits
        self._initialize_personality_traits()
    
    def _initialize_personality_traits(self):
        """Set personality-specific behavioral parameters."""
        personality_configs = {
            NPCPersonality.FRIENDLY: {
                'chattiness': 0.8,
                'mood_volatility': 0.2,
                'memory_span': 15,
                'default_responses': self._get_friendly_responses()
            },
            NPCPersonality.CAUTIOUS: {
                'chattiness': 0.3,
                'mood_volatility': 0.6,
                'memory_span': 20,
                'default_responses': self._get_cautious_responses()
            },
            NPCPersonality.GRUFF: {
                'chattiness': 0.2,
                'mood_volatility': 0.4,
                'memory_span': 8,
                'default_responses': self._get_gruff_responses()
            },
            NPCPersonality.SCHOLARLY: {
                'chattiness': 0.9,
                'mood_volatility': 0.1,
                'memory_span': 25,
                'default_responses': self._get_scholarly_responses()
            },
            NPCPersonality.GREEDY: {
                'chattiness': 0.6,
                'mood_volatility': 0.5,
                'memory_span': 12,
                'default_responses': self._get_greedy_responses()
            },
            NPCPersonality.NOBLE: {
                'chattiness': 0.4,
                'mood_volatility': 0.2,
                'memory_span': 18,
                'default_responses': self._get_noble_responses()
            },
            NPCPersonality.MYSTERIOUS: {
                'chattiness': 0.3,
                'mood_volatility': 0.3,
                'memory_span': 30,
                'default_responses': self._get_mysterious_responses()
            },
            NPCPersonality.CHEERFUL: {
                'chattiness': 0.9,
                'mood_volatility': 0.1,
                'memory_span': 12,
                'default_responses': self._get_cheerful_responses()
            },
            NPCPersonality.STERN: {
                'chattiness': 0.2,
                'mood_volatility': 0.3,
                'memory_span': 15,
                'default_responses': self._get_stern_responses()
            },
            NPCPersonality.ECCENTRIC: {
                'chattiness': 0.7,
                'mood_volatility': 0.8,
                'memory_span': 8,
                'default_responses': self._get_eccentric_responses()
            }
        }
        
        config = personality_configs.get(self.personality, {})
        self.chattiness = config.get('chattiness', 0.5)
        self.mood_volatility = config.get('mood_volatility', 0.3)
        self.memory_span = config.get('memory_span', 10)
        self.personality_responses = config.get('default_responses', {})
    
    def _get_friendly_responses(self) -> Dict[str, List[str]]:
        """Get personality-specific responses for friendly NPCs."""
        return {
            'greeting': [
                "Hello there! What a pleasant surprise!",
                "Well hello! How are you doing today?",
                "Welcome, friend! How can I help you?"
            ],
            'farewell': [
                "Take care now! Come back anytime!",
                "Safe travels, my friend!",
                "It was lovely chatting with you!"
            ],
            'thanks': [
                "Oh, you're too kind!",
                "My pleasure entirely!",
                "Happy to help!"
            ]
        }
    
    def _get_cautious_responses(self) -> Dict[str, List[str]]:
        """Get personality-specific responses for cautious NPCs."""
        return {
            'greeting': [
                "Who goes there?",
                "State your business.",
                "I... I suppose you can approach."
            ],
            'farewell': [
                "Watch yourself out there.",
                "Be careful who you trust.",
                "Stay safe... if you can."
            ],
            'thanks': [
                "Just... just being careful.",
                "Don't mention it. To anyone.",
                "We all look out for ourselves."
            ]
        }
    
    def _get_gruff_responses(self) -> Dict[str, List[str]]:
        """Get personality-specific responses for gruff NPCs."""
        return {
            'greeting': [
                "What do you want?",
                "Make it quick.",
                "Hmph. You again."
            ],
            'farewell': [
                "About time.",
                "Good riddance.",
                "Don't let the door hit you."
            ],
            'thanks': [
                "Whatever.",
                "Just doing my job.",
                "Don't make a big deal of it."
            ]
        }
    
    def _get_scholarly_responses(self) -> Dict[str, List[str]]:
        """Get personality-specific responses for scholarly NPCs."""
        return {
            'greeting': [
                "Ah, a visitor! How intellectually stimulating!",
                "Welcome, seeker of knowledge!",
                "Greetings! I do hope you've come to learn something new."
            ],
            'farewell': [
                "May your journey be filled with discovery!",
                "Go forth and expand your understanding!",
                "Knowledge shared is knowledge multiplied!"
            ],
            'thanks': [
                "The pursuit of knowledge is its own reward!",
                "Education is the greatest gift one can give!",
                "I am merely a humble vessel of learning!"
            ]
        }
    
    def _get_greedy_responses(self) -> Dict[str, List[str]]:
        """Get personality-specific responses for greedy NPCs."""
        return {
            'greeting': [
                "Ah, a potential customer!",
                "Welcome! Got coin to spend?",
                "What can I sell you today?"
            ],
            'farewell': [
                "Come back when you have more gold!",
                "Don't forget to tell your rich friends about me!",
                "Money talks, everything else walks!"
            ],
            'thanks': [
                "Pleasure doing business!",
                "Your gold is as good as anyone's!",
                "I do so love satisfied customers!"
            ]
        }
    
    def _get_noble_responses(self) -> Dict[str, List[str]]:
        """Get personality-specific responses for noble NPCs."""
        return {
            'greeting': [
                "Good day to you, citizen.",
                "I acknowledge your presence.",
                "Approach with proper decorum, if you please."
            ],
            'farewell': [
                "You are dismissed.",
                "May your endeavors prove fruitful.",
                "Conduct yourself with honor."
            ],
            'thanks': [
                "Your gratitude is noted.",
                "One does what one must.",
                "Noblesse oblige, as they say."
            ]
        }
    
    def _get_mysterious_responses(self) -> Dict[str, List[str]]:
        """Get personality-specific responses for mysterious NPCs."""
        return {
            'greeting': [
                "We meet again... or do we?",
                "The threads of fate weave strangely.",
                "You have arrived precisely when expected."
            ],
            'farewell': [
                "Until the stars align once more...",
                "Remember: not all truths are meant to be spoken.",
                "The path ahead is shrouded in shadow."
            ],
            'thanks': [
                "Gratitude is a curious thing.",
                "The debt flows both ways, traveler.",
                "What is given freely has the most value."
            ]
        }
    
    def _get_cheerful_responses(self) -> Dict[str, List[str]]:
        """Get personality-specific responses for cheerful NPCs."""
        return {
            'greeting': [
                "Oh wonderful! A new friend!",
                "What a marvelous day this is turning out to be!",
                "Hello hello! Isn't life just fantastic?"
            ],
            'farewell': [
                "Oh, what a delightful visit!",
                "Have the most wonderful day!",
                "Smile! The world is beautiful!"
            ],
            'thanks': [
                "Oh my goodness, you're so sweet!",
                "This just makes my whole day!",
                "You're absolutely wonderful!"
            ]
        }
    
    def _get_stern_responses(self) -> Dict[str, List[str]]:
        """Get personality-specific responses for stern NPCs."""
        return {
            'greeting': [
                "State your business efficiently.",
                "I trust you have good reason to disturb me.",
                "Speak plainly and quickly."
            ],
            'farewell': [
                "See that you conduct yourself properly.",
                "I expect better behavior in the future.",
                "Discipline yourself, or others will."
            ],
            'thanks': [
                "Gratitude is unnecessary. Do better.",
                "Actions matter more than words.",
                "Competence is its own reward."
            ]
        }
    
    def _get_eccentric_responses(self) -> Dict[str, List[str]]:
        """Get personality-specific responses for eccentric NPCs."""
        return {
            'greeting': [
                "Oh my! Did you see that purple butterfly? No? Just me then!",
                "Fascinating! Your aura is particularly... Tuesday-ish today!",
                "Welcome, welcome! The teapots told me you were coming!"
            ],
            'farewell': [
                "Goodbye! Or should I say... hello to your future past?",
                "May the rubber ducks guide your journey!",
                "Don't forget to feed your shadow on the way out!"
            ],
            'thanks': [
                "Oh splendid! My collection of gratitudes grows!",
                "You're most welcome! The clockwork mice approve!",
                "Wonderful! That's exactly what my soup spoon predicted!"
            ]
        }
    
    def get_personality_response(self, context: str) -> Optional[str]:
        """Get a personality-appropriate response for a given context."""
        import random
        responses = self.personality_responses.get(context, [])
        return random.choice(responses) if responses else None
    
    def update_conversation_memory(self, character_name: str, topic: str):
        """Update conversation memory with a new topic."""
        if character_name not in self.conversation_memory:
            self.conversation_memory[character_name] = []
        
        memory = self.conversation_memory[character_name]
        if topic not in memory:
            memory.append(topic)
            
            # Limit memory span
            if len(memory) > self.memory_span:
                memory.pop(0)
    
    def has_discussed_topic(self, character_name: str, topic: str) -> bool:
        """Check if a topic has been discussed with a character."""
        return topic in self.conversation_memory.get(character_name, [])
    
    def get_mood_modifier(self) -> int:
        """Get reaction modifier based on current mood."""
        mood_modifiers = {
            NPCMood.CONTENT: 0,
            NPCMood.HAPPY: 2,
            NPCMood.ANNOYED: -1,
            NPCMood.ANGRY: -3,
            NPCMood.EXCITED: 1,
            NPCMood.WORRIED: -1,
            NPCMood.SUSPICIOUS: -2,
            NPCMood.GRATEFUL: 3
        }
        return mood_modifiers.get(self.current_mood, 0)
    
    def change_mood(self, new_mood: NPCMood, intensity: float = 1.0):
        """Change NPC mood with volatility consideration."""
        if intensity * self.mood_volatility > 0.5:
            self.current_mood = new_mood
    
    def get_enhanced_reaction(self, character_alignment_manager) -> NPCReaction:
        """Get reaction including mood and personality modifiers."""
        base_reaction = super().get_reaction_to_character(character_alignment_manager)
        
        # Apply mood modifier
        mood_mod = self.get_mood_modifier()
        total_reaction = base_reaction.value + mood_mod
        
        # Apply personality modifiers for specific alignments
        personality_alignment_mods = {
            NPCPersonality.FRIENDLY: {Alignment.GOOD: 1, Alignment.NEUTRAL: 0, Alignment.EVIL: -1},
            NPCPersonality.CAUTIOUS: {Alignment.GOOD: 1, Alignment.NEUTRAL: -1, Alignment.EVIL: -2},
            NPCPersonality.STERN: {Alignment.GOOD: 1, Alignment.NEUTRAL: 0, Alignment.EVIL: -2},
            NPCPersonality.NOBLE: {Alignment.GOOD: 2, Alignment.NEUTRAL: 0, Alignment.EVIL: -3}
        }
        
        char_alignment = character_alignment_manager.get_alignment()
        if self.personality in personality_alignment_mods:
            personality_mod = personality_alignment_mods[self.personality].get(char_alignment, 0)
            total_reaction += personality_mod
        
        # Clamp to valid reaction range
        total_reaction = max(-3, min(3, total_reaction))
        return NPCReaction(total_reaction)
    
    @abstractmethod
    def get_available_services(self) -> List[str]:
        """Get list of services this NPC can provide."""
        pass
    
    @abstractmethod
    def can_provide_service(self, service: str, character) -> Tuple[bool, str]:
        """Check if NPC can provide a specific service to character."""
        pass
    
    def get_conversation_topics(self, character) -> List[str]:
        """Get available conversation topics for this character."""
        # Base topics available to all NPCs
        base_topics = ['greeting', 'about_area', 'goodbye']
        
        # Add service-related topics
        service_topics = [f"about_{service}" for service in self.services_offered]
        
        # Add knowledge topics
        knowledge_topics = [f"ask_about_{knowledge}" for knowledge in self.special_knowledge]
        
        return base_topics + service_topics + knowledge_topics
    
    def save_to_dict(self) -> Dict[str, Any]:
        """Save NPC state to dictionary."""
        base_data = super().save_to_dict()
        base_data.update({
            'npc_id': self.npc_id,
            'personality': self.personality.value,
            'description': self.description,
            'current_mood': self.current_mood.value,
            'conversation_memory': self.conversation_memory,
            'last_interaction': self.last_interaction,
            'services_offered': self.services_offered,
            'special_knowledge': self.special_knowledge,
            'quest_hooks': self.quest_hooks,
            'chattiness': self.chattiness,
            'mood_volatility': self.mood_volatility
        })
        return base_data
    
    def load_from_dict(self, data: Dict[str, Any]):
        """Load NPC state from dictionary."""
        self.npc_id = data.get('npc_id', self.npc_id)
        self.personality = NPCPersonality(data.get('personality', self.personality.value))
        self.description = data.get('description', self.description)
        self.current_mood = NPCMood(data.get('current_mood', NPCMood.CONTENT.value))
        self.conversation_memory = data.get('conversation_memory', {})
        self.last_interaction = data.get('last_interaction', {})
        self.services_offered = data.get('services_offered', [])
        self.special_knowledge = data.get('special_knowledge', [])
        self.quest_hooks = data.get('quest_hooks', [])
        self.chattiness = data.get('chattiness', 0.5)
        self.mood_volatility = data.get('mood_volatility', 0.3)
        
        # Reinitialize personality traits after loading
        self._initialize_personality_traits()