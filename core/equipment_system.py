from typing import Dict, Optional, Any, List
from items.base_item import BaseItem, ItemType
from items.weapons import Weapon
from items.armor import Armor, ArmorType
from core.inventory_system import InventorySystem

class EquipmentSlot:
    def __init__(self, slot_name: str, allowed_types: list):
        self.slot_name = slot_name
        self.allowed_types = allowed_types
        self.equipped_item: Optional[BaseItem] = None
    
    def can_equip(self, item: BaseItem) -> bool:
        """Check if item can be equipped in this slot."""
        return item.item_type in self.allowed_types
    
    def equip(self, item: BaseItem) -> bool:
        """Equip item in this slot."""
        if self.can_equip(item):
            self.equipped_item = item
            return True
        return False
    
    def unequip(self) -> Optional[BaseItem]:
        """Remove equipped item and return it."""
        item = self.equipped_item
        self.equipped_item = None
        return item

class EquipmentSystem:
    def __init__(self, character, inventory_system: InventorySystem):
        self.character = character
        self.inventory_system = inventory_system
        
        # Define equipment slots
        self.slots = {
            'weapon': EquipmentSlot('weapon', [ItemType.WEAPON]),
            'armor': EquipmentSlot('armor', [ItemType.ARMOR]),
            'accessory': EquipmentSlot('accessory', [ItemType.ACCESSORY])
        }
        
        # Add off-hand weapon slot for dual-wielding classes
        if hasattr(character, 'character_class'):
            dual_wield_classes = ['rogue', 'ranger', 'ninja', 'bard']
            if character.character_class.lower() in dual_wield_classes:
                self.slots['offhand'] = EquipmentSlot('offhand', [ItemType.WEAPON])

        # Add shield slot (future-proof; shield items will use this slot)
        # Minimal viable: no shield item types yet; helpers will handle None safely
        self.slots['shield'] = EquipmentSlot('shield', [ItemType.ARMOR])
        
        # Track applied bonuses for removal
        self.applied_bonuses = {}
    
    def can_equip_item(self, item: BaseItem) -> tuple[bool, str]:
        """Check if item can be equipped by this character."""
        # Check class restrictions
        if not item.can_be_used_by_class(self.character.character_class):
            return False, f"Only {', '.join(item.class_restrictions)} can use this item."
        
        # Check level requirements
        if not item.can_be_used_by_level(self.character.level):
            return False, f"You need to be level {item.level_requirement} to use this item."
        
        # Check if appropriate slot exists
        slot = self._get_slot_for_item(item)
        if not slot:
            return False, "This item cannot be equipped."
        
        return True, "OK"
    
    def _get_slot_for_item(self, item: BaseItem) -> Optional[str]:
        """Get the appropriate equipment slot for an item."""
        # Shields are represented as Armor but should go to 'shield' slot if present
        if hasattr(item, 'is_shield') and getattr(item, 'is_shield') and 'shield' in self.slots:
            return 'shield'
        for slot_name, slot in self.slots.items():
            if slot.can_equip(item):
                return slot_name
        return None
    
    def equip_item(self, item_id: str) -> str:
        """Equip item from inventory."""
        # Find item in inventory
        inv_item = self.inventory_system.get_item(item_id)
        if not inv_item:
            return "You don't have that item."
        
        item = inv_item.item
        
        # Check if item can be equipped
        can_equip, message = self.can_equip_item(item)
        if not can_equip:
            return message
        
        # Get appropriate slot
        slot_name = self._get_slot_for_item(item)
        if not slot_name:
            return "This item cannot be equipped."

        # Special handling for weapons: if main-hand is occupied and off-hand exists and is free,
        # equip into off-hand for dual-wielding classes
        if item.item_type == ItemType.WEAPON:
            main_slot = self.slots.get('weapon')
            off_slot = self.slots.get('offhand')
            if main_slot and main_slot.equipped_item and off_slot and not off_slot.equipped_item:
                slot_name = 'offhand'
        
        slot = self.slots[slot_name]
        
        # Unequip current item if any
        if slot.equipped_item:
            self.unequip_item(slot_name)
        
        # Equip new item
        slot.equip(item)
        inv_item.equipped = True
        
        # Apply item bonuses
        self._apply_item_bonuses(item, slot_name)
        
        # Recalculate character stats
        self.character.recalculate_stats()
        
        return f"You equip the {item.name}."
    
    def unequip_item(self, slot_name: str) -> str:
        """Unequip item from specified slot."""
        if slot_name not in self.slots:
            return "Invalid equipment slot."
        
        slot = self.slots[slot_name]
        if not slot.equipped_item:
            return f"You don't have anything equipped in your {slot_name} slot."
        
        item = slot.unequip()
        
        # Find item in inventory and mark as unequipped
        for inv_item in self.inventory_system.items.values():
            if inv_item.item.item_id == item.item_id and inv_item.equipped:
                inv_item.equipped = False
                break
        
        # Remove item bonuses
        self._remove_item_bonuses(item, slot_name)
        
        # Recalculate character stats
        self.character.recalculate_stats()
        
        return f"You unequip the {item.name}."
    
    def _apply_item_bonuses(self, item: BaseItem, slot_name: str):
        """Apply stat bonuses from equipped item."""
        bonuses = {}
        
        # Apply stat bonuses
        for stat, bonus in item.stat_bonuses.items():
            if bonus != 0:
                bonuses[stat] = bonus
                if stat in self.character.stats:
                    self.character.stats[stat] += bonus
        
        # Store applied bonuses for removal
        self.applied_bonuses[slot_name] = bonuses
    
    def _remove_item_bonuses(self, item: BaseItem, slot_name: str):
        """Remove stat bonuses from unequipped item."""
        if slot_name in self.applied_bonuses:
            bonuses = self.applied_bonuses[slot_name]
            
            # Remove stat bonuses
            for stat, bonus in bonuses.items():
                if stat in self.character.stats:
                    self.character.stats[stat] -= bonus
            
            # Clear stored bonuses
            del self.applied_bonuses[slot_name]
    
    def get_equipped_weapon(self) -> Optional[Weapon]:
        """Get currently equipped main-hand weapon."""
        weapon_slot = self.slots.get('weapon')
        if weapon_slot and weapon_slot.equipped_item:
            return weapon_slot.equipped_item
        return None
        
    def get_offhand_weapon(self) -> Optional[Weapon]:
        """Get currently equipped off-hand weapon (for dual-wielding)."""
        offhand_slot = self.slots.get('offhand')
        if offhand_slot and offhand_slot.equipped_item:
            return offhand_slot.equipped_item
        return None
        
    def get_all_weapons(self) -> List[Weapon]:
        """Get all equipped weapons (main-hand and off-hand)."""
        weapons = []
        main_weapon = self.get_equipped_weapon()
        if main_weapon:
            weapons.append(main_weapon)
        offhand_weapon = self.get_offhand_weapon()
        if offhand_weapon:
            weapons.append(offhand_weapon)
        return weapons
    
    def get_equipped_armor(self) -> Optional[Armor]:
        """Get currently equipped armor."""
        armor_slot = self.slots.get('armor')
        if armor_slot and armor_slot.equipped_item:
            return armor_slot.equipped_item
        return None

    def get_equipped_shield(self) -> Optional[Armor]:
        """Get currently equipped shield (if shield slot used)."""
        shield_slot = self.slots.get('shield')
        if shield_slot and shield_slot.equipped_item:
            # Shields will be represented by Armor until a Shield class exists
            return shield_slot.equipped_item  # type: ignore[return-value]
        return None
    
    def get_armor_class_bonus(self) -> int:
        """Get AC bonus from equipped armor."""
        armor = self.get_equipped_armor()
        if armor:
            return armor.ac_bonus
        return 0

    def get_shield_ac_bonus(self) -> int:
        """Get AC bonus from equipped shield (0 if none)."""
        shield = self.get_equipped_shield()
        if shield and hasattr(shield, 'ac_bonus'):
            return getattr(shield, 'ac_bonus', 0)
        return 0
    
    def get_max_dex_bonus(self) -> Optional[int]:
        """Get max DEX bonus from equipped armor."""
        armor = self.get_equipped_armor()
        if armor:
            return armor.max_dex_bonus
        return None
    
    def get_attack_speed_modifier(self) -> float:
        """Get attack speed from equipped weapon."""
        weapon = self.get_equipped_weapon()
        if weapon and hasattr(weapon, 'attack_speed'):
            return weapon.attack_speed
        return 6.0  # Default unarmed speed
    
    def get_damage_dice(self) -> str:
        """Get damage dice from equipped weapon."""
        weapon = self.get_equipped_weapon()
        if weapon:
            return weapon.damage_dice
        return "1d2"  # Default unarmed damage
    
    def get_attack_bonus(self) -> int:
        """Get attack bonus from equipped weapon."""
        weapon = self.get_equipped_weapon()
        if weapon:
            return weapon.attack_bonus
        return 0
    
    def get_damage_bonus(self) -> int:
        """Get damage bonus from equipped weapon."""
        weapon = self.get_equipped_weapon()
        if weapon:
            return weapon.damage_bonus
        return 0
    
    def get_crit_range(self) -> int:
        """Get critical hit range from equipped weapon."""
        weapon = self.get_equipped_weapon()
        if weapon:
            return weapon.crit_range
        return 20  # Default crit only on 20
    
    def get_equipment_display(self) -> str:
        """Generate formatted equipment display."""
        lines = []
        lines.append("=== EQUIPMENT ===")
        
        for slot_name, slot in self.slots.items():
            if slot.equipped_item:
                lines.append(f"{slot_name.title()}: {slot.equipped_item.name}")
            else:
                lines.append(f"{slot_name.title()}: None")
        
        # Show combat stats for all weapons
        weapons = []
        main_weapon = self.get_equipped_weapon()
        if main_weapon:
            weapons.append(("Main Hand", main_weapon))
        
        if hasattr(self, 'get_offhand_weapon'):
            offhand_weapon = self.get_offhand_weapon()
            if offhand_weapon:
                weapons.append(("Off Hand", offhand_weapon))
        
        if weapons:
            lines.append("")
            lines.append("=== COMBAT STATS ===")
            for hand_name, weapon in weapons:
                lines.append(f"{hand_name}: {weapon.name}")
                lines.append(f"  Damage: {weapon.damage_dice}")
                if hasattr(weapon, 'attacks_per_turn'):
                    lines.append(f"  Attacks per Turn: {weapon.attacks_per_turn}")
                if hasattr(weapon, 'damage_bonus') and weapon.damage_bonus > 0:
                    lines.append(f"  Damage Bonus: +{weapon.damage_bonus}")
                if hasattr(weapon, 'attack_bonus') and weapon.attack_bonus > 0:
                    lines.append(f"  Attack Bonus: +{weapon.attack_bonus}")
                if hasattr(weapon, 'crit_range'):
                    lines.append(f"  Critical: {weapon.crit_range}-20")
                lines.append("")
        
        # Show armor stats if armor equipped
        armor = self.get_equipped_armor()
        if armor:
            lines.append("")
            lines.append("=== DEFENSE STATS ===")
            lines.append(f"Armor: {armor.name}")
            lines.append(f"AC Bonus: +{armor.ac_bonus}")
            if armor.max_dex_bonus is not None:
                lines.append(f"Max DEX Bonus: +{armor.max_dex_bonus}")
            else:
                lines.append("Max DEX Bonus: Unlimited")

        # Show shield stats if equipped
        shield = self.get_equipped_shield()
        if shield:
            if not armor:
                lines.append("")
                lines.append("=== DEFENSE STATS ===")
            lines.append(f"Shield: {shield.name}")
            lines.append(f"Shield AC Bonus: +{getattr(shield, 'ac_bonus', 0)}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert equipment to dictionary for serialization."""
        equipment_data = {}
        
        for slot_name, slot in self.slots.items():
            if slot.equipped_item:
                equipment_data[slot_name] = slot.equipped_item.item_id
            else:
                equipment_data[slot_name] = None
        
        return {
            'equipped_items': equipment_data,
            'applied_bonuses': self.applied_bonuses
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Load equipment from dictionary."""
        equipped_items = data.get('equipped_items', {})
        self.applied_bonuses = data.get('applied_bonuses', {})
        
        # Re-equip items (this requires items to be loaded in inventory first)
        for slot_name, item_id in equipped_items.items():
            if item_id and slot_name in self.slots:
                inv_item = self.inventory_system.get_item(item_id)
                if inv_item:
                    self.slots[slot_name].equip(inv_item.item)
                    inv_item.equipped = True

    # --- Helpers for Knight and armor checks ---
    def has_shield_equipped(self) -> bool:
        """Return True if a shield is equipped in the shield slot."""
        return self.get_equipped_shield() is not None

    def has_heavy_armor(self) -> bool:
        """Return True if equipped armor is heavy type."""
        armor = self.get_equipped_armor()
        if not armor:
            return False
        return getattr(armor, 'armor_type', None) == ArmorType.HEAVY