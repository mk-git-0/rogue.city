"""
Tutorial Cave Area for Rogue City
Guided 15-minute learning experience with progressive skill introduction.
"""

from typing import Dict, List, Optional, Any
from .base_area import BaseArea, Room, ExitDirection, RoomExit


class TutorialCaveArea(BaseArea):
    """
    Tutorial cave area providing guided learning experience.
    Features progressive difficulty and skill introduction over ~15 minutes.
    """
    
    def __init__(self):
        """Initialize tutorial cave area."""
        super().__init__(
            area_id="tutorial_cave",
            name="Tutorial Cave",
            description="A cave system designed to teach new adventurers the basics of exploration and combat."
        )
        
        # Tutorial-specific properties
        self.tutorial_complete = False
        self.required_encounters = ['tutorial_goblin', 'boss_encounter']
        self.optional_encounters = ['tutorial_rat']
        self.encounters_completed = set()
        
        # Tutorial progression tracking
        self.lessons_learned = {
            'movement': False,
            'examination': False,
            'item_pickup': False,
            'combat': False,
            'auto_combat': False,
            'exploration': False
        }
        
    def _load_area_data(self) -> None:
        """Load tutorial cave data from JSON file."""
        data = self._load_json_data("tutorial_cave.json")
        if not data:
            self._create_default_cave()
            return
            
        # Load room data
        rooms_data = data.get("rooms", {})
        for room_id, room_data in rooms_data.items():
            self._create_room_from_data(room_id, room_data)
            
        # Set starting room
        area_info = data.get("area_info", {})
        self.starting_room = area_info.get("starting_room", "cave_entrance")
        
        # Load map data
        self._load_map_data("tutorial_cave_map.txt")
        
        # Set up map legend
        self.map_legend = {
            "[*]": "Your current location",
            "[?]": "Unexplored area",
            "[Main]": "Main Chamber",
            "[Entrance]": "Cave Entrance",
            "[Exit]": "Cave Exit"
        }
        
    def _create_room_from_data(self, room_id: str, room_data: Dict[str, Any]) -> None:
        """Create a room from JSON data."""
        room = Room(
            room_id=room_id,
            name=room_data["name"],
            description=room_data["description"],
            coords=tuple(room_data.get("coords")) if room_data.get("coords") else None,
            room_type=room_data.get("room_type", "normal"),
            lighting=room_data.get("lighting", "bright"),
        )
        
        # Set room properties
        room.is_safe = room_data.get("is_safe", room.room_type == 'safe_zone')
        room.ambient_sound = room_data.get("ambient_sound", "")
        
        # Add exits
        exits_data = room_data.get("exits", {})
        for direction_str, exit_data in exits_data.items():
            try:
                direction = ExitDirection(direction_str)
                room.add_exit(
                    direction=direction,
                    destination_room=exit_data["destination"],
                    destination_area=exit_data.get("destination_area")
                )
            except ValueError:
                print(f"Warning: Invalid direction '{direction_str}' in room {room_id}")
                
        # Add items
        items_data = room_data.get("items", {})
        for item_id, item_data in items_data.items():
            room.add_item(
                item_id=item_id,
                name=item_data["name"],
                description=item_data["description"],
                can_take=item_data.get("can_take", True),
                quantity=item_data.get("quantity", 1)
            )
            
        # Add enemies
        enemies_data = room_data.get("enemies", {})
        for enemy_id, enemy_data in enemies_data.items():
            room.add_enemy(
                enemy_id=enemy_id,
                enemy_type=enemy_data["enemy_type"],
                quantity=enemy_data.get("quantity", 1),
                encounter_name=enemy_data.get("encounter_name", enemy_data["enemy_type"]),
                respawn=enemy_data.get("respawn", False)
            )
            
        self.add_room(room)
        
    def _create_default_cave(self) -> None:
        """Create default cave structure if JSON data not available."""
        # Cave Entrance
        entrance = Room(
            "cave_entrance",
            "Cave Entrance", 
            "You stand at the mouth of a dark cave. Water drips from the ceiling, and strange sounds echo from within."
        )
        entrance.is_safe = True
        entrance.add_item("rusty_dagger", "rusty dagger", "A rusty dagger lies on the ground.")
        entrance.add_exit(ExitDirection.NORTH, "main_chamber")
        entrance.add_exit(ExitDirection.SOUTH, "forest_entrance", "forest_path")
        self.add_room(entrance)
        
        # Main Chamber
        main_chamber = Room(
            "main_chamber",
            "Main Cave Chamber",
            "A larger cavern opens before you. A small goblin guards the eastern passage."
        )
        main_chamber.add_enemy("tutorial_goblin", "tutorial_goblin", encounter_name="goblin")
        main_chamber.add_exit(ExitDirection.SOUTH, "cave_entrance")
        main_chamber.add_exit(ExitDirection.EAST, "eastern_passage")
        main_chamber.add_exit(ExitDirection.WEST, "western_alcove") 
        main_chamber.add_exit(ExitDirection.NORTH, "boss_chamber")
        self.add_room(main_chamber)
        
        # Eastern Passage (Optional)
        eastern = Room(
            "eastern_passage",
            "Eastern Passage",
            "A narrow passage with a small rat scurrying about."
        )
        eastern.add_enemy("tutorial_rat", "tutorial_rat", encounter_name="cave rat")
        eastern.add_item("healing_herb", "healing herb", "A healing herb grows from the wall.")
        eastern.add_exit(ExitDirection.WEST, "main_chamber")
        self.add_room(eastern)
        
        # Western Alcove (Optional)
        western = Room(
            "western_alcove", 
            "Western Alcove",
            "A small alcove with ancient bones scattered about."
        )
        western.is_safe = True
        western.add_item("silver_coin", "silver coin", "A silver coin glints among the bones.")
        western.add_exit(ExitDirection.EAST, "main_chamber")  
        self.add_room(western)
        
        # Boss Chamber
        boss_chamber = Room(
            "boss_chamber",
            "Final Chamber",
            "The deepest chamber with ancient stone pillars and a natural spring."
        )
        boss_chamber.add_enemy("boss_encounter", "tutorial_multi", encounter_name="goblin warriors", quantity=2)
        boss_chamber.add_item("crystal_gem", "crystal gem", "A glowing crystal gem sits by the spring.")
        boss_chamber.add_exit(ExitDirection.SOUTH, "main_chamber")
        boss_chamber.add_exit(ExitDirection.UP, "cave_exit")
        self.add_room(boss_chamber)
        
        # Cave Exit
        cave_exit = Room(
            "cave_exit",
            "Cave Exit",
            "You emerge at the far end of the cave onto a hillside overlooking the forest."
        )
        cave_exit.is_safe = True
        cave_exit.add_exit(ExitDirection.DOWN, "boss_chamber")
        cave_exit.add_exit(ExitDirection.EAST, "forest_clearing", "forest_path")
        self.add_room(cave_exit)
        
        self.starting_room = "cave_entrance"
        
    def get_starting_room(self) -> str:
        """Return the starting room ID for the tutorial cave."""
        return self.starting_room
        
    def get_tutorial_status(self) -> Dict[str, Any]:
        """Get tutorial progress and status."""
        required_rooms = ["cave_entrance", "main_chamber", "boss_chamber", "cave_exit"]
        visited_required = sum(1 for room_id in required_rooms if self.get_room(room_id).visited)
        
        return {
            'area_name': self.name,
            'tutorial_complete': self.tutorial_complete,
            'lessons_learned': self.lessons_learned.copy(),
            'encounters_completed': len(self.encounters_completed),
            'required_encounters': len(self.required_encounters),
            'rooms_visited': visited_required,
            'required_rooms': len(required_rooms),
            'completion_percentage': (visited_required / len(required_rooms)) * 100
        }
        
    def on_room_enter(self, room_id: str, character) -> List[str]:
        """Handle tutorial events when entering a room."""
        messages = []
        room = self.get_room(room_id)
        if not room:
            return messages
            
        # Mark room as visited
        if not room.visited:
            self.visit_room(room_id)
            
        # Tutorial-specific room events
        if room_id == "cave_entrance" and not self.lessons_learned['examination']:
            messages.append("This is the cave entrance. Try using 'look' to examine your surroundings!")
            
        elif room_id == "main_chamber" and not self.lessons_learned['combat']:
            if room.get_active_enemies():
                messages.append("An enemy blocks your path! Use 'attack' to engage in combat.")
                
        elif room_id == "boss_chamber" and not room.visited:
            messages.append("This is the final challenge! Multiple enemies await. Good luck!")
            
        elif room_id == "cave_exit":
            messages.append("Congratulations! You have completed the tutorial cave!")
            self.tutorial_complete = True
            
        return messages
        
    def on_enemy_defeated(self, enemy_id: str, room_id: str) -> List[str]:
        """Handle tutorial events when enemy is defeated."""
        messages = []
        room = self.get_room(room_id)
        if room:
            room.defeat_enemy(enemy_id)
            self.encounters_completed.add(enemy_id)
            
        # Tutorial messages for first combat
        if enemy_id == "tutorial_goblin" and not self.lessons_learned['combat']:
            self.lessons_learned['combat'] = True
            messages.append("Well done! You've won your first combat. You can use 'auto' to enable automatic attacking.")
            
        elif enemy_id == "boss_encounter":
            messages.append("Excellent! You've defeated the final challenge. The path forward is clear!")
            
        return messages
        
    def on_item_taken(self, item_id: str, room_id: str) -> List[str]:
        """Handle tutorial events when item is taken."""
        messages = []
        
        if item_id == "rusty_dagger" and not self.lessons_learned['item_pickup']:
            self.lessons_learned['item_pickup'] = True
            messages.append("Good! You picked up your first item. Items can help you in combat and exploration.")
            
        elif item_id == "healing_herb":
            messages.append("Herbs can restore health. Keep exploring to find more useful items!")
            
        elif item_id == "crystal_gem":
            messages.append("The crystal gem pulses with magical energy. This marks your mastery of the cave!")
            
        return messages
        
    def get_contextual_help(self, room_id: str) -> Optional[str]:
        """Get contextual help based on current room and tutorial progress."""
        room = self.get_room(room_id)
        if not room:
            return None
            
        # Provide help based on room and progress
        if room_id == "cave_entrance" and not self.lessons_learned['examination']:
            return "Try 'look' to examine the room, and 'get dagger' to pick up the weapon."
            
        elif room_id == "main_chamber" and room.get_active_enemies() and not self.lessons_learned['combat']:
            return "There's an enemy here! Use 'attack' to fight it."
            
        elif len([r for r in self.rooms.values() if r.visited]) > 1 and not self.lessons_learned['exploration']:
            return "You can use 'map' to see the cave layout and 'exits' to see where you can go."
            
        return None
        
    def check_tutorial_completion(self) -> bool:
        """Check if tutorial objectives are complete."""
        # Required: visit key rooms and defeat required enemies
        required_rooms = ["cave_entrance", "main_chamber", "boss_chamber"]
        rooms_visited = all(self.get_room(room_id).visited for room_id in required_rooms)
        
        required_enemies_defeated = all(
            enemy_id in self.encounters_completed 
            for enemy_id in self.required_encounters
        )
        
        self.tutorial_complete = rooms_visited and required_enemies_defeated
        return self.tutorial_complete
        
    def get_next_objective(self) -> Optional[str]:
        """Get the next tutorial objective for the player."""
        if not self.get_room("cave_entrance").visited:
            return "Explore the cave entrance. Use 'look' to examine your surroundings."
            
        entrance = self.get_room("cave_entrance")
        if entrance.get_visible_items() and not self.lessons_learned['item_pickup']:
            return "Pick up the dagger using 'get dagger'."
            
        if not self.get_room("main_chamber").visited:
            return "Go north to enter the main chamber."
            
        main_chamber = self.get_room("main_chamber")
        if main_chamber.get_active_enemies() and 'tutorial_goblin' not in self.encounters_completed:
            return "Defeat the goblin in the main chamber using 'attack'."
            
        if not self.lessons_learned['exploration']:
            return "Explore the optional side areas (east and west) to find items and practice combat."
            
        if not self.get_room("boss_chamber").visited:
            return "Head north to the final chamber for the graduation fight."
            
        boss_chamber = self.get_room("boss_chamber") 
        if boss_chamber.get_active_enemies() and 'boss_encounter' not in self.encounters_completed:
            return "Defeat the goblin warriors in the final chamber."
            
        if not self.get_room("cave_exit").visited:
            return "Go up to exit the cave and complete the tutorial."
            
        return "Tutorial complete! You can now explore the forest."
        
    def get_progress_summary(self) -> str:
        """Get a summary of tutorial progress."""
        status = self.get_tutorial_status()
        
        progress_lines = [
            f"Tutorial Cave Progress: {status['completion_percentage']:.0f}%",
            f"Rooms Visited: {status['rooms_visited']}/{status['required_rooms']}",
            f"Encounters Won: {status['encounters_completed']}/{status['required_encounters']}",
        ]
        
        # Add lesson status
        learned = [lesson for lesson, completed in status['lessons_learned'].items() if completed]
        if learned:
            progress_lines.append(f"Skills Learned: {', '.join(learned)}")
            
        next_obj = self.get_next_objective()
        if next_obj:
            progress_lines.append(f"Next Objective: {next_obj}")
            
        return "\n".join(progress_lines)


# Test function for tutorial cave
def _test_tutorial_cave():
    """Test tutorial cave functionality."""
    cave = TutorialCaveArea()
    
    # Test basic structure
    assert cave.area_id == "tutorial_cave"
    assert cave.starting_room == "cave_entrance"
    assert len(cave.rooms) > 0
    
    # Test room access
    entrance = cave.get_room("cave_entrance")
    assert entrance is not None
    assert entrance.is_safe == True
    
    main_chamber = cave.get_room("main_chamber")
    assert main_chamber is not None
    assert len(main_chamber.get_active_enemies()) > 0
    
    # Test tutorial progression
    status = cave.get_tutorial_status()
    assert status['tutorial_complete'] == False
    
    # Test room entering
    messages = cave.on_room_enter("cave_entrance", None)
    assert len(messages) > 0
    
    # Test item pickup
    item_messages = cave.on_item_taken("rusty_dagger", "cave_entrance")
    assert len(item_messages) > 0
    assert cave.lessons_learned['item_pickup'] == True
    
    # Test objectives
    objective = cave.get_next_objective()
    assert objective is not None
    
    print("Tutorial cave tests passed!")


if __name__ == "__main__":
    _test_tutorial_cave()