from characters.base_race import BaseRace
from typing import Dict, Any


class Halfling(BaseRace):
    """Halfling race - small and nimble folk with natural stealth abilities"""
    
    def get_name(self) -> str:
        return "Halfling"
    
    def get_description(self) -> str:
        return "Small and nimble folk with natural stealth abilities"
    
    def get_stat_modifiers(self) -> Dict[str, int]:
        return {
            "strength": -2,
            "dexterity": 3,
            "constitution": -1,
            "intelligence": 0,
            "wisdom": 1,
            "charisma": 0
        }
    
    def get_special_abilities(self) -> Dict[str, Any]:
        return {
            "natural_stealth": {
                "description": "Natural stealth bonuses",
                "bonus": 2
            },
            "small_size": {
                "description": "Small size provides defensive bonuses",
                "ac_bonus": 1
            },
            "luck_bonus": {
                "description": "Natural luck in dangerous situations",
                "bonus_type": "luck"
            }
        }
    
    def get_experience_modifier(self) -> int:
        return 25