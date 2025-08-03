"""
Gypsy Character Class for Rogue City
Traditional MajorMUD wandering fortune teller with minor magic and trickery.
"""

from .base_character import BaseCharacter
from core.alignment_system import Alignment
from typing import Dict, Any, Tuple, List


class Gypsy(BaseCharacter):
    """
    Gypsy class - Wandering fortune teller and trickster
    
    VERSATILE TRICKSTER - Moderate progression, luck-based
    
    Experience Penalty: +25% (versatile abilities require more experience)
    Stat Modifiers: +2 CHA, +2 DEX, +1 INT, -2 STR, -1 CON, -1 WIS
    Hit Die: d6 (light build)
    Attack Speed: 3.0 seconds (moderate combat speed)
    Critical Range: 20 (standard critical chance)
    
    FORTUNE AND FATE CORE:
    - Fortune telling to predict danger and opportunities
    - Minor illusion magic for deception and trickery
    - Wanderer's luck for avoiding traps and finding treasure
    - Charm magic with limited enchantment abilities
    - Sleight of hand for enhanced theft and trickery
    - Gypsy curses to inflict minor hexes on enemies
    
    GYPSY ABILITIES:
    - Fortune Telling: Predict danger and opportunities
    - Minor Illusions: Create small magical deceptions
    - Wanderer's Luck: Bonus to avoiding traps and finding treasure
    - Charm Magic: Limited enchantment abilities
    - Sleight of Hand: Enhanced theft and trickery skills
    - Gypsy Curse: Inflict minor hexes on enemies
    
    EQUIPMENT ACCESS:
    - Weapons: Light weapons, throwing weapons, exotic weapons
    - Armor: Light armor and colorful clothing
    - Magic: Can use minor magical items and charms
    - Accessories: Fortunetelling tools, charms, jewelry
    """
    
    def __init__(self, name: str, race_id: str = "human", alignment: Alignment = Alignment.NEUTRAL):
        """Initialize Gypsy character with fortune and trickery systems"""
        super().__init__(name, 'gypsy', race_id, alignment)
        
        # Fortune telling attributes
        self.fortune_uses_per_day = max(2, self.level // 2)
        self.fortune_uses_used = 0
        self.fortune_bonus = self._calculate_fortune_bonus()
        
        # Illusion and charm magic
        self.illusion_uses_per_day = max(1, self.level // 3)
        self.illusion_uses_used = 0
        self.charm_uses_per_day = max(1, self.level // 4)
        self.charm_uses_used = 0
        self.charm_save_dc = self._calculate_charm_dc()
        
        # Wanderer's luck system
        self.luck_pool = self._calculate_luck_pool()
        self.luck_used = 0
        self.luck_bonus = self._calculate_luck_bonus()
        
        # Sleight of hand and trickery
        self.sleight_bonus = self._calculate_sleight_bonus()
        self.pickpocket_bonus = self._calculate_pickpocket_bonus()
        
        # Gypsy curse abilities
        self.curse_uses_per_day = max(1, self.level // 5)
        self.curse_uses_used = 0
        self.curse_save_dc = self._calculate_curse_dc()
        
        # Exotic knowledge and languages
        self.languages_known = self._get_starting_languages()
        self.lore_bonus = self._calculate_lore_bonus()
        
    def get_hit_die_value(self) -> int:
        """Gypsies use d6 hit die (light build)"""
        return 6
        
    def get_hit_die_type(self) -> str:
        """Return dice notation for hit die"""
        return "1d6"
        
    def get_attack_speed(self) -> float:
        """Return attack speed in seconds (considering equipped weapon)"""
        if hasattr(self, 'equipment_system') and self.equipment_system:
            return self.equipment_system.get_attack_speed_modifier()
        return self.get_base_attack_speed()
    
    def get_base_attack_speed(self) -> float:
        """Gypsies attack every 3 seconds unarmed (moderate speed)"""
        return 3.0
        
    def get_critical_range(self) -> int:
        """Gypsies crit on natural 20 (standard critical)"""
        return 20
        
    def get_experience_penalty(self) -> int:
        """Gypsies have +25% experience penalty"""
        return 25
        
    def get_special_abilities(self) -> Dict[str, Any]:
        """Comprehensive Gypsy special abilities"""
        return {
            # Fortune telling
            'fortune_telling': self.get_fortune_uses_remaining(),
            'fortune_bonus': self.get_fortune_bonus(),
            'predict_danger': True,
            'predict_opportunity': True,
            'divine_guidance': self.level >= 3,
            
            # Illusion magic
            'minor_illusions': self.get_illusion_uses_remaining(),
            'ghost_sound': True,
            'mage_hand': self.level >= 2,
            'prestidigitation': True,
            'major_illusion': self.level >= 8,
            
            # Charm magic
            'charm_magic': self.get_charm_uses_remaining(),
            'charm_save_dc': self.get_charm_save_dc(),
            'charm_person': True,
            'suggestion': self.level >= 6,
            'mass_charm': self.level >= 12,
            
            # Wanderer's luck
            'wanderers_luck': self.get_luck_remaining(),
            'luck_bonus': self.get_luck_bonus(),
            'avoid_traps': True,
            'find_treasure': True,
            'lucky_breaks': True,
            
            # Sleight of hand and trickery
            'sleight_of_hand': self.get_sleight_bonus(),
            'pickpocket': self.get_pickpocket_bonus(),
            'palm_object': True,
            'plant_object': self.level >= 4,
            'master_thief': self.level >= 10,
            
            # Gypsy curses
            'gypsy_curse': self.get_curse_uses_remaining(),
            'curse_save_dc': self.get_curse_save_dc(),
            'minor_hex': True,
            'evil_eye': self.level >= 3,
            'major_curse': self.level >= 9,
            
            # Knowledge and languages
            'exotic_lore': self.get_lore_bonus(),
            'languages_known': len(self.languages_known),
            'read_magic': self.level >= 2,
            'identify_magic': self.level >= 5,
            
            # Social abilities
            'fast_talk': True,
            'gather_information': True,
            'streetwise': True,
            'persuasion': self.level >= 3,
            
            # Equipment proficiencies
            'light_weapon_proficiency': True,
            'exotic_weapon_proficiency': self.level >= 6,
            'thrown_weapon_mastery': True
        }
    
    # === FORTUNE TELLING ABILITIES ===
    
    def get_fortune_uses_remaining(self) -> int:
        """Get fortune telling uses remaining"""
        return max(0, self.fortune_uses_per_day - self.fortune_uses_used)
    
    def _calculate_fortune_bonus(self) -> int:
        """Calculate fortune telling bonus"""
        base_bonus = 2
        cha_bonus = max(0, (self.stats['charisma'] - 10) // 2)
        int_bonus = max(0, (self.stats['intelligence'] - 10) // 4)
        level_bonus = self.level // 3
        return base_bonus + cha_bonus + int_bonus + level_bonus
    
    def get_fortune_bonus(self) -> int:
        """Get fortune telling bonus"""
        return self._calculate_fortune_bonus()
    
    def can_tell_fortune(self) -> bool:
        """Check if gypsy can tell fortunes"""
        return self.get_fortune_uses_remaining() > 0
    
    def tell_fortune(self, fortune_type: str = "general") -> Dict[str, Any]:
        """Tell fortune with various focuses"""
        if not self.can_tell_fortune():
            return {'success': False, 'reason': 'No fortune telling uses remaining'}
        
        self.fortune_uses_used += 1
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            fortune_roll = dice.roll("1d20") + self.get_fortune_bonus()
            
            success = fortune_roll >= 15
            if success:
                fortunes = {
                    'danger': 'You sense danger approaching from the shadows',
                    'opportunity': 'Fortune smiles upon you - opportunity awaits',
                    'treasure': 'Hidden wealth lies near, waiting to be found',
                    'combat': 'The spirits whisper of coming battle',
                    'general': 'The fates reveal glimpses of your destiny'
                }
                message = fortunes.get(fortune_type, fortunes['general'])
                
                return {
                    'success': True,
                    'fortune_type': fortune_type,
                    'message': message,
                    'bonus_duration': 5 + self.level,  # Rounds of bonus
                    'remaining_uses': self.get_fortune_uses_remaining()
                }
            else:
                return {
                    'success': False,
                    'message': 'The spirits remain silent',
                    'remaining_uses': self.get_fortune_uses_remaining()
                }
        except ImportError:
            import random
            success = random.randint(1, 20) + self.get_fortune_bonus() >= 15
            return {
                'success': success,
                'message': 'Fortune revealed' if success else 'The spirits remain silent',
                'remaining_uses': self.get_fortune_uses_remaining()
            }
    
    def predict_danger(self) -> bool:
        """Predict incoming danger"""
        if not self.can_tell_fortune():
            return False
        
        fortune_result = self.tell_fortune('danger')
        return fortune_result.get('success', False)
    
    def predict_opportunity(self) -> bool:
        """Predict upcoming opportunities"""
        if not self.can_tell_fortune():
            return False
        
        fortune_result = self.tell_fortune('opportunity')
        return fortune_result.get('success', False)
    
    # === ILLUSION MAGIC ABILITIES ===
    
    def get_illusion_uses_remaining(self) -> int:
        """Get illusion magic uses remaining"""
        return max(0, self.illusion_uses_per_day - self.illusion_uses_used)
    
    def can_cast_illusion(self) -> bool:
        """Check if gypsy can cast illusions"""
        return self.get_illusion_uses_remaining() > 0
    
    def cast_minor_illusion(self, illusion_type: str = "visual") -> Dict[str, Any]:
        """Cast minor illusion magic"""
        if not self.can_cast_illusion():
            return {'success': False, 'reason': 'No illusion uses remaining'}
        
        self.illusion_uses_used += 1
        
        illusion_effects = {
            'visual': 'Creates a minor visual illusion',
            'sound': 'Produces phantom sounds',
            'distraction': 'Creates distracting effects',
            'disguise': 'Alters appearance slightly'
        }
        
        return {
            'success': True,
            'illusion_type': illusion_type,
            'effect': illusion_effects.get(illusion_type, illusion_effects['visual']),
            'duration_minutes': 5 + self.level,
            'remaining_uses': self.get_illusion_uses_remaining()
        }
    
    def create_ghost_sound(self, sound_description: str) -> bool:
        """Create phantom sounds"""
        return self.cast_minor_illusion('sound').get('success', False)
    
    def can_cast_major_illusion(self) -> bool:
        """Check if gypsy can cast major illusions"""
        return self.level >= 8 and self.can_cast_illusion()
    
    def cast_major_illusion(self) -> Dict[str, Any]:
        """Cast major illusion affecting multiple senses"""
        if not self.can_cast_major_illusion():
            return {'success': False, 'reason': 'Major illusion not available'}
        
        self.illusion_uses_used += 2  # Costs 2 uses
        
        return {
            'success': True,
            'effect': 'Complex illusion affecting sight, sound, and smell',
            'duration_minutes': 10 + self.level,
            'area_effect': True,
            'remaining_uses': self.get_illusion_uses_remaining()
        }
    
    # === CHARM MAGIC ABILITIES ===
    
    def get_charm_uses_remaining(self) -> int:
        """Get charm magic uses remaining"""
        return max(0, self.charm_uses_per_day - self.charm_uses_used)
    
    def _calculate_charm_dc(self) -> int:
        """Calculate charm magic save DC"""
        base_dc = 10
        cha_bonus = max(0, (self.stats['charisma'] - 10) // 2)
        level_bonus = self.level // 3
        return base_dc + cha_bonus + level_bonus
    
    def get_charm_save_dc(self) -> int:
        """Get charm magic save DC"""
        return self._calculate_charm_dc()
    
    def can_cast_charm(self) -> bool:
        """Check if gypsy can cast charm magic"""
        return self.get_charm_uses_remaining() > 0
    
    def cast_charm_person(self, target_level: int = 1) -> Dict[str, Any]:
        """Cast charm person spell"""
        if not self.can_cast_charm():
            return {'success': False, 'reason': 'No charm uses remaining'}
        
        self.charm_uses_used += 1
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            will_save = dice.roll("1d20") + target_level
            success = will_save < self.get_charm_save_dc()
            
            return {
                'success': success,
                'target_level': target_level,
                'save_dc': self.get_charm_save_dc(),
                'duration_hours': self.level,
                'remaining_uses': self.get_charm_uses_remaining()
            }
        except ImportError:
            import random
            success = random.randint(1, 20) + target_level < self.get_charm_save_dc()
            return {
                'success': success,
                'remaining_uses': self.get_charm_uses_remaining()
            }
    
    # === WANDERER'S LUCK ABILITIES ===
    
    def _calculate_luck_pool(self) -> int:
        """Calculate luck pool size"""
        base_pool = 3 + self.level
        cha_bonus = max(0, (self.stats['charisma'] - 10) // 2)
        return base_pool + cha_bonus
    
    def get_luck_pool(self) -> int:
        """Get total luck pool"""
        return self._calculate_luck_pool()
    
    def get_luck_remaining(self) -> int:
        """Get luck pool remaining"""
        return max(0, self.get_luck_pool() - self.luck_used)
    
    def _calculate_luck_bonus(self) -> int:
        """Calculate base luck bonus"""
        base_bonus = 1
        level_bonus = self.level // 4
        return base_bonus + level_bonus
    
    def get_luck_bonus(self) -> int:
        """Get base luck bonus"""
        return self._calculate_luck_bonus()
    
    def can_use_luck(self, cost: int = 1) -> bool:
        """Check if gypsy can use luck"""
        return self.get_luck_remaining() >= cost
    
    def use_wanderers_luck(self, luck_type: str = "general", cost: int = 1) -> Dict[str, Any]:
        """Use wanderer's luck for various benefits"""
        if not self.can_use_luck(cost):
            return {'success': False, 'reason': 'Insufficient luck remaining'}
        
        self.luck_used += cost
        base_bonus = self.get_luck_bonus()
        
        luck_effects = {
            'avoid_trap': {'bonus': base_bonus + 3, 'description': 'Bonus to avoid traps'},
            'find_treasure': {'bonus': base_bonus + 2, 'description': 'Bonus to find hidden treasure'},
            'save_throw': {'bonus': base_bonus + 1, 'description': 'Bonus to saving throws'},
            'skill_check': {'bonus': base_bonus + 2, 'description': 'Bonus to skill checks'},
            'general': {'bonus': base_bonus, 'description': 'General luck bonus'}
        }
        
        effect = luck_effects.get(luck_type, luck_effects['general'])
        
        return {
            'success': True,
            'luck_type': luck_type,
            'bonus': effect['bonus'],
            'description': effect['description'],
            'remaining_luck': self.get_luck_remaining()
        }
    
    def avoid_trap_with_luck(self) -> int:
        """Use luck to avoid traps"""
        result = self.use_wanderers_luck('avoid_trap', 1)
        return result.get('bonus', 0) if result.get('success') else 0
    
    def find_treasure_with_luck(self) -> int:
        """Use luck to find treasure"""
        result = self.use_wanderers_luck('find_treasure', 2)
        return result.get('bonus', 0) if result.get('success') else 0
    
    # === SLEIGHT OF HAND ABILITIES ===
    
    def _calculate_sleight_bonus(self) -> int:
        """Calculate sleight of hand bonus"""
        base_bonus = 3
        dex_bonus = max(0, (self.stats['dexterity'] - 10) // 2)
        cha_bonus = max(0, (self.stats['charisma'] - 10) // 4)
        level_bonus = self.level // 2
        return base_bonus + dex_bonus + cha_bonus + level_bonus
    
    def get_sleight_bonus(self) -> int:
        """Get sleight of hand bonus"""
        return self._calculate_sleight_bonus()
    
    def _calculate_pickpocket_bonus(self) -> int:
        """Calculate pickpocket bonus"""
        base_bonus = 2
        dex_bonus = max(0, (self.stats['dexterity'] - 10) // 2)
        cha_bonus = max(0, (self.stats['charisma'] - 10) // 3)
        level_bonus = self.level // 3
        return base_bonus + dex_bonus + cha_bonus + level_bonus
    
    def get_pickpocket_bonus(self) -> int:
        """Get pickpocket bonus"""
        return self._calculate_pickpocket_bonus()
    
    def attempt_sleight_of_hand(self, difficulty: int = 15) -> bool:
        """Attempt sleight of hand maneuver"""
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            sleight_roll = dice.roll("1d20") + self.get_sleight_bonus()
            return sleight_roll >= difficulty
        except ImportError:
            import random
            return random.randint(1, 20) + self.get_sleight_bonus() >= difficulty
    
    def attempt_pickpocket(self, target_level: int = 1) -> bool:
        """Attempt to pickpocket a target"""
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            pickpocket_roll = dice.roll("1d20") + self.get_pickpocket_bonus()
            dc = 10 + target_level
            return pickpocket_roll >= dc
        except ImportError:
            import random
            return random.randint(1, 20) + self.get_pickpocket_bonus() >= (10 + target_level)
    
    def palm_object(self, object_size: str = "small") -> bool:
        """Palm an object with sleight of hand"""
        size_modifiers = {'tiny': 0, 'small': 2, 'medium': 5, 'large': 10}
        difficulty = 12 + size_modifiers.get(object_size, 2)
        return self.attempt_sleight_of_hand(difficulty)
    
    # === GYPSY CURSE ABILITIES ===
    
    def get_curse_uses_remaining(self) -> int:
        """Get gypsy curse uses remaining"""
        return max(0, self.curse_uses_per_day - self.curse_uses_used)
    
    def _calculate_curse_dc(self) -> int:
        """Calculate curse save DC"""
        base_dc = 12
        cha_bonus = max(0, (self.stats['charisma'] - 10) // 2)
        level_bonus = self.level // 4
        return base_dc + cha_bonus + level_bonus
    
    def get_curse_save_dc(self) -> int:
        """Get curse save DC"""
        return self._calculate_curse_dc()
    
    def can_cast_curse(self) -> bool:
        """Check if gypsy can cast curses"""
        return self.get_curse_uses_remaining() > 0
    
    def cast_gypsy_curse(self, curse_type: str = "minor_hex") -> Dict[str, Any]:
        """Cast a gypsy curse"""
        if not self.can_cast_curse():
            return {'success': False, 'reason': 'No curse uses remaining'}
        
        self.curse_uses_used += 1
        
        curse_effects = {
            'minor_hex': {'penalty': -1, 'duration': 'hours', 'description': 'Minor bad luck'},
            'evil_eye': {'penalty': -2, 'duration': 'hours', 'description': 'Cursed with misfortune'},
            'major_curse': {'penalty': -3, 'duration': 'days', 'description': 'Significant curse'}
        }
        
        if curse_type == 'major_curse' and self.level < 9:
            curse_type = 'evil_eye'
        elif curse_type == 'evil_eye' and self.level < 3:
            curse_type = 'minor_hex'
        
        effect = curse_effects.get(curse_type, curse_effects['minor_hex'])
        
        return {
            'success': True,
            'curse_type': curse_type,
            'penalty': effect['penalty'],
            'duration': effect['duration'],
            'description': effect['description'],
            'save_dc': self.get_curse_save_dc(),
            'remaining_uses': self.get_curse_uses_remaining()
        }
    
    # === LORE AND LANGUAGES ===
    
    def _get_starting_languages(self) -> List[str]:
        """Get starting languages known"""
        return ['common', 'gypsy', 'thieves_cant']
    
    def _calculate_lore_bonus(self) -> int:
        """Calculate exotic lore bonus"""
        base_bonus = 2
        int_bonus = max(0, (self.stats['intelligence'] - 10) // 2)
        cha_bonus = max(0, (self.stats['charisma'] - 10) // 4)
        level_bonus = self.level // 3
        return base_bonus + int_bonus + cha_bonus + level_bonus
    
    def get_lore_bonus(self) -> int:
        """Get exotic lore bonus"""
        return self._calculate_lore_bonus()
    
    def learn_language(self, language: str) -> bool:
        """Learn a new language"""
        if language not in self.languages_known:
            self.languages_known.append(language)
            return True
        return False
    
    def attempt_lore_check(self, difficulty: int = 15) -> bool:
        """Attempt exotic lore check"""
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            lore_roll = dice.roll("1d20") + self.get_lore_bonus()
            return lore_roll >= difficulty
        except ImportError:
            import random
            return random.randint(1, 20) + self.get_lore_bonus() >= difficulty
    
    # === EQUIPMENT RESTRICTIONS ===
    
    def can_use_weapon(self, weapon) -> bool:
        """Gypsies can use light and exotic weapons"""
        if hasattr(weapon, 'weapon_category'):
            allowed = ['light', 'simple', 'thrown']
            if self.level >= 6:
                allowed.append('exotic')
            return weapon.weapon_category.lower() in allowed
        if hasattr(weapon, 'weapon_type'):
            allowed_types = ['dagger', 'dart', 'sling', 'whip', 'scimitar']
            if self.level >= 6:
                allowed_types.extend(['chakram', 'bola', 'net'])
            return weapon.weapon_type.lower() in allowed_types
        return True  # Default allow for basic weapons
    
    def can_use_armor(self, armor) -> bool:
        """Gypsies can use light armor"""
        if hasattr(armor, 'armor_type'):
            allowed_types = ['light', 'leather', 'cloth', 'padded']
            return armor.armor_type.lower() in allowed_types
        return True  # Default allow for basic armor
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Gypsy':
        """Create Gypsy from save data"""
        race_id = data.get('race_id', 'human')
        
        # Load alignment from save data or default to neutral
        alignment = Alignment.NEUTRAL
        if 'alignment_data' in data:
            alignment_name = data['alignment_data'].get('alignment', 'NEUTRAL')
            alignment = getattr(Alignment, alignment_name, Alignment.NEUTRAL)
        
        gypsy = cls(data['character_name'], race_id, alignment)
        
        # Restore basic character data
        gypsy.level = data['level']
        gypsy.experience = data['experience']
        gypsy.base_stats = data.get('base_stats', gypsy.base_stats)
        gypsy.stats = data['stats']
        
        # Restore derived stats
        derived = data['derived_stats']
        gypsy.max_hp = derived['max_hp']
        gypsy.current_hp = derived['current_hp']
        gypsy.armor_class = derived['armor_class']
        gypsy.base_attack_bonus = derived['base_attack_bonus']
        
        # Restore location
        location = data['current_location']
        gypsy.current_area = location.get('area_id')
        gypsy.current_room = location.get('room_id')
        
        # Initialize item systems
        gypsy.initialize_item_systems()
        
        # Restore inventory and equipment data
        if 'inventory' in data:
            gypsy.inventory_system.from_dict(data['inventory'])
        if 'equipment' in data:
            gypsy.equipment_system.from_dict(data['equipment'])
        
        # Restore character creation state
        gypsy.unallocated_stats = data.get('unallocated_stats', 0)
        gypsy.creation_complete = data.get('creation_complete', True)
        
        # Load alignment data
        if 'alignment_data' in data:
            gypsy.load_alignment_data(data['alignment_data'])
        
        # Restore gypsy-specific attributes
        gypsy_data = data.get('gypsy_data', {})
        gypsy.fortune_uses_used = gypsy_data.get('fortune_uses_used', 0)
        gypsy.illusion_uses_used = gypsy_data.get('illusion_uses_used', 0)
        gypsy.charm_uses_used = gypsy_data.get('charm_uses_used', 0)
        gypsy.luck_used = gypsy_data.get('luck_used', 0)
        gypsy.curse_uses_used = gypsy_data.get('curse_uses_used', 0)
        gypsy.languages_known = gypsy_data.get('languages_known', ['common', 'gypsy', 'thieves_cant'])
        
        # Recalculate gypsy-specific attributes
        gypsy.fortune_uses_per_day = max(2, gypsy.level // 2)
        gypsy.fortune_bonus = gypsy._calculate_fortune_bonus()
        gypsy.illusion_uses_per_day = max(1, gypsy.level // 3)
        gypsy.charm_uses_per_day = max(1, gypsy.level // 4)
        gypsy.charm_save_dc = gypsy._calculate_charm_dc()
        gypsy.luck_pool = gypsy._calculate_luck_pool()
        gypsy.luck_bonus = gypsy._calculate_luck_bonus()
        gypsy.sleight_bonus = gypsy._calculate_sleight_bonus()
        gypsy.pickpocket_bonus = gypsy._calculate_pickpocket_bonus()
        gypsy.curse_uses_per_day = max(1, gypsy.level // 5)
        gypsy.curse_save_dc = gypsy._calculate_curse_dc()
        gypsy.lore_bonus = gypsy._calculate_lore_bonus()
        
        return gypsy
    
    def to_dict(self) -> Dict[str, Any]:
        """Override to include gypsy-specific data"""
        data = super().to_dict()
        data['gypsy_data'] = {
            'fortune_uses_used': self.fortune_uses_used,
            'illusion_uses_used': self.illusion_uses_used,
            'charm_uses_used': self.charm_uses_used,
            'luck_used': self.luck_used,
            'curse_uses_used': self.curse_uses_used,
            'languages_known': self.languages_known
        }
        return data
        
    def __str__(self) -> str:
        """String representation of Gypsy"""
        abilities = []
        
        # Fortune telling
        fortune_remaining = self.get_fortune_uses_remaining()
        abilities.append(f"Fortune {fortune_remaining}")
        
        # Luck pool
        luck_remaining = self.get_luck_remaining()
        abilities.append(f"Luck {luck_remaining}")
        
        # Illusions
        illusion_remaining = self.get_illusion_uses_remaining()
        abilities.append(f"Illusion {illusion_remaining}")
        
        # Charm magic
        charm_remaining = self.get_charm_uses_remaining()
        if charm_remaining > 0:
            abilities.append(f"Charm {charm_remaining}")
        
        # Sleight of hand
        sleight = self.get_sleight_bonus()
        abilities.append(f"Sleight +{sleight}")
        
        # Curses
        curse_remaining = self.get_curse_uses_remaining()
        if curse_remaining > 0:
            abilities.append(f"Curse {curse_remaining}")
        
        # Languages
        languages = len(self.languages_known)
        abilities.append(f"{languages} Languages")
            
        base_str = super().__str__()
        if abilities:
            base_str += f" [{', '.join(abilities)}]"
        return base_str