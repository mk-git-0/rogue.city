"""
MajorMUD Quest System - Core Framework

Implements the complete MajorMUD reputation-based quest line system with:
- Three alignment-based quest lines (Good/Neutral/Evil)
- Progressive difficulty and experience rewards (150k to 175M exp)
- Multi-step quest progression with NPC interactions
- Class-specific rewards and bonuses
- Quest state tracking and global world events
"""

import json
import os
from enum import Enum
from typing import Dict, List, Optional, Any
from core.alignment_system import Alignment

class QuestStatus(Enum):
    """Quest status states"""
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    LOCKED = "locked"

class QuestStep(Enum):
    """Quest step progression"""
    NOT_STARTED = 0
    STEP_1 = 1
    STEP_2 = 2
    STEP_3 = 3
    STEP_4 = 4
    STEP_5 = 5
    COMPLETED = 6

class Quest:
    """Individual quest definition and state tracking"""
    
    def __init__(self, quest_id: str, data: Dict[str, Any]):
        self.quest_id = quest_id
        self.name = data['name']
        self.description = data['description']
        self.quest_giver = data['quest_giver']
        self.alignment_requirement = data['alignment_requirement']
        self.level_requirement = data['level_requirement']
        self.prerequisites = data.get('prerequisites', [])
        self.steps = data['steps']
        self.rewards = data['rewards']
        self.failure_consequences = data.get('failure_consequences', {})
        self.abandon_consequences = data.get('abandon_consequences', {})
        
        # Quest state
        self.status = QuestStatus.AVAILABLE
        self.current_step = QuestStep.NOT_STARTED
        self.step_progress = {}
        self.quest_flags = {}

    def can_accept(self, character) -> bool:
        """Check if character can accept this quest"""
        # Check alignment requirement
        if self.alignment_requirement != 'any':
            if character.alignment.name.lower() != self.alignment_requirement:
                return False
        
        # Check level requirement
        if character.level < self.level_requirement:
            return False
        
        # Check prerequisites
        for prereq in self.prerequisites:
            if not character.has_completed_quest(prereq):
                return False
        
        return True

    def get_current_objective(self) -> str:
        """Get current quest objective text"""
        if self.current_step == QuestStep.NOT_STARTED:
            return "Quest not started"
        elif self.current_step == QuestStep.COMPLETED:
            return "Quest completed"
        else:
            step_index = self.current_step.value - 1
            if step_index < len(self.steps):
                return self.steps[step_index]['objective']
        return "Unknown objective"

    def advance_step(self):
        """Advance to next quest step"""
        if self.current_step.value < QuestStep.COMPLETED.value:
            self.current_step = QuestStep(self.current_step.value + 1)
            if self.current_step == QuestStep.COMPLETED:
                self.status = QuestStatus.COMPLETED

class QuestSystem:
    """MajorMUD reputation-based quest line system"""
    
    # Alignment-based quest line configuration
    ALIGNMENT_QUEST_LINES = {
        'good': {
            'quest_giver': 'chancellor_annora',
            'faction': 'forces_of_light',
            'philosophy': 'Justice and protection of innocents',
            'location': 'Rogue City Temple District'
        },
        'neutral': {
            'quest_giver': 'hooded_traveller',
            'faction': 'seekers_of_balance',
            'philosophy': 'Maintaining cosmic equilibrium',
            'location': 'Neutral Observatory'
        },
        'evil': {
            'quest_giver': 'balthazar_dark_lord',
            'faction': 'forces_of_shadow',
            'philosophy': 'Power through any means necessary',
            'location': 'Dark Temple Undercity'
        }
    }
    
    def __init__(self, game_engine):
        self.game = game_engine
        self.quest_definitions = {}
        self.character_quests = {}  # character_id -> quest_data
        self.global_quest_flags = {}
        self.load_quest_data()
    
    def load_quest_data(self):
        """Load quest definitions from JSON files"""
        quest_file = os.path.join('data', 'quests', 'quest_definitions.json')
        if os.path.exists(quest_file):
            try:
                with open(quest_file, 'r') as f:
                    quest_data = json.load(f)
                
                for quest_id, data in quest_data.items():
                    self.quest_definitions[quest_id] = Quest(quest_id, data)
                    
                print(f"Loaded {len(self.quest_definitions)} quest definitions")
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading quest data: {e}")
                self._create_default_quest_data()
        else:
            print("Quest definitions not found, creating default data")
            self._create_default_quest_data()
    
    def _create_default_quest_data(self):
        """Create default quest definitions"""
        # This will be populated by quest data creation
        pass
    
    def get_character_quest_data(self, character_id: str) -> Dict:
        """Get quest data for specific character"""
        if character_id not in self.character_quests:
            self.character_quests[character_id] = {
                'active_quests': {},
                'completed_quests': [],
                'failed_quests': [],
                'quest_flags': {}
            }
        return self.character_quests[character_id]
    
    def get_available_quests(self, character) -> List[Quest]:
        """Get all quests available to character"""
        available_quests = []
        
        for quest in self.quest_definitions.values():
            if quest.can_accept(character):
                # Check if already active or completed
                char_data = self.get_character_quest_data(character.character_id)
                if (quest.quest_id not in char_data['active_quests'] and
                    quest.quest_id not in char_data['completed_quests']):
                    available_quests.append(quest)
        
        return available_quests
    
    def get_active_quests(self, character) -> List[Quest]:
        """Get character's active quests"""
        char_data = self.get_character_quest_data(character.character_id)
        active_quests = []
        
        for quest_id in char_data['active_quests']:
            if quest_id in self.quest_definitions:
                quest = self.quest_definitions[quest_id]
                # Restore quest state
                quest_state = char_data['active_quests'][quest_id]
                quest.status = QuestStatus(quest_state['status'])
                quest.current_step = QuestStep(quest_state['current_step'])
                quest.step_progress = quest_state.get('step_progress', {})
                quest.quest_flags = quest_state.get('quest_flags', {})
                active_quests.append(quest)
        
        return active_quests
    
    def get_completed_quests(self, character) -> List[str]:
        """Get character's completed quest IDs"""
        char_data = self.get_character_quest_data(character.character_id)
        return char_data['completed_quests']
    
    def accept_quest(self, character, quest_id: str) -> bool:
        """Accept a quest for character"""
        if quest_id not in self.quest_definitions:
            return False
        
        quest = self.quest_definitions[quest_id]
        if not quest.can_accept(character):
            return False
        
        char_data = self.get_character_quest_data(character.character_id)
        
        # Initialize quest state
        quest_state = {
            'status': QuestStatus.ACTIVE.value,
            'current_step': QuestStep.STEP_1.value,
            'step_progress': {},
            'quest_flags': {},
            'accepted_at': self.game.get_game_time() if self.game else "unknown"
        }
        
        char_data['active_quests'][quest_id] = quest_state
        quest.status = QuestStatus.ACTIVE
        quest.current_step = QuestStep.STEP_1
        
        return True
    
    def abandon_quest(self, character, quest_id: str) -> bool:
        """Abandon an active quest"""
        char_data = self.get_character_quest_data(character.character_id)
        
        if quest_id not in char_data['active_quests']:
            return False
        
        quest = self.quest_definitions.get(quest_id)
        if quest:
            # Apply abandon consequences
            self._apply_consequences(character, quest.abandon_consequences)
        
        # Remove from active quests
        del char_data['active_quests'][quest_id]
        
        # Add to failed quests
        char_data['failed_quests'].append({
            'quest_id': quest_id,
            'reason': 'abandoned',
            'abandoned_at': self.game.get_game_time() if self.game else "unknown"
        })
        
        return True
    
    def complete_quest(self, character, quest_id: str) -> bool:
        """Complete a quest and apply rewards"""
        char_data = self.get_character_quest_data(character.character_id)
        
        if quest_id not in char_data['active_quests']:
            return False
        
        quest = self.quest_definitions.get(quest_id)
        if not quest:
            return False
        
        # Apply quest rewards
        self._apply_rewards(character, quest.rewards)
        
        # Move from active to completed
        del char_data['active_quests'][quest_id]
        char_data['completed_quests'].append(quest_id)
        
        # Set global quest flag
        self.global_quest_flags[f"{quest_id}_completed"] = True
        
        return True
    
    def _apply_rewards(self, character, rewards: Dict[str, Any]):
        """Apply quest rewards to character"""
        # Universal rewards
        if 'experience' in rewards:
            character.gain_experience(rewards['experience'])
            if hasattr(self.game, 'ui_manager'):
                self.game.ui_manager.log_success(f"You gain {rewards['experience']:,} experience from the quest.")
        
        if 'gold' in rewards and hasattr(character, 'currency') and character.currency:
            character.currency.add_gold(rewards['gold'])
            if hasattr(self.game, 'ui_manager'):
                self.game.ui_manager.log_success(f"You receive {rewards['gold']} gold pieces.")
        
        if 'items' in rewards and rewards['items']:
            # Ensure item systems are initialized
            if not getattr(character, 'inventory_system', None):
                character.initialize_item_systems()
            from core.item_factory import ItemFactory
            item_factory = ItemFactory()
            for item_id in rewards['items']:
                item = item_factory.create_item(item_id)
                if item and character.inventory_system.add_item(item):
                    if hasattr(self.game, 'ui_manager'):
                        self.game.ui_manager.log_success(f"You receive: {item.name}")
                else:
                    if hasattr(self.game, 'ui_manager'):
                        self.game.ui_manager.log_error(f"Could not add reward item '{item_id}' to inventory.")
        
        # Class-specific rewards
        class_rewards = rewards.get('class_specific', {})
        character_class = getattr(character, 'character_class', '').lower()
        
        if character_class in class_rewards:
            class_bonus = class_rewards[character_class]
            
            # Apply stat/ability bonuses
            for key, bonus in class_bonus.items():
                if key == 'abilities' and isinstance(bonus, list):
                    if not hasattr(character, 'special_abilities'):
                        character.special_abilities = []
                    for ability in bonus:
                        if ability not in character.special_abilities:
                            character.special_abilities.append(ability)
                            if hasattr(self.game, 'ui_manager'):
                                self.game.ui_manager.log_success(f"Gained special ability: {ability}")
                elif hasattr(character, key) and isinstance(getattr(character, key), (int, float)):
                    current_value = getattr(character, key)
                    setattr(character, key, current_value + bonus)
                    if hasattr(self.game, 'ui_manager'):
                        self.game.ui_manager.log_success(f"Class bonus: +{bonus} {key}")
    
    def _apply_consequences(self, character, consequences: Dict[str, Any]):
        """Apply quest failure/abandon consequences"""
        # Apply faction reputation losses via AlignmentManager
        if 'reputation_loss' in consequences:
            for faction, loss in consequences['reputation_loss'].items():
                if hasattr(character, 'alignment_manager'):
                    new_rep = character.alignment_manager.modify_reputation(faction, -abs(loss))
                    if hasattr(self.game, 'ui_manager'):
                        self.game.ui_manager.log_error(
                            f"Reputation with {faction.replace('_',' ').title()} decreased by {abs(loss)} (now {new_rep})."
                        )
        
        # Apply alignment drift
        if 'alignment_shift' in consequences:
            shift = int(consequences['alignment_shift'])
            if hasattr(character, 'alignment_manager'):
                # Positive shift moves toward Evil, negative toward Good (example policy)
                # Map shift to drift actions; use granular increments
                drift_action = 'murder_for_gain' if shift > 0 else 'help_innocent'
                steps = min(10, abs(shift) // 5 or 1)
                for _ in range(steps):
                    character.alignment_manager.add_alignment_drift(drift_action)
                if hasattr(self.game, 'ui_manager'):
                    self.game.ui_manager.log_system(
                        f"Alignment shifted {'toward Evil' if shift > 0 else 'toward Good'} by {abs(shift)}."
                    )
    
    def get_quest_journal(self, character) -> Dict[str, Any]:
        """Get formatted quest journal for character"""
        active_quests = self.get_active_quests(character)
        completed_quests = self.get_completed_quests(character)
        available_quests = self.get_available_quests(character)
        
        char_data = self.get_character_quest_data(character.character_id)
        failed_quests = char_data['failed_quests']
        
        return {
            'active': active_quests,
            'completed': completed_quests,
            'available': available_quests,
            'failed': failed_quests
        }
    
    def get_alignment_quest_line(self, alignment: str) -> Dict[str, Any]:
        """Get quest line information for alignment"""
        return self.ALIGNMENT_QUEST_LINES.get(alignment.lower(), {})
    
    def save_quest_data(self, character):
        """Save character quest data"""
        # Quest data is maintained in character_quests dictionary
        # This would be called by the main save system
        pass
    
    def load_character_quest_data(self, character, quest_data: Dict):
        """Load character quest data from save file"""
        self.character_quests[character.character_id] = quest_data