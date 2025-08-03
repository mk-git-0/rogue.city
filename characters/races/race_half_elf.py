from characters.base_race import BaseRace
from typing import Dict, Any


class HalfElf(BaseRace):
    """Half-Elf race - combining human adaptability with elven magical heritage"""
    
    def get_name(self) -> str:
        return "Half-Elf"
    
    def get_description(self) -> str:
        return "Combining human adaptability with elven magical heritage"
    
    def get_stat_modifiers(self) -> Dict[str, int]:
        return {
            "strength": 0,
            "dexterity": 0,
            "constitution": -1,
            "intelligence": 1,
            "wisdom": 1,
            "charisma": 1
        }
    
    def get_special_abilities(self) -> Dict[str, Any]:
        return {
            "nightvision": {
                "description": "Can see in dark areas without light sources",
                "range": "normal"
            },
            "versatility_bonus": {
                "description": "Inherits human adaptability with elven heritage",
                "bonus_type": "hybrid"
            }
        }
    
    def get_experience_modifier(self) -> int:
        return 15