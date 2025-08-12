from typing import Dict, List, Optional, Any
from items.base_item import BaseItem, InventoryItem, ItemType

class InventorySystem:
    def __init__(self, character):
        self.character = character
        self.items: Dict[str, InventoryItem] = {}  # item_id -> InventoryItem
        
        # Calculate base carrying capacity
        self._calculate_carrying_capacity()
    
    def _calculate_carrying_capacity(self):
        """Calculate carrying capacity based on STR modifier."""
        base_capacity = 50.0  # base 50 lbs
        str_bonus = (self.character.stats['strength'] - 10) // 2
        self.max_weight = base_capacity + (str_bonus * 5)
    
    def get_current_weight(self) -> float:
        """Get total weight of all items in inventory."""
        return sum(inv_item.get_total_weight() for inv_item in self.items.values())
    
    def is_encumbered(self) -> bool:
        """Check if character is over carrying capacity."""
        return self.get_current_weight() > self.max_weight
    
    def get_encumbrance_penalty(self) -> float:
        """Get movement/action penalty for being over capacity."""
        if not self.is_encumbered():
            return 0.0
        
        overweight = self.get_current_weight() - self.max_weight
        # 10% penalty per 10 lbs over capacity, max 50%
        return min(0.5, (overweight / 10.0) * 0.1)
    
    def can_add_item(self, item: BaseItem, quantity: int = 1) -> bool:
        """Check if item can be added without exceeding capacity."""
        additional_weight = item.weight * quantity
        return (self.get_current_weight() + additional_weight) <= self.max_weight
    
    def add_item(self, item: BaseItem, quantity: int = 1) -> bool:
        """Add item to inventory. Returns True if successful."""
        # Check if we can carry the additional weight
        if not self.can_add_item(item, quantity):
            return False
        
        # Check if item already exists and is stackable
        if item.item_id in self.items:
            existing_item = self.items[item.item_id]
            if item.item_type == ItemType.CONSUMABLE:  # Consumables are stackable
                existing_item.quantity += quantity
                return True
            else:
                # Non-stackable items - need new entry with different key
                counter = 1
                new_id = f"{item.item_id}_{counter}"
                while new_id in self.items:
                    counter += 1
                    new_id = f"{item.item_id}_{counter}"
                self.items[new_id] = InventoryItem(item, quantity)
                return True
        else:
            # New item
            self.items[item.item_id] = InventoryItem(item, quantity)
            return True
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """Remove item from inventory. Returns True if successful."""
        if item_id not in self.items:
            return False
        
        inv_item = self.items[item_id]
        
        if inv_item.quantity <= quantity:
            # Remove entire stack
            del self.items[item_id]
        else:
            # Reduce quantity
            inv_item.quantity -= quantity
        
        return True
    
    def get_item(self, item_id: str) -> Optional[InventoryItem]:
        """Get inventory item by ID."""
        return self.items.get(item_id)
    
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Check if inventory contains item with sufficient quantity."""
        if item_id not in self.items:
            return False
        return self.items[item_id].quantity >= quantity
    
    def find_item_by_name(self, name: str) -> Optional[str]:
        """Find item ID by name with preference for unequipped copies.

        Strategy:
        1) Exact match, prefer unequipped; then exact match equipped
        2) Partial match, prefer unequipped; then partial match equipped
        """
        name_lower = name.lower()

        exact_unequipped = []
        exact_equipped = []
        partial_unequipped = []
        partial_equipped = []

        for item_id, inv_item in self.items.items():
            item_name = inv_item.item.name.lower()
            is_exact = item_name == name_lower
            is_partial = name_lower in item_name
            if not (is_exact or is_partial):
                continue
            if is_exact:
                if inv_item.equipped:
                    exact_equipped.append(item_id)
                else:
                    exact_unequipped.append(item_id)
            else:
                if inv_item.equipped:
                    partial_equipped.append(item_id)
                else:
                    partial_unequipped.append(item_id)

        for bucket in (exact_unequipped, exact_equipped, partial_unequipped, partial_equipped):
            if bucket:
                return bucket[0]

        return None
    
    def get_items_by_type(self, item_type: ItemType) -> Dict[str, InventoryItem]:
        """Get all items of a specific type."""
        return {item_id: inv_item for item_id, inv_item in self.items.items() 
                if inv_item.item.item_type == item_type}
    
    def get_inventory_display(self) -> str:
        """Generate formatted inventory display."""
        if not self.items:
            return "Your inventory is empty."
        
        lines = []
        lines.append("=== INVENTORY ===")
        
        # Group items by type
        weapons = self.get_items_by_type(ItemType.WEAPON)
        armor = self.get_items_by_type(ItemType.ARMOR)
        consumables = self.get_items_by_type(ItemType.CONSUMABLE)
        accessories = self.get_items_by_type(ItemType.ACCESSORY)
        
        if weapons:
            lines.append("Weapons:")
            for item_id, inv_item in weapons.items():
                equipped_marker = " (equipped)" if inv_item.equipped else ""
                lines.append(f"  {inv_item.get_display_name()}{equipped_marker}")
        
        if armor:
            lines.append("Armor:")
            for item_id, inv_item in armor.items():
                equipped_marker = " (equipped)" if inv_item.equipped else ""
                lines.append(f"  {inv_item.get_display_name()}{equipped_marker}")
        
        if accessories:
            lines.append("Accessories:")
            for item_id, inv_item in accessories.items():
                equipped_marker = " (equipped)" if inv_item.equipped else ""
                lines.append(f"  {inv_item.get_display_name()}{equipped_marker}")
        
        if consumables:
            lines.append("Consumables:")
            for item_id, inv_item in consumables.items():
                lines.append(f"  {inv_item.get_display_name()}")
        
        # Weight information
        current_weight = self.get_current_weight()
        lines.append(f"Weight: {current_weight:.1f}/{self.max_weight:.1f} lbs")
        
        if self.is_encumbered():
            penalty = self.get_encumbrance_penalty()
            lines.append(f"ENCUMBERED! Movement penalty: {penalty*100:.0f}%")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert inventory to dictionary for serialization."""
        return {
            'items': {item_id: inv_item.to_dict() for item_id, inv_item in self.items.items()},
            'max_weight': self.max_weight
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Load inventory from dictionary."""
        self.items = {}
        self.max_weight = data.get('max_weight', 50.0)
        
        for item_id, item_data in data.get('items', {}).items():
            inv_item = InventoryItem.from_dict(item_data)
            self.items[item_id] = inv_item