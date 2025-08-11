import json
import os
from typing import Dict, Optional, List, Any
from items.base_item import BaseItem, ItemType
from items.weapons import (
    Weapon, RustyDagger, TrainingSword, WoodenStaff, HandWraps,
    IronSword, SteelDagger, OakStaff, MysticWraps
)
from items.armor import (
    Armor, LeatherScraps, ClothRobes, PaddedArmor, SimpleGarb,
    LeatherArmor, ChainMail, MageRobes, MysticRobes,
    WoodenShield, Buckler, HeaterShield
)
from items.consumables import (
    Consumable, MinorHealthPotion, MajorHealthPotion, MinorManaPotion,
    MajorManaPotion, Rations, HerbalRemedy
)

class ItemFactory:
    def __init__(self):
        self.data_path = "data/items"
        
        # Predefined item classes for quick instantiation
        self.item_classes = {
            # Weapons
            'rusty_dagger': RustyDagger,
            'training_sword': TrainingSword,
            'wooden_staff': WoodenStaff,
            'hand_wraps': HandWraps,
            'iron_sword': IronSword,
            'steel_dagger': SteelDagger,
            'oak_staff': OakStaff,
            'mystic_wraps': MysticWraps,
            
            # Armor
            'leather_scraps': LeatherScraps,
            'cloth_robes': ClothRobes,
            'padded_armor': PaddedArmor,
            'simple_garb': SimpleGarb,
            'leather_armor': LeatherArmor,
            'chain_mail': ChainMail,
            'mage_robes': MageRobes,
            'mystic_robes': MysticRobes,
            'wooden_shield': WoodenShield,
            'buckler': Buckler,
            'heater_shield': HeaterShield,
            
            # Consumables
            'minor_health_potion': MinorHealthPotion,
            'major_health_potion': MajorHealthPotion,
            'minor_mana_potion': MinorManaPotion,
            'major_mana_potion': MajorManaPotion,
            'rations': Rations,
            'herbal_remedy': HerbalRemedy
        }
        
        # Cached item databases
        self._weapon_data: Optional[Dict] = None
        self._armor_data: Optional[Dict] = None
        self._consumable_data: Optional[Dict] = None
    
    def create_item(self, item_id: str) -> Optional[BaseItem]:
        """Create an item by ID. First tries predefined classes, then JSON data."""
        # Try predefined classes first
        if item_id in self.item_classes:
            return self.item_classes[item_id]()
        
        # Try loading from JSON data
        return self._create_from_json(item_id)
    
    def _create_from_json(self, item_id: str) -> Optional[BaseItem]:
        """Create item from JSON database."""
        # Try weapons first
        weapon_data = self._get_weapon_data()
        if weapon_data and item_id in weapon_data:
            return Weapon.from_dict(weapon_data[item_id])
        
        # Try armor
        armor_data = self._get_armor_data()
        if armor_data and item_id in armor_data:
            return Armor.from_dict(armor_data[item_id])
        
        # Try consumables
        consumable_data = self._get_consumable_data()
        if consumable_data and item_id in consumable_data:
            return Consumable.from_dict(consumable_data[item_id])
        
        return None
    
    def _get_weapon_data(self) -> Optional[Dict]:
        """Load and cache weapon data."""
        if self._weapon_data is None:
            weapons_file = os.path.join(self.data_path, "weapons.json")
            if os.path.exists(weapons_file):
                with open(weapons_file, 'r') as f:
                    self._weapon_data = json.load(f)
            else:
                self._weapon_data = {}
        return self._weapon_data
    
    def _get_armor_data(self) -> Optional[Dict]:
        """Load and cache armor data."""
        if self._armor_data is None:
            armor_file = os.path.join(self.data_path, "armor.json")
            if os.path.exists(armor_file):
                with open(armor_file, 'r') as f:
                    self._armor_data = json.load(f)
            else:
                self._armor_data = {}
        return self._armor_data
    
    def _get_consumable_data(self) -> Optional[Dict]:
        """Load and cache consumable data."""
        if self._consumable_data is None:
            consumables_file = os.path.join(self.data_path, "consumables.json")
            if os.path.exists(consumables_file):
                with open(consumables_file, 'r') as f:
                    self._consumable_data = json.load(f)
            else:
                self._consumable_data = {}
        return self._consumable_data
    
    def get_starting_equipment(self, character_class: str) -> Dict[str, BaseItem]:
        """Get starting equipment for a character class."""
        class_equipment = {
            'rogue': {
                'weapon': 'rusty_dagger',
                'armor': 'leather_scraps',
                'consumable': 'minor_health_potion'
            },
            'knight': {
                'weapon': 'training_sword',
                'armor': 'padded_armor',
                'consumable': 'minor_health_potion',
                'shield': 'wooden_shield'
            },
            'mage': {
                'weapon': 'wooden_staff',
                'armor': 'cloth_robes',
                'consumable': 'minor_health_potion',
                'mana_potion': 'minor_mana_potion'
            },
            'mystic': {
                'weapon': 'hand_wraps',
                'armor': 'simple_garb',
                'consumable': 'herbal_remedy'
            },
            'warrior': {
                'weapon': 'training_sword',
                'armor': 'padded_armor',
                'consumable': 'minor_health_potion'
            },
            'barbarian': {
                'weapon': 'iron_sword',
                'armor': 'leather_armor',
                'consumable': 'rations'
            },
            'ranger': {
                'weapon': 'iron_sword',
                'armor': 'leather_armor',
                'consumable': 'rations'
            },
            'thief': {
                'weapon': 'steel_dagger',
                'armor': 'leather_armor',
                'consumable': 'minor_health_potion'
            },
            'priest': {
                'weapon': 'wooden_staff',
                'armor': 'cloth_robes',
                'consumable': 'minor_health_potion'
            },
            'paladin': {
                'weapon': 'training_sword',
                'armor': 'chain_mail',
                'consumable': 'minor_health_potion'
            },
            'spellsword': {
                'weapon': 'iron_sword',
                'armor': 'padded_armor',
                'consumable': 'minor_mana_potion'
            },
            'ninja': {
                'weapon': 'steel_dagger',
                'armor': 'leather_armor',
                'consumable': 'herbal_remedy'
            },
            'warlock': {
                'weapon': 'wooden_staff',
                'armor': 'mage_robes',
                'consumable': 'minor_mana_potion'
            },
            'necromancer': {
                'weapon': 'wooden_staff',
                'armor': 'mage_robes',
                'consumable': 'minor_mana_potion'
            },
            'witchhunter': {
                'weapon': 'iron_sword',
                'armor': 'chain_mail',
                'consumable': 'minor_health_potion'
            },
            'bard': {
                'weapon': 'wooden_staff',
                'armor': 'leather_armor',
                'consumable': 'minor_health_potion'
            },
            'druid': {
                'weapon': 'wooden_staff',
                'armor': 'leather_armor',
                'consumable': 'herbal_remedy'
            },
            'missionary': {
                'weapon': 'wooden_staff',
                'armor': 'cloth_robes',
                'consumable': 'minor_health_potion'
            },
            'gypsy': {
                'weapon': 'steel_dagger',
                'armor': 'leather_scraps',
                'consumable': 'minor_health_potion'
            }
        }
        
        equipment = {}
        class_items = class_equipment.get(character_class.lower(), {})
        
        for slot, item_id in class_items.items():
            item = self.create_item(item_id)
            if item:
                equipment[slot] = item
        
        return equipment
    
    def get_items_for_class(self, character_class: str) -> Dict[str, BaseItem]:
        """Get all items that can be used by a specific class."""
        items = {}
        
        # Check all predefined items
        for item_id, item_class in self.item_classes.items():
            item = item_class()
            if item.can_be_used_by_class(character_class):
                items[item_id] = item
        
        # TODO: Also check JSON database items
        
        return items
    
    def get_tutorial_items(self) -> List[BaseItem]:
        """Get items that should appear in tutorial areas."""
        tutorial_items = []
        
        # Basic items for tutorial
        tutorial_item_ids = [
            'rusty_dagger', 'training_sword', 'wooden_staff', 'hand_wraps',
            'minor_health_potion', 'rations'
        ]
        
        for item_id in tutorial_item_ids:
            item = self.create_item(item_id)
            if item:
                tutorial_items.append(item)
        
        return tutorial_items
    
    def get_forest_items(self) -> List[BaseItem]:
        """Get items that should appear in forest areas."""
        forest_items = []
        
        # Better items for forest exploration
        forest_item_ids = [
            'iron_sword', 'steel_dagger', 'oak_staff', 'mystic_wraps',
            'leather_armor', 'chain_mail', 'mage_robes', 'mystic_robes',
            'major_health_potion', 'major_mana_potion'
        ]
        
        for item_id in forest_item_ids:
            item = self.create_item(item_id)
            if item:
                forest_items.append(item)
        
        return forest_items
    
    def get_all_weapons(self) -> List[BaseItem]:
        """Get all available weapons."""
        weapons = []
        
        for item_id, item_class in self.item_classes.items():
            item = item_class()
            if item.item_type == ItemType.WEAPON:
                weapons.append(item)
        
        return weapons
    
    def get_all_armor(self) -> List[BaseItem]:
        """Get all available armor."""
        armor = []
        
        for item_id, item_class in self.item_classes.items():
            item = item_class()
            if item.item_type == ItemType.ARMOR:
                armor.append(item)
        
        return armor
    
    def get_all_consumables(self) -> List[BaseItem]:
        """Get all available consumables."""
        consumables = []
        
        for item_id, item_class in self.item_classes.items():
            item = item_class()
            if item.item_type == ItemType.CONSUMABLE:
                consumables.append(item)
        
        return consumables
    
    def reload_data(self):
        """Reload all JSON data from files."""
        self._weapon_data = None
        self._armor_data = None
        self._consumable_data = None