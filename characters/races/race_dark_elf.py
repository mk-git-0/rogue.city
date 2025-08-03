from characters.base_race import BaseRace
from typing import Dict, Any


class DarkElf(BaseRace):
    """Dark-Elf race - brilliant arcane masters with unmatched magical abilities"""
    
    def get_name(self) -> str:
        return "Dark-Elf"
    
    def get_description(self) -> str:
        return "Brilliant arcane masters with unmatched magical abilities"
    
    def get_stat_modifiers(self) -> Dict[str, int]:
        return {
            "strength": -2,
            "dexterity": 0,
            "constitution": -1,
            "intelligence": 3,
            "wisdom": 1,
            "charisma": 1
        }
    
    def get_special_abilities(self) -> Dict[str, Any]:
        return {
            "perfect_darkvision": {
                "description": "Can see in magical darkness",
                "range": "perfect"
            },
            "spell_power": {
                "description": "Superior magical enhancement",
                "bonus": 2
            },
            "arcane_mastery": {
                "description": "Natural understanding of arcane magic",
                "bonus_type": "magical"
            }
        }
    
    def get_experience_modifier(self) -> int:
        return 50