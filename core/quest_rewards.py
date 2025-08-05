"""
Quest Rewards System - Class-specific rewards and progression bonuses

Handles the calculation and application of MajorMUD-style quest rewards including:
- Universal experience and gold rewards
- Class-specific stat bonuses and abilities
- Alignment-based reputation and equipment access
- Progressive reward scaling for quest tiers
"""

import json
import os
from typing import Dict, List, Optional, Any
from core.alignment_system import Alignment

class QuestRewardCalculator:
    """Calculates and applies quest rewards based on character class and quest tier"""
    
    def __init__(self):
        self.reward_data = {}
        self.load_reward_data()
    
    def load_reward_data(self):
        """Load quest reward data from JSON files"""
        reward_file = os.path.join('data', 'quests', 'quest_rewards.json')
        if os.path.exists(reward_file):
            try:
                with open(reward_file, 'r') as f:
                    self.reward_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading quest reward data: {e}")
                self._create_default_reward_data()
        else:
            self._create_default_reward_data()
    
    def _create_default_reward_data(self):
        """Create default reward data if file doesn't exist"""
        self.reward_data = {
            "experience_progression": {
                "quest_tier_1": 150000,
                "quest_tier_2": 2000000,
                "quest_tier_3": 7500000,
                "quest_tier_4": 30000000,
                "quest_tier_5": 175000000
            },
            "class_specific_rewards": {},
            "universal_rewards": {},
            "alignment_bonuses": {}
        }
    
    def get_quest_tier(self, quest_id: str) -> int:
        """Determine quest tier based on quest ID"""
        # Extract tier from quest ID pattern (good_quest_1, evil_quest_2, etc.)
        if '_quest_' in quest_id:
            try:
                tier_str = quest_id.split('_quest_')[1]
                return int(tier_str)
            except (IndexError, ValueError):
                return 1
        return 1
    
    def calculate_universal_rewards(self, quest_id: str, quest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate universal rewards (experience, gold, items)"""
        rewards = {}
        
        # Get base rewards from quest data
        base_rewards = quest_data.get('rewards', {})
        
        # Experience reward
        if 'experience' in base_rewards:
            rewards['experience'] = base_rewards['experience']
        else:
            # Calculate based on tier if not specified
            tier = self.get_quest_tier(quest_id)
            exp_key = f"quest_tier_{tier}"
            exp_progression = self.reward_data.get('experience_progression', {})
            rewards['experience'] = exp_progression.get(exp_key, 150000)
        
        # Gold reward
        if 'gold' in base_rewards:
            rewards['gold'] = base_rewards['gold']
        
        # Item rewards
        if 'items' in base_rewards:
            rewards['items'] = base_rewards['items']
        
        return rewards
    
    def calculate_class_rewards(self, character, quest_id: str, quest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate class-specific rewards for character"""
        class_rewards = {}
        
        # Get character class
        character_class = character.character_class.class_name.lower()
        
        # Get quest tier
        tier = self.get_quest_tier(quest_id)
        tier_key = f"quest_tier_{tier}"
        
        # Get class-specific rewards from quest data
        quest_class_rewards = quest_data.get('rewards', {}).get('class_specific', {})
        if character_class in quest_class_rewards:
            class_rewards.update(quest_class_rewards[character_class])
        
        # Get general class rewards for this tier
        general_class_rewards = self.reward_data.get('class_specific_rewards', {})
        if character_class in general_class_rewards:
            tier_rewards = general_class_rewards[character_class].get(tier_key, {})
            class_rewards.update(tier_rewards)
        
        return class_rewards
    
    def calculate_alignment_bonuses(self, character, quest_id: str, quest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate alignment-based bonuses"""
        alignment_bonuses = {}
        
        character_alignment = character.alignment.name.lower()
        alignment_data = self.reward_data.get('alignment_bonuses', {}).get(character_alignment, {})
        
        # Reputation bonuses
        reputation_bonus = alignment_data.get('reputation_bonus', {})
        if reputation_bonus:
            alignment_bonuses['reputation_bonus'] = reputation_bonus
        
        # Equipment access
        equipment_access = alignment_data.get('equipment_access', [])
        if equipment_access:
            alignment_bonuses['equipment_access'] = equipment_access
        
        # Special abilities
        special_abilities = alignment_data.get('special_abilities', [])
        if special_abilities:
            alignment_bonuses['special_abilities'] = special_abilities
        
        return alignment_bonuses
    
    def apply_universal_rewards(self, character, rewards: Dict[str, Any]):
        """Apply universal rewards to character"""
        applied_rewards = []
        
        # Experience reward
        if 'experience' in rewards:
            exp_amount = rewards['experience']
            character.gain_experience(exp_amount)
            applied_rewards.append(f"Gained {exp_amount:,} experience points")
        
        # Gold reward
        if 'gold' in rewards:
            gold_amount = rewards['gold']
            if hasattr(character, 'currency') and character.currency:
                character.currency.add_gold(gold_amount)
                applied_rewards.append(f"Received {gold_amount} gold pieces")
        
        # Item rewards
        if 'items' in rewards:
            for item_id in rewards['items']:
                # TODO: Add item to character inventory
                applied_rewards.append(f"Received item: {item_id}")
        
        return applied_rewards
    
    def apply_class_rewards(self, character, class_rewards: Dict[str, Any]):
        """Apply class-specific rewards to character"""
        applied_rewards = []
        
        for reward_type, reward_value in class_rewards.items():
            if reward_type == 'abilities':
                # Special abilities list
                for ability in reward_value:
                    self._grant_special_ability(character, ability)
                    applied_rewards.append(f"Gained ability: {ability}")
            
            elif hasattr(character, reward_type):
                # Stat bonuses
                current_value = getattr(character, reward_type)
                if isinstance(current_value, (int, float)):
                    new_value = current_value + reward_value
                    setattr(character, reward_type, new_value)
                    applied_rewards.append(f"Class bonus: +{reward_value} {reward_type}")
            
            else:
                # Custom reward types
                applied_rewards.append(f"Class bonus: {reward_type} +{reward_value}")
        
        return applied_rewards
    
    def apply_alignment_bonuses(self, character, alignment_bonuses: Dict[str, Any]):
        """Apply alignment-based bonuses to character"""
        applied_rewards = []
        
        # Reputation bonuses
        if 'reputation_bonus' in alignment_bonuses:
            rep_bonuses = alignment_bonuses['reputation_bonus']
            for faction, bonus in rep_bonuses.items():
                # TODO: Apply reputation bonus to faction
                applied_rewards.append(f"Reputation bonus: +{bonus} with {faction}")
        
        # Equipment access
        if 'equipment_access' in alignment_bonuses:
            equipment_types = alignment_bonuses['equipment_access']
            for equipment_type in equipment_types:
                applied_rewards.append(f"Equipment access: {equipment_type}")
        
        # Special abilities
        if 'special_abilities' in alignment_bonuses:
            abilities = alignment_bonuses['special_abilities']
            for ability in abilities:
                self._grant_special_ability(character, ability)
                applied_rewards.append(f"Alignment ability: {ability}")
        
        return applied_rewards
    
    def _grant_special_ability(self, character, ability: str):
        """Grant a special ability to the character"""
        if not hasattr(character, 'special_abilities'):
            character.special_abilities = []
        
        if ability not in character.special_abilities:
            character.special_abilities.append(ability)
    
    def calculate_and_apply_all_rewards(self, character, quest_id: str, quest_data: Dict[str, Any]) -> List[str]:
        """Calculate and apply all rewards for quest completion"""
        all_applied_rewards = []
        
        # Universal rewards
        universal_rewards = self.calculate_universal_rewards(quest_id, quest_data)
        universal_applied = self.apply_universal_rewards(character, universal_rewards)
        all_applied_rewards.extend(universal_applied)
        
        # Class-specific rewards
        class_rewards = self.calculate_class_rewards(character, quest_id, quest_data)
        if class_rewards:
            class_applied = self.apply_class_rewards(character, class_rewards)
            all_applied_rewards.extend(class_applied)
        
        # Alignment bonuses
        alignment_bonuses = self.calculate_alignment_bonuses(character, quest_id, quest_data)
        if alignment_bonuses:
            alignment_applied = self.apply_alignment_bonuses(character, alignment_bonuses)
            all_applied_rewards.extend(alignment_applied)
        
        return all_applied_rewards
    
    def preview_rewards(self, character, quest_id: str, quest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preview rewards without applying them"""
        reward_preview = {
            'universal': self.calculate_universal_rewards(quest_id, quest_data),
            'class_specific': self.calculate_class_rewards(character, quest_id, quest_data),
            'alignment_bonuses': self.calculate_alignment_bonuses(character, quest_id, quest_data)
        }
        
        return reward_preview
    
    def format_reward_preview(self, character, quest_id: str, quest_data: Dict[str, Any]) -> str:
        """Format reward preview for display"""
        preview = self.preview_rewards(character, quest_id, quest_data)
        
        output = []
        output.append("QUEST REWARDS PREVIEW:")
        output.append("")
        
        # Universal rewards
        universal = preview['universal']
        if 'experience' in universal:
            output.append(f"• {universal['experience']:,} experience points")
        if 'gold' in universal:
            output.append(f"• {universal['gold']} gold pieces")
        if 'items' in universal:
            for item in universal['items']:
                output.append(f"• Item: {item}")
        
        # Class-specific rewards
        class_rewards = preview['class_specific']
        if class_rewards:
            output.append("")
            output.append(f"CLASS BONUSES ({character.character_class.class_name}):")
            for reward_type, value in class_rewards.items():
                if reward_type == 'abilities':
                    for ability in value:
                        output.append(f"• Ability: {ability}")
                else:
                    output.append(f"• {reward_type}: +{value}")
        
        # Alignment bonuses
        alignment_bonuses = preview['alignment_bonuses']
        if alignment_bonuses:
            output.append("")
            output.append(f"ALIGNMENT BONUSES ({character.alignment.name}):")
            
            if 'reputation_bonus' in alignment_bonuses:
                for faction, bonus in alignment_bonuses['reputation_bonus'].items():
                    output.append(f"• Reputation: +{bonus} with {faction}")
            
            if 'special_abilities' in alignment_bonuses:
                for ability in alignment_bonuses['special_abilities']:
                    output.append(f"• Alignment Ability: {ability}")
        
        return '\n'.join(output)

# Global reward calculator instance
quest_reward_calculator = QuestRewardCalculator()