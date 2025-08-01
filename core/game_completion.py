"""
Game completion system for Rogue City with statistics tracking and achievements.
Handles play time, statistics, achievements, and final completion display.
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class GameStatistics:
    """Container for game statistics."""
    start_time: float = field(default_factory=time.time)
    enemies_defeated: int = 0
    areas_explored: int = 0
    items_found: int = 0
    levels_gained: int = 0
    total_damage_dealt: int = 0
    total_damage_taken: int = 0
    commands_entered: int = 0
    times_died: int = 0
    items_equipped: int = 0
    areas_discovered: List[str] = field(default_factory=list)
    enemies_defeated_list: List[str] = field(default_factory=list)
    items_found_list: List[str] = field(default_factory=list)


@dataclass
class Achievement:
    """Individual achievement definition."""
    id: str
    name: str
    description: str
    condition_met: bool = False
    hidden: bool = False


class GameCompletion:
    """Manages game completion, statistics, and achievements."""
    
    def __init__(self, game_engine):
        self.game = game_engine
        self.stats = GameStatistics()
        self.achievements: Dict[str, Achievement] = {}
        self.game_completed = False
        self.completion_time: Optional[float] = None
        self.setup_achievements()
    
    def setup_achievements(self):
        """Initialize all available achievements."""
        achievements_data = [
            # Tutorial achievements
            ("tutorial_complete", "Tutorial Master", "Complete the tutorial cave", False),
            ("first_combat", "First Blood", "Win your first combat", False),
            ("first_item", "Treasure Hunter", "Find your first item", False),
            ("first_level", "Growing Stronger", "Reach level 2", False),
            
            # Combat achievements
            ("monster_slayer", "Monster Slayer", "Defeat 10 enemies", False),
            ("veteran_warrior", "Veteran Warrior", "Defeat 25 enemies", False),
            ("combat_expert", "Combat Expert", "Win 5 combats without taking damage", False),
            ("critical_master", "Critical Master", "Land 10 critical hits", False),
            
            # Exploration achievements
            ("explorer", "Explorer", "Discover 5 different areas", False),
            ("cartographer", "Cartographer", "Explore every room available", False),
            ("forest_ranger", "Forest Ranger", "Complete forest exploration", False),
            
            # Character achievements
            ("equipment_master", "Equipment Master", "Equip 10 different items", False),
            ("inventory_full", "Pack Rat", "Fill your inventory to capacity", False),
            ("stat_boost", "Enhanced", "Gain stat bonuses from equipment", False),
            
            # Class-specific achievements (determined by character class)
            ("rogue_master", "Master Thief", "Complete game as Rogue (Difficulty 11)", False),
            ("knight_master", "Noble Warrior", "Complete game as Knight (Difficulty 3)", False),
            ("mage_master", "Arcane Scholar", "Complete game as Mage (Difficulty 9)", False),
            ("mystic_master", "Enlightened One", "Complete game as Mystic (Difficulty 6)", False),
            
            # Speed achievements
            ("speedrun", "Speed Runner", "Complete game in under 30 minutes", False),
            ("casual_explorer", "Casual Explorer", "Take time to explore (over 60 minutes)", False),
            
            # Special achievements
            ("perfectionist", "Perfectionist", "Complete without dying", False),
            ("pacifist", "Peaceful Soul", "Complete with minimal combat", False),
            ("collector", "Collector", "Find every available item", False),
            ("city_reached", "Rogue City Reached", "Successfully reach Rogue City", False),
        ]
        
        for aid, name, desc, hidden in achievements_data:
            self.achievements[aid] = Achievement(aid, name, desc, False, hidden)
    
    def track_game_start(self):
        """Track when the game actually starts (after character creation)."""
        self.stats.start_time = time.time()
    
    def track_command_entered(self):
        """Track player command entry."""
        self.stats.commands_entered += 1
    
    def track_enemy_defeat(self, enemy_name: str, damage_dealt: int = 0):
        """Track enemy defeat and related statistics."""
        self.stats.enemies_defeated += 1
        self.stats.total_damage_dealt += damage_dealt
        
        if enemy_name not in self.stats.enemies_defeated_list:
            self.stats.enemies_defeated_list.append(enemy_name)
        
        # Check achievements
        self._check_achievement("first_combat")
        
        if self.stats.enemies_defeated >= 10:
            self._check_achievement("monster_slayer")
        
        if self.stats.enemies_defeated >= 25:
            self._check_achievement("veteran_warrior")
    
    def track_area_discovery(self, area_name: str):
        """Track area discovery."""
        if area_name not in self.stats.areas_discovered:
            self.stats.areas_discovered.append(area_name)
            self.stats.areas_explored += 1
            
            # Check achievements
            if self.stats.areas_explored >= 5:
                self._check_achievement("explorer")
            
            # Specific area achievements
            if "tutorial" in area_name.lower():
                self._check_achievement("tutorial_complete")
            elif "forest" in area_name.lower():
                self._check_achievement("forest_ranger")
    
    def track_item_found(self, item_name: str):
        """Track item discovery."""
        if item_name not in self.stats.items_found_list:
            self.stats.items_found_list.append(item_name)
            self.stats.items_found += 1
            
            # Check achievements
            self._check_achievement("first_item")
    
    def track_item_equipped(self, item_name: str):
        """Track item equipment."""
        self.stats.items_equipped += 1
        
        if self.stats.items_equipped >= 10:
            self._check_achievement("equipment_master")
        
        self._check_achievement("stat_boost")
    
    def track_level_gained(self, new_level: int):
        """Track level progression."""
        self.stats.levels_gained += 1
        
        if new_level >= 2:
            self._check_achievement("first_level")
    
    def track_damage_taken(self, damage: int):
        """Track damage taken."""
        self.stats.total_damage_taken += damage
    
    def track_death(self):
        """Track player death."""
        self.stats.times_died += 1
    
    def track_critical_hit(self):
        """Track critical hit."""
        # This would be called from combat system
        pass
    
    def check_inventory_full(self, is_full: bool):
        """Check if inventory is full for achievement."""
        if is_full:
            self._check_achievement("inventory_full")
    
    def complete_game(self, final_area: str = "Rogue City"):
        """Mark game as completed and display completion screen."""
        if self.game_completed:
            return
        
        self.game_completed = True
        self.completion_time = time.time()
        
        # Final achievements
        self._check_achievement("city_reached")
        
        # Class-specific achievement
        if hasattr(self.game, 'current_player') and self.game.current_player:
            player_class = self.game.current_player.character_class.lower()
            class_achievement = f"{player_class}_master"
            if class_achievement in self.achievements:
                self._check_achievement(class_achievement)
        
        # Time-based achievements
        play_time = self.get_play_time_minutes()
        if play_time < 30:
            self._check_achievement("speedrun")
        elif play_time > 60:
            self._check_achievement("casual_explorer")
        
        # Death-based achievement
        if self.stats.times_died == 0:
            self._check_achievement("perfectionist")
        
        # Combat-based achievement (fewer than 5 enemies defeated)
        if self.stats.enemies_defeated < 5:
            self._check_achievement("pacifist")
        
        self.display_completion_screen()
    
    def _check_achievement(self, achievement_id: str):
        """Check and unlock an achievement."""
        if achievement_id in self.achievements and not self.achievements[achievement_id].condition_met:
            self.achievements[achievement_id].condition_met = True
            achievement = self.achievements[achievement_id]
            
            # Display achievement notification
            if hasattr(self.game, 'ui'):
                self.game.ui.log_info("")
                self.game.ui.log_success(f"🏆 ACHIEVEMENT UNLOCKED: {achievement.name}")
                self.game.ui.log_info(f"   {achievement.description}")
                self.game.ui.log_info("")
    
    def get_play_time_minutes(self) -> int:
        """Get total play time in minutes."""
        if self.completion_time:
            return int((self.completion_time - self.stats.start_time) / 60)
        else:
            return int((time.time() - self.stats.start_time) / 60)
    
    def get_play_time_formatted(self) -> str:
        """Get formatted play time string."""
        if self.completion_time:
            total_seconds = int(self.completion_time - self.stats.start_time)
        else:
            total_seconds = int(time.time() - self.stats.start_time)
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        else:
            return f"{minutes}m {seconds}s"
    
    def get_completion_percentage(self) -> int:
        """Calculate game completion percentage."""
        total_achievements = len([a for a in self.achievements.values() if not a.hidden])
        completed_achievements = len([a for a in self.achievements.values() if a.condition_met and not a.hidden])
        
        if total_achievements == 0:
            return 100
        
        return int((completed_achievements / total_achievements) * 100)
    
    def display_completion_screen(self):
        """Display the final game completion screen."""
        if not hasattr(self.game, 'ui'):
            return
        
        ui = self.game.ui
        player = self.game.current_player if hasattr(self.game, 'current_player') else None
        
        # Clear screen and show completion
        ui.log_info("\n" * 3)
        ui.log_success("🎉" * 20)
        ui.log_success("🎉" + " " * 16 + "CONGRATULATIONS!" + " " * 16 + "🎉")
        ui.log_success("🎉" + " " * 14 + "You have reached Rogue City!" + " " * 14 + "🎉")
        ui.log_success("🎉" * 20)
        ui.log_info("")
        
        # Character information
        if player:
            ui.log_info(f"Character: {player.name} the {player.character_class} (Level {player.level})")
        
        # Play statistics
        ui.log_info(f"Play Time: {self.get_play_time_formatted()}")
        ui.log_info(f"Enemies Defeated: {self.stats.enemies_defeated}")
        ui.log_info(f"Areas Explored: {self.stats.areas_explored}")
        ui.log_info(f"Items Found: {self.stats.items_found}")
        ui.log_info(f"Commands Entered: {self.stats.commands_entered}")
        
        if self.stats.levels_gained > 0:
            ui.log_info(f"Levels Gained: {self.stats.levels_gained}")
        
        ui.log_info("")
        
        # Achievements
        earned_achievements = [a for a in self.achievements.values() if a.condition_met and not a.hidden]
        if earned_achievements:
            ui.log_info("ACHIEVEMENTS EARNED:")
            for achievement in earned_achievements:
                ui.log_success(f"✓ {achievement.name} - {achievement.description}")
        
        ui.log_info("")
        
        # Completion stats
        completion_pct = self.get_completion_percentage()
        ui.log_info(f"Game Completion: {completion_pct}%")
        
        # Class-specific completion message
        if player:
            class_messages = {
                "rogue": f"You mastered the shadows and reached the city through cunning and stealth! (Difficulty {self._get_class_difficulty(player.character_class)})",
                "knight": f"Your noble valor and steadfast courage have brought you to Rogue City! (Difficulty {self._get_class_difficulty(player.character_class)})",
                "mage": f"Through arcane knowledge and mystical power, you have arrived at your destination! (Difficulty {self._get_class_difficulty(player.character_class)})",
                "mystic": f"Your balance of mind and body has guided you safely to Rogue City! (Difficulty {self._get_class_difficulty(player.character_class)})"
            }
            
            class_key = player.character_class.lower()
            if class_key in class_messages:
                ui.log_info("")
                ui.log_info(class_messages[class_key])
        
        ui.log_info("")
        ui.log_success("Thank you for playing Rogue City!")
        ui.log_info("Your character has been saved for future adventures.")
        
        # Additional stats for impressive demo
        if self.stats.total_damage_dealt > 0:
            ui.log_info(f"\nCombat Statistics:")
            ui.log_info(f"Total Damage Dealt: {self.stats.total_damage_dealt}")
            ui.log_info(f"Total Damage Taken: {self.stats.total_damage_taken}")
            
            if self.stats.enemies_defeated > 0:
                avg_damage = self.stats.total_damage_dealt // self.stats.enemies_defeated
                ui.log_info(f"Average Damage per Enemy: {avg_damage}")
        
        ui.log_info("")
        ui.log_success("🌟 " * 10)
        ui.log_success("🌟" + " " * 8 + "A ROGUE CITY ADVENTURE COMPLETE" + " " * 8 + "🌟")
        ui.log_success("🌟 " * 10)
        ui.log_info("")
    
    def _get_class_difficulty(self, character_class: str) -> int:
        """Get difficulty rating for character class."""
        difficulty_map = {
            "rogue": 11,
            "knight": 3,
            "mage": 9,
            "mystic": 6
        }
        return difficulty_map.get(character_class.lower(), 5)
    
    def display_current_stats(self):
        """Display current game statistics."""
        if not hasattr(self.game, 'ui'):
            return
        
        ui = self.game.ui
        ui.log_info("=== CURRENT GAME STATISTICS ===")
        ui.log_info(f"Play Time: {self.get_play_time_formatted()}")
        ui.log_info(f"Enemies Defeated: {self.stats.enemies_defeated}")
        ui.log_info(f"Areas Explored: {self.stats.areas_explored}")
        ui.log_info(f"Items Found: {self.stats.items_found}")
        ui.log_info(f"Commands Entered: {self.stats.commands_entered}")
        
        # Show recent achievements
        recent_achievements = [a for a in self.achievements.values() if a.condition_met and not a.hidden]
        if recent_achievements:
            ui.log_info("")
            ui.log_info("Recent Achievements:")
            for achievement in recent_achievements[-3:]:  # Show last 3
                ui.log_success(f"✓ {achievement.name}")
    
    def display_achievements(self):
        """Display all achievements and their status."""
        if not hasattr(self.game, 'ui'):
            return
        
        ui = self.game.ui
        ui.log_info("=== ACHIEVEMENTS ===")
        
        # Separate earned and unearned
        earned = [a for a in self.achievements.values() if a.condition_met and not a.hidden]
        unearned = [a for a in self.achievements.values() if not a.condition_met and not a.hidden]
        
        if earned:
            ui.log_info("EARNED:")
            for achievement in earned:
                ui.log_success(f"✓ {achievement.name} - {achievement.description}")
        
        if unearned:
            ui.log_info("")
            ui.log_info("NOT YET EARNED:")
            for achievement in unearned:
                ui.log_info(f"◯ {achievement.name} - {achievement.description}")
        
        completion_pct = self.get_completion_percentage()
        ui.log_info("")
        ui.log_info(f"Achievement Progress: {len(earned)}/{len(earned) + len(unearned)} ({completion_pct}%)")
    
    def save_statistics(self) -> Dict[str, Any]:
        """Save statistics data for character save file."""
        return {
            'statistics': {
                'start_time': self.stats.start_time,
                'enemies_defeated': self.stats.enemies_defeated,
                'areas_explored': self.stats.areas_explored,
                'items_found': self.stats.items_found,
                'levels_gained': self.stats.levels_gained,
                'total_damage_dealt': self.stats.total_damage_dealt,
                'total_damage_taken': self.stats.total_damage_taken,
                'commands_entered': self.stats.commands_entered,
                'times_died': self.stats.times_died,
                'items_equipped': self.stats.items_equipped,
                'areas_discovered': self.stats.areas_discovered,
                'enemies_defeated_list': self.stats.enemies_defeated_list,
                'items_found_list': self.stats.items_found_list
            },
            'achievements': {
                aid: {
                    'name': achievement.name,
                    'description': achievement.description,
                    'condition_met': achievement.condition_met,
                    'hidden': achievement.hidden
                }
                for aid, achievement in self.achievements.items()
            },
            'game_completed': self.game_completed,
            'completion_time': self.completion_time
        }
    
    def load_statistics(self, save_data: Dict[str, Any]):
        """Load statistics data from character save file."""
        if 'statistics' in save_data:
            stats_data = save_data['statistics']
            self.stats.start_time = stats_data.get('start_time', time.time())
            self.stats.enemies_defeated = stats_data.get('enemies_defeated', 0)
            self.stats.areas_explored = stats_data.get('areas_explored', 0)
            self.stats.items_found = stats_data.get('items_found', 0)
            self.stats.levels_gained = stats_data.get('levels_gained', 0)
            self.stats.total_damage_dealt = stats_data.get('total_damage_dealt', 0)
            self.stats.total_damage_taken = stats_data.get('total_damage_taken', 0)
            self.stats.commands_entered = stats_data.get('commands_entered', 0)
            self.stats.times_died = stats_data.get('times_died', 0)
            self.stats.items_equipped = stats_data.get('items_equipped', 0)
            self.stats.areas_discovered = stats_data.get('areas_discovered', [])
            self.stats.enemies_defeated_list = stats_data.get('enemies_defeated_list', [])
            self.stats.items_found_list = stats_data.get('items_found_list', [])
        
        if 'achievements' in save_data:
            achievements_data = save_data['achievements']
            for aid, achievement_data in achievements_data.items():
                if aid in self.achievements:
                    self.achievements[aid].condition_met = achievement_data.get('condition_met', False)
        
        self.game_completed = save_data.get('game_completed', False)
        self.completion_time = save_data.get('completion_time')