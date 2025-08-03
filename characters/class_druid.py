"""
Druid Character Class for Rogue City
Traditional MajorMUD protector of nature with shapeshifting and elemental magic.
"""

from .base_character import BaseCharacter
from core.alignment_system import Alignment
from typing import Dict, Any, Tuple, List


class Druid(BaseCharacter):
    """
    Druid class - Nature's guardian with shapeshifting and elemental magic
    
    NATURE'S GUARDIAN - Slow progression, complex magic system with many abilities
    
    Experience Penalty: +45% (complex magic system with shapeshifting and many abilities)
    Alignment Restriction: Neutral only (True Neutral philosophy required)
    Stat Modifiers: +3 WIS, +2 CON, +1 CHA, -2 STR, -2 INT
    Hit Die: d8 (moderate HP progression)
    Attack Speed: 3.0 seconds (moderate combat speed)
    Critical Range: 20 (standard critical chance)
    
    NATURE MASTERY CORE:
    - Shapeshifting into animal forms (wolf, bear, eagle, etc.)
    - Full access to druidic spells for healing and nature control
    - Animal communication to speak with all natural creatures
    - Weather control to influence local weather patterns
    - Plant control to command plants and accelerate growth
    - Elemental immunity and resistance to natural damage types
    
    DRUID ABILITIES:
    - Shapeshifting: Transform into animal forms (wolf, bear, eagle)
    - Nature Magic: Full access to druidic spells
    - Animal Communication: Speak with all natural creatures
    - Weather Control: Influence local weather patterns
    - Plant Control: Command plants and accelerate growth
    - Elemental Immunity: Resistance to natural damage types
    
    EQUIPMENT RESTRICTIONS:
    - Natural materials only (no metal armor or weapons)
    - Can use leather, hide, wood, stone, bone weapons and armor
    - Cannot use manufactured metal items
    - Gains bonuses with natural magical items
    
    ALIGNMENT REQUIREMENT:
    - Must be True Neutral to maintain druidic powers
    - Loses abilities if alignment shifts away from Neutral
    - Philosophy of natural balance above all else
    """
    
    def __init__(self, name: str, race_id: str = "human", alignment: Alignment = Alignment.NEUTRAL):
        """Initialize Druid character with nature magic and shapeshifting systems"""
        # Force Neutral alignment for Druids
        if alignment != Alignment.NEUTRAL:
            alignment = Alignment.NEUTRAL
            
        super().__init__(name, 'druid', race_id, alignment)
        
        # Shapeshifting system
        self.shapeshifting_uses_per_day = max(1, self.level // 2)
        self.shapeshifting_uses_used = 0
        self.current_form = 'human'
        self.available_forms = self._get_available_forms()
        self.form_duration_remaining = 0
        
        # Nature magic system
        self.druid_spell_level = self.level  # Full caster
        self.nature_spells_per_day = self._calculate_nature_spells()
        self.nature_spells_used = {}  # Track by spell level
        self.spell_save_dc = self._calculate_spell_save_dc()
        
        # Animal communication
        self.speak_with_animals_active = False
        self.animal_friendship_uses = max(2, self.level // 3)
        self.animal_friendship_used = 0
        self.summon_nature_ally = self.level >= 5
        
        # Weather and plant control
        self.weather_control_uses = max(1, self.level // 4)
        self.weather_control_used = 0
        self.plant_control_uses = max(2, self.level // 3)
        self.plant_control_used = 0
        
        # Elemental resistances and immunities
        self.elemental_resistances = self._calculate_elemental_resistances()
        self.nature_immunity = self._calculate_nature_immunities()
        self.woodland_stride = True  # Always active
        self.trackless_step = self.level >= 3
        
        # Nature knowledge
        self.nature_lore_bonus = self._calculate_nature_lore()
        self.survival_bonus = self._calculate_survival_bonus()
        self.animal_handling_bonus = self._calculate_animal_handling()
        
    def get_hit_die_value(self) -> int:
        """Druids use d8 hit die (moderate HP progression)"""
        return 8
        
    def get_hit_die_type(self) -> str:
        """Return dice notation for hit die"""
        return "1d8"
        
    def get_attack_speed(self) -> float:
        """Return attack speed in seconds (varies by form)"""
        if self.current_form != 'human':
            form_speeds = {
                'wolf': 2.5,      # Faster in wolf form
                'bear': 3.5,      # Slower but stronger
                'eagle': 2.0,     # Very fast aerial attacks
                'panther': 2.0,   # Very fast predator
                'boar': 3.0       # Moderate speed
            }
            return form_speeds.get(self.current_form, 3.0)
        
        if hasattr(self, 'equipment_system') and self.equipment_system:
            return self.equipment_system.get_attack_speed_modifier()
        return self.get_base_attack_speed()
    
    def get_base_attack_speed(self) -> float:
        """Druids attack every 3 seconds unarmed (moderate speed)"""
        return 3.0
        
    def get_critical_range(self) -> int:
        """Druids crit on natural 20 (standard critical, varies by form)"""
        if self.current_form in ['wolf', 'panther']:
            return 19  # Predators have improved crit
        return 20
        
    def get_experience_penalty(self) -> int:
        """Druids have +45% experience penalty"""
        return 45
        
    def get_special_abilities(self) -> Dict[str, Any]:
        """Comprehensive Druid special abilities"""
        # Check if still Neutral aligned
        if self.get_alignment() != Alignment.NEUTRAL:
            return {
                'lost_nature_connection': True,
                'abilities_lost': 'All druidic abilities lost due to alignment change',
                'equipment_proficiency': True  # Still retains basic training
            }
        
        return {
            # Shapeshifting
            'shapeshifting': self.get_shapeshifting_remaining(),
            'current_form': self.current_form,
            'available_forms': self.available_forms.copy(),
            'form_duration': self.form_duration_remaining,
            'unlimited_shapeshifting': self.level >= 18,
            
            # Nature magic (full spell progression)
            'druid_spell_level': self.druid_spell_level,
            'nature_spells_per_day': self.get_nature_spells_per_day(),
            'spell_save_dc': self.get_spell_save_dc(),
            'spontaneous_summon': True,  # Can convert spells to summon spells
            'nature_spell_mastery': self.level >= 12,
            
            # Animal abilities
            'speak_with_animals': True,
            'animal_friendship': self.get_animal_friendship_remaining(),
            'summon_nature_ally': self.summon_nature_ally,
            'animal_empathy': True,
            'wild_empathy': self.level >= 1,
            
            # Weather and plant control
            'weather_control': self.get_weather_control_remaining(),
            'plant_control': self.get_plant_control_remaining(),
            'call_lightning': self.level >= 5,
            'control_winds': self.level >= 7,
            'earthquake': self.level >= 15,
            
            # Elemental resistances
            'elemental_resistances': self.elemental_resistances.copy(),
            'nature_immunities': self.nature_immunity.copy(),
            'poison_immunity': self.level >= 9,
            'disease_immunity': self.level >= 9,
            'charm_immunity': self.level >= 13,  # Immune to enchantments
            
            # Nature mastery
            'woodland_stride': self.woodland_stride,
            'trackless_step': self.trackless_step,
            'resist_nature_lure': self.level >= 4,
            'venom_immunity': self.level >= 9,
            'timeless_body': self.level >= 15,
            
            # Knowledge and survival
            'nature_lore': self.get_nature_lore_bonus(),
            'survival_master': self.get_survival_bonus(),
            'animal_handling': self.get_animal_handling_bonus(),
            'identify_plants': True,
            'predict_weather': True,
            
            # Equipment restrictions
            'no_metal_equipment': True,
            'natural_materials_only': True,
            'wooden_shield_mastery': True,
            'natural_weapon_proficiency': True
        }
    
    # === SHAPESHIFTING ABILITIES ===
    
    def get_shapeshifting_remaining(self) -> int:
        """Get shapeshifting uses remaining"""
        if self.level >= 18:
            return float('inf')  # Unlimited at level 18
        return max(0, self.shapeshifting_uses_per_day - self.shapeshifting_uses_used)
    
    def _get_available_forms(self) -> List[str]:
        """Get available animal forms"""
        forms = []
        
        # Forms unlock by level
        if self.level >= 1:
            forms.extend(['wolf', 'boar'])
        if self.level >= 3:
            forms.append('bear')
        if self.level >= 5:
            forms.extend(['panther', 'hawk'])
        if self.level >= 7:
            forms.append('eagle')
        if self.level >= 9:
            forms.extend(['dire_wolf', 'brown_bear'])
        if self.level >= 12:
            forms.extend(['elemental_small'])  # Small elementals
        if self.level >= 16:
            forms.extend(['elemental_large'])  # Large elementals
        if self.level >= 20:
            forms.extend(['dragon'])  # Ancient druids can become dragons
        
        return forms
    
    def can_shapeshift(self, form: str = None) -> bool:
        """Check if druid can shapeshift"""
        if self.get_alignment() != Alignment.NEUTRAL:
            return False
        if self.level >= 18:
            return True  # Unlimited
        if self.get_shapeshifting_remaining() <= 0:
            return False
        if form and form not in self.available_forms:
            return False
        return True
    
    def shapeshift(self, new_form: str) -> Dict[str, Any]:
        """Transform into animal form"""
        if not self.can_shapeshift(new_form):
            return {'success': False, 'reason': 'Cannot shapeshift to that form'}
        
        if new_form not in self.available_forms:
            return {'success': False, 'reason': f'Form {new_form} not available'}
        
        # Use shapeshifting charge (unless unlimited)
        if self.level < 18:
            self.shapeshifting_uses_used += 1
        
        old_form = self.current_form
        self.current_form = new_form
        
        # Set duration (hours = level)
        self.form_duration_remaining = self.level * 60  # Minutes
        
        # Apply form bonuses
        form_bonuses = self._get_form_bonuses(new_form)
        
        return {
            'success': True,
            'old_form': old_form,
            'new_form': new_form,
            'duration_minutes': self.form_duration_remaining,
            'bonuses': form_bonuses,
            'remaining_uses': self.get_shapeshifting_remaining()
        }
    
    def _get_form_bonuses(self, form: str) -> Dict[str, Any]:
        """Get stat bonuses and abilities for animal form"""
        form_data = {
            'wolf': {
                'str_bonus': 2, 'dex_bonus': 4, 'con_bonus': 2,
                'ac_bonus': 2, 'speed_bonus': 20,
                'special': ['scent', 'trip_attack', 'pack_tactics']
            },
            'bear': {
                'str_bonus': 8, 'dex_bonus': 0, 'con_bonus': 4,
                'ac_bonus': 3, 'speed_bonus': 0,
                'special': ['improved_grab', 'powerful_claws', 'intimidating_presence']
            },
            'eagle': {
                'str_bonus': -4, 'dex_bonus': 6, 'con_bonus': 0,
                'ac_bonus': 1, 'speed_bonus': 0,
                'special': ['flight', 'keen_sight', 'dive_attack']
            },
            'panther': {
                'str_bonus': 4, 'dex_bonus': 6, 'con_bonus': 2,
                'ac_bonus': 2, 'speed_bonus': 20,
                'special': ['pounce', 'rake', 'stealth_master']
            },
            'boar': {
                'str_bonus': 4, 'dex_bonus': 0, 'con_bonus': 6,
                'ac_bonus': 4, 'speed_bonus': 0,
                'special': ['charge', 'tusks', 'ferocity']
            }
        }
        
        return form_data.get(form, {})
    
    def revert_to_human(self) -> Dict[str, Any]:
        """Revert to human form"""
        if self.current_form == 'human':
            return {'success': False, 'reason': 'Already in human form'}
        
        old_form = self.current_form
        self.current_form = 'human'
        self.form_duration_remaining = 0
        
        return {
            'success': True,
            'old_form': old_form,
            'new_form': 'human',
            'bonuses_removed': True
        }
    
    def get_current_form_bonuses(self) -> Dict[str, int]:
        """Get current form's stat bonuses"""
        if self.current_form == 'human':
            return {}
        return self._get_form_bonuses(self.current_form)
    
    # === NATURE MAGIC ABILITIES ===
    
    def _calculate_nature_spells(self) -> Dict[int, int]:
        """Calculate druidic spells per day by level (full progression)"""
        if self.druid_spell_level < 1:
            return {}
        
        # Druid spell progression (full caster like cleric)
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
        
        base_spells = spell_progression.get(min(self.druid_spell_level, 20), {})
        
        # Add wisdom bonus spells
        wis_bonus = max(0, (self.stats['wisdom'] - 10) // 2)
        final_spells = base_spells.copy()
        
        for spell_level in range(1, 10):
            if spell_level in final_spells:
                bonus = 0
                if wis_bonus >= spell_level:
                    bonus = 1 + (wis_bonus - spell_level) // 4
                final_spells[spell_level] += bonus
        
        return final_spells
    
    def get_nature_spells_per_day(self) -> Dict[int, int]:
        """Get druidic spells per day"""
        return self._calculate_nature_spells()
    
    def _calculate_spell_save_dc(self) -> int:
        """Calculate spell save DC"""
        base_dc = 10
        wis_bonus = max(0, (self.stats['wisdom'] - 10) // 2)
        return base_dc + wis_bonus
    
    def get_spell_save_dc(self, spell_level: int = 1) -> int:
        """Get spell save DC for given spell level"""
        return self._calculate_spell_save_dc() + spell_level
    
    def get_nature_spells_remaining(self, spell_level: int) -> int:
        """Get nature spells remaining for given level"""
        per_day = self.get_nature_spells_per_day().get(spell_level, 0)
        used = self.nature_spells_used.get(spell_level, 0)
        return max(0, per_day - used)
    
    def can_cast_nature_spell(self, spell_level: int) -> bool:
        """Check if druid can cast nature spell of given level"""
        if self.get_alignment() != Alignment.NEUTRAL:
            return False
        return self.get_nature_spells_remaining(spell_level) > 0
    
    def cast_nature_spell(self, spell_name: str, spell_level: int, target=None) -> Dict[str, Any]:
        """Cast a druidic spell"""
        if not self.can_cast_nature_spell(spell_level):
            return {'success': False, 'reason': f'No level {spell_level} spells remaining'}
        
        if spell_level not in self.nature_spells_used:
            self.nature_spells_used[spell_level] = 0
        self.nature_spells_used[spell_level] += 1
        
        # Extensive druid spell list
        spell_effects = {
            # Level 1
            'cure_light_wounds': {'healing': 8 + self.level, 'target_required': True},
            'detect_animals': {'range': 100, 'duration': 60},
            'speak_with_animals': {'duration': 600, 'all_animals': True},
            'entangle': {'area': 40, 'duration': 60, 'save_dc': self.get_spell_save_dc(1)},
            
            # Level 2
            'barkskin': {'ac_bonus': 2 + self.level//6, 'duration': 600},
            'hold_animal': {'save_dc': self.get_spell_save_dc(2), 'duration': 60},
            'flame_blade': {'damage': 6 + self.level, 'duration': 60},
            
            # Level 3
            'cure_moderate_wounds': {'healing': 16 + self.level, 'target_required': True},
            'call_lightning': {'damage': 20 + self.level, 'area_effect': True},
            'plant_growth': {'area': 100, 'permanent': True},
            
            # Level 4
            'ice_storm': {'damage': 25 + self.level, 'area': 20},
            'flame_strike': {'damage': 30 + self.level, 'divine_fire': True},
            'freedom_of_movement': {'duration': 600, 'immunity': 'paralysis'},
            
            # Level 5
            'cure_critical_wounds': {'healing': 24 + self.level, 'target_required': True},
            'wall_of_fire': {'damage': 15 + self.level, 'duration': 120},
            'commune_with_nature': {'area': 1000, 'knowledge': 'complete'},
            
            # Level 6
            'heal': {'healing': 'full', 'target_required': True},
            'transport_via_plants': {'teleport': True, 'range': 'unlimited'},
            'antilife_shell': {'protection': 'living_creatures', 'duration': 600},
            
            # Level 7
            'fire_storm': {'damage': 40 + self.level, 'area': 40},
            'animate_plants': {'plant_allies': 4, 'duration': 600},
            'changestaff': {'staff_ally': True, 'duration': 600},
            
            # Level 8
            'earthquake': {'area': 80, 'devastating': True},
            'whirlwind': {'damage': 35 + self.level, 'duration': 60},
            'word_of_recall': {'teleport_home': True, 'instant': True},
            
            # Level 9
            'storm_of_vengeance': {'damage': 50 + self.level, 'duration': 100, 'area': 100},
            'elemental_swarm': {'elementals': 8, 'duration': 600},
            'shapechange': {'any_form': True, 'duration': 600}
        }
        
        effect = spell_effects.get(spell_name, {})
        
        # Apply healing if applicable
        if 'healing' in effect and target:
            if effect['healing'] == 'full':
                healing_done = target.max_hp - target.current_hp
                target.current_hp = target.max_hp
            else:
                healing_done = target.heal(effect['healing'])
            effect['healing_done'] = healing_done
        
        return {
            'success': True,
            'spell_name': spell_name,
            'spell_level': spell_level,
            'effect': effect,
            'save_dc': self.get_spell_save_dc(spell_level),
            'remaining_spells': self.get_nature_spells_remaining(spell_level)
        }
    
    # === ANIMAL COMMUNICATION ABILITIES ===
    
    def get_animal_friendship_remaining(self) -> int:
        """Get animal friendship uses remaining"""
        return max(0, self.animal_friendship_uses - self.animal_friendship_used)
    
    def can_speak_with_animals(self) -> bool:
        """Check if druid can speak with animals"""
        return self.get_alignment() == Alignment.NEUTRAL
    
    def speak_with_animals(self, duration_minutes: int = 60) -> Dict[str, Any]:
        """Activate speak with animals ability"""
        if not self.can_speak_with_animals():
            return {'success': False, 'reason': 'Lost connection to nature'}
        
        self.speak_with_animals_active = True
        return {
            'success': True,
            'duration_minutes': duration_minutes,
            'all_animals': True,
            'automatic_understanding': True
        }
    
    def use_animal_friendship(self, animal_hd: int = 1) -> Dict[str, Any]:
        """Use animal friendship ability"""
        if self.get_animal_friendship_remaining() <= 0:
            return {'success': False, 'reason': 'No animal friendship uses remaining'}
        
        if self.get_alignment() != Alignment.NEUTRAL:
            return {'success': False, 'reason': 'Lost connection to nature'}
        
        self.animal_friendship_used += 1
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            friendship_roll = dice.roll("1d20") + self.get_animal_handling_bonus()
            dc = 10 + animal_hd
            success = friendship_roll >= dc
            
            return {
                'success': success,
                'friendship_roll': friendship_roll,
                'dc': dc,
                'animal_reaction': 'friendly' if success else 'neutral',
                'duration_hours': self.level if success else 0,
                'remaining_uses': self.get_animal_friendship_remaining()
            }
        except ImportError:
            import random
            success = random.randint(1, 20) + self.get_animal_handling_bonus() >= (10 + animal_hd)
            return {
                'success': success,
                'animal_reaction': 'friendly' if success else 'neutral',
                'remaining_uses': self.get_animal_friendship_remaining()
            }
    
    def can_summon_nature_ally(self) -> bool:
        """Check if druid can summon nature allies"""
        return self.summon_nature_ally and self.get_alignment() == Alignment.NEUTRAL
    
    # === WEATHER AND PLANT CONTROL ===
    
    def get_weather_control_remaining(self) -> int:
        """Get weather control uses remaining"""
        return max(0, self.weather_control_uses - self.weather_control_used)
    
    def get_plant_control_remaining(self) -> int:
        """Get plant control uses remaining"""
        return max(0, self.plant_control_uses - self.plant_control_used)
    
    def control_weather(self, weather_type: str = "clear") -> Dict[str, Any]:
        """Control local weather patterns"""
        if self.get_weather_control_remaining() <= 0:
            return {'success': False, 'reason': 'No weather control uses remaining'}
        
        if self.get_alignment() != Alignment.NEUTRAL:
            return {'success': False, 'reason': 'Lost connection to nature'}
        
        self.weather_control_used += 1
        
        weather_effects = {
            'clear': {'visibility': 'perfect', 'movement': 'normal'},
            'rain': {'visibility': 'reduced', 'fire_resistance': True},
            'fog': {'visibility': 'minimal', 'stealth_bonus': 4},
            'wind': {'ranged_penalty': -4, 'flying_difficult': True},
            'storm': {'lightning': True, 'damage': 10, 'area_denial': True}
        }
        
        effect = weather_effects.get(weather_type, weather_effects['clear'])
        
        return {
            'success': True,
            'weather_type': weather_type,
            'effect': effect,
            'duration_hours': self.level,
            'area_miles': self.level // 2,
            'remaining_uses': self.get_weather_control_remaining()
        }
    
    def control_plants(self, plant_action: str = "entangle") -> Dict[str, Any]:
        """Control plants in the area"""
        if self.get_plant_control_remaining() <= 0:
            return {'success': False, 'reason': 'No plant control uses remaining'}
        
        if self.get_alignment() != Alignment.NEUTRAL:
            return {'success': False, 'reason': 'Lost connection to nature'}
        
        self.plant_control_used += 1
        
        plant_actions = {
            'entangle': {'area': 40, 'duration': 60, 'save_dc': self.get_spell_save_dc(2)},
            'animate': {'plant_allies': 2, 'duration': 300},
            'growth': {'area': 100, 'movement_bonus': True, 'permanent': True},
            'wall': {'barrier': True, 'hp': 50 + self.level * 5, 'duration': 600}
        }
        
        effect = plant_actions.get(plant_action, plant_actions['entangle'])
        
        return {
            'success': True,
            'plant_action': plant_action,
            'effect': effect,
            'remaining_uses': self.get_plant_control_remaining()
        }
    
    # === ELEMENTAL RESISTANCES AND IMMUNITIES ===
    
    def _calculate_elemental_resistances(self) -> Dict[str, int]:
        """Calculate elemental damage resistances"""
        resistances = {}
        
        if self.level >= 4:
            resistances['fire'] = 5 + self.level // 4
            resistances['cold'] = 5 + self.level // 4
        if self.level >= 6:
            resistances['electricity'] = 5 + self.level // 4
            resistances['acid'] = 5 + self.level // 4
        if self.level >= 8:
            resistances['sonic'] = 5 + self.level // 4
        
        return resistances
    
    def _calculate_nature_immunities(self) -> List[str]:
        """Calculate nature-based immunities"""
        immunities = []
        
        if self.level >= 9:
            immunities.extend(['poison', 'disease'])
        if self.level >= 13:
            immunities.extend(['charm', 'compulsion'])
        if self.level >= 15:
            immunities.extend(['natural_aging', 'ability_drain'])
        
        return immunities
    
    def get_elemental_resistance(self, damage_type: str) -> int:
        """Get resistance to elemental damage type"""
        if self.get_alignment() != Alignment.NEUTRAL:
            return 0
        return self.elemental_resistances.get(damage_type, 0)
    
    def is_immune_to_effect(self, effect_type: str) -> bool:
        """Check immunity to various effects"""
        if self.get_alignment() != Alignment.NEUTRAL:
            return False
        return effect_type in self.nature_immunity
    
    # === NATURE KNOWLEDGE AND SURVIVAL ===
    
    def _calculate_nature_lore(self) -> int:
        """Calculate nature lore bonus"""
        base_bonus = 5
        wis_bonus = max(0, (self.stats['wisdom'] - 10) // 2)
        int_bonus = max(0, (self.stats['intelligence'] - 10) // 4)
        level_bonus = self.level + 5  # +1 per level + 5 base
        return base_bonus + wis_bonus + int_bonus + level_bonus
    
    def get_nature_lore_bonus(self) -> int:
        """Get nature lore bonus"""
        return self._calculate_nature_lore()
    
    def _calculate_survival_bonus(self) -> int:
        """Calculate survival bonus"""
        base_bonus = 4
        wis_bonus = max(0, (self.stats['wisdom'] - 10) // 2)
        con_bonus = max(0, (self.stats['constitution'] - 10) // 4)
        level_bonus = self.level + 3  # +1 per level + 3 base
        return base_bonus + wis_bonus + con_bonus + level_bonus
    
    def get_survival_bonus(self) -> int:
        """Get survival bonus"""
        return self._calculate_survival_bonus()
    
    def _calculate_animal_handling(self) -> int:
        """Calculate animal handling bonus"""
        base_bonus = 6
        wis_bonus = max(0, (self.stats['wisdom'] - 10) // 2)
        cha_bonus = max(0, (self.stats['charisma'] - 10) // 4)
        level_bonus = self.level + 4  # +1 per level + 4 base
        return base_bonus + wis_bonus + cha_bonus + level_bonus
    
    def get_animal_handling_bonus(self) -> int:
        """Get animal handling bonus"""
        return self._calculate_animal_handling()
    
    def can_woodland_stride(self) -> bool:
        """Check if druid can move through natural terrain unhindered"""
        return self.woodland_stride and self.get_alignment() == Alignment.NEUTRAL
    
    def leaves_no_trail(self) -> bool:
        """Check if druid leaves no trail in natural terrain"""
        return self.trackless_step and self.get_alignment() == Alignment.NEUTRAL
    
    # === EQUIPMENT RESTRICTIONS ===
    
    def can_use_weapon(self, weapon) -> bool:
        """Druids can only use natural materials"""
        if hasattr(weapon, 'material'):
            forbidden_materials = ['metal', 'steel', 'iron', 'adamantine', 'mithril']
            return weapon.material.lower() not in forbidden_materials
        # Default check - assume wood/stone weapons are okay
        if hasattr(weapon, 'weapon_type'):
            natural_weapons = ['club', 'quarterstaff', 'spear', 'dart', 'sling', 'scimitar']
            return weapon.weapon_type.lower() in natural_weapons
        return True  # Default allow if we can't determine material
    
    def can_use_armor(self, armor) -> bool:
        """Druids can only use natural material armor"""
        if hasattr(armor, 'material'):
            forbidden_materials = ['metal', 'steel', 'iron', 'plate', 'chainmail']
            return armor.material.lower() not in forbidden_materials
        if hasattr(armor, 'armor_type'):
            natural_armor = ['leather', 'hide', 'studded_leather', 'padded']
            return armor.armor_type.lower() in natural_armor
        return True  # Default allow for basic armor
    
    def can_equip_item(self, item) -> Tuple[bool, str]:
        """Check if druid can equip an item"""
        # Check for metal items
        if hasattr(item, 'material'):
            forbidden_materials = ['metal', 'steel', 'iron', 'adamantine', 'mithril']
            if item.material.lower() in forbidden_materials:
                return False, "Druids cannot use metal items - natural materials only"
        
        # Druids get bonuses with natural magical items
        if hasattr(item, 'material') and item.material.lower() in ['wood', 'stone', 'bone', 'crystal']:
            if hasattr(item, 'is_magical') and item.is_magical:
                return True, "Natural magical item - receives druidic blessing"
        
        return True, "Equipment allowed"
    
    def set_alignment(self, new_alignment: Alignment) -> bool:
        """Override to handle fallen druid mechanics"""
        old_alignment = self.get_alignment()
        success = super().set_alignment(new_alignment)
        
        # Check if druid has lost nature connection
        if success and old_alignment == Alignment.NEUTRAL and new_alignment != Alignment.NEUTRAL:
            # Druid has lost connection - lose all nature abilities
            self.shapeshifting_uses_used = self.shapeshifting_uses_per_day
            self.nature_spells_used = {level: per_day for level, per_day in self.get_nature_spells_per_day().items()}
            self.animal_friendship_used = self.animal_friendship_uses
            self.weather_control_used = self.weather_control_uses
            self.plant_control_used = self.plant_control_uses
            # Revert to human form
            self.current_form = 'human'
            self.form_duration_remaining = 0
        
        return success
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Druid':
        """Create Druid from save data"""
        race_id = data.get('race_id', 'human')
        
        # Load alignment from save data or default to neutral
        alignment = Alignment.NEUTRAL
        if 'alignment_data' in data:
            alignment_name = data['alignment_data'].get('alignment', 'NEUTRAL')
            alignment = getattr(Alignment, alignment_name, Alignment.NEUTRAL)
        
        druid = cls(data['character_name'], race_id, alignment)
        
        # Restore basic character data
        druid.level = data['level']
        druid.experience = data['experience']
        druid.base_stats = data.get('base_stats', druid.base_stats)
        druid.stats = data['stats']
        
        # Restore derived stats
        derived = data['derived_stats']
        druid.max_hp = derived['max_hp']
        druid.current_hp = derived['current_hp']
        druid.armor_class = derived['armor_class']
        druid.base_attack_bonus = derived['base_attack_bonus']
        
        # Restore location
        location = data['current_location']
        druid.current_area = location.get('area_id')
        druid.current_room = location.get('room_id')
        
        # Initialize item systems
        druid.initialize_item_systems()
        
        # Restore inventory and equipment data
        if 'inventory' in data:
            druid.inventory_system.from_dict(data['inventory'])
        if 'equipment' in data:
            druid.equipment_system.from_dict(data['equipment'])
        
        # Restore character creation state
        druid.unallocated_stats = data.get('unallocated_stats', 0)
        druid.creation_complete = data.get('creation_complete', True)
        
        # Load alignment data
        if 'alignment_data' in data:
            druid.load_alignment_data(data['alignment_data'])
        
        # Restore druid-specific attributes
        druid_data = data.get('druid_data', {})
        druid.shapeshifting_uses_used = druid_data.get('shapeshifting_uses_used', 0)
        druid.current_form = druid_data.get('current_form', 'human')
        druid.form_duration_remaining = druid_data.get('form_duration_remaining', 0)
        druid.nature_spells_used = druid_data.get('nature_spells_used', {})
        druid.animal_friendship_used = druid_data.get('animal_friendship_used', 0)
        druid.weather_control_used = druid_data.get('weather_control_used', 0)
        druid.plant_control_used = druid_data.get('plant_control_used', 0)
        druid.speak_with_animals_active = druid_data.get('speak_with_animals_active', False)
        
        # Recalculate druid-specific attributes
        druid.shapeshifting_uses_per_day = max(1, druid.level // 2)
        druid.available_forms = druid._get_available_forms()
        druid.druid_spell_level = druid.level
        druid.nature_spells_per_day = druid._calculate_nature_spells()
        druid.spell_save_dc = druid._calculate_spell_save_dc()
        druid.animal_friendship_uses = max(2, druid.level // 3)
        druid.summon_nature_ally = druid.level >= 5
        druid.weather_control_uses = max(1, druid.level // 4)
        druid.plant_control_uses = max(2, druid.level // 3)
        druid.elemental_resistances = druid._calculate_elemental_resistances()
        druid.nature_immunity = druid._calculate_nature_immunities()
        druid.trackless_step = druid.level >= 3
        druid.nature_lore_bonus = druid._calculate_nature_lore()
        druid.survival_bonus = druid._calculate_survival_bonus()
        druid.animal_handling_bonus = druid._calculate_animal_handling()
        
        return druid
    
    def to_dict(self) -> Dict[str, Any]:
        """Override to include druid-specific data"""
        data = super().to_dict()
        data['druid_data'] = {
            'shapeshifting_uses_used': self.shapeshifting_uses_used,
            'current_form': self.current_form,
            'form_duration_remaining': self.form_duration_remaining,
            'nature_spells_used': self.nature_spells_used,
            'animal_friendship_used': self.animal_friendship_used,
            'weather_control_used': self.weather_control_used,
            'plant_control_used': self.plant_control_used,
            'speak_with_animals_active': self.speak_with_animals_active
        }
        return data
        
    def __str__(self) -> str:
        """String representation of Druid"""
        # Check if lost nature connection
        if self.get_alignment() != Alignment.NEUTRAL:
            return super().__str__() + " [LOST NATURE CONNECTION]"
        
        abilities = []
        
        # Current form
        if self.current_form != 'human':
            abilities.append(f"{self.current_form.title()} Form ({self.form_duration_remaining}min)")
        else:
            shapeshifts = self.get_shapeshifting_remaining()
            if shapeshifts == float('inf'):
                abilities.append("Unlimited Shifts")
            else:
                abilities.append(f"Shifts {shapeshifts}")
        
        # Spell levels
        total_spells = sum(self.get_nature_spells_per_day().values())
        max_level = max(self.get_nature_spells_per_day().keys()) if self.get_nature_spells_per_day() else 0
        abilities.append(f"Spells {total_spells} (L{max_level})")
        
        # Weather/Plant control
        weather = self.get_weather_control_remaining()
        plants = self.get_plant_control_remaining()
        if weather > 0:
            abilities.append(f"Weather {weather}")
        if plants > 0:
            abilities.append(f"Plants {plants}")
        
        # Animal friendship
        animals = self.get_animal_friendship_remaining()
        if animals > 0:
            abilities.append(f"Animals {animals}")
        
        # High-level abilities
        if self.can_woodland_stride():
            abilities.append("Woodland Stride")
        if self.leaves_no_trail():
            abilities.append("Trackless")
        if self.level >= 15:
            abilities.append("Timeless")
            
        base_str = super().__str__()
        if abilities:
            base_str += f" [{', '.join(abilities)}]"
        return base_str