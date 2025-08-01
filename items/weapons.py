from typing import Dict, Any
from .base_item import BaseItem, ItemType, ItemRarity

class Weapon(BaseItem):
    def __init__(self, item_id: str, name: str, description: str, 
                 damage_dice: str, attack_speed: float, crit_range: int = 20,
                 weight: float = 0.0, value: int = 0, rarity: ItemRarity = ItemRarity.COMMON):
        super().__init__(item_id, name, description, ItemType.WEAPON, weight, value, rarity)
        
        # Combat properties
        self.damage_dice = damage_dice  # e.g., "1d4", "1d6+1", "2d4"
        self.attack_speed = attack_speed  # seconds between attacks
        self.crit_range = crit_range  # critical hit on this roll or higher (20 = only nat 20)
        
        # Combat bonuses
        self.attack_bonus = 0  # bonus to attack rolls
        self.damage_bonus = 0  # bonus to damage rolls
    
    def get_tooltip_text(self) -> str:
        """Generate weapon-specific tooltip."""
        lines = []
        lines.append(f"=== {self.name.upper()} ===")
        lines.append(f"Type: Weapon")
        lines.append(f"Damage: {self.damage_dice}")
        if self.damage_bonus > 0:
            lines.append(f"Damage Bonus: +{self.damage_bonus}")
        lines.append(f"Attack Speed: {self.attack_speed}s")
        if self.attack_bonus > 0:
            lines.append(f"Attack Bonus: +{self.attack_bonus}")
        if self.crit_range < 20:
            lines.append(f"Critical: {self.crit_range}-20")
        else:
            lines.append(f"Critical: 20")
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
        """Convert weapon to dictionary."""
        data = super().to_dict()
        data.update({
            'damage_dice': self.damage_dice,
            'attack_speed': self.attack_speed,
            'crit_range': self.crit_range,
            'attack_bonus': self.attack_bonus,
            'damage_bonus': self.damage_bonus
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Weapon':
        """Create weapon from dictionary."""
        weapon = cls(
            item_id=data['item_id'],
            name=data['name'],
            description=data['description'],
            damage_dice=data['damage_dice'],
            attack_speed=data['attack_speed'],
            crit_range=data.get('crit_range', 20),
            weight=data.get('weight', 0.0),
            value=data.get('value', 0),
            rarity=ItemRarity(data.get('rarity', 'common'))
        )
        
        weapon.class_restrictions = data.get('class_restrictions', [])
        weapon.level_requirement = data.get('level_requirement', 1)
        weapon.stat_bonuses = data.get('stat_bonuses', {
            'strength': 0, 'dexterity': 0, 'constitution': 0,
            'intelligence': 0, 'wisdom': 0, 'charisma': 0
        })
        weapon.attack_bonus = data.get('attack_bonus', 0)
        weapon.damage_bonus = data.get('damage_bonus', 0)
        
        return weapon


# Specific weapon classes for easy instantiation

class RustyDagger(Weapon):
    def __init__(self):
        super().__init__(
            item_id="rusty_dagger",
            name="Rusty Dagger",
            description="A small, rusty blade that has seen better days. Despite its worn appearance, it's still sharp enough to be deadly in the right hands.",
            damage_dice="1d4",
            attack_speed=2.0,
            crit_range=19,  # Rogues get improved crit range
            weight=1.0,
            value=5,
            rarity=ItemRarity.COMMON
        )
        self.class_restrictions = ["rogue"]

class TrainingSword(Weapon):
    def __init__(self):
        super().__init__(
            item_id="training_sword",
            name="Training Sword",
            description="A sturdy practice sword used to train new knights. While not the finest blade, it's well-balanced and reliable.",
            damage_dice="1d6",
            attack_speed=4.0,
            weight=3.0,
            value=10,
            rarity=ItemRarity.COMMON
        )
        self.class_restrictions = ["knight"]

class WoodenStaff(Weapon):
    def __init__(self):
        super().__init__(
            item_id="wooden_staff",
            name="Wooden Staff",
            description="A simple wooden staff that helps focus magical energies. More useful for spellcasting than physical combat.",
            damage_dice="1d4",
            attack_speed=6.0,
            weight=2.0,
            value=8,
            rarity=ItemRarity.COMMON
        )
        self.class_restrictions = ["mage"]
        self.stat_bonuses['intelligence'] = 1

class HandWraps(Weapon):
    def __init__(self):
        super().__init__(
            item_id="hand_wraps",
            name="Hand Wraps",
            description="Simple cloth wrappings that protect the hands during unarmed combat while maintaining flexibility.",
            damage_dice="1d3",
            attack_speed=3.0,
            weight=0.5,
            value=3,
            rarity=ItemRarity.COMMON
        )
        self.class_restrictions = ["mystic"]

class IronSword(Weapon):
    def __init__(self):
        super().__init__(
            item_id="iron_sword",
            name="Iron Sword",
            description="A well-forged iron blade with a sturdy crossguard. A significant upgrade over training weapons.",
            damage_dice="1d8",
            attack_speed=4.0,
            weight=4.0,
            value=50,
            rarity=ItemRarity.UNCOMMON
        )
        self.class_restrictions = ["knight"]
        self.attack_bonus = 1

class SteelDagger(Weapon):
    def __init__(self):
        super().__init__(
            item_id="steel_dagger",
            name="Steel Dagger",
            description="A finely crafted steel dagger with a razor-sharp edge. Perfectly balanced for quick, precise strikes.",
            damage_dice="1d4+1",
            attack_speed=1.8,
            crit_range=19,
            weight=1.5,
            value=40,
            rarity=ItemRarity.UNCOMMON
        )
        self.class_restrictions = ["rogue"]
        self.attack_bonus = 1

class OakStaff(Weapon):
    def __init__(self):
        super().__init__(
            item_id="oak_staff",
            name="Oak Staff",
            description="A staff carved from ancient oak, inscribed with mystical runes that enhance magical focus.",
            damage_dice="1d6",
            attack_speed=5.5,
            weight=3.0,
            value=60,
            rarity=ItemRarity.UNCOMMON
        )
        self.class_restrictions = ["mage"]
        self.stat_bonuses['intelligence'] = 2
        self.stat_bonuses['wisdom'] = 1

class MysticWraps(Weapon):
    def __init__(self):
        super().__init__(
            item_id="mystic_wraps",
            name="Mystic Wraps",
            description="Enchanted wrappings that enhance the wearer's natural combat abilities and spiritual focus.",
            damage_dice="1d4",
            attack_speed=2.5,
            weight=0.8,
            value=35,
            rarity=ItemRarity.UNCOMMON
        )
        self.class_restrictions = ["mystic"]
        self.stat_bonuses['dexterity'] = 1
        self.stat_bonuses['wisdom'] = 1