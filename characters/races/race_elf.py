from characters.base_race import BaseRace
from typing import Dict, Any


class Elf(BaseRace):
    """Elf race - ancient magical race with natural spellcasting abilities"""
    
    def get_name(self) -> str:
        return "Elf"
    
    def get_description(self) -> str:
        return "Ancient magical race with natural spellcasting abilities"
    
    def get_stat_modifiers(self) -> Dict[str, int]:
        return {
            "strength": -1,
            "dexterity": 0,
            "constitution": -1,
            "intelligence": 2,
            "wisdom": 2,
            "charisma": 0
        }
    
    def get_special_abilities(self) -> Dict[str, Any]:
        return {
            "nightvision": {
                "description": "Can see in dark areas without light sources",
                "range": "normal"
            },
            "spell_power": {
                "description": "Natural magical enhancement",
                "bonus": 1
            },
            "nature_affinity": {
                "description": "Natural connection to woodland environments",
                "bonus_type": "environmental"
            }
        }
    
    def get_experience_modifier(self) -> int:
        return 25