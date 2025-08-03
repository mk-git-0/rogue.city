from characters.base_race import BaseRace
from typing import Dict, Any


class GauntOne(BaseRace):
    """Gaunt One race - mysterious beings with perfect vision and supernatural perception"""
    
    def get_name(self) -> str:
        return "Gaunt One"
    
    def get_description(self) -> str:
        return "Mysterious beings with perfect vision and supernatural perception"
    
    def get_stat_modifiers(self) -> Dict[str, int]:
        return {
            "strength": -2,
            "dexterity": 0,
            "constitution": -2,
            "intelligence": 4,
            "wisdom": 2,
            "charisma": -1
        }
    
    def get_special_abilities(self) -> Dict[str, Any]:
        return {
            "perfect_darkvision": {
                "description": "Perfect vision in any darkness",
                "range": "perfect"
            },
            "heightened_perception": {
                "description": "Supernatural awareness and perception",
                "bonus": 3
            },
            "magical_sight": {
                "description": "Can see magical auras and effects",
                "bonus_type": "magical"
            }
        }
    
    def get_experience_modifier(self) -> int:
        return 50