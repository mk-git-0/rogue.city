"""
Quest Manager - Individual Character Quest Tracking

Handles individual character quest progression, state management,
and integration with the character save system.
"""

import json
from typing import Dict, List, Optional, Any
from core.quest_system import Quest, QuestStatus, QuestStep

class CharacterQuestManager:
    """Manages quest state for individual characters"""
    
    def __init__(self, character, quest_system):
        self.character = character
        self.quest_system = quest_system
        self.character_id = getattr(character, 'character_id', character.name)
        
        # Quest tracking data
        self.active_quests = {}  # quest_id -> quest_state
        self.completed_quests = []  # list of completed quest_ids
        self.failed_quests = []  # list of failed quest data
        self.quest_flags = {}  # custom quest flags
        self.reputation_changes = {}  # faction -> reputation_change
        
        # Load character quest data
        self.load_quest_data()
    
    def load_quest_data(self):
        """Load quest data from character save or quest system"""
        quest_data = self.quest_system.get_character_quest_data(self.character_id)
        
        self.active_quests = quest_data.get('active_quests', {})
        self.completed_quests = quest_data.get('completed_quests', [])
        self.failed_quests = quest_data.get('failed_quests', [])
        self.quest_flags = quest_data.get('quest_flags', {})
        self.reputation_changes = quest_data.get('reputation_changes', {})
    
    def save_quest_data(self) -> Dict[str, Any]:
        """Save quest data for character save file"""
        return {
            'active_quests': self.active_quests,
            'completed_quests': self.completed_quests,
            'failed_quests': self.failed_quests,
            'quest_flags': self.quest_flags,
            'reputation_changes': self.reputation_changes
        }
    
    def get_available_quests(self) -> List[Quest]:
        """Get quests available to this character"""
        available_quests = []
        
        for quest in self.quest_system.quest_definitions.values():
            if self.can_accept_quest(quest):
                available_quests.append(quest)
        
        return available_quests
    
    def can_accept_quest(self, quest: Quest) -> bool:
        """Check if character can accept a specific quest"""
        # Already active or completed
        if (quest.quest_id in self.active_quests or 
            quest.quest_id in self.completed_quests):
            return False
        
        # Check alignment requirement
        if quest.alignment_requirement != 'any':
            char_alignment = self.character.alignment.name.lower()
            if char_alignment != quest.alignment_requirement:
                return False
        
        # Check level requirement
        if self.character.level < quest.level_requirement:
            return False
        
        # Check prerequisites
        for prereq in quest.prerequisites:
            if prereq not in self.completed_quests:
                return False
        
        return True
    
    def accept_quest(self, quest_id: str) -> bool:
        """Accept a quest"""
        if quest_id not in self.quest_system.quest_definitions:
            return False
        
        quest = self.quest_system.quest_definitions[quest_id]
        if not self.can_accept_quest(quest):
            return False
        
        # Initialize quest state
        quest_state = {
            'status': QuestStatus.ACTIVE.value,
            'current_step': QuestStep.STEP_1.value,
            'step_progress': {},
            'quest_flags': {},
            'accepted_at': self.quest_system.game.get_game_time() if self.quest_system.game else "unknown",
            'completion_data': {}
        }
        
        self.active_quests[quest_id] = quest_state
        
        # Update quest system
        self.quest_system.character_quests[self.character_id] = {
            'active_quests': self.active_quests,
            'completed_quests': self.completed_quests,
            'failed_quests': self.failed_quests,
            'quest_flags': self.quest_flags
        }
        
        return True
    
    def abandon_quest(self, quest_id: str) -> bool:
        """Abandon an active quest"""
        if quest_id not in self.active_quests:
            return False
        
        quest = self.quest_system.quest_definitions.get(quest_id)
        if quest:
            # Apply abandon consequences
            self._apply_consequences(quest.abandon_consequences, "abandoned")
        
        # Move to failed quests
        quest_state = self.active_quests[quest_id]
        self.failed_quests.append({
            'quest_id': quest_id,
            'reason': 'abandoned',
            'abandoned_at': self.quest_system.game.get_game_time() if self.quest_system.game else "unknown",
            'progress': quest_state.get('current_step', 1)
        })
        
        # Remove from active
        del self.active_quests[quest_id]
        
        return True
    
    def advance_quest_step(self, quest_id: str) -> bool:
        """Advance a quest to the next step"""
        if quest_id not in self.active_quests:
            return False
        
        quest_state = self.active_quests[quest_id]
        current_step = quest_state['current_step']
        
        quest = self.quest_system.quest_definitions.get(quest_id)
        if not quest:
            return False
        
        # Check if can advance
        if current_step >= len(quest.steps):
            # Quest is ready to complete
            return self.complete_quest(quest_id)
        
        # Advance step
        quest_state['current_step'] = current_step + 1
        
        return True
    
    def complete_quest(self, quest_id: str) -> bool:
        """Complete a quest and apply rewards"""
        if quest_id not in self.active_quests:
            return False
        
        quest = self.quest_system.quest_definitions.get(quest_id)
        if not quest:
            return False
        
        # Apply rewards
        self._apply_rewards(quest.rewards)
        
        # Move from active to completed
        del self.active_quests[quest_id]
        self.completed_quests.append(quest_id)
        
        # Set global quest flag
        self.quest_system.global_quest_flags[f"{quest_id}_completed"] = True
        
        return True
    
    def fail_quest(self, quest_id: str, reason: str = "failed") -> bool:
        """Fail a quest"""
        if quest_id not in self.active_quests:
            return False
        
        quest = self.quest_system.quest_definitions.get(quest_id)
        if quest:
            # Apply failure consequences
            self._apply_consequences(quest.failure_consequences, reason)
        
        # Move to failed quests
        quest_state = self.active_quests[quest_id]
        self.failed_quests.append({
            'quest_id': quest_id,
            'reason': reason,
            'failed_at': self.quest_system.game.get_game_time() if self.quest_system.game else "unknown",
            'progress': quest_state.get('current_step', 1)
        })
        
        # Remove from active
        del self.active_quests[quest_id]
        
        return True
    
    def _apply_rewards(self, rewards: Dict[str, Any]):
        """Apply quest rewards to character using reward calculator"""
        from core.quest_rewards import quest_reward_calculator
        
        # Find the quest that was completed
        quest_id = None
        quest_data = None
        
        # Get the quest ID from the calling context (this is a simplified approach)
        # In a full implementation, this would be passed as a parameter
        for qid, quest in self.quest_system.quest_definitions.items():
            if quest.rewards == rewards:
                quest_id = qid
                quest_data = {'rewards': rewards}
                break
        
        if quest_id and quest_data:
            # Use the reward calculator for comprehensive reward application
            applied_rewards = quest_reward_calculator.calculate_and_apply_all_rewards(
                self.character, quest_id, quest_data
            )
            
            # Print reward messages
            for reward_msg in applied_rewards:
                print(reward_msg)
        else:
            # Fallback to original method
            self._apply_rewards_fallback(rewards)
    
    def _apply_rewards_fallback(self, rewards: Dict[str, Any]):
        """Fallback reward application method"""
        # Universal rewards
        if 'experience' in rewards:
            self.character.gain_experience(rewards['experience'])
        
        if 'gold' in rewards:
            if hasattr(self.character, 'currency'):
                self.character.currency.add_gold(rewards['gold'])
        
        if 'items' in rewards:
            for item_id in rewards['items']:
                # TODO: Add item to character inventory
                print(f"Received item: {item_id}")
        
        # Class-specific rewards
        class_rewards = rewards.get('class_specific', {})
        character_class = self.character.character_class.class_name.lower()
        
        if character_class in class_rewards:
            class_bonus = class_rewards[character_class]
            self._apply_class_bonuses(class_bonus)
        
        # Special abilities
        special_abilities = rewards.get('special_abilities', [])
        for ability in special_abilities:
            self._grant_special_ability(ability)
        
        # Reputation changes
        reputation_changes = rewards.get('reputation_bonus', {})
        for faction, bonus in reputation_changes.items():
            if faction not in self.reputation_changes:
                self.reputation_changes[faction] = 0
            self.reputation_changes[faction] += bonus
    
    def _apply_class_bonuses(self, bonuses: Dict[str, Any]):
        """Apply class-specific stat bonuses"""
        for stat, bonus in bonuses.items():
            if hasattr(self.character, stat):
                current_value = getattr(self.character, stat)
                if isinstance(current_value, (int, float)):
                    setattr(self.character, stat, current_value + bonus)
                    print(f"Class bonus: +{bonus} {stat}")
            elif stat == 'abilities':
                # Special abilities list
                for ability in bonus:
                    self._grant_special_ability(ability)
    
    def _grant_special_ability(self, ability: str):
        """Grant a special ability to the character"""
        if not hasattr(self.character, 'special_abilities'):
            self.character.special_abilities = []
        
        if ability not in self.character.special_abilities:
            self.character.special_abilities.append(ability)
            print(f"Gained special ability: {ability}")
    
    def _apply_consequences(self, consequences: Dict[str, Any], reason: str):
        """Apply quest failure/abandon consequences"""
        if 'reputation_loss' in consequences:
            for faction, loss in consequences['reputation_loss'].items():
                if faction not in self.reputation_changes:
                    self.reputation_changes[faction] = 0
                self.reputation_changes[faction] -= loss
                print(f"Lost {loss} reputation with {faction}")
        
        if 'alignment_shift' in consequences:
            shift = consequences['alignment_shift']
            # TODO: Apply alignment shift
            print(f"Alignment shifted by {shift}")
        
        # Special consequences
        for consequence, value in consequences.items():
            if consequence not in ['reputation_loss', 'alignment_shift']:
                self.quest_flags[f"{consequence}_{reason}"] = value
    
    def get_quest_info(self, quest_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a quest"""
        quest = self.quest_system.quest_definitions.get(quest_id)
        if not quest:
            return None
        
        info = {
            'quest_id': quest_id,
            'name': quest.name,
            'description': quest.description,
            'quest_giver': quest.quest_giver,
            'alignment_requirement': quest.alignment_requirement,
            'level_requirement': quest.level_requirement,
            'prerequisites': quest.prerequisites,
            'rewards': quest.rewards,
            'status': 'available'
        }
        
        # Check status
        if quest_id in self.active_quests:
            info['status'] = 'active'
            quest_state = self.active_quests[quest_id]
            info['current_step'] = quest_state['current_step']
            info['current_objective'] = quest.steps[quest_state['current_step'] - 1]['objective']
            info['progress'] = quest_state.get('step_progress', {})
        elif quest_id in self.completed_quests:
            info['status'] = 'completed'
        elif any(failed['quest_id'] == quest_id for failed in self.failed_quests):
            info['status'] = 'failed'
            failed_data = next(failed for failed in self.failed_quests if failed['quest_id'] == quest_id)
            info['failure_reason'] = failed_data['reason']
        elif not self.can_accept_quest(quest):
            info['status'] = 'locked'
            info['lock_reason'] = self._get_lock_reason(quest)
        
        return info
    
    def _get_lock_reason(self, quest: Quest) -> str:
        """Get reason why quest is locked"""
        # Check alignment
        if quest.alignment_requirement != 'any':
            char_alignment = self.character.alignment.name.lower()
            if char_alignment != quest.alignment_requirement:
                return f"Requires {quest.alignment_requirement} alignment"
        
        # Check level
        if self.character.level < quest.level_requirement:
            return f"Requires level {quest.level_requirement}"
        
        # Check prerequisites
        for prereq in quest.prerequisites:
            if prereq not in self.completed_quests:
                prereq_quest = self.quest_system.quest_definitions.get(prereq)
                prereq_name = prereq_quest.name if prereq_quest else prereq
                return f"Requires completion of '{prereq_name}'"
        
        return "Unknown requirement"
    
    def get_journal(self) -> Dict[str, Any]:
        """Get formatted quest journal"""
        active = []
        for quest_id in self.active_quests:
            quest_info = self.get_quest_info(quest_id)
            if quest_info:
                active.append(quest_info)
        
        completed = []
        for quest_id in self.completed_quests:
            quest = self.quest_system.quest_definitions.get(quest_id)
            if quest:
                completed.append({
                    'quest_id': quest_id,
                    'name': quest.name,
                    'experience': quest.rewards.get('experience', 0)
                })
        
        available = []
        for quest in self.get_available_quests():
            quest_info = self.get_quest_info(quest.quest_id)
            if quest_info:
                available.append(quest_info)
        
        failed = []
        for failed_quest in self.failed_quests:
            quest = self.quest_system.quest_definitions.get(failed_quest['quest_id'])
            if quest:
                failed.append({
                    'quest_id': failed_quest['quest_id'],
                    'name': quest.name,
                    'reason': failed_quest['reason'],
                    'progress': failed_quest.get('progress', 0)
                })
        
        return {
            'active': active,
            'completed': completed,
            'available': available,
            'failed': failed,
            'character_name': self.character.name,
            'character_level': self.character.level,
            'character_alignment': self.character.alignment.name
        }
    
    def has_completed_quest(self, quest_id: str) -> bool:
        """Check if character has completed a specific quest"""
        return quest_id in self.completed_quests
    
    def get_quest_flag(self, flag_name: str) -> Any:
        """Get a quest flag value"""
        return self.quest_flags.get(flag_name)
    
    def set_quest_flag(self, flag_name: str, value: Any):
        """Set a quest flag value"""
        self.quest_flags[flag_name] = value
    
    def get_reputation_change(self, faction: str) -> int:
        """Get total reputation change for a faction"""
        return self.reputation_changes.get(faction, 0)