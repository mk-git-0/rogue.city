from .race_human import Human
from .race_elf import Elf
from .race_dark_elf import DarkElf
from .race_half_elf import HalfElf
from .race_dwarf import Dwarf
from .race_gnome import Gnome
from .race_halfling import Halfling
from .race_half_ogre import HalfOgre
from .race_goblin import Goblin
from .race_kang import Kang
from .race_nekojin import Nekojin
from .race_gaunt_one import GauntOne

# Race registry for easy access
RACE_REGISTRY = {
    "human": Human,
    "elf": Elf,
    "dark_elf": DarkElf,
    "half_elf": HalfElf,
    "dwarf": Dwarf,
    "gnome": Gnome,
    "halfling": Halfling,
    "half_ogre": HalfOgre,
    "goblin": Goblin,
    "kang": Kang,
    "nekojin": Nekojin,
    "gaunt_one": GauntOne
}

def get_race_class(race_id: str):
    """Get a race class by its ID"""
    return RACE_REGISTRY.get(race_id)

def get_all_races():
    """Get all available race classes"""
    return list(RACE_REGISTRY.values())

def get_race_ids():
    """Get all available race IDs"""
    return list(RACE_REGISTRY.keys())