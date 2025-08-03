from characters.base_race import BaseRace
from typing import Dict, Any


class Nekojin(BaseRace):
    """Nekojin race - cat-like people from the eastern deserts with natural grace"""
    
    def get_name(self) -> str:
        return "Nekojin"
    
    def get_description(self) -> str:
        return "Cat-like people from the eastern deserts with natural grace"
    
    def get_stat_modifiers(self) -> Dict[str, int]:
        return {
            "strength": -2,
            "dexterity": 3,
            "constitution": -1,
            "intelligence": -1,
            "wisdom": 1,
            "charisma": 2
        }
    
    def get_special_abilities(self) -> Dict[str, Any]:
        return {
            "natural_tracking": {
                "description": "Enhanced tracking abilities",
                "bonus_type": "skill"
            },
            "stealth": {
                "description": "Natural stealth bonuses",
                "bonus": 2
            },
            "fire_resistance": {
                "description": "Natural resistance to fire damage",
                "bonus_type": "resistance"
            },
            "cold_vulnerability": {
                "description": "Increased vulnerability to cold damage",
                "bonus_type": "vulnerability"
            }
        }
    
    def get_experience_modifier(self) -> int:
        return 40