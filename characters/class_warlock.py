"""
Warlock Character Class for Rogue City
Traditional MajorMUD battle mage with spellsword combat and weapon enchantment.
"""

from .base_character import BaseCharacter
from core.alignment_system import Alignment
from typing import Dict, Any, Tuple, List


class Warlock(BaseCharacter):
    """
    Warlock class - Battle mage with spellsword combat
    
    BATTLE MAGE - Expert progression, combines magic and combat effectively
    
    Experience Penalty: +55% (combines magic and combat effectively)
    Stat Modifiers: +2 STR, +2 INT, +1 CON, +1 CHA, -2 WIS, -1 DEX
    Hit Die: d8 (good HP progression for a caster)
    Attack Speed: 3.0 seconds (moderate combat speed)
    Critical Range: 20 (standard critical chance)
    
    SPELLSWORD MASTERY CORE:
    - Spellsword combat allowing spellcasting while wielding weapons
    - Weapon enchantment to imbue weapons with magical properties
    - Eldritch blast signature magical attack scaling with level
    - Battle magic focus on combat-oriented spells
    - Arcane armor providing magical protection stacking with physical
    - Spell parry to deflect attacks using magic
    
    WARLOCK ABILITIES:
    - Spellsword Combat: Cast spells while wielding weapons
    - Weapon Enchantment: Imbue weapons with magical properties
    - Eldritch Blast: Signature magical attack scaling with level
    - Battle Magic: Combat-focused spell selection
    - Arcane Armor: Magical protection stacking with physical armor
    - Spell Parry: Deflect attacks using magic
    
    EQUIPMENT ACCESS:
    - Weapons: All weapons with magical enhancement capabilities
    - Armor: Medium armor with arcane enhancement
    - Magic: Full access to battle-focused magical items
    - Accessories: Magical focuses, enchanting tools, spell components
    """
    
    def __init__(self, name: str, race_id: str = "human", alignment: Alignment = Alignment.NEUTRAL):
        """Initialize Warlock character with battle magic and spellsword systems"""
        super().__init__(name, 'warlock', race_id, alignment)
        
        # Spellcasting system (hybrid caster, 3/4 progression)
        self.warlock_caster_level = max(1, (self.level * 3) // 4)
        self.battle_spells_per_day = self._calculate_battle_spells()
        self.battle_spells_used = {}  # Track by spell level
        self.spell_save_dc = self._calculate_spell_save_dc()
        
        # Eldritch blast system
        self.eldritch_blast_damage = self._calculate_eldritch_blast_damage()
        self.eldritch_blast_range = 60 + (self.level * 5)
        self.eldritch_blast_invocations = self._get_eldritch_invocations()
        
        # Weapon enchantment system
        self.weapon_enchantment_uses = max(2, self.level // 2)
        self.weapon_enchantment_used = 0
        self.enchantment_duration = 10 * self.level  # Minutes
        self.permanent_enchantments = self.level >= 15
        
        # Arcane armor system
        self.arcane_armor_bonus = self._calculate_arcane_armor()
        self.arcane_armor_active = False
        self.arcane_armor_duration = 60 * self.level  # Minutes
        
        # Spell parry system
        self.spell_parry_uses = max(1, self.level // 3)
        self.spell_parry_used = 0
        self.spell_parry_bonus = self._calculate_spell_parry_bonus()
        
        # Battle magic specialization
        self.battle_focus_bonus = self._calculate_battle_focus()
        self.spell_critical_chance = max(5, self.level // 2)  # % chance
        self.metamagic_mastery = self.level >= 12
        
        # Spellsword combat
        self.combat_casting_bonus = self._calculate_combat_casting()
        self.spell_strike = self.level >= 6  # Cast spell on weapon hit
        self.spell_channeling = self.level >= 10  # Channel spells through weapons
        
    def get_hit_die_value(self) -> int:
        """Warlocks use d8 hit die (good HP for a caster)"""
        return 8
        
    def get_hit_die_type(self) -> str:
        """Return dice notation for hit die"""
        return "1d8"
        
    def get_attack_speed(self) -> float:
        """Return attack speed in seconds (considering equipped weapon)"""
        if hasattr(self, 'equipment_system') and self.equipment_system:
            return self.equipment_system.get_attack_speed_modifier()
        return self.get_base_attack_speed()
    
    def get_base_attack_speed(self) -> float:
        """Warlocks attack every 3 seconds unarmed (moderate speed)"""
        return 3.0
        
    def get_critical_range(self) -> int:
        """Warlocks crit on natural 20 (standard critical)"""
        return 20
        
    def get_experience_penalty(self) -> int:
        """Warlocks have +55% experience penalty"""
        return 55
        
    def get_special_abilities(self) -> Dict[str, Any]:
        """Comprehensive Warlock special abilities"""
        return {
            # Spellcasting
            'warlock_caster_level': self.warlock_caster_level,
            'battle_spells_per_day': self.get_battle_spells_per_day(),
            'spell_save_dc': self.get_spell_save_dc(),
            'battle_magic_focus': self.get_battle_focus_bonus(),
            'spell_critical': self.spell_critical_chance,
            
            # Eldritch blast
            'eldritch_blast_damage': self.get_eldritch_blast_damage(),
            'eldritch_blast_range': self.eldritch_blast_range,
            'eldritch_invocations': self.eldritch_blast_invocations.copy(),
            'blast_mastery': self.level >= 10,
            
            # Weapon enchantment
            'weapon_enchantment': self.get_weapon_enchantment_remaining(),
            'enchantment_duration': self.enchantment_duration,
            'permanent_enchantments': self.permanent_enchantments,
            'enchantment_mastery': self.level >= 8,
            
            # Arcane armor
            'arcane_armor_bonus': self.get_arcane_armor_bonus(),
            'arcane_armor_active': self.arcane_armor_active,
            'arcane_armor_duration': self.arcane_armor_duration,
            'improved_arcane_armor': self.level >= 12,
            
            # Spell parry
            'spell_parry': self.get_spell_parry_remaining(),
            'spell_parry_bonus': self.get_spell_parry_bonus(),
            'spell_reflection': self.level >= 16,
            
            # Spellsword combat
            'combat_casting': self.get_combat_casting_bonus(),
            'spell_strike': self.spell_strike,
            'spell_channeling': self.spell_channeling,
            'spellsword_mastery': self.level >= 14,
            
            # Metamagic
            'metamagic_mastery': self.metamagic_mastery,
            'quicken_spell': self.level >= 10,
            'empower_spell': self.level >= 8,
            'maximize_spell': self.level >= 16,
            
            # Equipment proficiencies
            'all_weapon_proficiency': True,
            'medium_armor_proficiency': True,
            'magical_item_mastery': True,
            'focus_weapon_proficiency': True
        }
    
    # === SPELLCASTING SYSTEM ===
    
    def _calculate_battle_spells(self) -> Dict[int, int]:
        """Calculate battle spells per day (3/4 caster progression)"""
        if self.warlock_caster_level < 1:
            return {}
        
        # Warlock spell progression (3/4 caster like ranger/paladin)
        spell_progression = {
            1: {1: 1}, 2: {1: 2}, 3: {1: 3}, 4: {1: 3, 2: 1},
            5: {1: 4, 2: 2}, 6: {1: 4, 2: 3}, 7: {1: 4, 2: 3, 3: 1},
            8: {1: 4, 2: 4, 3: 2}, 9: {1: 5, 2: 4, 3: 3},
            10: {1: 5, 2: 4, 3: 3, 4: 1}, 11: {1: 5, 2: 5, 3: 4, 4: 2},
            12: {1: 5, 2: 5, 3: 4, 4: 3}, 13: {1: 5, 2: 5, 3: 4, 4: 3, 5: 1},
            14: {1: 5, 2: 5, 3: 5, 4: 4, 5: 2}, 15: {1: 5, 2: 5, 3: 5, 4: 4, 5: 3},
            16: {1: 5, 2: 5, 3: 5, 4: 4, 5: 3, 6: 1}, 17: {1: 5, 2: 5, 3: 5, 4: 5, 5: 4, 6: 2},
            18: {1: 5, 2: 5, 3: 5, 4: 5, 5: 4, 6: 3}, 19: {1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 4},
            20: {1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 5}
        }
        
        base_spells = spell_progression.get(min(self.warlock_caster_level, 20), {})
        
        # Add intelligence bonus spells
        int_bonus = max(0, (self.stats['intelligence'] - 10) // 2)
        final_spells = base_spells.copy()
        
        for spell_level in range(1, 7):  # Warlocks get up to 6th level spells
            if spell_level in final_spells:
                bonus = 0
                if int_bonus >= spell_level:
                    bonus = 1 + (int_bonus - spell_level) // 4
                final_spells[spell_level] += bonus
        
        return final_spells
    
    def get_battle_spells_per_day(self) -> Dict[int, int]:
        """Get battle spells per day"""
        return self._calculate_battle_spells()
    
    def _calculate_spell_save_dc(self) -> int:
        """Calculate spell save DC"""
        base_dc = 10
        int_bonus = max(0, (self.stats['intelligence'] - 10) // 2)
        return base_dc + int_bonus
    
    def get_spell_save_dc(self, spell_level: int = 1) -> int:
        """Get spell save DC for given spell level"""
        return self._calculate_spell_save_dc() + spell_level
    
    def get_battle_spells_remaining(self, spell_level: int) -> int:
        """Get battle spells remaining for given level"""
        per_day = self.get_battle_spells_per_day().get(spell_level, 0)
        used = self.battle_spells_used.get(spell_level, 0)
        return max(0, per_day - used)
    
    def can_cast_battle_spell(self, spell_level: int) -> bool:
        """Check if warlock can cast battle spell of given level"""
        return self.get_battle_spells_remaining(spell_level) > 0
    
    def cast_battle_spell(self, spell_name: str, spell_level: int, target=None) -> Dict[str, Any]:
        """Cast a battle-focused spell"""
        if not self.can_cast_battle_spell(spell_level):
            return {'success': False, 'reason': f'No level {spell_level} spells remaining'}
        
        if spell_level not in self.battle_spells_used:
            self.battle_spells_used[spell_level] = 0
        self.battle_spells_used[spell_level] += 1
        
        # Battle-focused spell list
        spell_effects = {
            # Level 1
            'magic_weapon': {'weapon_bonus': 1, 'duration': 600},
            'shield': {'ac_bonus': 4, 'duration': 600},
            'magic_missile': {'damage': 3 + self.warlock_caster_level, 'auto_hit': True},
            'true_strike': {'attack_bonus': 20, 'duration': 1},
            
            # Level 2  
            'bulls_strength': {'str_bonus': 4, 'duration': 600},
            'cats_grace': {'dex_bonus': 4, 'duration': 600},
            'blur': {'concealment': 20, 'duration': 600},
            'scorching_ray': {'damage': 8 + self.warlock_caster_level, 'ranged_touch': True},
            
            # Level 3
            'fireball': {'damage': 15 + self.warlock_caster_level, 'area': 20},
            'haste': {'extra_attack': True, 'ac_bonus': 1, 'duration': 60},
            'keen_edge': {'critical_range': 'doubled', 'duration': 600},
            'vampiric_touch': {'damage': 12 + self.warlock_caster_level, 'healing': 'half_damage'},
            
            # Level 4
            'greater_magic_weapon': {'weapon_bonus': 3, 'duration': 3600},
            'stoneskin': {'damage_reduction': 10, 'duration': 600},
            'wall_of_fire': {'damage': 20 + self.warlock_caster_level, 'duration': 120},
            'dimension_door': {'teleport': 400, 'instant': True},
            
            # Level 5
            'cone_of_cold': {'damage': 25 + self.warlock_caster_level, 'area': 60},
            'cloudkill': {'poison_cloud': True, 'area': 20, 'duration': 60},
            'telekinesis': {'force': 25 * self.warlock_caster_level, 'duration': 60},
            'hold_monster': {'paralysis': True, 'duration': 60},
            
            # Level 6
            'disintegrate': {'damage': 40 + self.warlock_caster_level, 'fort_negates': True},
            'chain_lightning': {'damage': 30 + self.warlock_caster_level, 'targets': 6},
            'mass_bulls_strength': {'str_bonus': 4, 'targets': 'party', 'duration': 600},
            'antimagic_field': {'magic_immunity': True, 'area': 10, 'duration': 60}
        }
        
        effect = spell_effects.get(spell_name, {})
        
        # Apply spell critical chance
        critical_success = False
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            crit_roll = dice.roll("1d100")
            critical_success = crit_roll <= self.spell_critical_chance
        except ImportError:
            import random
            critical_success = random.randint(1, 100) <= self.spell_critical_chance
        
        if critical_success and 'damage' in effect:
            effect['damage'] = int(effect['damage'] * 1.5)
            effect['spell_critical'] = True
        
        return {
            'success': True,
            'spell_name': spell_name,
            'spell_level': spell_level,
            'effect': effect,
            'save_dc': self.get_spell_save_dc(spell_level),
            'critical_success': critical_success,
            'remaining_spells': self.get_battle_spells_remaining(spell_level)
        }
    
    # === ELDRITCH BLAST SYSTEM ===
    
    def _calculate_eldritch_blast_damage(self) -> str:
        """Calculate eldritch blast damage dice"""
        dice_count = 1 + (self.level - 1) // 4  # 1d6 per 4 levels
        return f"{dice_count}d6"
    
    def get_eldritch_blast_damage(self) -> str:
        """Get eldritch blast damage dice"""
        return self._calculate_eldritch_blast_damage()
    
    def _get_eldritch_invocations(self) -> List[str]:
        """Get available eldritch blast invocations"""
        invocations = ['basic_blast']
        
        if self.level >= 5:
            invocations.append('eldritch_spear')  # Increased range
        if self.level >= 8:
            invocations.append('eldritch_chain')  # Chain to multiple targets
        if self.level >= 12:
            invocations.append('eldritch_cone')   # Cone area effect
        if self.level >= 16:
            invocations.append('eldritch_doom')   # Penetrates resistances
        
        return invocations
    
    def cast_eldritch_blast(self, invocation: str = 'basic_blast', targets: int = 1) -> Dict[str, Any]:
        """Cast eldritch blast with invocation"""
        if invocation not in self.eldritch_blast_invocations:
            invocation = 'basic_blast'
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            damage_dice = self.get_eldritch_blast_damage()
            base_damage = sum(dice.roll("1d6") for _ in range(int(damage_dice[0])))
        except ImportError:
            import random
            dice_count = int(self.get_eldritch_blast_damage()[0])
            base_damage = sum(random.randint(1, 6) for _ in range(dice_count))
        
        # Apply invocation effects
        invocation_effects = {
            'basic_blast': {'damage': base_damage, 'range': self.eldritch_blast_range},
            'eldritch_spear': {'damage': base_damage, 'range': self.eldritch_blast_range * 2},
            'eldritch_chain': {'damage': base_damage, 'targets': min(targets, 3), 'range': self.eldritch_blast_range},
            'eldritch_cone': {'damage': base_damage, 'area': 'cone_30ft', 'range': 30},
            'eldritch_doom': {'damage': int(base_damage * 1.5), 'penetrating': True, 'range': self.eldritch_blast_range}
        }
        
        effect = invocation_effects.get(invocation, invocation_effects['basic_blast'])
        
        return {
            'success': True,
            'invocation': invocation,
            'damage': effect['damage'],
            'range': effect.get('range', self.eldritch_blast_range),
            'targets': effect.get('targets', 1),
            'area': effect.get('area', 'single'),
            'penetrating': effect.get('penetrating', False),
            'unlimited_uses': True  # Eldritch blast is at-will
        }
    
    # === WEAPON ENCHANTMENT SYSTEM ===
    
    def get_weapon_enchantment_remaining(self) -> int:
        """Get weapon enchantment uses remaining"""
        return max(0, self.weapon_enchantment_uses - self.weapon_enchantment_used)
    
    def can_enchant_weapon(self) -> bool:
        """Check if warlock can enchant weapons"""
        return self.get_weapon_enchantment_remaining() > 0
    
    def enchant_weapon(self, enchantment_type: str, permanent: bool = False) -> Dict[str, Any]:
        """Enchant a weapon with magical properties"""
        if not self.can_enchant_weapon():
            return {'success': False, 'reason': 'No weapon enchantment uses remaining'}
        
        if permanent and not self.permanent_enchantments:
            permanent = False
        
        self.weapon_enchantment_used += 1 if not permanent else 2
        
        enchantment_effects = {
            'flame_weapon': {'damage_bonus': '1d6', 'damage_type': 'fire', 'description': 'Weapon burns with magical fire'},
            'frost_weapon': {'damage_bonus': '1d4', 'damage_type': 'cold', 'slow_effect': True, 'description': 'Weapon chills with ice'},
            'shock_weapon': {'damage_bonus': '1d4', 'damage_type': 'electricity', 'stun_chance': 10, 'description': 'Weapon crackles with lightning'},
            'keen_edge': {'critical_range': 'doubled', 'description': 'Weapon edge becomes supernaturally sharp'},
            'dancing_weapon': {'independent_attacks': True, 'extra_attacks': 1, 'description': 'Weapon fights independently'},
            'vorpal_edge': {'decapitation_chance': 5, 'damage_bonus': '2d6', 'description': 'Weapon can sever heads'}
        }
        
        effect = enchantment_effects.get(enchantment_type, enchantment_effects['flame_weapon'])
        duration = 'permanent' if permanent else f"{self.enchantment_duration} minutes"
        
        return {
            'success': True,
            'enchantment_type': enchantment_type,
            'effect': effect,
            'duration': duration,
            'permanent': permanent,
            'remaining_uses': self.get_weapon_enchantment_remaining()
        }
    
    def can_make_permanent_enchantment(self) -> bool:
        """Check if warlock can make permanent enchantments"""
        return self.permanent_enchantments
    
    # === ARCANE ARMOR SYSTEM ===
    
    def _calculate_arcane_armor(self) -> int:
        """Calculate arcane armor AC bonus"""
        base_bonus = 2
        int_bonus = max(0, (self.stats['intelligence'] - 10) // 4)
        level_bonus = self.level // 4
        return base_bonus + int_bonus + level_bonus
    
    def get_arcane_armor_bonus(self) -> int:
        """Get arcane armor AC bonus"""
        return self._calculate_arcane_armor()
    
    def activate_arcane_armor(self) -> Dict[str, Any]:
        """Activate arcane armor protection"""
        self.arcane_armor_active = True
        ac_bonus = self.get_arcane_armor_bonus()
        
        additional_effects = {}
        if self.level >= 12:  # Improved arcane armor
            additional_effects.update({
                'spell_resistance': 5 + self.level,
                'energy_resistance': 10
            })
        
        return {
            'success': True,
            'ac_bonus': ac_bonus,
            'duration_minutes': self.arcane_armor_duration,
            'additional_effects': additional_effects,
            'stacks_with_physical': True
        }
    
    def deactivate_arcane_armor(self):
        """Deactivate arcane armor"""
        self.arcane_armor_active = False
    
    # === SPELL PARRY SYSTEM ===
    
    def get_spell_parry_remaining(self) -> int:
        """Get spell parry uses remaining"""
        return max(0, self.spell_parry_uses - self.spell_parry_used)
    
    def _calculate_spell_parry_bonus(self) -> int:
        """Calculate spell parry bonus"""
        base_bonus = 4
        int_bonus = max(0, (self.stats['intelligence'] - 10) // 2)
        level_bonus = self.level // 3
        return base_bonus + int_bonus + level_bonus
    
    def get_spell_parry_bonus(self) -> int:
        """Get spell parry bonus"""
        return self._calculate_spell_parry_bonus()
    
    def can_spell_parry(self) -> bool:
        """Check if warlock can use spell parry"""
        return self.get_spell_parry_remaining() > 0
    
    def attempt_spell_parry(self, incoming_attack: int) -> Dict[str, Any]:
        """Attempt to parry attack with magic"""
        if not self.can_spell_parry():
            return {'success': False, 'reason': 'No spell parry uses remaining'}
        
        self.spell_parry_used += 1
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            parry_roll = dice.roll("1d20") + self.get_spell_parry_bonus()
            success = parry_roll >= incoming_attack
            
            # Spell reflection at high level
            reflected = False
            if self.level >= 16 and success:
                reflect_roll = dice.roll("1d100")
                reflected = reflect_roll <= 25  # 25% chance to reflect
            
            return {
                'success': success,
                'parry_roll': parry_roll,
                'incoming_attack': incoming_attack,
                'reflected': reflected,
                'remaining_uses': self.get_spell_parry_remaining()
            }
        except ImportError:
            import random
            success = random.randint(1, 20) + self.get_spell_parry_bonus() >= incoming_attack
            reflected = success and self.level >= 16 and random.randint(1, 4) == 1
            return {
                'success': success,
                'reflected': reflected,
                'remaining_uses': self.get_spell_parry_remaining()
            }
    
    # === SPELLSWORD COMBAT ===
    
    def _calculate_combat_casting(self) -> int:
        """Calculate combat casting bonus"""
        base_bonus = 3
        con_bonus = max(0, (self.stats['constitution'] - 10) // 2)
        level_bonus = self.level // 2
        return base_bonus + con_bonus + level_bonus
    
    def get_combat_casting_bonus(self) -> int:
        """Get combat casting bonus"""
        return self._calculate_combat_casting()
    
    def _calculate_battle_focus(self) -> int:
        """Calculate battle magic focus bonus"""
        base_bonus = 2
        int_bonus = max(0, (self.stats['intelligence'] - 10) // 4)
        level_bonus = self.level // 4
        return base_bonus + int_bonus + level_bonus
    
    def get_battle_focus_bonus(self) -> int:
        """Get battle magic focus bonus"""
        return self._calculate_battle_focus()
    
    def can_spell_strike(self) -> bool:
        """Check if warlock can use spell strike"""
        return self.spell_strike
    
    def perform_spell_strike(self, spell_name: str, spell_level: int) -> Dict[str, Any]:
        """Perform spell strike (cast spell on weapon hit)"""
        if not self.can_spell_strike():
            return {'success': False, 'reason': 'Spell strike not available'}
        
        if not self.can_cast_battle_spell(spell_level):
            return {'success': False, 'reason': 'No spells remaining'}
        
        # Cast spell as part of weapon attack
        spell_result = self.cast_battle_spell(spell_name, spell_level)
        
        return {
            'success': True,
            'spell_result': spell_result,
            'weapon_attack_bonus': 4,  # +4 to hit for spell strike
            'combined_damage': True,
            'spell_effects_on_hit': True
        }
    
    def can_channel_spell(self) -> bool:
        """Check if warlock can channel spells through weapons"""
        return self.spell_channeling
    
    def channel_spell_through_weapon(self, spell_name: str, spell_level: int) -> Dict[str, Any]:
        """Channel spell through weapon for enhanced effect"""
        if not self.can_channel_spell():
            return {'success': False, 'reason': 'Spell channeling not available'}
        
        if not self.can_cast_battle_spell(spell_level):
            return {'success': False, 'reason': 'No spells remaining'}
        
        spell_result = self.cast_battle_spell(spell_name, spell_level)
        
        # Enhance spell when channeled through weapon
        if 'damage' in spell_result.get('effect', {}):
            weapon_bonus = max(1, self.level // 4)
            spell_result['effect']['damage'] += weapon_bonus
            spell_result['effect']['weapon_channeled'] = True
        
        return {
            'success': True,
            'spell_result': spell_result,
            'channeled': True,
            'enhanced_effect': True
        }
    
    # === METAMAGIC ABILITIES ===
    
    def can_use_metamagic(self) -> bool:
        """Check if warlock can use metamagic"""
        return self.metamagic_mastery
    
    def apply_quicken_spell(self) -> Dict[str, Any]:
        """Apply quicken spell metamagic"""
        if not self.can_use_metamagic() or self.level < 10:
            return {'success': False, 'reason': 'Quicken spell not available'}
        
        return {
            'success': True,
            'casting_time': 'swift_action',
            'additional_spell_this_turn': True,
            'spell_level_increase': 4
        }
    
    def apply_empower_spell(self) -> Dict[str, Any]:
        """Apply empower spell metamagic"""
        if not self.can_use_metamagic() or self.level < 8:
            return {'success': False, 'reason': 'Empower spell not available'}
        
        return {
            'success': True,
            'damage_multiplier': 1.5,
            'spell_level_increase': 2
        }
    
    def apply_maximize_spell(self) -> Dict[str, Any]:
        """Apply maximize spell metamagic"""
        if not self.can_use_metamagic() or self.level < 16:
            return {'success': False, 'reason': 'Maximize spell not available'}
        
        return {
            'success': True,
            'maximize_damage': True,
            'spell_level_increase': 3
        }
    
    # === EQUIPMENT ACCESS ===
    
    def can_use_weapon(self, weapon) -> bool:
        """Warlocks can use all weapon types"""
        return True
    
    def can_use_armor(self, armor) -> bool:
        """Warlocks can use light and medium armor"""
        if hasattr(armor, 'armor_type'):
            allowed_types = ['light', 'medium', 'leather', 'chain', 'scale', 'studded']
            return armor.armor_type.lower() in allowed_types
        return True  # Default allow for basic armor
    
    def calculate_derived_stats(self):
        """Override to include arcane armor bonus"""
        super().calculate_derived_stats()
        
        # Add arcane armor AC bonus if active
        if self.arcane_armor_active:
            self.armor_class += self.get_arcane_armor_bonus()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Warlock':
        """Create Warlock from save data"""
        race_id = data.get('race_id', 'human')
        
        # Load alignment from save data or default to neutral
        alignment = Alignment.NEUTRAL
        if 'alignment_data' in data:
            alignment_name = data['alignment_data'].get('alignment', 'NEUTRAL')
            alignment = getattr(Alignment, alignment_name, Alignment.NEUTRAL)
        
        warlock = cls(data['character_name'], race_id, alignment)
        
        # Restore basic character data
        warlock.level = data['level']
        warlock.experience = data['experience']
        warlock.base_stats = data.get('base_stats', warlock.base_stats)
        warlock.stats = data['stats']
        
        # Restore derived stats
        derived = data['derived_stats']
        warlock.max_hp = derived['max_hp']
        warlock.current_hp = derived['current_hp']
        warlock.armor_class = derived['armor_class']
        warlock.base_attack_bonus = derived['base_attack_bonus']
        
        # Restore location
        location = data['current_location']
        warlock.current_area = location.get('area_id')
        warlock.current_room = location.get('room_id')
        
        # Initialize item systems
        warlock.initialize_item_systems()
        
        # Restore inventory and equipment data
        if 'inventory' in data:
            warlock.inventory_system.from_dict(data['inventory'])
        if 'equipment' in data:
            warlock.equipment_system.from_dict(data['equipment'])
        
        # Restore character creation state
        warlock.unallocated_stats = data.get('unallocated_stats', 0)
        warlock.creation_complete = data.get('creation_complete', True)
        
        # Load alignment data
        if 'alignment_data' in data:
            warlock.load_alignment_data(data['alignment_data'])
        
        # Load currency data
        if 'currency_data' in data:
            warlock.load_currency_data(data['currency_data'])
        
        # Restore warlock-specific attributes
        warlock_data = data.get('warlock_data', {})
        warlock.battle_spells_used = warlock_data.get('battle_spells_used', {})
        warlock.weapon_enchantment_used = warlock_data.get('weapon_enchantment_used', 0)
        warlock.spell_parry_used = warlock_data.get('spell_parry_used', 0)
        warlock.arcane_armor_active = warlock_data.get('arcane_armor_active', False)
        
        # Recalculate warlock-specific attributes
        warlock.warlock_caster_level = max(1, (warlock.level * 3) // 4)
        warlock.battle_spells_per_day = warlock._calculate_battle_spells()
        warlock.spell_save_dc = warlock._calculate_spell_save_dc()
        warlock.eldritch_blast_damage = warlock._calculate_eldritch_blast_damage()
        warlock.eldritch_blast_range = 60 + (warlock.level * 5)
        warlock.eldritch_blast_invocations = warlock._get_eldritch_invocations()
        warlock.weapon_enchantment_uses = max(2, warlock.level // 2)
        warlock.enchantment_duration = 10 * warlock.level
        warlock.permanent_enchantments = warlock.level >= 15
        warlock.arcane_armor_bonus = warlock._calculate_arcane_armor()
        warlock.arcane_armor_duration = 60 * warlock.level
        warlock.spell_parry_uses = max(1, warlock.level // 3)
        warlock.spell_parry_bonus = warlock._calculate_spell_parry_bonus()
        warlock.battle_focus_bonus = warlock._calculate_battle_focus()
        warlock.spell_critical_chance = max(5, warlock.level // 2)
        warlock.metamagic_mastery = warlock.level >= 12
        warlock.combat_casting_bonus = warlock._calculate_combat_casting()
        warlock.spell_strike = warlock.level >= 6
        warlock.spell_channeling = warlock.level >= 10
        
        return warlock
    
    def to_dict(self) -> Dict[str, Any]:
        """Override to include warlock-specific data"""
        data = super().to_dict()
        data['warlock_data'] = {
            'battle_spells_used': self.battle_spells_used,
            'weapon_enchantment_used': self.weapon_enchantment_used,
            'spell_parry_used': self.spell_parry_used,
            'arcane_armor_active': self.arcane_armor_active
        }
        return data
        
    def __str__(self) -> str:
        """String representation of Warlock"""
        abilities = []
        
        # Spell levels
        total_spells = sum(self.get_battle_spells_per_day().values())
        max_level = max(self.get_battle_spells_per_day().keys()) if self.get_battle_spells_per_day() else 0
        abilities.append(f"Spells {total_spells} (L{max_level})")
        
        # Eldritch blast
        blast_damage = self.get_eldritch_blast_damage()
        abilities.append(f"Blast {blast_damage}")
        
        # Weapon enchantment
        enchant_remaining = self.get_weapon_enchantment_remaining()
        abilities.append(f"Enchant {enchant_remaining}")
        
        # Arcane armor
        if self.arcane_armor_active:
            armor_bonus = self.get_arcane_armor_bonus()
            abilities.append(f"Arcane AC +{armor_bonus}")
        
        # Spell parry
        parry_remaining = self.get_spell_parry_remaining()
        if parry_remaining > 0:
            abilities.append(f"Parry {parry_remaining}")
        
        # High-level abilities
        if self.can_spell_strike():
            abilities.append("Spell Strike")
        if self.can_channel_spell():
            abilities.append("Channel")
        if self.can_make_permanent_enchantment():
            abilities.append("Permanent")
        if self.can_use_metamagic():
            abilities.append("Metamagic")
            
        base_str = super().__str__()
        if abilities:
            base_str += f" [{', '.join(abilities)}]"
        return base_str