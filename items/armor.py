from typing import Dict, Any
from .base_item import BaseItem, ItemType, ItemRarity
from enum import Enum

class ArmorType(Enum):
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
    ROBES = "robes"

class Armor(BaseItem):
    def __init__(self, item_id: str, name: str, description: str, 
                 ac_bonus: int, armor_type: ArmorType, max_dex_bonus: int = None,
                 weight: float = 0.0, value: int = 0, rarity: ItemRarity = ItemRarity.COMMON):
        super().__init__(item_id, name, description, ItemType.ARMOR, weight, value, rarity)
        
        # Armor properties
        self.ac_bonus = ac_bonus  # bonus to armor class
        self.armor_type = armor_type
        self.max_dex_bonus = max_dex_bonus  # None means no limit on DEX bonus
        
        # Penalties
        self.stealth_penalty = 0  # penalty to stealth checks
        self.movement_penalty = 0  # penalty to movement speed

        # Shield marker (used by EquipmentSystem routing)
        self.is_shield: bool = False
    
    def get_effective_dex_bonus(self, dex_modifier: int) -> int:
        """Calculate the effective DEX bonus with armor restrictions."""
        if self.max_dex_bonus is None:
            return dex_modifier
        return min(dex_modifier, self.max_dex_bonus)
    
    def get_tooltip_text(self) -> str:
        """Generate armor-specific tooltip."""
        lines = []
        lines.append(f"=== {self.name.upper()} ===")
        lines.append(f"Type: Armor ({self.armor_type.value.title()})")
        lines.append(f"AC Bonus: +{self.ac_bonus}")
        
        if self.max_dex_bonus is not None:
            lines.append(f"Max DEX Bonus: +{self.max_dex_bonus}")
        else:
            lines.append(f"Max DEX Bonus: Unlimited")
        
        if self.stealth_penalty > 0:
            lines.append(f"Stealth Penalty: -{self.stealth_penalty}")
        
        if self.movement_penalty > 0:
            lines.append(f"Movement Penalty: -{self.movement_penalty}")
        
        lines.append(f"Weight: {self.weight} lbs")
        lines.append(f"Value: {self.value} gold")
        
        if self.level_requirement > 1:
            lines.append(f"Level Required: {self.level_requirement}")
        
        if self.class_restrictions:
            lines.append(f"Classes: {', '.join(self.class_restrictions)}")
        
        # Show stat bonuses if any
        bonuses = [f"{stat.title()}: +{bonus}" for stat, bonus in self.stat_bonuses.items() if bonus > 0]
        if bonuses:
            lines.append("Stat Bonuses:")
            for bonus in bonuses:
                lines.append(f"  {bonus}")
        
        lines.append("")
        lines.append(self.description)
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert armor to dictionary."""
        data = super().to_dict()
        data.update({
            'ac_bonus': self.ac_bonus,
            'armor_type': self.armor_type.value,
            'max_dex_bonus': self.max_dex_bonus,
            'stealth_penalty': self.stealth_penalty,
            'movement_penalty': self.movement_penalty
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Armor':
        """Create armor from dictionary."""
        armor = cls(
            item_id=data['item_id'],
            name=data['name'],
            description=data['description'],
            ac_bonus=data['ac_bonus'],
            armor_type=ArmorType(data['armor_type']),
            max_dex_bonus=data.get('max_dex_bonus'),
            weight=data.get('weight', 0.0),
            value=data.get('value', 0),
            rarity=ItemRarity(data.get('rarity', 'common'))
        )
        
        armor.class_restrictions = data.get('class_restrictions', [])
        armor.level_requirement = data.get('level_requirement', 1)
        armor.stat_bonuses = data.get('stat_bonuses', {
            'strength': 0, 'dexterity': 0, 'constitution': 0,
            'intelligence': 0, 'wisdom': 0, 'charisma': 0
        })
        armor.stealth_penalty = data.get('stealth_penalty', 0)
        armor.movement_penalty = data.get('movement_penalty', 0)
        
        return armor


# Specific armor classes for easy instantiation

class LeatherScraps(Armor):
    def __init__(self):
        super().__init__(
            item_id="leather_scraps",
            name="Leather Scraps",
            description="Rough pieces of leather hastily sewn together. Provides minimal protection but doesn't restrict movement.",
            ac_bonus=1,
            armor_type=ArmorType.LIGHT,
            max_dex_bonus=None,
            weight=5.0,
            value=5,
            rarity=ItemRarity.COMMON
        )
        self.class_restrictions = ["rogue", "mystic"]

class ClothRobes(Armor):
    def __init__(self):
        super().__init__(
            item_id="cloth_robes",
            name="Cloth Robes",
            description="Simple cloth robes that provide minimal protection but allow for easy spellcasting.",
            ac_bonus=1,
            armor_type=ArmorType.ROBES,
            max_dex_bonus=None,
            weight=2.0,
            value=8,
            rarity=ItemRarity.COMMON
        )
        self.class_restrictions = ["mage"]

class PaddedArmor(Armor):
    def __init__(self):
        super().__init__(
            item_id="padded_armor",
            name="Padded Armor",
            description="Thick layers of quilted fabric that provide basic protection for training warriors.",
            ac_bonus=1,
            armor_type=ArmorType.LIGHT,
            max_dex_bonus=8,
            weight=10.0,
            value=15,
            rarity=ItemRarity.COMMON
        )
        self.class_restrictions = ["knight"]

class SimpleGarb(Armor):
    def __init__(self):
        super().__init__(
            item_id="simple_garb",
            name="Simple Garb",
            description="Plain, comfortable clothing that doesn't restrict movement or meditation.",
            ac_bonus=0,
            armor_type=ArmorType.LIGHT,
            max_dex_bonus=None,
            weight=1.0,
            value=2,
            rarity=ItemRarity.COMMON
        )
        self.class_restrictions = ["mystic"]

class LeatherArmor(Armor):
    def __init__(self):
        super().__init__(
            item_id="leather_armor",
            name="Leather Armor",
            description="Well-crafted leather armor that provides good protection while maintaining flexibility.",
            ac_bonus=2,
            armor_type=ArmorType.LIGHT,
            max_dex_bonus=None,
            weight=10.0,
            value=50,
            rarity=ItemRarity.UNCOMMON
        )
        self.class_restrictions = ["rogue", "mystic"]

class ChainMail(Armor):
    def __init__(self):
        super().__init__(
            item_id="chain_mail",
            name="Chain Mail",
            description="Interlocking metal rings that provide excellent protection against slashing attacks.",
            ac_bonus=4,
            armor_type=ArmorType.MEDIUM,
            max_dex_bonus=2,
            weight=30.0,
            value=150,
            rarity=ItemRarity.UNCOMMON
        )
        self.class_restrictions = ["knight"]
        self.stealth_penalty = 2

class MageRobes(Armor):
    def __init__(self):
        super().__init__(
            item_id="mage_robes",
            name="Mage Robes",
            description="Enchanted robes woven with magical threads that enhance spellcasting abilities.",
            ac_bonus=2,
            armor_type=ArmorType.ROBES,
            max_dex_bonus=None,
            weight=4.0,
            value=120,
            rarity=ItemRarity.UNCOMMON
        )
        self.class_restrictions = ["mage"]
        self.stat_bonuses['intelligence'] = 1
        self.stat_bonuses['wisdom'] = 1

class MysticRobes(Armor):
    def __init__(self):
        super().__init__(
            item_id="mystic_robes",
            name="Mystic Robes",
            description="Flowing robes that enhance spiritual focus and provide protection through mystical means.",
            ac_bonus=2,
            armor_type=ArmorType.LIGHT,
            max_dex_bonus=None,
            weight=3.0,
            value=80,
            rarity=ItemRarity.UNCOMMON
        )
        self.class_restrictions = ["mystic"]
        self.stat_bonuses['wisdom'] = 2


# Shield classes (treated as Armor items with is_shield = True)

class WoodenShield(Armor):
    def __init__(self):
        super().__init__(
            item_id="wooden_shield",
            name="Wooden Shield",
            description="A simple wooden shield offering basic protection.",
            ac_bonus=1,
            armor_type=ArmorType.LIGHT,
            weight=6.0,
            value=8,
            rarity=ItemRarity.COMMON
        )
        self.is_shield = True
        self.class_restrictions = ["knight", "warrior", "paladin", "ranger", "witchhunter"]

class Buckler(Armor):
    def __init__(self):
        super().__init__(
            item_id="buckler",
            name="Buckler",
            description="A small round shield that is light and easy to carry.",
            ac_bonus=2,
            armor_type=ArmorType.LIGHT,
            weight=5.0,
            value=20,
            rarity=ItemRarity.UNCOMMON
        )
        self.is_shield = True
        self.class_restrictions = ["knight", "warrior", "paladin", "ranger", "witchhunter"]

class HeaterShield(Armor):
    def __init__(self):
        super().__init__(
            item_id="heater_shield",
            name="Heater Shield",
            description="A sturdy heater shield providing solid defense.",
            ac_bonus=3,
            armor_type=ArmorType.MEDIUM,
            weight=10.0,
            value=45,
            rarity=ItemRarity.UNCOMMON
        )
        self.is_shield = True
        self.class_restrictions = ["knight", "warrior", "paladin", "witchhunter"]