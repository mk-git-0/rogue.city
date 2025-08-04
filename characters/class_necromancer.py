"""
Necromancer Character Class for Rogue City
Traditional MajorMUD master of death, undead, and dark magic with minion control.
"""

from .base_character import BaseCharacter
from core.alignment_system import Alignment
from typing import Dict, Any, Tuple, List


class Necromancer(BaseCharacter):
    """
    Necromancer class - Master of death, undead, and dark magic
    
    DEATH MAGIC MASTER - Expert progression, extremely powerful but socially restricted
    
    Experience Penalty: +65% (extremely powerful but socially restricted)
    Alignment Preference: Evil preferred (Good prohibited, Neutral difficult)
    Stat Modifiers: +3 INT, +2 WIS, +1 CHA, -3 STR, -2 DEX, -1 CON
    Hit Die: d4 (lowest HP, must rely on minions and magic)
    Attack Speed: 4.0 seconds (slow combat, focuses on magic)
    Critical Range: 20 (standard critical chance)
    
    DEATH MASTERY CORE:
    - Animate dead to create skeleton and zombie minions
    - Death magic including life drain, fear, curses, and instant death
    - Speak with dead to communicate with deceased spirits
    - Undead control to command existing undead creatures
    - Life drain to steal HP from enemies and heal self
    - Death immunity providing resistance to death effects and level drain
    
    NECROMANCER ABILITIES:
    - Animate Dead: Create skeleton and zombie minions
    - Death Magic: Life drain, fear, curses, instant death spells
    - Speak with Dead: Communicate with deceased spirits
    - Undead Control: Command existing undead creatures
    - Life Drain: Steal HP from enemies to heal self
    - Death Immunity: Resistance to death effects and level drain
    
    EQUIPMENT ACCESS:
    - Weapons: Simple weapons, focuses on spell damage
    - Armor: Robes and dark clothing, bone/obsidian items
    - Magic: Full access to necromantic magical items
    - Accessories: Necromantic focuses, bone items, dark talismans
    
    ALIGNMENT RESTRICTIONS:
    - Evil alignment preferred for full power
    - Good alignment prohibited (loses most abilities)
    - Neutral alignment possible but with significant penalties
    - Dark reputation affects NPC reactions and quest availability
    """
    
    def __init__(self, name: str, race_id: str = "human", alignment: Alignment = Alignment.EVIL):
        """Initialize Necromancer character with death magic and minion systems"""
        super().__init__(name, 'necromancer', race_id, alignment)
        
        # Death magic spellcasting (full caster)
        self.necromancer_caster_level = self.level
        self.death_spells_per_day = self._calculate_death_spells()
        self.death_spells_used = {}  # Track by spell level
        self.spell_save_dc = self._calculate_spell_save_dc()
        
        # Undead minion system
        self.max_undead_minions = self._calculate_max_minions()
        self.active_minions = []  # List of active minions
        self.minion_control_range = 100 + (self.level * 10)  # Feet
        self.permanent_minions = self.level >= 12
        
        # Life drain and death touch
        self.life_drain_uses_per_day = max(3, self.level // 2)
        self.life_drain_uses_used = 0
        self.life_drain_range = 30  # Feet
        self.death_touch = self.level >= 8
        
        # Speak with dead and spirit communication
        self.speak_with_dead_uses = max(1, self.level // 3)
        self.speak_with_dead_used = 0
        self.spirit_sight = self.level >= 4
        self.commune_with_dead = self.level >= 10
        
        # Undead control abilities
        self.undead_control_uses = max(2, self.level // 4)
        self.undead_control_used = 0
        self.control_duration = self.level * 10  # Minutes
        self.mass_control = self.level >= 16
        
        # Death immunities and resistances
        self.death_immunity_level = self._calculate_death_immunity()
        self.negative_energy_affinity = self.level >= 6
        self.level_drain_resistance = max(0, self.level // 5)
        
        # Fear and intimidation
        self.fear_aura_range = 15 + self.level  # Feet
        self.intimidation_bonus = self._calculate_intimidation()
        self.cause_fear = True
        self.mass_fear = self.level >= 12
        
        # Alignment penalties for non-evil
        self.alignment_penalty = self._calculate_alignment_penalty()
        
    def get_hit_die_value(self) -> int:
        """Necromancers use d4 hit die (lowest HP, glass cannon)"""
        return 4
        
    def get_hit_die_type(self) -> str:
        """Return dice notation for hit die"""
        return "1d4"
        
    def get_attack_speed(self) -> float:
        """Return attack speed in seconds (considering equipped weapon)"""
        if hasattr(self, 'equipment_system') and self.equipment_system:
            return self.equipment_system.get_attack_speed_modifier()
        return self.get_base_attack_speed()
    
    def get_base_attack_speed(self) -> float:
        """Necromancers attack every 4 seconds unarmed (slow, focuses on magic)"""
        return 4.0
        
    def get_critical_range(self) -> int:
        """Necromancers crit on natural 20 (standard critical)"""
        return 20
        
    def get_experience_penalty(self) -> int:
        """Necromancers have +65% experience penalty"""
        return 65
        
    def get_special_abilities(self) -> Dict[str, Any]:
        """Comprehensive Necromancer special abilities"""
        # Alignment restrictions affect abilities
        alignment_factor = 1.0
        if self.get_alignment() == Alignment.GOOD:
            return {
                'forbidden_necromancy': True,
                'abilities_lost': 'Good alignment prohibits necromantic magic',
                'basic_spellcasting_only': True
            }
        elif self.get_alignment() == Alignment.NEUTRAL:
            alignment_factor = 0.75  # 25% penalty for neutral
        
        return {
            # Death magic spellcasting
            'necromancer_caster_level': self.necromancer_caster_level,
            'death_spells_per_day': self.get_death_spells_per_day(),
            'spell_save_dc': self.get_spell_save_dc(),
            'death_magic_mastery': True,
            'spell_penetration': self.level // 4,
            
            # Undead minion control
            'max_undead_minions': int(self.get_max_undead_minions() * alignment_factor),
            'active_minions': len(self.active_minions),
            'minion_control_range': self.minion_control_range,
            'permanent_minions': self.permanent_minions and self.get_alignment() == Alignment.EVIL,
            'create_greater_undead': self.level >= 15,
            
            # Life drain and death touch
            'life_drain': self.get_life_drain_remaining(),
            'life_drain_range': self.life_drain_range,
            'death_touch': self.death_touch and self.get_alignment() != Alignment.GOOD,
            'energy_drain': self.level >= 12,
            'soul_trap': self.level >= 18,
            
            # Spirit communication
            'speak_with_dead': self.get_speak_with_dead_remaining(),
            'spirit_sight': self.spirit_sight,
            'commune_with_dead': self.commune_with_dead,
            'ghost_form': self.level >= 20,
            
            # Undead control
            'undead_control': self.get_undead_control_remaining(),
            'control_duration': int(self.control_duration * alignment_factor),
            'mass_control': self.mass_control and self.get_alignment() == Alignment.EVIL,
            'undead_mastery': self.level >= 14,
            
            # Death immunities
            'death_immunity_level': int(self.get_death_immunity_level() * alignment_factor),
            'negative_energy_affinity': self.negative_energy_affinity,
            'level_drain_resistance': self.level_drain_resistance,
            'poison_immunity': self.level >= 9,
            'disease_immunity': self.level >= 9,
            
            # Fear and intimidation
            'fear_aura_range': self.fear_aura_range,
            'intimidation_master': self.get_intimidation_bonus(),
            'cause_fear': self.cause_fear,
            'mass_fear': self.mass_fear,
            'terrifying_presence': self.level >= 16,
            
            # Alignment penalties
            'alignment_penalty': self.alignment_penalty,
            'social_stigma': True,
            'npc_fear_reaction': True,
            
            # Equipment proficiencies  
            'simple_weapon_proficiency': True,
            'necromantic_item_mastery': True,
            'bone_weapon_proficiency': True,
            'dark_magic_focus': True
        }
    
    # === DEATH MAGIC SPELLCASTING ===
    
    def _calculate_death_spells(self) -> Dict[int, int]:
        """Calculate death magic spells per day (full caster like wizard)"""
        if self.necromancer_caster_level < 1:
            return {}
        
        # Full caster progression
        spell_progression = {
            1: {1: 3}, 2: {1: 4}, 3: {1: 4, 2: 2}, 4: {1: 5, 2: 3},
            5: {1: 5, 2: 3, 3: 2}, 6: {1: 5, 2: 4, 3: 3},
            7: {1: 6, 2: 4, 3: 3, 4: 1}, 8: {1: 6, 2: 4, 3: 4, 4: 2},
            9: {1: 6, 2: 5, 3: 4, 4: 3, 5: 1}, 10: {1: 6, 2: 5, 3: 4, 4: 3, 5: 2},
            11: {1: 6, 2: 5, 3: 5, 4: 4, 5: 3, 6: 1}, 12: {1: 6, 2: 5, 3: 5, 4: 4, 5: 3, 6: 2},
            13: {1: 6, 2: 5, 3: 5, 4: 4, 5: 4, 6: 3, 7: 1}, 14: {1: 6, 2: 5, 3: 5, 4: 4, 5: 4, 6: 3, 7: 2},
            15: {1: 6, 2: 5, 3: 5, 4: 4, 5: 4, 6: 4, 7: 3, 8: 1}, 16: {1: 6, 2: 5, 3: 5, 4: 4, 5: 4, 6: 4, 7: 3, 8: 2},
            17: {1: 6, 2: 5, 3: 5, 4: 4, 5: 4, 6: 4, 7: 4, 8: 3, 9: 1}, 18: {1: 6, 2: 5, 3: 5, 4: 4, 5: 4, 6: 4, 7: 4, 8: 3, 9: 2},
            19: {1: 6, 2: 5, 3: 5, 4: 4, 5: 4, 6: 4, 7: 4, 8: 4, 9: 3}, 20: {1: 6, 2: 5, 3: 5, 4: 4, 5: 4, 6: 4, 7: 4, 8: 4, 9: 4}
        }
        
        base_spells = spell_progression.get(min(self.necromancer_caster_level, 20), {})
        
        # Add intelligence bonus spells
        int_bonus = max(0, (self.stats['intelligence'] - 10) // 2)
        final_spells = base_spells.copy()
        
        for spell_level in range(1, 10):
            if spell_level in final_spells:
                bonus = 0
                if int_bonus >= spell_level:
                    bonus = 1 + (int_bonus - spell_level) // 4
                final_spells[spell_level] += bonus
        
        # Apply alignment penalty for non-evil
        if self.get_alignment() != Alignment.EVIL:
            for spell_level in final_spells:
                final_spells[spell_level] = max(1, int(final_spells[spell_level] * 0.75))
        
        return final_spells
    
    def get_death_spells_per_day(self) -> Dict[int, int]:
        """Get death magic spells per day"""
        return self._calculate_death_spells()
    
    def _calculate_spell_save_dc(self) -> int:
        """Calculate spell save DC"""
        base_dc = 10
        int_bonus = max(0, (self.stats['intelligence'] - 10) // 2)
        evil_bonus = 1 if self.get_alignment() == Alignment.EVIL else 0
        return base_dc + int_bonus + evil_bonus
    
    def get_spell_save_dc(self, spell_level: int = 1) -> int:
        """Get spell save DC for given spell level"""
        return self._calculate_spell_save_dc() + spell_level
    
    def get_death_spells_remaining(self, spell_level: int) -> int:
        """Get death spells remaining for given level"""
        per_day = self.get_death_spells_per_day().get(spell_level, 0)
        used = self.death_spells_used.get(spell_level, 0)
        return max(0, per_day - used)
    
    def can_cast_death_spell(self, spell_level: int) -> bool:
        """Check if necromancer can cast death spell of given level"""
        if self.get_alignment() == Alignment.GOOD:
            return False
        return self.get_death_spells_remaining(spell_level) > 0
    
    def cast_death_spell(self, spell_name: str, spell_level: int, target=None) -> Dict[str, Any]:
        """Cast a necromantic spell"""
        if not self.can_cast_death_spell(spell_level):
            return {'success': False, 'reason': f'No level {spell_level} spells remaining'}
        
        if spell_level not in self.death_spells_used:
            self.death_spells_used[spell_level] = 0
        self.death_spells_used[spell_level] += 1
        
        # Comprehensive necromantic spell list
        spell_effects = {
            # Level 1
            'chill_touch': {'damage': 6 + self.level, 'strength_damage': 1, 'undead_fear': True},
            'cause_fear': {'fear': True, 'duration': 60, 'single_target': True},
            'detect_undead': {'range': 100, 'duration': 600, 'sense_undead': True},
            'ray_of_enfeeblement': {'strength_drain': 4 + self.level//2, 'duration': 60},
            
            # Level 2
            'ghoul_touch': {'paralysis': True, 'duration': 30, 'stench': True},
            'death_knell': {'instant_kill': True, 'hp_gain': 8, 'temp_stats': True},
            'command_undead': {'control_undead': True, 'duration': 600, 'intelligent': False},
            'false_life': {'temp_hp': 8 + self.level, 'duration': 3600},
            
            # Level 3
            'animate_dead': {'create_undead': True, 'hd_limit': self.level * 2, 'permanent': True},
            'vampiric_touch': {'damage': 12 + self.level, 'healing': 'half_damage', 'touch': True},
            'halt_undead': {'paralyze_undead': True, 'targets': 3, 'duration': 60},
            'speak_with_dead': {'communication': True, 'questions': 5, 'duration': 60},
            
            # Level 4
            'enervation': {'negative_levels': 2, 'no_save': True, 'ranged_touch': True},
            'fear': {'mass_fear': True, 'area': 30, 'duration': 60},
            'contagion': {'disease': True, 'fort_negates': True, 'touch': True},
            'bestow_curse': {'curse': True, 'permanent': True, 'various_effects': True},
            
            # Level 5
            'slay_living': {'instant_death': True, 'damage': 30 + self.level, 'fort_partial': True},
            'circle_of_death': {'mass_death': True, 'area': 40, 'hd_limit': self.level * 2},
            'waves_of_fatigue': {'fatigue': True, 'area': 30, 'no_save': True},
            'magic_jar': {'possess': True, 'duration': 3600, 'int_contest': True},
            
            # Level 6
            'create_undead': {'create_greater_undead': True, 'shadows_wights': True, 'permanent': True},
            'harm': {'damage': min(150, 10 * self.level), 'will_half': True, 'touch': True},
            'soul_bind': {'trap_soul': True, 'permanent': True, 'will_negates': True},
            'eyebite': {'various_effects': True, 'fort_negates': True, 'unlimited': True},
            
            # Level 7
            'control_undead': {'dominate_undead': True, 'intelligent': True, 'duration': 600},
            'waves_of_exhaustion': {'exhaustion': True, 'area': 60, 'no_save': True},
            'finger_of_death': {'instant_death': True, 'damage': 70 + self.level, 'fort_partial': True},
            'destruction': {'utterly_destroy': True, 'fort_negates': True, 'expensive': True},
            
            # Level 8
            'create_greater_undead': {'create_powerful_undead': True, 'spectres_wraiths': True},
            'horrid_wilting': {'mass_damage': True, 'damage': 80 + self.level, 'area': 30},
            'symbol_of_death': {'mass_instant_death': True, 'hd_limit': 150, 'will_negates': True},
            'clone': {'create_duplicate': True, 'permanent': True, 'expensive': True},
            
            # Level 9
            'wail_of_the_banshee': {'mass_death': True, 'area': 30, 'fort_negates': True},
            'energy_drain': {'negative_levels': 4, 'permanent': True, 'fort_partial': True},
            'soul_bind_greater': {'permanent_soul_trap': True, 'no_save': True},
            'astral_projection': {'travel_planes': True, 'duration': 'unlimited', 'party': True}
        }
        
        effect = spell_effects.get(spell_name, {})
        
        # Evil alignment bonus
        if self.get_alignment() == Alignment.EVIL and 'damage' in effect:
            effect['damage'] = int(effect.get('damage', 0) * 1.1)  # +10% damage
            effect['evil_bonus'] = True
        
        return {
            'success': True,
            'spell_name': spell_name,
            'spell_level': spell_level,
            'effect': effect,
            'save_dc': self.get_spell_save_dc(spell_level),
            'remaining_spells': self.get_death_spells_remaining(spell_level)
        }
    
    # === UNDEAD MINION SYSTEM ===
    
    def _calculate_max_minions(self) -> int:
        """Calculate maximum undead minions"""
        base_minions = 1 + (self.level // 3)  # 1 at level 1, +1 every 3 levels
        cha_bonus = max(0, (self.stats['charisma'] - 10) // 4)
        return base_minions + cha_bonus
    
    def get_max_undead_minions(self) -> int:
        """Get maximum undead minions"""
        return self._calculate_max_minions()
    
    def can_animate_dead(self) -> bool:
        """Check if necromancer can animate dead"""
        if self.get_alignment() == Alignment.GOOD:
            return False
        return len(self.active_minions) < self.get_max_undead_minions()
    
    def animate_dead(self, corpse_type: str = "skeleton", hd: int = 1) -> Dict[str, Any]:
        """Animate dead to create undead minions"""
        if not self.can_animate_dead():
            return {'success': False, 'reason': 'Maximum minions reached or alignment prohibits'}
        
        if not self.can_cast_death_spell(3):  # Animate Dead is 3rd level
            return {'success': False, 'reason': 'No 3rd level spells remaining'}
        
        # Use spell slot
        self.cast_death_spell('animate_dead', 3)
        
        # Create minion
        minion_types = {
            'skeleton': {'hp': 8 + hd * 6, 'damage': '1d6', 'ac': 13, 'special': ['undead_traits']},
            'zombie': {'hp': 15 + hd * 8, 'damage': '1d8', 'ac': 11, 'special': ['undead_traits', 'tough']},
            'wight': {'hp': 25 + hd * 8, 'damage': '2d6', 'ac': 15, 'special': ['energy_drain', 'undead_traits']},
            'wraith': {'hp': 35 + hd * 8, 'damage': '2d8', 'ac': 17, 'special': ['incorporeal', 'energy_drain']},
            'spectre': {'hp': 50 + hd * 10, 'damage': '3d6', 'ac': 19, 'special': ['incorporeal', 'level_drain']},
            'death_knight': {'hp': 75 + hd * 12, 'damage': '4d6', 'ac': 21, 'special': ['spells', 'aura_of_despair']}
        }
        
        # Level restrictions on minion types
        available_types = ['skeleton', 'zombie']
        if self.level >= 7:
            available_types.append('wight')
        if self.level >= 10:
            available_types.append('wraith')
        if self.level >= 13:
            available_types.append('spectre')
        if self.level >= 16:
            available_types.append('death_knight')
        
        if corpse_type not in available_types:
            corpse_type = 'skeleton'
        
        minion_data = minion_types[corpse_type]
        minion = {
            'type': corpse_type,
            'hd': hd,
            'hp': minion_data['hp'],
            'max_hp': minion_data['hp'],
            'damage': minion_data['damage'],
            'ac': minion_data['ac'],
            'special_abilities': minion_data['special'],
            'controlled': True,
            'permanent': self.permanent_minions or self.get_alignment() == Alignment.EVIL
        }
        
        self.active_minions.append(minion)
        
        return {
            'success': True,
            'minion_type': corpse_type,
            'minion_data': minion,
            'permanent': minion['permanent'],
            'active_minions': len(self.active_minions),
            'max_minions': self.get_max_undead_minions()
        }
    
    def dismiss_minion(self, minion_index: int) -> bool:
        """Dismiss an undead minion"""
        if 0 <= minion_index < len(self.active_minions):
            dismissed = self.active_minions.pop(minion_index)
            return True
        return False
    
    def get_minion_status(self) -> List[Dict[str, Any]]:
        """Get status of all active minions"""
        return [
            {
                'index': i,
                'type': minion['type'],
                'hp': f"{minion['hp']}/{minion['max_hp']}",
                'controlled': minion['controlled'],
                'permanent': minion['permanent']
            }
            for i, minion in enumerate(self.active_minions)
        ]
    
    # === LIFE DRAIN AND DEATH TOUCH ===
    
    def get_life_drain_remaining(self) -> int:
        """Get life drain uses remaining"""
        return max(0, self.life_drain_uses_per_day - self.life_drain_uses_used)
    
    def can_life_drain(self) -> bool:
        """Check if necromancer can use life drain"""
        if self.get_alignment() == Alignment.GOOD:
            return False
        return self.get_life_drain_remaining() > 0
    
    def use_life_drain(self, target=None, distance: int = 30) -> Dict[str, Any]:
        """Use life drain ability"""
        if not self.can_life_drain():
            return {'success': False, 'reason': 'No life drain uses remaining'}
        
        if distance > self.life_drain_range:
            return {'success': False, 'reason': f'Target too far (max {self.life_drain_range} feet)'}
        
        self.life_drain_uses_used += 1
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            drain_amount = dice.roll("2d6") + self.level
            
            # Evil alignment bonus
            if self.get_alignment() == Alignment.EVIL:
                drain_amount = int(drain_amount * 1.2)
            
            # Heal self for half the drained amount
            healing = drain_amount // 2
            self.heal(healing)
            
            return {
                'success': True,
                'damage_dealt': drain_amount,
                'healing_received': healing,
                'target': target.name if target else 'unknown',
                'remaining_uses': self.get_life_drain_remaining()
            }
        except ImportError:
            import random
            drain_amount = random.randint(2, 12) + self.level
            healing = drain_amount // 2
            self.heal(healing)
            return {
                'success': True,
                'damage_dealt': drain_amount,
                'healing_received': healing,
                'remaining_uses': self.get_life_drain_remaining()
            }
    
    def can_death_touch(self) -> bool:
        """Check if necromancer can use death touch"""
        return self.death_touch and self.get_alignment() != Alignment.GOOD
    
    def attempt_death_touch(self, target_level: int = 1) -> Dict[str, Any]:
        """Attempt death touch attack"""
        if not self.can_death_touch():
            return {'success': False, 'reason': 'Death touch not available'}
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            death_roll = dice.roll("1d20") + self.level
            dc = 15 + target_level
            success = death_roll >= dc
            
            # Bonus for evil alignment
            if self.get_alignment() == Alignment.EVIL:
                death_roll += 2
                success = death_roll >= dc
            
            return {
                'success': success,
                'death_roll': death_roll,
                'dc': dc,
                'instant_death': success,
                'negative_levels': 2 if not success else 0  # Apply negative levels if fails
            }
        except ImportError:
            import random
            success = random.randint(1, 20) + self.level >= (15 + target_level)
            return {'success': success, 'instant_death': success}
    
    # === SPEAK WITH DEAD AND SPIRIT COMMUNICATION ===
    
    def get_speak_with_dead_remaining(self) -> int:
        """Get speak with dead uses remaining"""
        return max(0, self.speak_with_dead_uses - self.speak_with_dead_used)
    
    def can_speak_with_dead(self) -> bool:
        """Check if necromancer can speak with dead"""
        return self.get_speak_with_dead_remaining() > 0
    
    def speak_with_dead(self, corpse_age_days: int = 1) -> Dict[str, Any]:
        """Speak with a dead creature"""
        if not self.can_speak_with_dead():
            return {'success': False, 'reason': 'No speak with dead uses remaining'}
        
        # Time limit based on level
        max_age = self.level * 7  # Days
        if corpse_age_days > max_age:
            return {'success': False, 'reason': f'Corpse too old (max {max_age} days)'}
        
        self.speak_with_dead_used += 1
        
        questions_allowed = 3 + (self.level // 5)
        duration_minutes = 10 + self.level
        
        return {
            'success': True,
            'questions_allowed': questions_allowed,
            'duration_minutes': duration_minutes,
            'corpse_age_days': corpse_age_days,
            'truthful_answers': True,
            'remaining_uses': self.get_speak_with_dead_remaining()
        }
    
    def has_spirit_sight(self) -> bool:
        """Check if necromancer has spirit sight"""
        return self.spirit_sight
    
    def can_commune_with_dead(self) -> bool:
        """Check if necromancer can commune with dead"""
        return self.commune_with_dead
    
    # === UNDEAD CONTROL ===
    
    def get_undead_control_remaining(self) -> int:
        """Get undead control uses remaining"""
        return max(0, self.undead_control_uses - self.undead_control_used)
    
    def can_control_undead(self) -> bool:
        """Check if necromancer can control undead"""
        return self.get_undead_control_remaining() > 0
    
    def attempt_undead_control(self, undead_hd: int = 1, intelligent: bool = False) -> Dict[str, Any]:
        """Attempt to control existing undead"""
        if not self.can_control_undead():
            return {'success': False, 'reason': 'No undead control uses remaining'}
        
        self.undead_control_used += 1
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            control_roll = dice.roll("1d20") + self.level
            
            # Base DC varies by undead type
            base_dc = 10 + undead_hd
            if intelligent:
                base_dc += 5  # Intelligent undead resist more
            
            # Evil alignment bonus
            if self.get_alignment() == Alignment.EVIL:
                control_roll += 3
            
            success = control_roll >= base_dc
            
            return {
                'success': success,
                'control_roll': control_roll,
                'base_dc': base_dc,
                'duration_minutes': self.control_duration if success else 0,
                'permanent_control': success and self.level >= 15 and not intelligent,
                'remaining_uses': self.get_undead_control_remaining()
            }
        except ImportError:
            import random
            success = random.randint(1, 20) + self.level >= (10 + undead_hd)
            return {
                'success': success,
                'duration_minutes': self.control_duration if success else 0,
                'remaining_uses': self.get_undead_control_remaining()
            }
    
    def can_mass_control(self) -> bool:
        """Check if necromancer can use mass undead control"""
        return self.mass_control and self.get_alignment() == Alignment.EVIL
    
    # === DEATH IMMUNITIES AND RESISTANCES ===
    
    def _calculate_death_immunity(self) -> int:
        """Calculate death immunity level"""
        base_immunity = self.level // 4  # +1 every 4 levels
        evil_bonus = 2 if self.get_alignment() == Alignment.EVIL else 0
        return base_immunity + evil_bonus
    
    def get_death_immunity_level(self) -> int:
        """Get death immunity level"""
        return self._calculate_death_immunity()
    
    def is_immune_to_death_effect(self, effect_level: int) -> bool:
        """Check immunity to death effects"""
        return self.get_death_immunity_level() >= effect_level
    
    def has_negative_energy_affinity(self) -> bool:
        """Check if necromancer has negative energy affinity"""
        return self.negative_energy_affinity
    
    def get_level_drain_resistance(self) -> int:
        """Get resistance to level drain"""
        return self.level_drain_resistance
    
    # === ALIGNMENT PENALTIES ===
    
    def _calculate_alignment_penalty(self) -> int:
        """Calculate penalty for non-evil alignment"""
        if self.get_alignment() == Alignment.EVIL:
            return 0
        elif self.get_alignment() == Alignment.NEUTRAL:
            return -2  # -2 to spell DCs and ability checks
        else:  # Good
            return -10  # Severe penalty, most abilities disabled
    
    def _calculate_intimidation(self) -> int:
        """Calculate intimidation bonus"""
        base_bonus = 4
        cha_bonus = max(0, (self.stats['charisma'] - 10) // 2)
        level_bonus = self.level // 2
        evil_bonus = 2 if self.get_alignment() == Alignment.EVIL else 0
        return base_bonus + cha_bonus + level_bonus + evil_bonus
    
    def get_intimidation_bonus(self) -> int:
        """Get intimidation bonus"""
        return self._calculate_intimidation()
    
    def has_fear_aura(self) -> bool:
        """Check if necromancer has fear aura"""
        return self.level >= 8
    
    def fear_aura_effect(self, target_level: int = 1) -> Dict[str, Any]:
        """Apply fear aura effect"""
        if not self.has_fear_aura():
            return {'success': False, 'reason': 'No fear aura'}
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            fear_roll = dice.roll("1d20") + self.get_intimidation_bonus()
            dc = 12 + target_level
            success = fear_roll >= dc
            
            return {
                'success': success,
                'fear_roll': fear_roll,
                'dc': dc,
                'effect': 'frightened' if success else 'unaffected',
                'duration_rounds': 5 + self.level if success else 0,
                'aura_range': self.fear_aura_range
            }
        except ImportError:
            import random
            success = random.randint(1, 20) + self.get_intimidation_bonus() >= (12 + target_level)
            return {'success': success, 'effect': 'frightened' if success else 'unaffected'}
    
    # === EQUIPMENT RESTRICTIONS ===
    
    def can_use_weapon(self, weapon) -> bool:
        """Necromancers can use simple weapons and bone/obsidian items"""
        if hasattr(weapon, 'weapon_category'):
            return weapon.weapon_category.lower() in ['simple', 'necromantic']
        if hasattr(weapon, 'material'):
            preferred_materials = ['bone', 'obsidian', 'metal']
            return weapon.material.lower() in preferred_materials
        return True  # Default allow for basic weapons
    
    def can_use_armor(self, armor) -> bool:
        """Necromancers can use robes and light armor"""
        if hasattr(armor, 'armor_type'):
            allowed_types = ['robes', 'light', 'cloth', 'leather']
            return armor.armor_type.lower() in allowed_types
        return True  # Default allow for basic armor
    
    def can_equip_item(self, item) -> Tuple[bool, str]:
        """Check if necromancer can equip an item"""
        # Check for holy items (forbidden for evil)
        if hasattr(item, 'alignment') and item.alignment == 'good':
            if self.get_alignment() == Alignment.EVIL:
                return False, "Evil necromancers cannot use holy items"
        
        # Necromancers get bonuses with dark/necromantic items
        if hasattr(item, 'alignment') and item.alignment in ['evil', 'necromantic', 'dark']:
            return True, "Dark item - receives necromantic blessing"
        
        if hasattr(item, 'material') and item.material.lower() in ['bone', 'obsidian']:
            return True, "Natural necromantic material - enhanced power"
        
        return True, "Equipment allowed"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Necromancer':
        """Create Necromancer from save data"""
        race_id = data.get('race_id', 'human')
        
        # Load alignment from save data or default to evil
        alignment = Alignment.EVIL
        if 'alignment_data' in data:
            alignment_name = data['alignment_data'].get('alignment', 'EVIL')
            alignment = getattr(Alignment, alignment_name, Alignment.EVIL)
        
        necromancer = cls(data['character_name'], race_id, alignment)
        
        # Restore basic character data
        necromancer.level = data['level']
        necromancer.experience = data['experience']
        necromancer.base_stats = data.get('base_stats', necromancer.base_stats)
        necromancer.stats = data['stats']
        
        # Restore derived stats
        derived = data['derived_stats']
        necromancer.max_hp = derived['max_hp']
        necromancer.current_hp = derived['current_hp']
        necromancer.armor_class = derived['armor_class']
        necromancer.base_attack_bonus = derived['base_attack_bonus']
        
        # Restore location
        location = data['current_location']
        necromancer.current_area = location.get('area_id')
        necromancer.current_room = location.get('room_id')
        
        # Initialize item systems
        necromancer.initialize_item_systems()
        
        # Restore inventory and equipment data
        if 'inventory' in data:
            necromancer.inventory_system.from_dict(data['inventory'])
        if 'equipment' in data:
            necromancer.equipment_system.from_dict(data['equipment'])
        
        # Restore character creation state
        necromancer.unallocated_stats = data.get('unallocated_stats', 0)
        necromancer.creation_complete = data.get('creation_complete', True)
        
        # Load alignment data
        if 'alignment_data' in data:
            necromancer.load_alignment_data(data['alignment_data'])
        
        # Restore necromancer-specific attributes
        necromancer_data = data.get('necromancer_data', {})
        necromancer.death_spells_used = necromancer_data.get('death_spells_used', {})
        necromancer.active_minions = necromancer_data.get('active_minions', [])
        necromancer.life_drain_uses_used = necromancer_data.get('life_drain_uses_used', 0)
        necromancer.speak_with_dead_used = necromancer_data.get('speak_with_dead_used', 0)
        necromancer.undead_control_used = necromancer_data.get('undead_control_used', 0)
        
        # Recalculate necromancer-specific attributes
        necromancer.necromancer_caster_level = necromancer.level
        necromancer.death_spells_per_day = necromancer._calculate_death_spells()
        necromancer.spell_save_dc = necromancer._calculate_spell_save_dc()
        necromancer.max_undead_minions = necromancer._calculate_max_minions()
        necromancer.minion_control_range = 100 + (necromancer.level * 10)
        necromancer.permanent_minions = necromancer.level >= 12
        necromancer.life_drain_uses_per_day = max(3, necromancer.level // 2)
        necromancer.life_drain_range = 30
        necromancer.death_touch = necromancer.level >= 8
        necromancer.speak_with_dead_uses = max(1, necromancer.level // 3)
        necromancer.spirit_sight = necromancer.level >= 4
        necromancer.commune_with_dead = necromancer.level >= 10
        necromancer.undead_control_uses = max(2, necromancer.level // 4)
        necromancer.control_duration = necromancer.level * 10
        necromancer.mass_control = necromancer.level >= 16
        necromancer.death_immunity_level = necromancer._calculate_death_immunity()
        necromancer.negative_energy_affinity = necromancer.level >= 6
        necromancer.level_drain_resistance = max(0, necromancer.level // 5)
        necromancer.fear_aura_range = 15 + necromancer.level
        necromancer.intimidation_bonus = necromancer._calculate_intimidation()
        necromancer.cause_fear = True
        necromancer.mass_fear = necromancer.level >= 12
        necromancer.alignment_penalty = necromancer._calculate_alignment_penalty()
        
        return necromancer
    
    def to_dict(self) -> Dict[str, Any]:
        """Override to include necromancer-specific data"""
        data = super().to_dict()
        data['necromancer_data'] = {
            'death_spells_used': self.death_spells_used,
            'active_minions': self.active_minions,
            'life_drain_uses_used': self.life_drain_uses_used,
            'speak_with_dead_used': self.speak_with_dead_used,
            'undead_control_used': self.undead_control_used
        }
        return data
        
    def __str__(self) -> str:
        """String representation of Necromancer"""
        # Check alignment restrictions
        if self.get_alignment() == Alignment.GOOD:
            return super().__str__() + " [FORBIDDEN NECROMANCY]"
        
        abilities = []
        
        # Alignment status
        alignment_status = {
            Alignment.EVIL: "Dark Master",
            Alignment.NEUTRAL: "Neutral (Penalized)", 
            Alignment.GOOD: "Forbidden"
        }
        if self.get_alignment() != Alignment.EVIL:
            abilities.append(alignment_status[self.get_alignment()])
        
        # Spell levels
        total_spells = sum(self.get_death_spells_per_day().values())
        max_level = max(self.get_death_spells_per_day().keys()) if self.get_death_spells_per_day() else 0
        abilities.append(f"Spells {total_spells} (L{max_level})")
        
        # Active minions
        active_minions = len(self.active_minions)
        max_minions = self.get_max_undead_minions()
        abilities.append(f"Minions {active_minions}/{max_minions}")
        
        # Life drain
        life_drain = self.get_life_drain_remaining()
        abilities.append(f"Drain {life_drain}")
        
        # Speak with dead
        speak_dead = self.get_speak_with_dead_remaining()
        if speak_dead > 0:
            abilities.append(f"Speak {speak_dead}")
        
        # Undead control
        control = self.get_undead_control_remaining()
        if control > 0:
            abilities.append(f"Control {control}")
        
        # High-level abilities
        if self.can_death_touch():
            abilities.append("Death Touch")
        if self.has_fear_aura():
            abilities.append("Fear Aura")
        if self.can_mass_control():
            abilities.append("Mass Control")
        if self.level >= 20:
            abilities.append("Ghost Form")
            
        base_str = super().__str__()
        if abilities:
            base_str += f" [{', '.join(abilities)}]"
        return base_str