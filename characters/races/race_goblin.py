from characters.base_race import BaseRace
from typing import Dict, Any


class Goblin(BaseRace):
    """Goblin race - small but cunning creatures with natural stealth abilities"""
    
    def get_name(self) -> str:
        return "Goblin"
    
    def get_description(self) -> str:
        return "Small but cunning creatures with natural stealth abilities"
    
    def get_stat_modifiers(self) -> Dict[str, int]:
        return {
            "strength": -2,
            "dexterity": 2,
            "constitution": 0,
            "intelligence": 1,
            "wisdom": 1,
            "charisma": -1
        }
    
    def get_special_abilities(self) -> Dict[str, Any]:
        return {
            "natural_stealth": {
                "description": "Natural stealth bonuses",
                "bonus": 1
            },
            "darkvision": {
                "description": "Can see in darkness",
                "range": "normal"
            },
            "cunning": {
                "description": "Natural cunning and trickery",
                "bonus_type": "mental"
            }
        }
    
    def get_experience_modifier(self) -> int:
        return 15