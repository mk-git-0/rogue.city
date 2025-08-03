from characters.base_race import BaseRace
from typing import Dict, Any


class Dwarf(BaseRace):
    """Dwarf race - hardy mountain folk with natural resistance to magic and poison"""
    
    def get_name(self) -> str:
        return "Dwarf"
    
    def get_description(self) -> str:
        return "Hardy mountain folk with natural resistance to magic and poison"
    
    def get_stat_modifiers(self) -> Dict[str, int]:
        return {
            "strength": 3,
            "dexterity": -2,
            "constitution": 2,
            "intelligence": 0,
            "wisdom": 0,
            "charisma": -1
        }
    
    def get_special_abilities(self) -> Dict[str, Any]:
        return {
            "magic_resistance": {
                "description": "Natural resistance to magical effects",
                "bonus": 2
            },
            "underground_vision": {
                "description": "Can navigate underground environments",
                "bonus_type": "environmental"
            },
            "poison_resistance": {
                "description": "Natural resistance to poisons and toxins",
                "bonus_type": "resistance"
            }
        }
    
    def get_experience_modifier(self) -> int:
        return 20