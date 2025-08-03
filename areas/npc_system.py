"""
NPC system for Rogue City with alignment-based interactions.

Manages NPCs, their alignments, faction affiliations, and dynamic
reactions based on character alignment and reputation.
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
from core.alignment_system import Alignment, AlignmentSystem
from characters.alignment_manager import AlignmentManager


class NPCType(Enum):
    """Types of NPCs with different behavior patterns."""
    MERCHANT = "merchant"
    GUARD = "guard"
    PRIEST = "priest"
    SCHOLAR = "scholar"
    THIEF = "thief"
    NECROMANCER = "necromancer"
    CITIZEN = "citizen"
    NOBLE = "noble"


class NPCReaction(Enum):
    """NPC reaction levels to characters."""
    HOSTILE = -3
    UNFRIENDLY = -2
    DISTRUSTFUL = -1
    NEUTRAL = 0
    FRIENDLY = 1
    HELPFUL = 2
    DEVOTED = 3


class NPC:
    """
    Individual NPC with alignment, faction, and reaction system.
    """
    
    def __init__(self, name: str, npc_type: NPCType, alignment: Alignment, 
                 faction: str, base_reaction: int = 0):
        """
        Initialize an NPC.
        
        Args:
            name: NPC's name
            npc_type: Type of NPC (affects behavior)
            alignment: NPC's moral alignment
            faction: Faction the NPC belongs to
            base_reaction: Base reaction modifier (-3 to +3)
        """
        self.name = name
        self.npc_type = npc_type
        self.alignment = alignment
        self.faction = faction
        self.base_reaction = base_reaction
        
        # NPC-specific reputation with individual characters
        self.character_reputation: Dict[str, int] = {}
        
        # Dialogue options based on alignment and reputation
        self.dialogue_options = self._initialize_dialogue()
    
    def _initialize_dialogue(self) -> Dict[str, List[str]]:
        """Initialize alignment-specific dialogue options."""
        return {
            'greeting_good': [
                "Greetings, friend! How may I assist you?",
                "Well met, noble soul!",
                "The light shines upon you, traveler."
            ],
            'greeting_neutral': [
                "Hello there.",
                "What brings you here?",
                "Good day to you."
            ],
            'greeting_evil': [
                "What do you want?",
                "Keep moving, dark one.",
                "I have no business with your kind."
            ],
            'hostile': [
                "Get away from me!",
                "Guards! Guards!",
                "I want nothing to do with you!"
            ],
            'friendly': [
                "Always a pleasure to see you!",
                "What can I do for my friend?",
                "You're welcome here anytime."
            ]
        }
    
    def get_reaction_to_character(self, character_alignment_manager: AlignmentManager) -> NPCReaction:
        """
        Calculate NPC's reaction to a character.
        
        Args:
            character_alignment_manager: Character's alignment manager
            
        Returns:
            NPCReaction enum representing overall reaction
        """
        # Start with base reaction
        total_reaction = self.base_reaction
        
        # Add alignment-based modifier
        alignment_modifier = character_alignment_manager.get_npc_reaction_modifier(self.alignment)
        total_reaction += alignment_modifier
        
        # Add faction reputation modifier
        faction_modifier = character_alignment_manager.get_faction_reaction_modifier(self.faction)
        total_reaction += faction_modifier
        
        # Add individual reputation if exists
        char_name = getattr(character_alignment_manager, 'character_name', 'Unknown')
        if char_name in self.character_reputation:
            # Convert individual reputation to modifier
            individual_rep = self.character_reputation[char_name]
            rep_modifier = individual_rep // 20  # -5 to +5 range
            total_reaction += rep_modifier
        
        # Convert total to NPCReaction enum
        total_reaction = max(-3, min(3, total_reaction))  # Clamp to valid range
        return NPCReaction(total_reaction)
    
    def get_greeting(self, character_alignment_manager: AlignmentManager) -> str:
        """Get appropriate greeting based on character alignment and reaction."""
        reaction = self.get_reaction_to_character(character_alignment_manager)
        char_alignment = character_alignment_manager.get_alignment()
        
        # Choose dialogue based on reaction level
        if reaction.value <= -2:
            dialogue_key = 'hostile'
        elif reaction.value >= 2:
            dialogue_key = 'friendly'
        else:
            # Use alignment-based greeting
            if char_alignment == Alignment.GOOD:
                dialogue_key = 'greeting_good'
            elif char_alignment == Alignment.EVIL:
                dialogue_key = 'greeting_evil'
            else:
                dialogue_key = 'greeting_neutral'
        
        # Select appropriate dialogue
        import random
        dialogues = self.dialogue_options.get(dialogue_key, ["..."])
        return random.choice(dialogues)
    
    def modify_individual_reputation(self, character_name: str, change: int) -> int:
        """Modify this NPC's personal reputation with a specific character."""
        if character_name not in self.character_reputation:
            self.character_reputation[character_name] = 0
        
        self.character_reputation[character_name] += change
        self.character_reputation[character_name] = max(-100, min(100, self.character_reputation[character_name]))
        
        return self.character_reputation[character_name]
    
    def can_trade_with(self, character_alignment_manager: AlignmentManager) -> Tuple[bool, str]:
        """Check if NPC will trade with character."""
        reaction = self.get_reaction_to_character(character_alignment_manager)
        
        if reaction.value <= -2:
            return False, "I refuse to do business with you!"
        elif reaction.value <= -1:
            return True, "I suppose I can trade... but my prices are higher for your kind."
        else:
            return True, "I'm happy to trade with you!"
    
    def get_service_modifier(self, character_alignment_manager: AlignmentManager) -> float:
        """Get price/service modifier based on reaction."""
        reaction = self.get_reaction_to_character(character_alignment_manager)
        
        # Price multipliers based on reaction
        modifiers = {
            NPCReaction.HOSTILE: 3.0,      # Refuses or extremely expensive
            NPCReaction.UNFRIENDLY: 1.5,   # 50% markup
            NPCReaction.DISTRUSTFUL: 1.2,  # 20% markup
            NPCReaction.NEUTRAL: 1.0,      # Normal prices
            NPCReaction.FRIENDLY: 0.9,     # 10% discount
            NPCReaction.HELPFUL: 0.8,      # 20% discount
            NPCReaction.DEVOTED: 0.7       # 30% discount
        }
        
        return modifiers.get(reaction, 1.0)


class NPCSystem:
    """
    Manages all NPCs and their interactions with characters.
    """
    
    def __init__(self):
        """Initialize the NPC system."""
        self.npcs: Dict[str, NPC] = {}
        self.alignment_system = AlignmentSystem()
        
        # Initialize some default NPCs
        self._create_default_npcs()
    
    def _create_default_npcs(self):
        """Create default NPCs for testing and basic gameplay."""
        # Town Guard (Good alignment, guards faction)
        guard = NPC("Captain Aldric", NPCType.GUARD, Alignment.GOOD, "town_guards", base_reaction=1)
        self.add_npc("town_guard_captain", guard)
        
        # Merchant (Neutral alignment, merchants faction)
        merchant = NPC("Merchant Gareth", NPCType.MERCHANT, Alignment.NEUTRAL, "merchants", base_reaction=0)
        self.add_npc("general_merchant", merchant)
        
        # Priest (Good alignment, priests faction)
        priest = NPC("Brother Marcus", NPCType.PRIEST, Alignment.GOOD, "priests", base_reaction=1)
        self.add_npc("temple_priest", priest)
        
        # Thief (Evil alignment, thieves guild faction)
        thief = NPC("Shadowfinger", NPCType.THIEF, Alignment.EVIL, "thieves_guild", base_reaction=-1)
        self.add_npc("guild_thief", thief)
        
        # Scholar (Neutral alignment, scholars faction)
        scholar = NPC("Sage Eldwin", NPCType.SCHOLAR, Alignment.NEUTRAL, "scholars", base_reaction=0)
        self.add_npc("library_scholar", scholar)
    
    def add_npc(self, npc_id: str, npc: NPC):
        """Add an NPC to the system."""
        self.npcs[npc_id] = npc
    
    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """Get an NPC by ID."""
        return self.npcs.get(npc_id)
    
    def get_npcs_in_area(self, area_id: str) -> List[NPC]:
        """Get all NPCs in a specific area (placeholder for future area system)."""
        # This would be expanded when areas are fully implemented
        # For now, return all NPCs
        return list(self.npcs.values())
    
    def calculate_reaction(self, character_alignment: Alignment, npc_alignment: Alignment) -> int:
        """Calculate base reaction between character and NPC alignments."""
        return self.alignment_system.get_reaction_modifier(character_alignment, npc_alignment)
    
    def process_character_action(self, action_type: str, character_alignment_manager: AlignmentManager, 
                               affected_npcs: List[str] = None):
        """
        Process character action that affects NPC relationships.
        
        Args:
            action_type: Type of action ('help', 'attack', 'steal', etc.)
            character_alignment_manager: Character's alignment manager
            affected_npcs: List of NPC IDs affected by the action
        """
        if affected_npcs is None:
            affected_npcs = []
        
        char_name = getattr(character_alignment_manager, 'character_name', 'Unknown')
        
        # Define reputation changes for different actions
        reputation_changes = {
            'help_npc': 10,
            'attack_npc': -20,
            'steal_from_npc': -15,
            'complete_quest': 15,
            'fail_quest': -5,
            'protect_npc': 20,
            'betray_npc': -30
        }
        
        change = reputation_changes.get(action_type, 0)
        if change == 0:
            return
        
        # Apply reputation change to affected NPCs
        for npc_id in affected_npcs:
            npc = self.get_npc(npc_id)
            if npc:
                npc.modify_individual_reputation(char_name, change)
                
                # Also affect faction reputation through alignment manager
                character_alignment_manager.modify_reputation(npc.faction, change // 2)
    
    def get_npc_list_display(self, character_alignment_manager: AlignmentManager) -> List[str]:
        """Get formatted list of NPCs and their reactions to character."""
        display_lines = []
        
        for npc_id, npc in self.npcs.items():
            reaction = npc.get_reaction_to_character(character_alignment_manager)
            reaction_name = reaction.name.title()
            
            line = f"{npc.name} ({npc.npc_type.value.title()}) - {reaction_name}"
            display_lines.append(line)
        
        return display_lines
    
    def save_to_dict(self) -> Dict:
        """Serialize NPC system for save games."""
        npc_data = {}
        for npc_id, npc in self.npcs.items():
            npc_data[npc_id] = {
                'name': npc.name,
                'type': npc.npc_type.value,
                'alignment': npc.alignment.name,
                'faction': npc.faction,
                'base_reaction': npc.base_reaction,
                'character_reputation': npc.character_reputation
            }
        return npc_data
    
    def load_from_dict(self, data: Dict):
        """Load NPC system from save data."""
        for npc_id, npc_data in data.items():
            npc_type = NPCType(npc_data['type'])
            alignment = getattr(Alignment, npc_data['alignment'])
            
            npc = NPC(
                npc_data['name'],
                npc_type,
                alignment,
                npc_data['faction'],
                npc_data.get('base_reaction', 0)
            )
            
            # Load individual character reputations
            npc.character_reputation = npc_data.get('character_reputation', {})
            
            self.add_npc(npc_id, npc)