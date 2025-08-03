from characters.base_race import BaseRace
from typing import Dict, Any


class Human(BaseRace):
    """Human race - balanced and versatile, the baseline for all other races"""
    
    def get_name(self) -> str:
        return "Human"
    
    def get_description(self) -> str:
        return "Balanced and versatile, humans adapt to any profession"
    
    def get_stat_modifiers(self) -> Dict[str, int]:
        return {
            "strength": 0,
            "dexterity": 0,
            "constitution": 0,
            "intelligence": 0,
            "wisdom": 0,
            "charisma": 0
        }
    
    def get_special_abilities(self) -> Dict[str, Any]:
        return {
            "versatility": {
                "description": "Can excel in any class",
                "bonus_type": "general"
            }
        }
    
    def get_experience_modifier(self) -> int:
        return 0