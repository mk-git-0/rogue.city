"""
Base Area System for Rogue City
Room-based world framework with traditional MajorMUD navigation.
"""

import json
import os
from typing import Dict, List, Optional, Any, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class ExitDirection(Enum):
    """Standard MUD movement directions."""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    UP = "up"
    DOWN = "down"
    NORTHEAST = "northeast"
    NORTHWEST = "northwest"
    SOUTHEAST = "southeast"
    SOUTHWEST = "southwest"


@dataclass
class RoomExit:
    """Represents an exit from a room to another room."""
    direction: ExitDirection
    destination_room: str
    destination_area: Optional[str] = None  # For inter-area travel
    is_locked: bool = False
    lock_message: str = "That way is blocked."
    hidden: bool = False  # Hidden exits not shown in exits list
    
    def __str__(self) -> str:
        """String representation of exit."""
        dest = f"{self.destination_area}:{self.destination_room}" if self.destination_area else self.destination_room
        status = ""
        if self.is_locked:
            status += " [LOCKED]"
        if self.hidden:
            status += " [HIDDEN]"
        return f"{self.direction.value} -> {dest}{status}"


@dataclass
class RoomItem:
    """Represents an item in a room."""
    item_id: str
    name: str
    description: str
    can_take: bool = True
    quantity: int = 1
    respawn: bool = False  # Whether item respawns after being taken
    respawn_delay: int = 0  # Delay in minutes for respawn
    
    def __str__(self) -> str:
        """String representation of item."""
        return f"{self.name}" + (f" ({self.quantity})" if self.quantity > 1 else "")


@dataclass
class RoomEnemy:
    """Represents an enemy encounter in a room."""
    enemy_type: str
    quantity: int = 1
    respawn: bool = False
    respawn_delay: int = 0
    encounter_name: str = ""  # Custom encounter name
    triggered: bool = False  # Whether encounter has been triggered
    
    def __str__(self) -> str:
        """String representation of enemy."""
        name = self.encounter_name or self.enemy_type
        return f"{name}" + (f" (x{self.quantity})" if self.quantity > 1 else "")
    
    def get_display_name(self) -> str:
        """Get display name for enemy encounters."""
        return self.encounter_name or self.enemy_type


class Room:
    """Represents a single room in the world."""
    
    def __init__(self, room_id: str, name: str, description: str):
        """Initialize room with basic properties."""
        self.room_id = room_id
        self.name = name
        self.description = description
        
        # Navigation
        self.exits: Dict[ExitDirection, RoomExit] = {}
        
        # Contents
        self.items: Dict[str, RoomItem] = {}
        self.enemies: Dict[str, RoomEnemy] = {}
        
        # State tracking
        self.visited: bool = False
        self.discovered_items: set = set()  # Items player has found here
        self.defeated_enemies: set = set()  # Enemies defeated here
        
        # Special properties
        self.is_safe: bool = False  # No combat allowed
        self.is_dark: bool = False  # Requires light source
        self.ambient_sound: str = ""  # Background sound description
        self.special_actions: Dict[str, str] = {}  # Custom room actions
        
    def add_exit(self, direction: ExitDirection, destination_room: str, 
                 destination_area: Optional[str] = None, **kwargs) -> None:
        """Add an exit to this room."""
        exit_obj = RoomExit(
            direction=direction,
            destination_room=destination_room,
            destination_area=destination_area,
            **kwargs
        )
        self.exits[direction] = exit_obj
        
    def remove_exit(self, direction: ExitDirection) -> bool:
        """Remove an exit from this room."""
        if direction in self.exits:
            del self.exits[direction]
            return True
        return False
        
    def get_exit(self, direction: ExitDirection) -> Optional[RoomExit]:
        """Get exit in the specified direction."""
        return self.exits.get(direction)
        
    def get_available_exits(self, include_hidden: bool = False) -> Dict[ExitDirection, RoomExit]:
        """Get all available (unlocked, non-hidden) exits."""
        available = {}
        for direction, exit_obj in self.exits.items():
            if exit_obj.is_locked:
                continue
            if exit_obj.hidden and not include_hidden:
                continue
            available[direction] = exit_obj
        return available
        
    def add_item(self, item_id: str, name: str, description: str, **kwargs) -> None:
        """Add an item to this room."""
        item = RoomItem(
            item_id=item_id,
            name=name,
            description=description,
            **kwargs
        )
        self.items[item_id] = item
        
    def remove_item(self, item_id: str) -> Optional[RoomItem]:
        """Remove and return an item from this room."""
        if item_id in self.items:
            item = self.items[item_id]
            del self.items[item_id]
            self.discovered_items.add(item_id)
            return item
        return None
        
    def get_visible_items(self) -> List[RoomItem]:
        """Get all items visible to the player."""
        return [item for item in self.items.values() if item.quantity > 0]
        
    def add_enemy(self, enemy_id: str, enemy_type: str, **kwargs) -> None:
        """Add an enemy encounter to this room."""
        enemy = RoomEnemy(
            enemy_type=enemy_type,
            **kwargs
        )
        self.enemies[enemy_id] = enemy
        
    def get_active_enemies(self) -> List[RoomEnemy]:
        """Get all active (non-defeated) enemies."""
        return [enemy for enemy_id, enemy in self.enemies.items() 
                if enemy_id not in self.defeated_enemies and not enemy.triggered]
        
    def defeat_enemy(self, enemy_id: str) -> bool:
        """Mark an enemy as defeated."""
        if enemy_id in self.enemies:
            self.defeated_enemies.add(enemy_id)
            return True
        return False
        
    def get_full_description(self) -> str:
        """Get complete room description including contents."""
        desc_lines = [self.name, self.description]
        
        # Add ambient sound if present
        if self.ambient_sound:
            desc_lines.append(f"[{self.ambient_sound}]")
        
        # Add visible items
        visible_items = self.get_visible_items()
        if visible_items:
            if len(visible_items) == 1:
                desc_lines.append(f"{visible_items[0].description}")
            else:
                desc_lines.append("You see:")
                for item in visible_items:
                    desc_lines.append(f"  {item.description}")
        
        # Add active enemies
        active_enemies = self.get_active_enemies()
        if active_enemies:
            for enemy in active_enemies:
                desc_lines.append(f"A {enemy.get_display_name()} is here!")
        
        # Add exits
        available_exits = self.get_available_exits()
        if available_exits:
            exit_names = [exit_obj.direction.value for exit_obj in available_exits.values()]
            desc_lines.append(f"Exits: {', '.join(exit_names)}")
        else:
            desc_lines.append("There are no obvious exits.")
            
        return "\n".join(desc_lines)
        
    def to_dict(self) -> Dict[str, Any]:
        """Serialize room state for saving."""
        return {
            'room_id': self.room_id,
            'visited': self.visited,
            'discovered_items': list(self.discovered_items),
            'defeated_enemies': list(self.defeated_enemies),
            'items': {
                item_id: {
                    'quantity': item.quantity,
                    'item_id': item.item_id,
                    'name': item.name,
                    'description': item.description,
                    'can_take': item.can_take
                }
                for item_id, item in self.items.items()
            }
        }
        
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Restore room state from save data."""
        self.visited = data.get('visited', False)
        self.discovered_items = set(data.get('discovered_items', []))
        self.defeated_enemies = set(data.get('defeated_enemies', []))
        
        # Restore item quantities
        saved_items = data.get('items', {})
        for item_id, item_data in saved_items.items():
            if item_id in self.items:
                self.items[item_id].quantity = item_data.get('quantity', 1)


class BaseArea(ABC):
    """Abstract base class for game areas."""
    
    def __init__(self, area_id: str, name: str, description: str):
        """Initialize base area."""
        self.area_id = area_id
        self.name = name
        self.description = description
        
        # Room management
        self.rooms: Dict[str, Room] = {}
        self.starting_room: str = ""
        
        # Area state
        self.discovered: bool = False
        self.completed: bool = False
        
        # Map and navigation
        self.map_data: List[str] = []
        self.map_legend: Dict[str, str] = {}
        
        # Load area data
        self._load_area_data()
        
    @abstractmethod
    def _load_area_data(self) -> None:
        """Load area-specific data from JSON files."""
        pass
        
    @abstractmethod
    def get_starting_room(self) -> str:
        """Return the ID of the starting room for this area."""
        pass
        
    def add_room(self, room: Room) -> None:
        """Add a room to this area."""
        self.rooms[room.room_id] = room
        
    def get_room(self, room_id: str) -> Optional[Room]:
        """Get a room by ID."""
        return self.rooms.get(room_id)
        
    def get_room_list(self) -> List[str]:
        """Get list of all room IDs."""
        return list(self.rooms.keys())
        
    def visit_room(self, room_id: str) -> bool:
        """Mark a room as visited."""
        room = self.get_room(room_id)
        if room:
            room.visited = True
            if not self.discovered:
                self.discovered = True
            return True
        return False
        
    def get_map_display(self, current_room: str = None) -> str:
        """Get ASCII map with current position marked."""
        if not self.map_data:
            return f"No map available for {self.name}."
            
        map_lines = [f"=== {self.name.upper()} MAP ==="]
        
        # Process map data and mark current room
        for line in self.map_data:
            if current_room:
                # Mark current room position (this would need room-specific logic)
                display_line = line.replace("[?]", "[?]")  # Placeholder for room marking
                if f"[{current_room[0].upper()}]" in line:
                    display_line = line.replace(f"[{current_room[0].upper()}]", f"[{current_room[0].upper()}*]")
            else:
                display_line = line
            map_lines.append(display_line)
            
        # Add legend
        if self.map_legend:
            map_lines.append("")
            map_lines.append("Legend:")
            for symbol, meaning in self.map_legend.items():
                map_lines.append(f"  {symbol} = {meaning}")
                
        return "\n".join(map_lines)
        
    def check_area_completion(self) -> bool:
        """Check if area completion conditions are met."""
        # Default: area is complete when all rooms are visited
        for room in self.rooms.values():
            if not room.visited:
                return False
        self.completed = True
        return True
        
    def get_area_progress(self) -> Dict[str, Any]:
        """Get area completion progress."""
        visited_rooms = sum(1 for room in self.rooms.values() if room.visited)
        total_rooms = len(self.rooms)
        
        return {
            'area_id': self.area_id,
            'name': self.name,
            'discovered': self.discovered,
            'completed': self.completed,
            'rooms_visited': visited_rooms,
            'total_rooms': total_rooms,
            'completion_percentage': (visited_rooms / total_rooms * 100) if total_rooms > 0 else 0
        }

    # --- Room item helpers ---
    def add_item_to_room(self, room_id: str, item: Any, quantity: int = 1) -> bool:
        """Add a concrete item instance to a room as a room item.

        Args:
            room_id: Target room identifier
            item: An item object with item_id, name, description
            quantity: How many to add

        Returns:
            True if added, False otherwise
        """
        room = self.get_room(room_id)
        if not room or not hasattr(item, 'item_id'):
            return False

        item_id = getattr(item, 'item_id', None)
        name = getattr(item, 'name', str(item))
        description = getattr(item, 'description', name)

        if not item_id:
            return False

        # If item already exists in room, increase quantity
        if item_id in room.items:
            room.items[item_id].quantity += max(1, quantity)
            return True

        # Otherwise, add a new RoomItem entry
        room.add_item(item_id=item_id, name=name, description=description, quantity=max(1, quantity))
        return True

    def add_simple_item_to_room(
        self,
        room_id: str,
        item_id: str,
        name: str,
        description: str,
        quantity: int = 1,
        can_take: bool = True,
    ) -> bool:
        """Add a simple ad-hoc item (not from item factory) to a room.

        This is used for generic loot like "Goblin Ear" that isn't a defined item class.

        Args:
            room_id: Target room identifier
            item_id: Unique identifier for the room item (scoped to room)
            name: Display name of the item
            description: Description shown in room
            quantity: Quantity to add
            can_take: Whether the player can pick up the item
        """
        room = self.get_room(room_id)
        if not room:
            return False
        # If item already exists, bump quantity
        if item_id in room.items:
            room.items[item_id].quantity += max(1, quantity)
            return True

        room.add_item(
            item_id=item_id,
            name=name,
            description=description,
            can_take=can_take,
            quantity=max(1, quantity),
        )
        return True
        
    def to_dict(self) -> Dict[str, Any]:
        """Serialize area state for saving."""
        return {
            'area_id': self.area_id,
            'discovered': self.discovered,
            'completed': self.completed,
            'rooms': {
                room_id: room.to_dict()
                for room_id, room in self.rooms.items()
            }
        }
        
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Restore area state from save data."""
        self.discovered = data.get('discovered', False)
        self.completed = data.get('completed', False)
        
        # Restore room states
        saved_rooms = data.get('rooms', {})
        for room_id, room_data in saved_rooms.items():
            if room_id in self.rooms:
                self.rooms[room_id].from_dict(room_data)
                
    def _load_json_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """Helper method to load JSON data files."""
        try:
            # Get path relative to project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            file_path = os.path.join(project_root, "data", "areas", filename)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load area data from {filename}: {e}")
            return None
        
    def _load_map_data(self, filename: str) -> None:
        """Helper method to load ASCII map data."""
        try:
            # Get path relative to project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            file_path = os.path.join(project_root, "data", "maps", filename)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                self.map_data = f.read().strip().split('\n')
        except FileNotFoundError as e:
            print(f"Warning: Could not load map data from {filename}: {e}")
            self.map_data = [f"Map for {self.name} not found."]


# Utility functions
def parse_direction(direction_str: str) -> Optional[ExitDirection]:
    """Parse direction string to ExitDirection enum."""
    direction_map = {
        'n': ExitDirection.NORTH, 'north': ExitDirection.NORTH,
        's': ExitDirection.SOUTH, 'south': ExitDirection.SOUTH,
        'e': ExitDirection.EAST, 'east': ExitDirection.EAST,
        'w': ExitDirection.WEST, 'west': ExitDirection.WEST,
        'u': ExitDirection.UP, 'up': ExitDirection.UP,
        'd': ExitDirection.DOWN, 'down': ExitDirection.DOWN,
        'ne': ExitDirection.NORTHEAST, 'northeast': ExitDirection.NORTHEAST,
        'nw': ExitDirection.NORTHWEST, 'northwest': ExitDirection.NORTHWEST,
        'se': ExitDirection.SOUTHEAST, 'southeast': ExitDirection.SOUTHEAST,
        'sw': ExitDirection.SOUTHWEST, 'southwest': ExitDirection.SOUTHWEST,
    }
    return direction_map.get(direction_str.lower())


def get_opposite_direction(direction: ExitDirection) -> ExitDirection:
    """Get the opposite direction for creating two-way connections."""
    opposites = {
        ExitDirection.NORTH: ExitDirection.SOUTH,
        ExitDirection.SOUTH: ExitDirection.NORTH,
        ExitDirection.EAST: ExitDirection.WEST,
        ExitDirection.WEST: ExitDirection.EAST,
        ExitDirection.UP: ExitDirection.DOWN,
        ExitDirection.DOWN: ExitDirection.UP,
        ExitDirection.NORTHEAST: ExitDirection.SOUTHWEST,
        ExitDirection.SOUTHWEST: ExitDirection.NORTHEAST,
        ExitDirection.NORTHWEST: ExitDirection.SOUTHEAST,
        ExitDirection.SOUTHEAST: ExitDirection.NORTHWEST,
    }
    return opposites.get(direction, direction)


# Test function for area system
def _test_area_system():
    """Test area system functionality."""
    # Create a test room
    room = Room("test_room", "Test Room", "A simple test room.")
    
    # Test exits
    room.add_exit(ExitDirection.NORTH, "north_room")
    room.add_exit(ExitDirection.SOUTH, "south_room", is_locked=True)
    
    assert len(room.exits) == 2
    assert len(room.get_available_exits()) == 1  # Only north (south is locked)
    
    # Test items
    room.add_item("sword", "Iron Sword", "A sturdy iron sword lies here.")
    room.add_item("key", "Brass Key", "A small brass key glints on the ground.", quantity=1)
    
    items = room.get_visible_items()
    assert len(items) == 2
    
    # Test item removal
    removed_item = room.remove_item("sword")
    assert removed_item is not None
    assert removed_item.name == "Iron Sword"
    assert len(room.get_visible_items()) == 1
    
    # Test room description
    desc = room.get_full_description()
    assert "Test Room" in desc
    assert "Exits: north" in desc
    
    print("Area system tests passed!")


if __name__ == "__main__":
    _test_area_system()