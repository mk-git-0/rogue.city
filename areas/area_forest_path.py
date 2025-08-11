"""
Forest Path Area for Rogue City
30-minute exploration experience leading to Rogue City gates.
"""

from typing import Dict, List, Optional, Any
from .base_area import BaseArea, Room, ExitDirection, RoomExit


class ForestPathArea(BaseArea):
    """
    Forest path area providing exploration experience.
    Features multiple paths, optional areas, and leads to game completion.
    """
    
    def __init__(self):
        """Initialize forest path area."""
        super().__init__(
            area_id="forest_path",
            name="Forest Path",
            description="A vast forest stretching toward the legendary city of Rogue City."
        )
        
        # Exploration tracking
        self.game_completed = False
        self.optional_areas_discovered = set()
        self.secrets_found = set()
        
        # Path progression
        self.main_path_rooms = [
            "forest_entrance", "forest_clearing", "deep_forest", 
            "city_approach", "rogue_city_gates", "city_center"
        ]
        
        self.optional_areas = [
            "northern_woods", "ancient_grove", "side_path", 
            "southern_trail", "creek_crossing", "hidden_grove"
        ]
        
        # Special encounters completed
        self.major_encounters = ['forest_guardian', 'forest_wolves', 'path_bandits']
        self.encounters_completed = set()
        
    def _load_area_data(self) -> None:
        """Load forest area data from JSON file."""
        data = self._load_json_data("forest_areas.json")
        if not data:
            self._create_default_forest()
            return
            
        # Load room data
        rooms_data = data.get("rooms", {})
        for room_id, room_data in rooms_data.items():
            self._create_room_from_data(room_id, room_data)
            
        # Set starting room
        area_info = data.get("area_info", {})
        self.starting_room = area_info.get("starting_room", "forest_entrance")
        
        # Load map data
        self._load_map_data("forest_map.txt")
        
        # Set up map legend
        self.map_legend = {
            "[*]": "Your current location",
            "[?]": "Unexplored area",
            "[ROGUE CITY]": "Final destination",
            "[Clearing]": "Forest Clearing (safe)",
            "[Deep Forest]": "Deep Forest (guardian)"
        }
        
    def _create_room_from_data(self, room_id: str, room_data: Dict[str, Any]) -> None:
        """Create a room from JSON data."""
        room = Room(
            room_id=room_id,
            name=room_data["name"],
            description=room_data["description"]
        )
        
        # Set room properties
        room.is_safe = room_data.get("is_safe", False)
        room.ambient_sound = room_data.get("ambient_sound", "")
        
        # Special actions for specific rooms
        if "special_actions" in room_data:
            room.special_actions = room_data["special_actions"]
        
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
        
    def _create_default_forest(self) -> None:
        """Create default forest structure if JSON data not available."""
        # Forest Entrance
        entrance = Room(
            "forest_entrance",
            "Forest Entrance",
            "You stand at the edge of a vast forest with paths leading in multiple directions."
        )
        entrance.is_safe = True
        entrance.add_exit(ExitDirection.NORTH, "cave_entrance", "tutorial_cave")
        entrance.add_exit(ExitDirection.EAST, "forest_clearing")
        self.add_room(entrance)
        
        # Forest Clearing
        clearing = Room(
            "forest_clearing",
            "Forest Clearing",
            "A peaceful clearing with wildflowers and a gentle stream."
        )
        clearing.is_safe = True
        clearing.add_item("wildflowers", "wildflowers", "Beautiful wildflowers grow here.")
        # Loot: a small buckler can sometimes be found here
        clearing.add_item("buckler", "buckler", "A small round buckler lies half-buried in leaves.")
        clearing.add_exit(ExitDirection.WEST, "forest_entrance")
        clearing.add_exit(ExitDirection.EAST, "deep_forest")
        clearing.add_exit(ExitDirection.NORTH, "northern_woods")
        self.add_room(clearing)
        
        # Deep Forest
        deep_forest = Room(
            "deep_forest",
            "Deep Forest",
            "The deepest part of the forest with ancient trees and mysterious shadows."
        )
        deep_forest.add_enemy("forest_guardian", "orc", encounter_name="forest guardian")
        # Loot: a sturdier heater shield hidden among roots
        deep_forest.add_item("heater_shield", "heater shield", "A sturdy heater shield is wedged between massive roots.")
        deep_forest.add_exit(ExitDirection.WEST, "forest_clearing")
        deep_forest.add_exit(ExitDirection.EAST, "city_approach")
        self.add_room(deep_forest)
        
        # City Approach
        city_approach = Room(
            "city_approach",
            "City Approach",
            "The forest thins as you approach the legendary Rogue City."
        )
        city_approach.add_exit(ExitDirection.WEST, "deep_forest")
        city_approach.add_exit(ExitDirection.EAST, "rogue_city_gates")
        self.add_room(city_approach)
        
        # Rogue City Gates
        city_gates = Room(
            "rogue_city_gates", 
            "Gates of Rogue City",
            "You stand before the massive gates of the legendary Rogue City!"
        )
        city_gates.is_safe = True
        city_gates.add_exit(ExitDirection.WEST, "city_approach")
        city_gates.add_exit(ExitDirection.NORTH, "city_center")
        self.add_room(city_gates)
        
        # City Center (Game Completion)
        city_center = Room(
            "city_center",
            "Rogue City Center",
            "You have reached Rogue City! Congratulations - your journey is complete!"
        )
        city_center.is_safe = True
        city_center.add_exit(ExitDirection.SOUTH, "rogue_city_gates")
        self.add_room(city_center)
        
        self.starting_room = "forest_entrance"
        
    def get_starting_room(self) -> str:
        """Return the starting room ID for the forest path."""
        return self.starting_room
        
    def on_room_enter(self, room_id: str, character) -> List[str]:
        """Handle events when entering a room."""
        messages = []
        room = self.get_room(room_id)
        if not room:
            return messages
            
        # Mark room as visited
        if not room.visited:
            self.visit_room(room_id)
            
            # Track optional area discovery
            if room_id in self.optional_areas:
                self.optional_areas_discovered.add(room_id)
                
        # Special room messages
        if room_id == "forest_entrance":
            messages.append("You enter the great forest. Multiple paths stretch before you - choose your route wisely!")
            
        elif room_id == "forest_clearing":
            messages.append("This peaceful clearing seems like a good place to rest and plan your next move.")
            
        elif room_id == "deep_forest" and room.get_active_enemies():
            messages.append("The forest guardian blocks your path! You must prove yourself worthy to continue.")
            
        elif room_id == "ancient_grove":
            messages.append("You have discovered an ancient grove! This mystical place holds rare magical items.")
            self.secrets_found.add("ancient_grove")
            
        elif room_id == "hidden_grove":
            messages.append("You found the hidden grove! Legend speaks of powerful artifacts in this secret place.")
            self.secrets_found.add("hidden_grove")
            
        elif room_id == "city_approach":
            messages.append("The forest thins ahead - you can see the walls of Rogue City in the distance!")
            
        elif room_id == "rogue_city_gates":
            messages.append("You have reached the gates of the legendary Rogue City! Your destination awaits!")
            
        elif room_id == "city_center":
            messages.append("CONGRATULATIONS! You have completed your journey to Rogue City!")
            messages.append("Thank you for playing this demo of Rogue City RPG!")
            self.game_completed = True
            
        return messages
        
    def on_enemy_defeated(self, enemy_id: str, room_id: str) -> List[str]:
        """Handle events when enemy is defeated."""
        messages = []
        room = self.get_room(room_id)
        if room:
            room.defeat_enemy(enemy_id)
            
        # Track major encounters
        encounter_mapping = {
            'forest_guardian': 'forest_guardian',
            'forest_wolves': 'forest_wolves', 
            'path_bandits': 'path_bandits'
        }
        
        for encounter_key, encounter_name in encounter_mapping.items():
            if encounter_key in enemy_id.lower():
                self.encounters_completed.add(encounter_name)
                break
                
        # Special defeat messages
        if 'forest_guardian' in enemy_id.lower():
            messages.append("The forest guardian acknowledges your strength and steps aside.")
            messages.append("The path to Rogue City is now clear!")
            
        elif 'forest_wolves' in enemy_id.lower():
            messages.append("The wolf pack retreats deeper into the forest.")
            
        elif 'bandits' in enemy_id.lower():
            messages.append("The bandits flee, leaving their hidden stash behind!")
            
        return messages
        
    def on_item_taken(self, item_id: str, room_id: str) -> List[str]:
        """Handle events when item is taken."""
        messages = []
        
        # Special item messages
        if item_id == "power_crystal":
            messages.append("The power crystal pulses with magical energy! This is a significant find.")
            self.secrets_found.add("power_crystal")
            
        elif item_id == "mystical_herb":
            messages.append("The mystical herb from the ancient grove may have powerful properties.")
            
        elif item_id == "hidden_stash":
            messages.append("The bandits' stash contains valuable supplies for your journey.")
            
        elif "rare" in item_id.lower():
            messages.append("This rare item will be valuable in the city!")
            
        return messages
        
    def get_exploration_status(self) -> Dict[str, Any]:
        """Get exploration progress and status."""
        main_path_visited = sum(1 for room_id in self.main_path_rooms if self.get_room(room_id).visited)
        optional_visited = len(self.optional_areas_discovered)
        
        return {
            'area_name': self.name,
            'game_completed': self.game_completed,
            'main_path_progress': main_path_visited,
            'total_main_rooms': len(self.main_path_rooms),
            'optional_areas_found': optional_visited,
            'total_optional_areas': len(self.optional_areas),
            'secrets_discovered': len(self.secrets_found),
            'major_encounters_defeated': len(self.encounters_completed),
            'completion_percentage': (main_path_visited / len(self.main_path_rooms)) * 100
        }
        
    def get_next_destination(self) -> Optional[str]:
        """Get suggested next destination for exploration."""
        # Follow main path progression
        for room_id in self.main_path_rooms:
            room = self.get_room(room_id)
            if room and not room.visited:
                return f"Continue on the main path to {room.name}."
                
        # Suggest optional areas
        unvisited_optional = [
            room_id for room_id in self.optional_areas 
            if room_id not in self.optional_areas_discovered
        ]
        
        if unvisited_optional:
            return f"Explore optional areas like {unvisited_optional[0].replace('_', ' ').title()}."
            
        # If everything explored
        if self.game_completed:
            return "Your journey is complete! Congratulations!"
        else:
            return "Continue toward Rogue City to complete your adventure."
            
    def get_exploration_summary(self) -> str:
        """Get a summary of exploration progress."""
        status = self.get_exploration_status()
        
        summary_lines = [
            f"Forest Exploration Progress: {status['completion_percentage']:.0f}%",
            f"Main Path: {status['main_path_progress']}/{status['total_main_rooms']} locations",
            f"Optional Areas: {status['optional_areas_found']}/{status['total_optional_areas']} discovered",
            f"Secrets Found: {status['secrets_discovered']}",
            f"Major Encounters: {status['major_encounters_defeated']}/{len(self.major_encounters)} defeated"
        ]
        
        if status['game_completed']:
            summary_lines.append("STATUS: Journey Complete! Welcome to Rogue City!")
        else:
            next_dest = self.get_next_destination()
            if next_dest:
                summary_lines.append(f"Next: {next_dest}")
                
        return "\n".join(summary_lines)
        
    def check_game_completion(self) -> bool:
        """Check if the game has been completed."""
        city_center = self.get_room("city_center")
        if city_center and city_center.visited:
            self.game_completed = True
            
        return self.game_completed
        
    def get_completion_rewards(self) -> Dict[str, Any]:
        """Get completion rewards and statistics."""
        if not self.game_completed:
            return {}
            
        status = self.get_exploration_status()
        
        # Calculate exploration rating
        exploration_score = 0
        exploration_score += status['main_path_progress'] * 10  # 10 points per main room
        exploration_score += status['optional_areas_found'] * 15  # 15 points per optional area
        exploration_score += status['secrets_discovered'] * 25  # 25 points per secret
        exploration_score += status['major_encounters_defeated'] * 20  # 20 points per encounter
        
        # Determine rating
        if exploration_score >= 300:
            rating = "Master Explorer"
        elif exploration_score >= 200:
            rating = "Expert Explorer"
        elif exploration_score >= 150:
            rating = "Skilled Explorer"
        else:
            rating = "Novice Explorer"
            
        return {
            'game_completed': True,
            'exploration_rating': rating,
            'total_score': exploration_score,
            'rooms_visited': status['main_path_progress'] + status['optional_areas_found'],
            'secrets_found': list(self.secrets_found),
            'encounters_defeated': list(self.encounters_completed),
            'completion_message': f"Congratulations! You reached Rogue City as a {rating}!"
        }
        
    def get_area_hints(self, current_room: str) -> List[str]:
        """Get location-specific hints for exploration."""
        hints = []
        
        room = self.get_room(current_room)
        if not room:
            return hints
            
        # General exploration hints
        if current_room == "forest_clearing":
            hints.append("This clearing connects to many paths. Try exploring in all directions!")
            
        elif current_room == "deep_forest" and room.get_active_enemies():
            hints.append("The forest guardian is powerful. Make sure you're prepared for combat!")
            
        elif current_room == "city_approach":
            hints.append("You're almost at Rogue City! The gates should be just ahead.")
            
        # Hint about unexplored areas
        available_exits = room.get_available_exits()
        for direction, exit_obj in available_exits.items():
            dest_room = self.get_room(exit_obj.destination_room)
            if dest_room and not dest_room.visited:
                hints.append(f"You haven't explored {direction.value} yet - there might be something interesting that way.")
                break
                
        return hints


# Test function for forest path
def _test_forest_path():
    """Test forest path functionality."""
    forest = ForestPathArea()
    
    # Test basic structure
    assert forest.area_id == "forest_path"
    assert forest.starting_room == "forest_entrance"
    assert len(forest.rooms) > 0
    
    # Test room access
    entrance = forest.get_room("forest_entrance")
    assert entrance is not None
    assert entrance.is_safe == True
    
    city_center = forest.get_room("city_center")
    assert city_center is not None
    
    # Test exploration tracking
    status = forest.get_exploration_status()
    assert status['game_completed'] == False
    
    # Test room entering
    messages = forest.on_room_enter("forest_entrance", None)
    assert len(messages) > 0
    
    # Test completion
    forest.visit_room("city_center")
    completion_check = forest.check_game_completion()
    assert completion_check == True
    
    # Test rewards
    rewards = forest.get_completion_rewards()
    assert rewards['game_completed'] == True
    
    print("Forest path tests passed!")


if __name__ == "__main__":
    _test_forest_path()