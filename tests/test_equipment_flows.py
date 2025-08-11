import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from characters.base_character import BaseCharacter
from core.alignment_system import Alignment
from core.item_factory import ItemFactory


class TestChar(BaseCharacter):
    def get_hit_die_value(self):
        return 8
    def get_hit_die_type(self):
        return "1d8"
    def get_base_attack_speed(self):
        return 3.0
    def get_critical_range(self):
        return 20
    def get_experience_penalty(self):
        return 0


def test_equip_unequip_and_shield_bonus():
    c = TestChar("EqTester", "warrior", alignment=Alignment.NEUTRAL)
    c.initialize_item_systems()
    base_ac = c.armor_class

    factory = ItemFactory()
    armor = factory.create_item('leather_armor')
    shield = factory.create_item('wooden_shield')

    # Add to inventory and equip
    assert c.inventory_system.add_item(armor)
    assert c.inventory_system.add_item(shield)

    msg = c.equipment_system.equip_item(armor.item_id)
    assert 'equip' in msg.lower()
    armor_ac = c.equipment_system.get_armor_class_bonus()

    msg = c.equipment_system.equip_item(shield.item_id)
    assert 'equip' in msg.lower()
    shield_ac = c.equipment_system.get_shield_ac_bonus()

    # AC should include armor bonus. Knight doubles shield but we are warrior; just check presence
    c.recalculate_stats()
    assert c.armor_class >= base_ac + armor_ac
    assert shield_ac >= 1

    # Unequip shield
    msg = c.equipment_system.unequip_item('shield')
    assert 'unequip' in msg.lower()
