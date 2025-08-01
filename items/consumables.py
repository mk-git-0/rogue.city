from typing import Dict, Any, Optional
from .base_item import BaseItem, ItemType, ItemRarity

class Consumable(BaseItem):
    def __init__(self, item_id: str, name: str, description: str,
                 usage_time: float = 0.0, weight: float = 0.0, value: int = 0, 
                 rarity: ItemRarity = ItemRarity.COMMON):
        super().__init__(item_id, name, description, ItemType.CONSUMABLE, weight, value, rarity)
        
        # Consumable properties
        self.usage_time = usage_time  # time in seconds to use the item
        self.stackable = True  # most consumables stack
        
        # Effects (override in subclasses)
        self.hp_restore = 0
        self.mana_restore = 0
        self.effect_description = ""
    
    def use(self, character) -> str:
        """Use the consumable and apply its effects to the character."""
        result_messages = []
        
        if self.hp_restore > 0:
            old_hp = character.current_hp
            character.heal(self.hp_restore)
            actual_healing = character.current_hp - old_hp
            if actual_healing > 0:
                result_messages.append(f"You recover {actual_healing} hit points.")
            else:
                result_messages.append("You are already at full health.")
        
        if self.mana_restore > 0 and hasattr(character, 'current_mana'):
            old_mana = character.current_mana
            character.restore_mana(self.mana_restore)
            actual_mana = character.current_mana - old_mana
            if actual_mana > 0:
                result_messages.append(f"You recover {actual_mana} mana points.")
            else:
                result_messages.append("Your mana is already full.")
        
        if self.effect_description:
            result_messages.append(self.effect_description)
        
        return " ".join(result_messages) if result_messages else "You use the item but feel no effect."
    
    def get_tooltip_text(self) -> str:
        """Generate consumable-specific tooltip."""
        lines = []
        lines.append(f"=== {self.name.upper()} ===")
        lines.append(f"Type: Consumable")
        
        if self.hp_restore > 0:
            lines.append(f"Restores: {self.hp_restore} HP")
        
        if self.mana_restore > 0:
            lines.append(f"Restores: {self.mana_restore} Mana")
        
        if self.usage_time > 0:
            lines.append(f"Usage Time: {self.usage_time}s")
        
        lines.append(f"Weight: {self.weight} lbs")
        lines.append(f"Value: {self.value} gold")
        lines.append(f"Stackable: {'Yes' if self.stackable else 'No'}")
        
        if self.level_requirement > 1:
            lines.append(f"Level Required: {self.level_requirement}")
        
        if self.class_restrictions:
            lines.append(f"Classes: {', '.join(self.class_restrictions)}")
        
        lines.append("")
        lines.append(self.description)
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert consumable to dictionary."""
        data = super().to_dict()
        data.update({
            'usage_time': self.usage_time,
            'stackable': self.stackable,
            'hp_restore': self.hp_restore,
            'mana_restore': self.mana_restore,
            'effect_description': self.effect_description
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Consumable':
        """Create consumable from dictionary."""
        consumable = cls(
            item_id=data['item_id'],
            name=data['name'],
            description=data['description'],
            usage_time=data.get('usage_time', 0.0),
            weight=data.get('weight', 0.0),
            value=data.get('value', 0),
            rarity=ItemRarity(data.get('rarity', 'common'))
        )
        
        consumable.class_restrictions = data.get('class_restrictions', [])
        consumable.level_requirement = data.get('level_requirement', 1)
        consumable.stat_bonuses = data.get('stat_bonuses', {
            'strength': 0, 'dexterity': 0, 'constitution': 0,
            'intelligence': 0, 'wisdom': 0, 'charisma': 0
        })
        consumable.stackable = data.get('stackable', True)
        consumable.hp_restore = data.get('hp_restore', 0)
        consumable.mana_restore = data.get('mana_restore', 0)
        consumable.effect_description = data.get('effect_description', "")
        
        return consumable


# Specific consumable classes

class MinorHealthPotion(Consumable):
    def __init__(self):
        super().__init__(
            item_id="minor_health_potion",
            name="Minor Health Potion",
            description="A small vial of red liquid that restores a modest amount of health when consumed.",
            usage_time=1.0,
            weight=0.5,
            value=25,
            rarity=ItemRarity.COMMON
        )
        self.hp_restore = 8  # 2d4+2 average
        self.effect_description = "The potion tastes bitter but you feel your wounds begin to heal."

class MajorHealthPotion(Consumable):
    def __init__(self):
        super().__init__(
            item_id="major_health_potion",
            name="Major Health Potion",
            description="A large vial of crimson liquid that provides significant healing when consumed.",
            usage_time=1.5,
            weight=0.8,
            value=100,
            rarity=ItemRarity.UNCOMMON
        )
        self.hp_restore = 18  # 4d4+4 average
        self.effect_description = "The potent potion warms your body as it rapidly heals your injuries."

class MinorManaPotion(Consumable):
    def __init__(self):
        super().__init__(
            item_id="minor_mana_potion",
            name="Minor Mana Potion",
            description="A small vial of blue liquid that restores magical energy when consumed.",
            usage_time=1.0,
            weight=0.5,
            value=30,
            rarity=ItemRarity.COMMON
        )
        self.mana_restore = 10
        self.effect_description = "The potion tingles with arcane energy as it restores your magical power."
        self.class_restrictions = ["mage"]

class MajorManaPotion(Consumable):
    def __init__(self):
        super().__init__(
            item_id="major_mana_potion",
            name="Major Mana Potion",
            description="A large vial of glowing blue liquid that significantly restores magical energy.",
            usage_time=1.5,
            weight=0.8,
            value=120,
            rarity=ItemRarity.UNCOMMON
        )
        self.mana_restore = 25
        self.effect_description = "The powerful potion surges with magical energy, greatly restoring your mana."
        self.class_restrictions = ["mage"]

class Rations(Consumable):
    def __init__(self):
        super().__init__(
            item_id="rations",
            name="Travel Rations",
            description="A day's worth of preserved food and water. Provides sustenance for long journeys.",
            usage_time=5.0,
            weight=2.0,
            value=5,
            rarity=ItemRarity.COMMON
        )
        self.hp_restore = 2
        self.effect_description = "The simple meal helps restore your strength and energy."

class HerbalRemedy(Consumable):
    def __init__(self):
        super().__init__(
            item_id="herbal_remedy",
            name="Herbal Remedy",
            description="A mixture of healing herbs that provides both physical and mental restoration.",
            usage_time=2.0,
            weight=0.3,
            value=40,
            rarity=ItemRarity.COMMON
        )
        self.hp_restore = 5
        self.mana_restore = 5
        self.effect_description = "The herbal mixture tastes earthy but leaves you feeling refreshed and focused."
        self.class_restrictions = ["mystic"]