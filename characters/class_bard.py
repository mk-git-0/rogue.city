"""
Bard Character Class for Rogue City
Traditional MajorMUD versatile performer with song magic and support abilities.
"""

from .base_character import BaseCharacter
from core.alignment_system import Alignment
from typing import Dict, Any, Tuple, List


class Bard(BaseCharacter):
    """
    Bard class - Musical support and versatile performer
    
    SUPPORT CLASS - Moderate progression, party-focused
    
    Experience Penalty: +15% (moderate power, support focus)
    Stat Modifiers: +2 CHA, +1 DEX, +1 INT, -1 STR, -1 CON, -1 WIS
    Hit Die: d6 (light combatant)
    Attack Speed: 3.5 seconds (moderate combat speed)
    Critical Range: 20 (standard critical chance)
    
    MUSICAL MAGIC CORE:
    - Bardic songs that inspire allies and confuse enemies
    - Lore mastery for identifying creatures and magical effects
    - Jack of all trades with bonus to all skills and saves
    - Charm magic to influence NPCs through charisma
    - Countersong to dispel sound-based magical effects
    - Inspire courage for party-wide combat bonuses
    
    BARDIC ABILITIES:
    - Bardic Songs: Inspire allies, confuse enemies through music
    - Jack of All Trades: Bonus to all skills and saves
    - Lore Master: Identify creatures, items, and magical effects
    - Charm Person: Influence NPCs through charisma
    - Countersong: Dispel sound-based magical effects
    - Inspire Courage: Party-wide combat bonuses
    
    EQUIPMENT ACCESS:
    - Weapons: Light weapons, one-handed weapons, instruments
    - Armor: Light armor only (medium at higher levels)
    - Magic: Can use magical instruments and light magical items
    - Accessories: Musical instruments, charm accessories
    """
    
    def __init__(self, name: str, race_id: str = "human", alignment: Alignment = Alignment.NEUTRAL):
        """Initialize Bard character with musical magic systems"""
        super().__init__(name, 'bard', race_id, alignment)
        
        # Musical magic attributes
        self.bardic_songs_per_day = self._calculate_bardic_songs()
        self.bardic_songs_used = 0
        self.active_song = None
        self.song_duration_remaining = 0
        
        # Lore and knowledge attributes
        self.lore_bonus = self._calculate_lore_bonus()
        self.jack_of_trades_bonus = self._calculate_jack_of_trades()
        
        # Charm and social attributes
        self.charm_uses_per_day = max(1, self.level // 3)
        self.charm_uses_used = 0
        self.charm_save_dc = self._calculate_charm_dc()
        
        # Performance attributes
        self.instruments_known = self._get_starting_instruments()
        self.performance_bonus = self._calculate_performance()
        
    def get_hit_die_value(self) -> int:
        """Bards use d6 hit die (light combatant)"""
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
        """Bards attack every 3.5 seconds unarmed (moderate speed)"""
        return 3.5
        
    def get_critical_range(self) -> int:
        """Bards crit on natural 20 (standard critical)"""
        return 20
        
    def get_experience_penalty(self) -> int:
        """Bards have +15% experience penalty"""
        return 15
        
    def get_special_abilities(self) -> Dict[str, Any]:
        """Comprehensive Bard special abilities"""
        return {
            # Musical magic
            'bardic_songs': self.get_bardic_songs_remaining(),
            'active_song': self.active_song,
            'song_duration': self.song_duration_remaining,
            'inspire_courage': True,
            'inspire_competence': self.level >= 3,
            'countersong': self.level >= 2,
            'fascinate': self.level >= 1,
            'suggestion': self.level >= 6,
            
            # Knowledge and lore
            'lore_master': self.get_lore_bonus(),
            'jack_of_trades': self.get_jack_of_trades_bonus(),
            'bardic_knowledge': True,
            'identify_magic': self.level >= 2,
            'legend_lore': self.level >= 5,
            
            # Social abilities
            'charm_person': self.get_charm_uses_remaining(),
            'charm_save_dc': self.get_charm_save_dc(),
            'diplomacy_master': True,
            'gather_information': True,
            'bluff_master': self.level >= 3,
            
            # Performance
            'instruments_known': len(self.instruments_known),
            'performance_bonus': self.get_performance_bonus(),
            'versatile_performer': self.level >= 4,
            
            # Equipment proficiencies
            'light_armor_proficiency': True,
            'simple_weapon_proficiency': True,
            'instrument_proficiency': True
        }
    
    # === BARDIC SONG ABILITIES ===
    
    def _calculate_bardic_songs(self) -> int:
        """Calculate bardic songs per day"""
        base_songs = 1 + (self.level // 2)  # 1 at level 1, +1 every 2 levels
        cha_bonus = max(0, (self.stats['charisma'] - 10) // 2)
        return base_songs + cha_bonus
    
    def get_bardic_songs_per_day(self) -> int:
        """Get total bardic songs per day"""
        return self._calculate_bardic_songs()
    
    def get_bardic_songs_remaining(self) -> int:
        """Get bardic songs remaining today"""
        return max(0, self.get_bardic_songs_per_day() - self.bardic_songs_used)
    
    def can_use_bardic_song(self) -> bool:
        """Check if bard can use a bardic song"""
        return self.get_bardic_songs_remaining() > 0 and self.active_song is None
    
    def start_bardic_song(self, song_type: str) -> bool:
        """Start a bardic song"""
        if not self.can_use_bardic_song():
            return False
        
        valid_songs = self._get_available_songs()
        if song_type not in valid_songs:
            return False
        
        self.bardic_songs_used += 1
        self.active_song = song_type
        self.song_duration_remaining = self._get_song_duration(song_type)
        return True
    
    def _get_available_songs(self) -> List[str]:
        """Get list of available bardic songs"""
        songs = ['inspire_courage', 'fascinate']
        if self.level >= 2:
            songs.append('countersong')
        if self.level >= 3:
            songs.append('inspire_competence')
        if self.level >= 6:
            songs.append('suggestion')
        if self.level >= 9:
            songs.append('inspire_greatness')
        if self.level >= 12:
            songs.append('song_of_freedom')
        if self.level >= 15:
            songs.append('inspire_heroics')
        return songs
    
    def _get_song_duration(self, song_type: str) -> int:
        """Get duration in rounds for bardic song"""
        base_duration = 5 + self.level  # 5 + level rounds
        return base_duration
    
    def get_inspire_courage_bonus(self) -> int:
        """Get inspire courage bonus"""
        base_bonus = 1
        if self.level >= 8:
            base_bonus = 2
        if self.level >= 14:
            base_bonus = 3
        return base_bonus
    
    def get_inspire_competence_bonus(self) -> int:
        """Get inspire competence bonus"""
        return 2 + (self.level // 6)  # +2 base, +1 every 6 levels
    
    def can_use_countersong(self) -> bool:
        """Check if bard can use countersong"""
        return self.level >= 2
    
    def countersong_save_bonus(self) -> int:
        """Get save bonus from countersong"""
        return 4  # +4 bonus to saves vs sonic/language-dependent effects
    
    # === LORE AND KNOWLEDGE ABILITIES ===
    
    def _calculate_lore_bonus(self) -> int:
        """Calculate bardic lore bonus"""
        base_bonus = self.level
        int_bonus = (self.stats['intelligence'] - 10) // 2
        return base_bonus + int_bonus
    
    def get_lore_bonus(self) -> int:
        """Get current lore bonus"""
        return self._calculate_lore_bonus()
    
    def _calculate_jack_of_trades(self) -> int:
        """Calculate jack of all trades bonus"""
        return max(1, self.level // 4)  # +1 every 4 levels, minimum 1
    
    def get_jack_of_trades_bonus(self) -> int:
        """Get jack of all trades bonus"""
        return self._calculate_jack_of_trades()
    
    def attempt_lore_check(self, difficulty: int = 15) -> bool:
        """Attempt a bardic lore check"""
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            lore_roll = dice.roll("1d20") + self.get_lore_bonus()
            return lore_roll >= difficulty
        except ImportError:
            import random
            return random.randint(1, 20) + self.get_lore_bonus() >= difficulty
    
    def identify_creature(self, creature_type: str) -> Dict[str, Any]:
        """Attempt to identify a creature using bardic knowledge"""
        if self.attempt_lore_check(15):
            return {
                'identified': True,
                'creature_type': creature_type,
                'special_abilities': f"Known abilities of {creature_type}",
                'weaknesses': f"Known weaknesses of {creature_type}",
                'resistances': f"Known resistances of {creature_type}"
            }
        return {'identified': False}
    
    def identify_magic_item(self, item) -> Dict[str, Any]:
        """Attempt to identify a magic item"""
        if self.level < 2:
            return {'identified': False, 'reason': 'Level too low'}
        
        if self.attempt_lore_check(12):
            return {
                'identified': True,
                'item_type': getattr(item, 'item_type', 'unknown'),
                'magical_properties': getattr(item, 'magical_properties', 'unknown'),
                'command_words': getattr(item, 'command_words', 'none')
            }
        return {'identified': False}
    
    # === CHARM AND SOCIAL ABILITIES ===
    
    def _calculate_charm_dc(self) -> int:
        """Calculate save DC for charm abilities"""
        base_dc = 10
        cha_bonus = (self.stats['charisma'] - 10) // 2
        level_bonus = self.level // 2
        return base_dc + cha_bonus + level_bonus
    
    def get_charm_save_dc(self) -> int:
        """Get save DC for charm abilities"""
        return self._calculate_charm_dc()
    
    def get_charm_uses_remaining(self) -> int:
        """Get charm uses remaining today"""
        return max(0, self.charm_uses_per_day - self.charm_uses_used)
    
    def can_use_charm(self) -> bool:
        """Check if bard can use charm abilities"""
        return self.get_charm_uses_remaining() > 0
    
    def attempt_charm_person(self, target_level: int = 1) -> bool:
        """Attempt to charm a person"""
        if not self.can_use_charm():
            return False
        
        self.charm_uses_used += 1
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            # Target rolls Will save vs charm DC
            will_save = dice.roll("1d20") + target_level
            return will_save < self.get_charm_save_dc()
        except ImportError:
            import random
            will_save = random.randint(1, 20) + target_level
            return will_save < self.get_charm_save_dc()
    
    def get_diplomacy_bonus(self) -> int:
        """Get diplomacy skill bonus"""
        base_bonus = 3
        cha_bonus = (self.stats['charisma'] - 10) // 2
        level_bonus = self.level // 2
        return base_bonus + cha_bonus + level_bonus
    
    def attempt_diplomacy(self, difficulty: int = 15) -> bool:
        """Attempt a diplomacy check"""
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            diplomacy_roll = dice.roll("1d20") + self.get_diplomacy_bonus()
            return diplomacy_roll >= difficulty
        except ImportError:
            import random
            return random.randint(1, 20) + self.get_diplomacy_bonus() >= difficulty
    
    # === PERFORMANCE ABILITIES ===
    
    def _get_starting_instruments(self) -> List[str]:
        """Get starting musical instruments"""
        return ['lute', 'flute']  # Starting instruments
    
    def _calculate_performance(self) -> int:
        """Calculate performance skill bonus"""
        base_bonus = 3
        cha_bonus = (self.stats['charisma'] - 10) // 2
        level_bonus = self.level
        return base_bonus + cha_bonus + level_bonus
    
    def get_performance_bonus(self) -> int:
        """Get performance skill bonus"""
        return self._calculate_performance()
    
    def learn_instrument(self, instrument: str) -> bool:
        """Learn a new instrument"""
        if instrument not in self.instruments_known:
            self.instruments_known.append(instrument)
            return True
        return False
    
    def can_use_instrument(self, instrument: str) -> bool:
        """Check if bard can use an instrument"""
        return instrument in self.instruments_known
    
    # === EQUIPMENT RESTRICTIONS ===
    
    def can_use_weapon(self, weapon) -> bool:
        """Bards can use simple and light weapons"""
        if hasattr(weapon, 'weapon_category'):
            return weapon.weapon_category.lower() in ['simple', 'light']
        if hasattr(weapon, 'weapon_type'):
            allowed_types = ['sword', 'dagger', 'staff', 'club', 'crossbow', 'bow']
            return weapon.weapon_type.lower() in allowed_types
        return True  # Default allow for basic weapons
    
    def can_use_armor(self, armor) -> bool:
        """Bards can use light armor, medium at higher levels"""
        if hasattr(armor, 'armor_type'):
            allowed_types = ['light', 'leather', 'cloth']
            if self.level >= 8:
                allowed_types.append('medium')  # Medium armor at level 8+
            return armor.armor_type.lower() in allowed_types
        return True  # Default allow for basic armor
    
    def calculate_derived_stats(self):
        """Override to use CHA for some spell-like abilities"""
        super().calculate_derived_stats()
        
        # Update spell-like ability DCs based on charisma
        self.charm_save_dc = self._calculate_charm_dc()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Bard':
        """Create Bard from save data"""
        race_id = data.get('race_id', 'human')
        
        # Load alignment from save data or default to neutral
        alignment = Alignment.NEUTRAL
        if 'alignment_data' in data:
            alignment_name = data['alignment_data'].get('alignment', 'NEUTRAL')
            alignment = getattr(Alignment, alignment_name, Alignment.NEUTRAL)
        
        bard = cls(data['character_name'], race_id, alignment)
        
        # Restore basic character data
        bard.level = data['level']
        bard.experience = data['experience']
        bard.base_stats = data.get('base_stats', bard.base_stats)
        bard.stats = data['stats']
        
        # Restore derived stats
        derived = data['derived_stats']
        bard.max_hp = derived['max_hp']
        bard.current_hp = derived['current_hp']
        bard.armor_class = derived['armor_class']
        bard.base_attack_bonus = derived['base_attack_bonus']
        
        # Restore location
        location = data['current_location']
        bard.current_area = location.get('area_id')
        bard.current_room = location.get('room_id')
        
        # Initialize item systems
        bard.initialize_item_systems()
        
        # Restore inventory and equipment data
        if 'inventory' in data:
            bard.inventory_system.from_dict(data['inventory'])
        if 'equipment' in data:
            bard.equipment_system.from_dict(data['equipment'])
        
        # Restore character creation state
        bard.unallocated_stats = data.get('unallocated_stats', 0)
        bard.creation_complete = data.get('creation_complete', True)
        
        # Load alignment data
        if 'alignment_data' in data:
            bard.load_alignment_data(data['alignment_data'])
        
        # Restore bard-specific attributes
        bard_data = data.get('bard_data', {})
        bard.bardic_songs_used = bard_data.get('bardic_songs_used', 0)
        bard.charm_uses_used = bard_data.get('charm_uses_used', 0)
        bard.instruments_known = bard_data.get('instruments_known', ['lute', 'flute'])
        bard.active_song = bard_data.get('active_song')
        bard.song_duration_remaining = bard_data.get('song_duration_remaining', 0)
        
        # Recalculate bard-specific attributes
        bard.bardic_songs_per_day = bard._calculate_bardic_songs()
        bard.lore_bonus = bard._calculate_lore_bonus()
        bard.jack_of_trades_bonus = bard._calculate_jack_of_trades()
        bard.charm_uses_per_day = max(1, bard.level // 3)
        bard.charm_save_dc = bard._calculate_charm_dc()
        bard.performance_bonus = bard._calculate_performance()
        
        return bard
    
    def to_dict(self) -> Dict[str, Any]:
        """Override to include bard-specific data"""
        data = super().to_dict()
        data['bard_data'] = {
            'bardic_songs_used': self.bardic_songs_used,
            'charm_uses_used': self.charm_uses_used,
            'instruments_known': self.instruments_known,
            'active_song': self.active_song,
            'song_duration_remaining': self.song_duration_remaining
        }
        return data
        
    def __str__(self) -> str:
        """String representation of Bard"""
        abilities = []
        
        # Bardic songs
        songs_remaining = self.get_bardic_songs_remaining()
        abilities.append(f"Songs {songs_remaining}")
        
        # Active song
        if self.active_song:
            abilities.append(f"{self.active_song.title()} ({self.song_duration_remaining})")
        
        # Lore bonus
        lore = self.get_lore_bonus()
        abilities.append(f"Lore +{lore}")
        
        # Jack of trades
        jack = self.get_jack_of_trades_bonus()
        abilities.append(f"Jack +{jack}")
        
        # Charm uses
        charm_remaining = self.get_charm_uses_remaining()
        if charm_remaining > 0:
            abilities.append(f"Charm {charm_remaining}")
        
        # Performance
        performance = self.get_performance_bonus()
        abilities.append(f"Perform +{performance}")
        
        # Instruments
        instruments = len(self.instruments_known)
        abilities.append(f"{instruments} Instruments")
            
        base_str = super().__str__()
        if abilities:
            base_str += f" [{', '.join(abilities)}]"
        return base_str