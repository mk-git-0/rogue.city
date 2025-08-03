from characters.base_race import BaseRace
from typing import Dict, Any


class Gnome(BaseRace):
    """Gnome race - small but clever inventors with natural mechanical abilities"""
    
    def get_name(self) -> str:
        return "Gnome"
    
    def get_description(self) -> str:
        return "Small but clever inventors with natural mechanical abilities"
    
    def get_stat_modifiers(self) -> Dict[str, int]:
        return {
            "strength": -2,
            "dexterity": 1,
            "constitution": -1,
            "intelligence": 2,
            "wisdom": 1,
            "charisma": 0
        }
    
    def get_special_abilities(self) -> Dict[str, Any]:
        return {
            "small_size": {
                "description": "Small size provides defensive bonuses",
                "ac_bonus": 1
            },
            "mechanical_aptitude": {
                "description": "Natural understanding of mechanical devices",
                "bonus_type": "skill"
            },
            "keen_senses": {
                "description": "Enhanced perception and awareness",
                "bonus_type": "perception"
            }
        }
    
    def get_experience_modifier(self) -> int:
        return 30