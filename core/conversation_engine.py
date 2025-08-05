"""
Conversation Engine for Rogue City NPC interactions.

Manages branching dialogue trees, conversation states, and dynamic
responses based on character alignment, reputation, and world events.
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
import random


class ConversationState(Enum):
    """Current state of a conversation."""
    IDLE = "idle"
    GREETING = "greeting"
    TOPIC_MENU = "topic_menu"
    DIALOGUE_BRANCH = "dialogue_branch"
    WAITING_RESPONSE = "waiting_response"
    ENDED = "ended"


class ConversationTopic:
    """Represents a conversation topic with requirements and responses."""
    
    def __init__(self, topic_id: str, topic_data: Dict[str, Any]):
        self.topic_id = topic_id
        self.name = topic_data.get('name', topic_id)
        self.requirements = topic_data.get('requirements', {})
        self.responses = topic_data.get('responses', {})
        self.unlocks = topic_data.get('unlocks', [])  # Topics this unlocks
        self.reputation_change = topic_data.get('reputation_change', 0)
        self.alignment_required = topic_data.get('alignment_required', None)
        self.faction_required = topic_data.get('faction_required', None)
        self.flags_required = topic_data.get('flags_required', [])
        self.consumable = topic_data.get('consumable', False)  # Can only use once
    
    def is_available(self, character, npc, global_flags: Dict[str, bool] = None) -> bool:
        """Check if this topic is available to the character."""
        if global_flags is None:
            global_flags = {}
        
        # Check alignment requirement
        if self.alignment_required:
            if character.alignment_manager.get_alignment().name.lower() != self.alignment_required.lower():
                return False
        
        # Check faction reputation requirement
        if self.faction_required:
            faction_name, min_rep = self.faction_required
            current_rep = character.alignment_manager.get_reputation(faction_name)
            if current_rep < min_rep:
                return False
        
        # Check required flags
        for flag in self.flags_required:
            if not global_flags.get(flag, False):
                return False
        
        return True
    
    def get_response(self, character, npc, context: str = "default") -> str:
        """Get the appropriate response text for this topic."""
        # Try character alignment specific response first
        alignment_key = character.alignment_manager.get_alignment().name.lower()
        if alignment_key in self.responses:
            responses = self.responses[alignment_key]
        elif context in self.responses:
            responses = self.responses[context]
        elif "default" in self.responses:
            responses = self.responses["default"]
        else:
            return "I have nothing to say about that."
        
        # If responses is a list, pick randomly
        if isinstance(responses, list):
            return random.choice(responses)
        else:
            return responses


class ConversationTree:
    """Manages branching dialogue trees for NPCs."""
    
    def __init__(self, npc_id: str, tree_data: Dict[str, Any]):
        self.npc_id = npc_id
        self.name = tree_data.get('name', 'Unknown')
        self.greeting_responses = tree_data.get('greetings', {})
        self.topics = {}
        self.conversation_history = {}  # Track what was discussed with each character
        
        # Load topics
        for topic_id, topic_data in tree_data.get('topics', {}).items():
            self.topics[topic_id] = ConversationTopic(topic_id, topic_data)
    
    def get_greeting(self, character, npc) -> str:
        """Get appropriate greeting based on character alignment and reputation."""
        alignment = character.alignment_manager.get_alignment().name.lower()
        reaction = npc.get_reaction_to_character(character.alignment_manager)
        
        # Try reaction-specific greeting first
        reaction_key = reaction.name.lower()
        if reaction_key in self.greeting_responses:
            greetings = self.greeting_responses[reaction_key]
        elif alignment in self.greeting_responses:
            greetings = self.greeting_responses[alignment]
        elif "default" in self.greeting_responses:
            greetings = self.greeting_responses["default"]
        else:
            return f"{self.name} nods at you."
        
        if isinstance(greetings, list):
            return random.choice(greetings)
        else:
            return greetings
    
    def get_available_topics(self, character, npc, global_flags: Dict[str, bool] = None) -> List[ConversationTopic]:
        """Get list of topics available to this character."""
        available = []
        char_name = character.name
        
        for topic in self.topics.values():
            # Skip if consumable and already used
            if topic.consumable and char_name in self.conversation_history:
                if topic.topic_id in self.conversation_history[char_name]:
                    continue
            
            # Check if topic is available
            if topic.is_available(character, npc, global_flags):
                available.append(topic)
        
        return available
    
    def use_topic(self, character, topic_id: str) -> bool:
        """Mark a topic as used by this character."""
        char_name = character.name
        if char_name not in self.conversation_history:
            self.conversation_history[char_name] = []
        
        if topic_id not in self.conversation_history[char_name]:
            self.conversation_history[char_name].append(topic_id)
            return True
        return False


class ConversationEngine:
    """Core conversation system managing all NPC interactions."""
    
    def __init__(self, game_engine):
        self.game = game_engine
        self.conversation_trees: Dict[str, ConversationTree] = {}
        self.active_conversations: Dict[str, Dict[str, Any]] = {}  # character_name -> conversation_data
        self.global_flags: Dict[str, bool] = {}
        
        # Load conversation data
        self.load_conversation_data()
    
    def load_conversation_data(self):
        """Load conversation trees from data files."""
        try:
            # Load conversation trees
            with open('data/npcs/conversation_trees.json', 'r') as f:
                trees_data = json.load(f)
                for npc_id, tree_data in trees_data.items():
                    self.conversation_trees[npc_id] = ConversationTree(npc_id, tree_data)
            
            # Load global flags
            try:
                with open('data/npcs/global_flags.json', 'r') as f:
                    self.global_flags = json.load(f)
            except FileNotFoundError:
                self.global_flags = {}
                
        except FileNotFoundError:
            # Create default conversation trees if files don't exist
            self._create_default_conversations()
    
    def _create_default_conversations(self):
        """Create basic conversation trees for testing."""
        # Default guard conversation
        guard_data = {
            'name': 'Captain Aldric',
            'greetings': {
                'good': ["Greetings, citizen. How may the guard assist you?"],
                'neutral': ["State your business in our town."],
                'evil': ["I'll be watching you. What do you want?"],
                'friendly': ["Always good to see a friend of the city!"],
                'hostile': ["You're not welcome here."]
            },
            'topics': {
                'about_town': {
                    'name': 'Tell me about this town',
                    'responses': {
                        'default': "Rogue City stands as a beacon of civilization in these frontier lands."
                    }
                },
                'local_threats': {
                    'name': 'Are there any dangers I should know about?',
                    'alignment_required': 'good',
                    'responses': {
                        'good': "Evil stirs in the ancient ruins to the north. Be careful if you venture there."
                    }
                },
                'bounties': {
                    'name': 'Any work for a capable warrior?',
                    'responses': {
                        'default': "There might be. Depends on your character and reputation."
                    }
                }
            }
        }
        self.conversation_trees['town_guard_captain'] = ConversationTree('town_guard_captain', guard_data)
    
    def start_conversation(self, character, npc_id: str) -> Tuple[bool, str]:
        """Start a conversation with an NPC."""
        # Get the NPC
        npc = self.game.area_manager.get_current_area().npcs.get(npc_id)
        if not npc:
            return False, "There's no one here by that name."
        
        # Check if NPC will talk
        reaction = npc.get_reaction_to_character(character.alignment_manager)
        if reaction.value <= -3:
            return False, f"{npc.name} refuses to speak with you."
        
        # Get conversation tree
        tree = self.conversation_trees.get(npc_id)
        if not tree:
            return False, f"{npc.name} has nothing to say."
        
        # Start conversation
        self.active_conversations[character.name] = {
            'npc_id': npc_id,
            'npc': npc,
            'tree': tree,
            'state': ConversationState.GREETING,
            'current_topics': []
        }
        
        greeting = tree.get_greeting(character, npc)
        return True, f"{npc.name} says: \"{greeting}\""
    
    def handle_talk_command(self, character, target_name: str) -> str:
        """Handle the 'talk' command."""
        success, message = self.start_conversation(character, target_name)
        if not success:
            return message
        
        # Show available topics
        return self._show_conversation_menu(character)
    
    def handle_ask_command(self, character, target_name: str, topic: str) -> str:
        """Handle the 'ask' command."""
        # Find NPC
        npc = self._find_npc_by_name(target_name)
        if not npc:
            return f"There's no one here named {target_name}."
        
        npc_id = self._get_npc_id_by_name(target_name)
        tree = self.conversation_trees.get(npc_id)
        if not tree:
            return f"{npc[1].name} has nothing to say about {topic}."
        
        # Find matching topic
        matching_topic = None
        for topic_obj in tree.topics.values():
            if topic.lower() in topic_obj.name.lower():
                matching_topic = topic_obj
                break
        
        if not matching_topic:
            return f"{npc[1].name} says: \"I don't know anything about {topic}.\""
        
        # Check if topic is available
        if not matching_topic.is_available(character, npc[1], self.global_flags):
            return f"{npc[1].name} says: \"I can't discuss that with you.\""
        
        # Get response
        response = matching_topic.get_response(character, npc[1])
        
        # Apply reputation change if any
        if matching_topic.reputation_change != 0:
            character.alignment_manager.modify_reputation(npc[1].faction, matching_topic.reputation_change)
        
        # Mark as used if consumable
        if matching_topic.consumable:
            tree.use_topic(character, matching_topic.topic_id)
        
        return f"{npc[1].name} says: \"{response}\""
    
    def handle_greet_command(self, character, target_name: str) -> str:
        """Handle the 'greet' command."""
        npc = self._find_npc_by_name(target_name)
        if not npc:
            return f"There's no one here named {target_name}."
        
        npc_id, npc_obj = npc
        tree = self.conversation_trees.get(npc_id)
        if not tree:
            return f"You greet {npc_obj.name}."
        
        # Greeting provides small reputation boost
        character.alignment_manager.modify_reputation(npc_obj.faction, 1)
        npc_obj.modify_individual_reputation(character.name, 1)
        
        greeting = tree.get_greeting(character, npc_obj)
        return f"You formally greet {npc_obj.name}.\n{npc_obj.name} says: \"{greeting}\"\n[Reputation with {npc_obj.faction} increased by 1]"
    
    def handle_tell_command(self, character, target_name: str, message: str) -> str:
        """Handle the 'tell' command."""
        npc = self._find_npc_by_name(target_name)
        if not npc:
            return f"There's no one here named {target_name}."
        
        npc_id, npc_obj = npc
        
        # Basic response system - could be expanded
        responses = [
            f"{npc_obj.name} listens to what you have to say.",
            f"{npc_obj.name} nods thoughtfully.",
            f"{npc_obj.name} considers your words."
        ]
        
        return random.choice(responses)
    
    def handle_whisper_command(self, character, target_name: str, message: str) -> str:
        """Handle the 'whisper' command."""
        npc = self._find_npc_by_name(target_name)
        if not npc:
            return f"There's no one here named {target_name}."
        
        npc_id, npc_obj = npc
        
        # Whisper responses
        responses = [
            f"You whisper to {npc_obj.name}.\n{npc_obj.name} leans in to listen.",
            f"You whisper quietly to {npc_obj.name}.\n{npc_obj.name} nods discretely.",
            f"You speak in hushed tones to {npc_obj.name}."
        ]
        
        return random.choice(responses)
    
    def _show_conversation_menu(self, character) -> str:
        """Show available conversation topics."""
        if character.name not in self.active_conversations:
            return "You're not in a conversation."
        
        conv_data = self.active_conversations[character.name]
        tree = conv_data['tree']
        npc = conv_data['npc']
        
        available_topics = tree.get_available_topics(character, npc, self.global_flags)
        
        if not available_topics:
            return f"{npc.name} has nothing more to discuss with you."
        
        menu_text = f"\n[Conversation with {npc.name}]\n"
        menu_text += "Available topics:\n"
        
        for i, topic in enumerate(available_topics, 1):
            menu_text += f"{i}. {topic.name}\n"
        
        menu_text += f"{len(available_topics) + 1}. Farewell\n"
        menu_text += "\nChoose a topic number or type 'quit' to end conversation:"
        
        return menu_text
    
    def _find_npc_by_name(self, name: str) -> Optional[Tuple[str, Any]]:
        """Find an NPC by name in the current area."""
        # Use the NPC system from areas
        if hasattr(self.game, 'npc_system'):
            npc_system = self.game.npc_system
        else:
            # Import and create NPC system if not already available
            from areas.npc_system import NPCSystem
            self.game.npc_system = NPCSystem()
            npc_system = self.game.npc_system
        
        # Search through all NPCs (for now, until we have area-specific NPC placement)
        for npc_id, npc in npc_system.npcs.items():
            if name.lower() in npc.name.lower():
                return (npc_id, npc)
        return None
    
    def _get_npc_id_by_name(self, name: str) -> Optional[str]:
        """Get NPC ID by name."""
        npc_data = self._find_npc_by_name(name)
        return npc_data[0] if npc_data else None
    
    def end_conversation(self, character_name: str):
        """End an active conversation."""
        if character_name in self.active_conversations:
            del self.active_conversations[character_name]
    
    def set_global_flag(self, flag_name: str, value: bool):
        """Set a global conversation flag."""
        self.global_flags[flag_name] = value
    
    def get_global_flag(self, flag_name: str) -> bool:
        """Get a global conversation flag."""
        return self.global_flags.get(flag_name, False)
    
    def save_to_dict(self) -> Dict[str, Any]:
        """Save conversation engine state."""
        return {
            'global_flags': self.global_flags,
            'conversation_history': {
                tree_id: tree.conversation_history 
                for tree_id, tree in self.conversation_trees.items()
            }
        }
    
    def load_from_dict(self, data: Dict[str, Any]):
        """Load conversation engine state."""
        self.global_flags = data.get('global_flags', {})
        
        # Load conversation history
        history_data = data.get('conversation_history', {})
        for tree_id, history in history_data.items():
            if tree_id in self.conversation_trees:
                self.conversation_trees[tree_id].conversation_history = history