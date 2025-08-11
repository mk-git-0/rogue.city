import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from characters.class_knight import Knight
from core.alignment_system import Alignment
from core.item_factory import ItemFactory


def test_knight_doubles_shield_ac_bonus():
    k = Knight('Sir Test', alignment=Alignment.GOOD)
    k.initialize_item_systems()

    factory = ItemFactory()
    shield = factory.create_item('wooden_shield')
    k.inventory_system.add_item(shield)
    k.equipment_system.equip_item(shield.item_id)

    base_ac = 10 + (k.stats['dexterity'] - 10) // 2
    k.calculate_derived_stats()

    # Knight calculate_derived_stats applies extra shield AC via multiplier
    # Total AC should exceed base_ac + shield base bonus
    shield_bonus = k.equipment_system.get_shield_ac_bonus()
    assert k.armor_class >= base_ac + shield_bonus + 1  # additional knight bonus
