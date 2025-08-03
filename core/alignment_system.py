"""
MajorMUD-style alignment system for Rogue City.

Implements the three-alignment system (Good, Neutral, Evil) that affects
NPC interactions, equipment usage, spell access, and quest availability.
"""

from enum import Enum
from typing import Dict, List, Tuple, Optional
import json


class Alignment(Enum):
    """Character alignment enumeration following MajorMUD standards."""
    GOOD = 1
    NEUTRAL = 2
    EVIL = 3


class AlignmentSystem:
    """
    Core alignment system managing reputation, restrictions, and NPC reactions.
    
    Handles alignment-based game mechanics including:
    - NPC reaction modifiers based on alignment differences
    - Equipment and spell restrictions
    - Reputation tracking with different factions
    - Alignment benefits and penalties
    """
    
    def __init__(self):
        """Initialize the alignment system."""
        self.faction_alignments = {
            'good_faction': Alignment.GOOD,
            'neutral_faction': Alignment.NEUTRAL,
            'evil_faction': Alignment.EVIL,
            'town_guards': Alignment.GOOD,
            'merchants': Alignment.NEUTRAL,
            'thieves_guild': Alignment.EVIL,
            'priests': Alignment.GOOD,
            'necromancers': Alignment.EVIL,
            'scholars': Alignment.NEUTRAL
        }
        
        # Load alignment definitions if available
        self.alignment_data = self._load_alignment_data()
    
    def _load_alignment_data(self) -> Dict:
        """Load alignment definitions from data file."""
        try:
            with open('data/alignments/alignment_definitions.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default data if file doesn't exist yet
            return {
                'good': {
                    'name': 'Good',
                    'philosophy': 'Protecting the innocent and upholding justice',
                    'benefits': ['holy_weapons', 'healing_bonus', 'turn_undead'],
                    'restrictions': ['no_evil_items', 'no_harm_innocents']
                },
                'neutral': {
                    'name': 'Neutral',
                    'philosophy': 'Balance in all things, pragmatic approach to conflicts',
                    'benefits': ['diplomatic_immunity', 'skill_bonus', 'item_versatility'],
                    'restrictions': ['limited_extreme_items']
                },
                'evil': {
                    'name': 'Evil',
                    'philosophy': 'Power through strength, achieving goals by any means',
                    'benefits': ['dark_weapons', 'necromantic_spells', 'intimidation'],
                    'restrictions': ['no_holy_items', 'no_heal_others']
                }
            }
    
    def get_alignment_description(self, alignment: Alignment) -> Dict:
        """Get detailed description of an alignment."""
        alignment_key = alignment.name.lower()
        return self.alignment_data.get(alignment_key, {})
    
    def get_reaction_modifier(self, character_alignment: Alignment, npc_alignment: Alignment) -> int:
        """
        Calculate NPC reaction modifier based on alignment differences.
        
        Returns:
            +2 for same alignment (friendly)
            -2 for opposed alignment (Good vs Evil)
            0 for neutral interactions
        """
        if character_alignment == npc_alignment:
            return 2  # Same alignment bonus
        elif self._are_opposed_alignments(character_alignment, npc_alignment):
            return -2  # Opposed alignment penalty
        else:
            return 0  # Neutral reaction
    
    def _are_opposed_alignments(self, alignment1: Alignment, alignment2: Alignment) -> bool:
        """Check if two alignments are directly opposed (Good vs Evil)."""
        opposed_pairs = [
            (Alignment.GOOD, Alignment.EVIL),
            (Alignment.EVIL, Alignment.GOOD)
        ]
        return (alignment1, alignment2) in opposed_pairs
    
    def get_faction_reaction(self, character_alignment: Alignment, faction_name: str) -> int:
        """Get reaction modifier for a specific faction."""
        if faction_name not in self.faction_alignments:
            return 0
        
        faction_alignment = self.faction_alignments[faction_name]
        return self.get_reaction_modifier(character_alignment, faction_alignment)
    
    def can_use_item(self, character_alignment: Alignment, item_alignment: Optional[str]) -> Tuple[bool, str]:
        """
        Check if character can use an item based on alignment restrictions.
        
        Args:
            character_alignment: Character's alignment
            item_alignment: Item's alignment restriction ('good', 'neutral', 'evil', or None)
        
        Returns:
            Tuple of (can_use: bool, reason: str)
        """
        if item_alignment is None:
            return True, ""
        
        item_align = item_alignment.lower()
        char_align = character_alignment.name.lower()
        
        # Good characters cannot use evil items
        if char_align == 'good' and item_align == 'evil':
            return False, "This cursed item burns your pure hands!"
        
        # Evil characters cannot use good items
        if char_align == 'evil' and item_align == 'good':
            return False, "This holy item sears your evil flesh!"
        
        # Neutral characters have some restrictions on extreme items
        if char_align == 'neutral' and item_align in ['good', 'evil']:
            # Neutral can use most items but with warnings for extreme ones
            return True, ""
        
        return True, ""
    
    def get_alignment_bonuses(self, alignment: Alignment) -> Dict[str, int]:
        """Get stat bonuses/penalties for an alignment."""
        bonuses = {
            Alignment.GOOD: {
                'healing_effectiveness': 10,
                'turn_undead_bonus': 2,
                'damage_vs_evil': 1
            },
            Alignment.NEUTRAL: {
                'skill_progression': 5,
                'diplomatic_bonus': 2,
                'versatility_bonus': 1
            },
            Alignment.EVIL: {
                'damage_vs_good': 1,
                'intimidation_bonus': 2,
                'necromantic_power': 10
            }
        }
        return bonuses.get(alignment, {})
    
    def get_starting_reputation(self, alignment: Alignment) -> Dict[str, int]:
        """Get starting reputation values for a new character."""
        base_reputation = {
            'good_faction': 0,
            'neutral_faction': 0,
            'evil_faction': 0,
            'town_guards': 0,
            'merchants': 0,
            'thieves_guild': 0,
            'priests': 0,
            'necromancers': 0,
            'scholars': 0
        }
        
        # Apply alignment-based starting modifiers
        if alignment == Alignment.GOOD:
            base_reputation['good_faction'] = 10
            base_reputation['town_guards'] = 15
            base_reputation['priests'] = 20
            base_reputation['evil_faction'] = -10
            base_reputation['thieves_guild'] = -15
            base_reputation['necromancers'] = -20
        elif alignment == Alignment.EVIL:
            base_reputation['evil_faction'] = 10
            base_reputation['thieves_guild'] = 15
            base_reputation['necromancers'] = 20
            base_reputation['good_faction'] = -10
            base_reputation['town_guards'] = -15
            base_reputation['priests'] = -20
        # Neutral starts with balanced reputation (all zeros)
        
        return base_reputation
    
    def calculate_alignment_drift(self, current_alignment: Alignment, action_type: str) -> Alignment:
        """
        Calculate potential alignment change based on character actions.
        
        Args:
            current_alignment: Character's current alignment
            action_type: Type of action taken ('help_innocent', 'kill_innocent', 'pragmatic', etc.)
        
        Returns:
            New alignment (may be same as current)
        """
        # This is a simplified drift system - can be expanded later
        drift_actions = {
            'help_innocent': Alignment.GOOD,
            'kill_innocent': Alignment.EVIL,
            'donate_charity': Alignment.GOOD,
            'steal_from_poor': Alignment.EVIL,
            'negotiate_peace': Alignment.NEUTRAL,
            'murder_for_gain': Alignment.EVIL,
            'protect_weak': Alignment.GOOD
        }
        
        target_alignment = drift_actions.get(action_type)
        if target_alignment and target_alignment != current_alignment:
            # In a full implementation, this would track drift points
            # For now, return current alignment (no immediate change)
            return current_alignment
        
        return current_alignment
    
    def get_alignment_display_name(self, alignment: Alignment) -> str:
        """Get display-friendly name for alignment."""
        names = {
            Alignment.GOOD: "Good",
            Alignment.NEUTRAL: "Neutral", 
            Alignment.EVIL: "Evil"
        }
        return names.get(alignment, "Unknown")
    
    def get_alignment_color_code(self, alignment: Alignment) -> str:
        """Get color code for alignment display (for future UI enhancement)."""
        colors = {
            Alignment.GOOD: "white",      # Pure/holy
            Alignment.NEUTRAL: "yellow",   # Balanced
            Alignment.EVIL: "red"         # Dark/sinister
        }
        return colors.get(alignment, "white")