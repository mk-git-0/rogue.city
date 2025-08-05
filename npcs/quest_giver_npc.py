"""
Quest Giver NPCs - Alignment-based quest distribution

Implements the three primary quest givers for MajorMUD alignment-based quest lines:
- Chancellor Annora (Good alignment quests)
- The Hooded Traveller (Neutral alignment quests)  
- Balthazar the Dark Lord (Evil alignment quests)
"""

import json
import os
from typing import Dict, List, Optional, Any
from areas.npc_system import NPC, NPCType
from core.alignment_system import Alignment

class QuestGiverNPC(NPC):
    """Base class for NPCs who give quests"""
    
    def __init__(self, npc_id: str, data: Dict[str, Any]):
        # Convert alignment string to Alignment enum
        alignment_str = data.get('alignment', 'neutral')
        alignment_map = {
            'good': Alignment.GOOD,
            'neutral': Alignment.NEUTRAL,
            'evil': Alignment.EVIL
        }
        alignment = alignment_map.get(alignment_str, Alignment.NEUTRAL)
        
        # Initialize base NPC
        super().__init__(
            name=data.get('name', npc_id),
            npc_type=NPCType.CITIZEN,  # Default to citizen, could add QUEST_GIVER type
            alignment=alignment,
            faction=data.get('faction', 'neutral'),
            base_reaction=0
        )
        
        # Store the original npc_id and data
        self.npc_id = npc_id
        self.description = data.get('description', '')
        
        # Quest giver specific properties
        self.alignment_requirement = data.get('alignment', 'neutral')
        self.faction = data.get('faction', 'neutral')
        self.quest_line = data.get('quest_line', [])
        self.available_quests = data.get('available_quests', [])
        self.personality = data.get('personality', 'friendly')
        self.quest_dialogue = data.get('quest_dialogue', {})
        
        # Quest state tracking
        self.active_conversations = {}  # character_id -> conversation_state
    
    def can_offer_quests_to(self, character) -> bool:
        """Check if this NPC can offer quests to the character"""
        # Check alignment compatibility
        if self.alignment_requirement != 'any':
            char_alignment = character.alignment.name.lower()
            if char_alignment != self.alignment_requirement:
                return False
        
        return True
    
    def get_available_quests_for(self, character) -> List[str]:
        """Get quest IDs available to this character"""
        if not self.can_offer_quests_to(character):
            return []
        
        # Initialize quest system if needed
        game = getattr(character, 'game_engine', None)
        if not game or not hasattr(game, 'quest_system'):
            return []
        
        quest_system = game.quest_system
        
        # Initialize character quest manager if needed
        if not hasattr(character, 'quest_manager'):
            from core.quest_manager import CharacterQuestManager
            character.quest_manager = CharacterQuestManager(character, quest_system)
        
        available_quests = []
        for quest_id in self.available_quests:
            if quest_id in quest_system.quest_definitions:
                quest = quest_system.quest_definitions[quest_id]
                if character.quest_manager.can_accept_quest(quest):
                    available_quests.append(quest_id)
        
        return available_quests
    
    def get_dialogue_response(self, character, dialogue_type: str) -> str:
        """Get appropriate dialogue response based on character and context"""
        # Check alignment compatibility first
        if not self.can_offer_quests_to(character):
            return self.quest_dialogue.get('alignment_mismatch', 
                "I sense we walk different paths, traveler.")
        
        # Check if character has available quests
        available_quests = self.get_available_quests_for(character)
        
        if dialogue_type == 'greeting':
            return self.quest_dialogue.get('greeting', f"Greetings, {character.name}.")
        
        elif dialogue_type == 'quest_inquiry':
            if available_quests:
                return self.quest_dialogue.get('quest_available', 
                    "I have tasks that need completing.")
            else:
                # Check if character has active quests from this NPC
                if hasattr(character, 'quest_manager'):
                    active_quests = character.quest_manager.get_journal()['active']
                    npc_quests = [q for q in active_quests if q.get('quest_giver') == self.npc_id]
                    if npc_quests:
                        return self.quest_dialogue.get('quest_in_progress',
                            "How goes your current mission?")
                
                return self.quest_dialogue.get('no_quests_available',
                    "I have no tasks for you at this time.")
        
        elif dialogue_type == 'quest_completed':
            return self.quest_dialogue.get('quest_completed',
                "Well done! Your efforts are appreciated.")
        
        elif dialogue_type == 'insufficient_level':
            return self.quest_dialogue.get('insufficient_level',
                "You need more experience before I can entrust you with this task.")
        
        return self.quest_dialogue.get('default',
            f"{self.name} looks at you thoughtfully.")
    
    def handle_ask_missions(self, character) -> str:
        """Handle 'ask <npc> missions' command"""
        available_quests = self.get_available_quests_for(character)
        
        if not self.can_offer_quests_to(character):
            return self.get_dialogue_response(character, 'alignment_mismatch')
        
        if not available_quests:
            return self.get_dialogue_response(character, 'quest_inquiry')
        
        # Get the first available quest for detailed presentation
        game = getattr(character, 'game_engine', None)
        if not game or not hasattr(game, 'quest_system'):
            return "Quest system not available."
        
        quest_system = game.quest_system
        quest_id = available_quests[0]
        quest = quest_system.quest_definitions.get(quest_id)
        
        if not quest:
            return "No quest information available."
        
        # Format quest offer
        response = []
        response.append(self.get_dialogue_response(character, 'quest_inquiry'))
        response.append("")
        response.append(f"[QUEST AVAILABLE: {quest.name}]")
        response.append(f"Objective: {quest.description}")
        
        exp_reward = quest.rewards.get('experience', 0)
        gold_reward = quest.rewards.get('gold', 0)
        response.append(f"Reward: {exp_reward:,} experience" + 
                       (f" + {gold_reward} gold" if gold_reward > 0 else "") + 
                       " + class bonuses")
        response.append(f"Requirements: {quest.alignment_requirement.title()} alignment, Level {quest.level_requirement}+")
        response.append("")
        response.append("Accept this quest? Use 'accept <quest name>' to accept.")
        
        return '\n'.join(response)

class ChancellorAnnora(QuestGiverNPC):
    """Chancellor Annora - Good alignment quest giver"""
    
    def __init__(self):
        data = {
            'name': 'Chancellor Annora',
            'description': ("A noble woman in gleaming white robes, bearing the holy symbol of light. "
                          "Her eyes shine with righteous purpose and unwavering determination to protect the innocent."),
            'location': 'rogue_city_temple_district',
            'alignment': 'good',
            'faction': 'forces_of_light',
            'personality': 'lawful_good_noble',
            'available_quests': ['good_quest_1', 'good_quest_2', 'good_quest_3'],
            'quest_dialogue': {
                'greeting': ("Greetings, traveler. I sense great potential within you. "
                           "Perhaps you are the champion we have been waiting for."),
                'quest_available': ("I have a mission that requires someone of your caliber. "
                                  "The innocent cry out for protection, and evil must not be allowed to triumph."),
                'quest_in_progress': "How goes your mission? The forces of light depend on your success.",
                'quest_completed': ("Excellent work, champion! Your deeds shall be remembered "
                                  "in the annals of righteousness."),
                'alignment_mismatch': ("I sense darkness in your heart. Return when you have "
                                     "found the path of light."),
                'insufficient_level': ("You show promise, but this task requires greater experience. "
                                     "Return when you have proven yourself further."),
                'default': "Chancellor Annora regards you with kind but appraising eyes."
            }
        }
        super().__init__('chancellor_annora', data)

class HoodedTraveller(QuestGiverNPC):
    """The Hooded Traveller - Neutral alignment quest giver"""
    
    def __init__(self):
        data = {
            'name': 'The Hooded Traveller',
            'description': ("A mysterious figure wrapped in grey robes, their face hidden in shadow. "
                          "They speak in riddles about cosmic balance and the eternal dance between order and chaos."),
            'location': 'neutral_observatory',
            'alignment': 'neutral',
            'faction': 'seekers_of_balance',
            'personality': 'mysterious_balanced',
            'available_quests': ['neutral_quest_1', 'neutral_quest_2'],
            'quest_dialogue': {
                'greeting': ("Balance is the key to all things, wanderer. "
                           "In you, I sense the potential to walk the middle path."),
                'quest_available': ("The scales tip too far in one direction. "
                                  "Will you help restore equilibrium to this troubled realm?"),
                'quest_in_progress': "The wheel turns, the balance shifts. How does your journey progress?",
                'quest_completed': ("Well done. The cosmic harmony is preserved, "
                                  "and the wheel continues its eternal turn."),
                'alignment_mismatch': ("You have strayed too far from the path of balance. "
                                     "Find the center before we speak again."),
                'insufficient_level': ("Wisdom comes with experience. Return when you have "
                                     "walked further along life's path."),
                'default': "The Hooded Traveller nods knowingly, as if seeing beyond the present moment."
            }
        }
        super().__init__('hooded_traveller', data)

class BalthazarDarkLord(QuestGiverNPC):
    """Balthazar the Dark Lord - Evil alignment quest giver"""
    
    def __init__(self):
        data = {
            'name': 'Balthazar the Dark Lord',
            'description': ("A commanding figure in black robes adorned with silver skulls. "
                          "His eyes burn with malevolent intelligence, and power radiates from his very presence. "
                          "He offers strength to those willing to embrace the darkness."),
            'location': 'dark_temple_undercity',
            'alignment': 'evil',
            'faction': 'forces_of_shadow',
            'personality': 'charismatic_evil',
            'available_quests': ['evil_quest_1', 'evil_quest_2'],
            'quest_dialogue': {
                'greeting': ("Ah, another soul seeking power. Good. The weak deserve their fate, "
                           "but you... you show promise."),
                'quest_available': ("Power is not given, it is taken. Are you prepared to do "
                                  "what must be done to claim your destiny?"),
                'quest_in_progress': ("The dark path is not for the squeamish. "
                                    "Show me your commitment to true power."),
                'quest_completed': ("Excellent. You understand that strength comes to those who seize it. "
                                  "Your dark education continues."),
                'alignment_mismatch': ("Your heart still clings to pathetic notions of 'good' and 'mercy'. "
                                     "Return when you have embraced your true nature."),
                'insufficient_level': ("Power respects only power. Grow stronger, "
                                     "then return to claim what is yours."),
                'default': "Balthazar's piercing gaze seems to weigh your soul and find it... interesting."
            }
        }
        super().__init__('balthazar_dark_lord', data)

# Quest giver factory
def create_quest_giver(npc_id: str) -> Optional[QuestGiverNPC]:
    """Create a quest giver NPC by ID"""
    quest_givers = {
        'chancellor_annora': ChancellorAnnora,
        'hooded_traveller': HoodedTraveller,
        'balthazar_dark_lord': BalthazarDarkLord
    }
    
    if npc_id in quest_givers:
        return quest_givers[npc_id]()
    
    return None

# Load quest giver data for integration with existing NPC system
def load_quest_giver_data() -> Dict[str, Dict[str, Any]]:
    """Load quest giver data for NPC system integration"""
    quest_givers_data = {}
    
    # Create instances to get their data
    annora = ChancellorAnnora()
    traveller = HoodedTraveller()
    balthazar = BalthazarDarkLord()
    
    quest_givers_data['chancellor_annora'] = {
        'name': annora.name,
        'description': annora.description,
        'location': annora.location,
        'alignment': annora.alignment_requirement,
        'faction': annora.faction,
        'npc_type': 'quest_giver',
        'available_quests': annora.available_quests,
        'quest_dialogue': annora.quest_dialogue
    }
    
    quest_givers_data['hooded_traveller'] = {
        'name': traveller.name,
        'description': traveller.description,
        'location': traveller.location,
        'alignment': traveller.alignment_requirement,
        'faction': traveller.faction,
        'npc_type': 'quest_giver',
        'available_quests': traveller.available_quests,
        'quest_dialogue': traveller.quest_dialogue
    }
    
    quest_givers_data['balthazar_dark_lord'] = {
        'name': balthazar.name,
        'description': balthazar.description,
        'location': balthazar.location,
        'alignment': balthazar.alignment_requirement,
        'faction': balthazar.faction,
        'npc_type': 'quest_giver',
        'available_quests': balthazar.available_quests,
        'quest_dialogue': balthazar.quest_dialogue
    }
    
    return quest_givers_data