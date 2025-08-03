from characters.base_race import BaseRace
from typing import Dict, Any


class HalfOgre(BaseRace):
    """Half-Ogre race - massive and strong but lacking in mental faculties"""
    
    def get_name(self) -> str:
        return "Half-Ogre"
    
    def get_description(self) -> str:
        return "Massive and strong but lacking in mental faculties"
    
    def get_stat_modifiers(self) -> Dict[str, int]:
        return {
            "strength": 4,
            "dexterity": 0,
            "constitution": 2,
            "intelligence": -3,
            "wisdom": -2,
            "charisma": -1
        }
    
    def get_special_abilities(self) -> Dict[str, Any]:
        return {
            "intimidation": {
                "description": "Natural intimidating presence",
                "bonus_type": "social"
            },
            "massive_size": {
                "description": "Large size provides reach advantages",
                "bonus_type": "size"
            },
            "damage_resistance": {
                "description": "Natural resistance to physical damage",
                "bonus_type": "resistance"
            }
        }
    
    def get_experience_modifier(self) -> int:
        return -10