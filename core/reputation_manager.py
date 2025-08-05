"""
Advanced Reputation Manager for Rogue City NPC interactions.

Extends the existing alignment system with comprehensive faction tracking,
dynamic reputation effects, and social consequence modeling.
"""

from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import json
from core.alignment_system import Alignment


class ReputationLevel(Enum):
    """Reputation levels with NPCs and factions."""
    HATED = -100      # Hostile on sight
    DESPISED = -75    # Extremely negative reactions
    DISLIKED = -50    # Strong negative reactions
    UNFRIENDLY = -25  # Mild negative reactions
    NEUTRAL = 0       # Standard reactions
    LIKED = 25        # Mild positive reactions
    RESPECTED = 50    # Strong positive reactions
    REVERED = 75      # Extremely positive reactions
    LEGENDARY = 100   # Mythical status


class FactionType(Enum):
    """Types of factions with different characteristics."""
    LAWFUL = "lawful"          # Town guards, paladins, priests
    CHAOTIC = "chaotic"        # Thieves, rogues, rebels
    NEUTRAL = "neutral"        # Merchants, scholars, citizens
    MILITARY = "military"      # Knights, warriors, soldiers
    MAGICAL = "magical"        # Mages, witches, necromancers
    RELIGIOUS = "religious"    # Priests, templars, cultists
    CRIMINAL = "criminal"      # Thieves guild, assassins, bandits
    MERCHANT = "merchant"      # Trading guilds, shopkeepers


class Faction:
    """Represents a faction with alignment tendencies and relationships."""
    
    def __init__(self, faction_id: str, name: str, faction_type: FactionType, 
                 alignment_tendency: Alignment, description: str = ""):
        self.faction_id = faction_id
        self.name = name
        self.faction_type = faction_type
        self.alignment_tendency = alignment_tendency
        self.description = description
        
        # Relationships with other factions
        self.allied_factions: List[str] = []
        self.enemy_factions: List[str] = []
        self.neutral_factions: List[str] = []
        
        # Faction-specific modifiers
        self.reputation_decay_rate = 0  # How fast reputation fades over time
        self.action_multiplier = 1.0    # Multiplier for reputation changes
        
    def get_base_reaction_to_alignment(self, character_alignment: Alignment) -> int:
        """Get base reaction modifier based on character alignment."""
        if self.alignment_tendency == character_alignment:
            return 10  # Same alignment bonus
        elif self.alignment_tendency == Alignment.NEUTRAL or character_alignment == Alignment.NEUTRAL:
            return 0   # Neutral doesn't conflict
        else:
            return -10  # Opposing alignment penalty


class ReputationManager:
    """Advanced reputation system managing faction relationships and consequences."""
    
    def __init__(self, character_name: str):
        self.character_name = character_name
        self.faction_reputations: Dict[str, int] = {}
        self.individual_reputations: Dict[str, int] = {}  # NPC-specific reputation
        self.faction_data: Dict[str, Faction] = {}
        self.reputation_history: List[Dict[str, Any]] = []
        
        # Load faction definitions
        self._load_faction_data()
        
        # Initialize reputation with all factions
        self._initialize_faction_reputations()
    
    def _load_faction_data(self):
        """Load faction definitions from data files."""
        try:
            with open('data/npcs/faction_definitions.json', 'r') as f:
                data = json.load(f)
                for faction_id, faction_info in data.items():
                    faction = Faction(
                        faction_id=faction_id,
                        name=faction_info['name'],
                        faction_type=FactionType(faction_info['type']),
                        alignment_tendency=getattr(Alignment, faction_info['alignment']),
                        description=faction_info.get('description', '')
                    )
                    
                    # Load relationships
                    faction.allied_factions = faction_info.get('allies', [])
                    faction.enemy_factions = faction_info.get('enemies', [])
                    faction.neutral_factions = faction_info.get('neutral', [])
                    
                    # Load modifiers
                    faction.reputation_decay_rate = faction_info.get('decay_rate', 0)
                    faction.action_multiplier = faction_info.get('action_multiplier', 1.0)
                    
                    self.faction_data[faction_id] = faction
                    
        except FileNotFoundError:
            self._create_default_factions()
    
    def _create_default_factions(self):
        """Create default faction data if files don't exist."""
        default_factions = {
            'town_guards': Faction('town_guards', 'Town Guard', FactionType.LAWFUL, Alignment.GOOD),
            'merchants': Faction('merchants', 'Merchant Guild', FactionType.MERCHANT, Alignment.NEUTRAL),
            'priests': Faction('priests', 'Temple of Light', FactionType.RELIGIOUS, Alignment.GOOD),
            'thieves_guild': Faction('thieves_guild', 'Thieves Guild', FactionType.CRIMINAL, Alignment.EVIL),
            'scholars': Faction('scholars', 'Academy of Learning', FactionType.MAGICAL, Alignment.NEUTRAL),
            'nobles': Faction('nobles', 'Noble Houses', FactionType.NEUTRAL, Alignment.NEUTRAL),
            'common_folk': Faction('common_folk', 'Common Citizens', FactionType.NEUTRAL, Alignment.NEUTRAL)
        }
        
        # Set up basic relationships
        default_factions['town_guards'].enemy_factions = ['thieves_guild']
        default_factions['town_guards'].allied_factions = ['priests', 'nobles']
        
        default_factions['thieves_guild'].enemy_factions = ['town_guards', 'priests']
        default_factions['thieves_guild'].neutral_factions = ['merchants']
        
        default_factions['priests'].allied_factions = ['town_guards']
        default_factions['priests'].enemy_factions = ['thieves_guild']
        
        default_factions['merchants'].neutral_factions = ['thieves_guild', 'town_guards', 'priests']
        
        self.faction_data = default_factions
    
    def _initialize_faction_reputations(self):
        """Initialize reputation with all factions at neutral."""
        for faction_id in self.faction_data.keys():
            if faction_id not in self.faction_reputations:
                self.faction_reputations[faction_id] = 0
    
    def get_reputation(self, faction_id: str) -> int:
        """Get current reputation with a faction."""
        return self.faction_reputations.get(faction_id, 0)
    
    def get_reputation_level(self, faction_id: str) -> ReputationLevel:
        """Get reputation level enum for a faction."""
        rep = self.get_reputation(faction_id)
        
        if rep >= 100:
            return ReputationLevel.LEGENDARY
        elif rep >= 75:
            return ReputationLevel.REVERED
        elif rep >= 50:
            return ReputationLevel.RESPECTED
        elif rep >= 25:
            return ReputationLevel.LIKED
        elif rep >= -25:
            return ReputationLevel.NEUTRAL
        elif rep >= -50:
            return ReputationLevel.UNFRIENDLY
        elif rep >= -75:
            return ReputationLevel.DISLIKED
        elif rep >= -100:
            return ReputationLevel.DESPISED
        else:
            return ReputationLevel.HATED
    
    def modify_reputation(self, faction_id: str, change: int, reason: str = "") -> int:
        """
        Modify reputation with a faction and handle cascading effects.
        
        Args:
            faction_id: ID of the faction
            change: Amount to change reputation (positive or negative)
            reason: Reason for the change (for history tracking)
            
        Returns:
            New reputation value
        """
        if faction_id not in self.faction_data:
            return 0
        
        faction = self.faction_data[faction_id]
        
        # Apply faction-specific multiplier
        actual_change = int(change * faction.action_multiplier)
        
        # Update reputation
        old_rep = self.faction_reputations.get(faction_id, 0)
        new_rep = max(-150, min(150, old_rep + actual_change))  # Cap at -150 to +150
        self.faction_reputations[faction_id] = new_rep
        
        # Record history
        self.reputation_history.append({
            'faction': faction_id,
            'change': actual_change,
            'old_value': old_rep,
            'new_value': new_rep,
            'reason': reason
        })
        
        # Handle cascading effects
        self._handle_faction_cascades(faction_id, actual_change, reason)
        
        return new_rep
    
    def _handle_faction_cascades(self, faction_id: str, change: int, reason: str):
        """Handle reputation changes cascading to allied/enemy factions."""
        if faction_id not in self.faction_data:
            return
        
        faction = self.faction_data[faction_id]
        cascade_strength = max(1, abs(change) // 3)  # Cascades are weaker
        
        # Positive reputation with allies
        if change > 0:
            for ally_id in faction.allied_factions:
                if ally_id in self.faction_reputations:
                    cascade_change = cascade_strength // 2  # Even weaker for allies
                    old_rep = self.faction_reputations[ally_id]
                    new_rep = max(-150, min(150, old_rep + cascade_change))
                    self.faction_reputations[ally_id] = new_rep
                    
                    self.reputation_history.append({
                        'faction': ally_id,
                        'change': cascade_change,
                        'old_value': old_rep,
                        'new_value': new_rep,
                        'reason': f"Allied with {faction.name}: {reason}"
                    })
        
        # Negative reputation with enemies
        elif change < 0:
            for enemy_id in faction.enemy_factions:
                if enemy_id in self.faction_reputations:
                    cascade_change = cascade_strength // 3  # Small positive gain with enemies
                    old_rep = self.faction_reputations[enemy_id]
                    new_rep = max(-150, min(150, old_rep + cascade_change))
                    self.faction_reputations[enemy_id] = new_rep
                    
                    self.reputation_history.append({
                        'faction': enemy_id,
                        'change': cascade_change,
                        'old_value': old_rep,
                        'new_value': new_rep,
                        'reason': f"Enemy of {faction.name}: {reason}"
                    })
    
    def get_faction_reaction_modifier(self, faction_id: str, character_alignment: Alignment) -> int:
        """Get total reaction modifier for a faction including alignment and reputation."""
        if faction_id not in self.faction_data:
            return 0
        
        faction = self.faction_data[faction_id]
        
        # Base alignment reaction
        alignment_mod = faction.get_base_reaction_to_alignment(character_alignment)
        
        # Reputation modifier (scaled down for reaction)
        rep_mod = self.get_reputation(faction_id) // 10  # -15 to +15 range
        
        return alignment_mod + rep_mod
    
    def get_individual_reputation(self, npc_id: str) -> int:
        """Get reputation with a specific NPC."""
        return self.individual_reputations.get(npc_id, 0)
    
    def modify_individual_reputation(self, npc_id: str, change: int, reason: str = "") -> int:
        """Modify reputation with a specific NPC."""
        old_rep = self.individual_reputations.get(npc_id, 0)
        new_rep = max(-100, min(100, old_rep + change))
        self.individual_reputations[npc_id] = new_rep
        
        # Record history
        self.reputation_history.append({
            'npc': npc_id,
            'change': change,
            'old_value': old_rep,
            'new_value': new_rep,
            'reason': reason
        })
        
        return new_rep
    
    def get_reputation_summary(self) -> Dict[str, Any]:
        """Get a summary of all reputation standings."""
        summary = {
            'factions': {},
            'individuals': {},
            'notable_standings': []
        }
        
        # Faction standings
        for faction_id, reputation in self.faction_reputations.items():
            if faction_id in self.faction_data:
                faction = self.faction_data[faction_id]
                level = self.get_reputation_level(faction_id)
                summary['factions'][faction_id] = {
                    'name': faction.name,
                    'reputation': reputation,
                    'level': level.name,
                    'description': level.name.replace('_', ' ').title()
                }
                
                # Note significant standings
                if abs(reputation) >= 50:
                    summary['notable_standings'].append({
                        'faction': faction.name,
                        'level': level.name.replace('_', ' ').title(),
                        'reputation': reputation
                    })
        
        # Individual standings (only notable ones)
        for npc_id, reputation in self.individual_reputations.items():
            if abs(reputation) >= 20:
                summary['individuals'][npc_id] = {
                    'reputation': reputation,
                    'description': 'Personal relationship'
                }
        
        return summary
    
    def get_faction_by_id(self, faction_id: str) -> Optional[Faction]:
        """Get faction object by ID."""
        return self.faction_data.get(faction_id)
    
    def save_to_dict(self) -> Dict[str, Any]:
        """Serialize reputation manager for save games."""
        return {
            'character_name': self.character_name,
            'faction_reputations': self.faction_reputations,
            'individual_reputations': self.individual_reputations,
            'reputation_history': self.reputation_history[-50:]  # Keep last 50 entries
        }
    
    def load_from_dict(self, data: Dict[str, Any]):
        """Load reputation manager from save data."""
        self.character_name = data.get('character_name', self.character_name)
        self.faction_reputations = data.get('faction_reputations', {})
        self.individual_reputations = data.get('individual_reputations', {})
        self.reputation_history = data.get('reputation_history', [])
        
        # Ensure all factions are initialized
        self._initialize_faction_reputations()
    
    def apply_time_decay(self, days_passed: int):
        """Apply reputation decay over time (for dynamic world)."""
        for faction_id, faction in self.faction_data.items():
            if faction.reputation_decay_rate > 0:
                current_rep = self.faction_reputations.get(faction_id, 0)
                if current_rep != 0:  # Only decay non-neutral reputations
                    decay = faction.reputation_decay_rate * days_passed
                    if current_rep > 0:
                        new_rep = max(0, current_rep - decay)
                    else:
                        new_rep = min(0, current_rep + decay)
                    
                    if new_rep != current_rep:
                        self.faction_reputations[faction_id] = int(new_rep)
                        self.reputation_history.append({
                            'faction': faction_id,
                            'change': int(new_rep - current_rep),
                            'old_value': current_rep,
                            'new_value': int(new_rep),
                            'reason': f'Time decay ({days_passed} days)'
                        })
    
    def get_price_modifier(self, faction_id: str) -> float:
        """Get price modifier for merchant transactions based on reputation."""
        rep_level = self.get_reputation_level(faction_id)
        
        modifiers = {
            ReputationLevel.LEGENDARY: 0.5,    # 50% discount
            ReputationLevel.REVERED: 0.7,      # 30% discount
            ReputationLevel.RESPECTED: 0.8,    # 20% discount
            ReputationLevel.LIKED: 0.9,        # 10% discount
            ReputationLevel.NEUTRAL: 1.0,      # Normal price
            ReputationLevel.UNFRIENDLY: 1.2,   # 20% markup
            ReputationLevel.DISLIKED: 1.5,     # 50% markup
            ReputationLevel.DESPISED: 2.0,     # 100% markup
            ReputationLevel.HATED: 3.0         # 200% markup
        }
        
        return modifiers.get(rep_level, 1.0)