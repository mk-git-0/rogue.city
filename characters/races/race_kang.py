from characters.base_race import BaseRace
from typing import Dict, Any


class Kang(BaseRace):
    """Kang race - snake-lizard hybrids from distant swamps with natural armor"""
    
    def get_name(self) -> str:
        return "Kang"
    
    def get_description(self) -> str:
        return "Snake-lizard hybrids from distant swamps with natural armor"
    
    def get_stat_modifiers(self) -> Dict[str, int]:
        return {
            "strength": 2,
            "dexterity": -1,
            "constitution": 1,
            "intelligence": 0,
            "wisdom": 1,
            "charisma": -2
        }
    
    def get_special_abilities(self) -> Dict[str, Any]:
        return {
            "poison_resistance": {
                "description": "Natural resistance to poisons",
                "bonus_type": "resistance"
            },
            "natural_armor": {
                "description": "Scaly skin provides armor bonus",
                "ac_bonus": 1
            },
            "swamp_adaptation": {
                "description": "Natural adaptation to swamp environments",
                "bonus_type": "environmental"
            }
        }
    
    def get_experience_modifier(self) -> int:
        return 35