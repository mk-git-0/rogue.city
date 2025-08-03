"""
Character alignment management for Rogue City.

Handles individual character alignment tracking, reputation management,
and alignment-based ability access.
"""

from typing import Dict, List, Optional, Tuple
from core.alignment_system import Alignment, AlignmentSystem


class AlignmentManager:
    """
    Manages alignment and reputation for individual characters.
    
    Tracks character alignment, faction reputation, alignment changes,
    and provides alignment-based bonuses and restrictions.
    """
    
    def __init__(self, initial_alignment: Alignment):
        """
        Initialize alignment manager for a character.
        
        Args:
            initial_alignment: Starting alignment for the character
        """
        self.alignment = initial_alignment
        self.alignment_system = AlignmentSystem()
        
        # Initialize reputation with starting values
        self.reputation = self.alignment_system.get_starting_reputation(initial_alignment)
        
        # Track alignment history for potential drift
        self.alignment_history = [initial_alignment]
        self.drift_points = {'good': 0, 'neutral': 0, 'evil': 0}
    
    def get_alignment(self) -> Alignment:
        """Get current character alignment."""
        return self.alignment
    
    def set_alignment(self, new_alignment: Alignment) -> bool:
        """
        Set character alignment (usually for character creation).
        
        Args:
            new_alignment: New alignment to set
            
        Returns:
            True if alignment was changed successfully
        """
        if new_alignment != self.alignment:
            self.alignment = new_alignment
            self.alignment_history.append(new_alignment)
            # Reset reputation to match new alignment
            self.reputation = self.alignment_system.get_starting_reputation(new_alignment)
            return True
        return False
    
    def get_reputation(self, faction: str) -> int:
        """Get reputation with a specific faction."""
        return self.reputation.get(faction, 0)
    
    def get_all_reputation(self) -> Dict[str, int]:
        """Get all faction reputation values."""
        return self.reputation.copy()
    
    def modify_reputation(self, faction: str, change: int) -> int:
        """
        Modify reputation with a faction.
        
        Args:
            faction: Faction name
            change: Reputation change (positive or negative)
            
        Returns:
            New reputation value
        """
        if faction not in self.reputation:
            self.reputation[faction] = 0
        
        self.reputation[faction] += change
        
        # Clamp reputation to valid range (-100 to +100)
        self.reputation[faction] = max(-100, min(100, self.reputation[faction]))
        
        return self.reputation[faction]
    
    def get_reputation_description(self, faction: str) -> str:
        """Get text description of reputation level with a faction."""
        rep = self.get_reputation(faction)
        
        if rep >= 80:
            return "Revered"
        elif rep >= 60:
            return "Honored"
        elif rep >= 40:
            return "Respected"
        elif rep >= 20:
            return "Liked"
        elif rep >= 10:
            return "Accepted"
        elif rep >= -10:
            return "Neutral"
        elif rep >= -20:
            return "Disliked"
        elif rep >= -40:
            return "Distrusted"
        elif rep >= -60:
            return "Despised"
        else:
            return "Hated"
    
    def can_use_item(self, item_alignment: Optional[str]) -> Tuple[bool, str]:
        """Check if character can use an item based on alignment."""
        return self.alignment_system.can_use_item(self.alignment, item_alignment)
    
    def get_npc_reaction_modifier(self, npc_alignment: Alignment) -> int:
        """Get reaction modifier when interacting with an NPC."""
        return self.alignment_system.get_reaction_modifier(self.alignment, npc_alignment)
    
    def get_faction_reaction_modifier(self, faction: str) -> int:
        """Get reaction modifier for a specific faction."""
        base_modifier = self.alignment_system.get_faction_reaction(self.alignment, faction)
        reputation_modifier = self._get_reputation_modifier(faction)
        return base_modifier + reputation_modifier
    
    def _get_reputation_modifier(self, faction: str) -> int:
        """Convert reputation to reaction modifier."""
        rep = self.get_reputation(faction)
        
        # Convert reputation to modifier (-3 to +3)
        if rep >= 60:
            return 3
        elif rep >= 30:
            return 2
        elif rep >= 10:
            return 1
        elif rep >= -10:
            return 0
        elif rep >= -30:
            return -1
        elif rep >= -60:
            return -2
        else:
            return -3
    
    def get_alignment_bonuses(self) -> Dict[str, int]:
        """Get stat bonuses from current alignment."""
        return self.alignment_system.get_alignment_bonuses(self.alignment)
    
    def add_alignment_drift(self, action_type: str) -> bool:
        """
        Add alignment drift based on character actions.
        
        Args:
            action_type: Type of action taken
            
        Returns:
            True if alignment changed, False otherwise
        """
        # Add drift points based on action
        drift_map = {
            'help_innocent': {'good': 2, 'evil': -1},
            'kill_innocent': {'evil': 3, 'good': -2},
            'donate_charity': {'good': 1, 'neutral': 1},
            'steal_from_poor': {'evil': 2, 'good': -1},
            'negotiate_peace': {'neutral': 2, 'good': 1, 'evil': -1},
            'murder_for_gain': {'evil': 3, 'good': -2},
            'protect_weak': {'good': 2, 'neutral': 1}
        }
        
        if action_type not in drift_map:
            return False
        
        # Apply drift points
        for alignment_name, points in drift_map[action_type].items():
            self.drift_points[alignment_name] += points
        
        # Check for alignment change (requires significant drift)
        return self._check_alignment_change()
    
    def _check_alignment_change(self) -> bool:
        """Check if accumulated drift points should cause alignment change."""
        current_name = self.alignment.name.lower()
        
        # Require significant drift to change alignment (20+ points)
        for alignment_name, points in self.drift_points.items():
            if alignment_name != current_name and points >= 20:
                # Alignment change threshold reached
                new_alignment = getattr(Alignment, alignment_name.upper())
                old_alignment = self.alignment
                self.alignment = new_alignment
                self.alignment_history.append(new_alignment)
                
                # Reset drift points
                self.drift_points = {'good': 0, 'neutral': 0, 'evil': 0}
                
                return True
        
        return False
    
    def get_alignment_display(self) -> str:
        """Get formatted alignment information for character display."""
        alignment_name = self.alignment_system.get_alignment_display_name(self.alignment)
        description = self.alignment_system.get_alignment_description(self.alignment)
        philosophy = description.get('philosophy', 'Unknown philosophy')
        
        return f"{alignment_name} - \"{philosophy}\""
    
    def get_reputation_display(self) -> List[str]:
        """Get formatted reputation information for character display."""
        display_lines = []
        
        # Show major faction reputations
        major_factions = ['good_faction', 'neutral_faction', 'evil_faction']
        for faction in major_factions:
            if faction in self.reputation:
                rep_value = self.reputation[faction]
                rep_desc = self.get_reputation_description(faction)
                faction_display = faction.replace('_', ' ').title()
                display_lines.append(f"  {faction_display}: {rep_value:+d} ({rep_desc})")
        
        return display_lines
    
    def save_to_dict(self) -> Dict:
        """Serialize alignment data for character save file."""
        return {
            'alignment': self.alignment.name,
            'reputation': self.reputation,
            'alignment_history': [a.name for a in self.alignment_history],
            'drift_points': self.drift_points
        }
    
    @classmethod
    def load_from_dict(cls, data: Dict) -> 'AlignmentManager':
        """Load alignment manager from character save data."""
        alignment_name = data.get('alignment', 'NEUTRAL')
        alignment = getattr(Alignment, alignment_name, Alignment.NEUTRAL)
        
        manager = cls(alignment)
        
        # Load reputation data
        if 'reputation' in data:
            manager.reputation = data['reputation']
        
        # Load alignment history
        if 'alignment_history' in data:
            manager.alignment_history = [
                getattr(Alignment, name, Alignment.NEUTRAL) 
                for name in data['alignment_history']
            ]
        
        # Load drift points
        if 'drift_points' in data:
            manager.drift_points = data['drift_points']
        
        return manager