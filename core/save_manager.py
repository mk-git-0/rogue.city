"""
Save Manager for Rogue City
Handles all save/load operations for character data and game configuration.
"""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
import shutil
from datetime import datetime


class SaveManager:
    """Handles all save/load operations for game data"""
    
    def __init__(self, save_directory: str = "data/saves/"):
        """Initialize save manager with save directory"""
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(parents=True, exist_ok=True)
        
        # Ensure other data directories exist
        Path("data/classes/").mkdir(parents=True, exist_ok=True)
        Path("data/config/").mkdir(parents=True, exist_ok=True)
        
    def save_character(self, character) -> bool:
        """Save character data to JSON file"""
        try:
            save_path = self.save_directory / f"{character.name}.json"
            
            # Create backup if file exists
            if save_path.exists():
                backup_path = save_path.with_suffix('.json.bak')
                shutil.copy2(save_path, backup_path)
                
            # Get character data and add timestamp
            save_data = character.to_dict()
            save_data['save_timestamp'] = datetime.now().isoformat()
            
            # Write to file with pretty formatting
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Error saving character '{character.name}': {e}")
            return False
            
    def load_character(self, character_name: str):
        """Load character from save file and return appropriate character instance"""
        try:
            save_path = self.save_directory / f"{character_name}.json"
            
            if not save_path.exists():
                return None
                
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
                
            # Validate required fields
            required_fields = ['character_name', 'character_class', 'level', 'stats']
            for field in required_fields:
                if field not in save_data:
                    raise ValueError(f"Missing required field: {field}")
                    
            # Import and create appropriate character class
            character_class = save_data['character_class'].lower()
            
            if character_class == 'rogue':
                from characters.class_rogue import Rogue
                return Rogue.from_dict(save_data)
            elif character_class == 'knight':
                from characters.class_knight import Knight
                return Knight.from_dict(save_data)
            elif character_class == 'mage':
                from characters.class_mage import Mage
                return Mage.from_dict(save_data)
            elif character_class == 'mystic':
                from characters.class_mystic import Mystic
                return Mystic.from_dict(save_data)
            elif character_class == 'ninja':
                from characters.class_ninja import Ninja
                return Ninja.from_dict(save_data)
            elif character_class == 'warlock':
                from characters.class_warlock import Warlock
                return Warlock.from_dict(save_data)
            elif character_class == 'necromancer':
                from characters.class_necromancer import Necromancer
                return Necromancer.from_dict(save_data)
            elif character_class == 'witchhunter':
                from characters.class_witchhunter import Witchhunter
                return Witchhunter.from_dict(save_data)
            else:
                raise ValueError(f"Unknown character class: {character_class}")
                
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error loading character '{character_name}': {e}")
            return None
            
    def list_saved_characters(self) -> List[Dict[str, Any]]:
        """Return list of available characters with basic info"""
        try:
            characters = []
            save_files = list(self.save_directory.glob("*.json"))
            
            for save_file in save_files:
                if save_file.name.endswith('.bak'):
                    continue
                    
                try:
                    with open(save_file, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                        
                    character_info = {
                        'name': save_data.get('character_name', save_file.stem),
                        'class': save_data.get('character_class', 'unknown'),
                        'level': save_data.get('level', 0),
                        'save_time': save_data.get('save_timestamp', 'unknown'),
                        'creation_complete': save_data.get('creation_complete', True)
                    }
                    characters.append(character_info)
                    
                except Exception as e:
                    print(f"Error reading save file {save_file}: {e}")
                    continue
                    
            # Sort by save timestamp (most recent first)
            characters.sort(key=lambda x: x.get('save_time', ''), reverse=True)
            return characters
            
        except Exception as e:
            print(f"Error listing saved characters: {e}")
            return []
            
    def delete_character(self, character_name: str) -> bool:
        """Delete character save file and backup"""
        try:
            save_path = self.save_directory / f"{character_name}.json"
            backup_path = save_path.with_suffix('.json.bak')
            
            deleted = False
            if save_path.exists():
                save_path.unlink()
                deleted = True
                
            if backup_path.exists():
                backup_path.unlink()
                
            return deleted
            
        except Exception as e:
            print(f"Error deleting character '{character_name}': {e}")
            return False
            
    def character_name_exists(self, name: str) -> bool:
        """Check if character name is already taken"""
        save_path = self.save_directory / f"{name}.json"
        return save_path.exists()
        
    def load_class_definitions(self) -> Dict[str, Any]:
        """Load class definition data from JSON file"""
        try:
            class_file = Path("data/classes/class_definitions.json")
            
            if not class_file.exists():
                # Return default class definitions if file doesn't exist
                return self._get_default_class_definitions()
                
            with open(class_file, 'r', encoding='utf-8') as f:
                class_data = json.load(f)
                
            # Validate class data structure
            required_classes = ['rogue', 'knight', 'mage', 'mystic', 'warrior', 'ranger', 'paladin', 'barbarian', 'thief', 'spellsword', 'priest', 'ninja', 'warlock', 'necromancer', 'witchhunter']
            for class_name in required_classes:
                if class_name not in class_data:
                    print(f"Warning: Missing class definition for {class_name}")
                    
            return class_data
            
        except Exception as e:
            print(f"Error loading class definitions: {e}")
            return self._get_default_class_definitions()
            
    def save_class_definitions(self, class_data: Dict[str, Any]) -> bool:
        """Save class definition data to JSON file"""
        try:
            class_file = Path("data/classes/class_definitions.json")
            
            with open(class_file, 'w', encoding='utf-8') as f:
                json.dump(class_data, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Error saving class definitions: {e}")
            return False
            
    def _get_default_class_definitions(self) -> Dict[str, Any]:
        """Return default class definitions if file is missing"""
        return {
            "rogue": {
                "name": "Rogue",
                "difficulty": 11,
                "description": "Masters of stealth and precision. High difficulty class that rewards skilled play with devastating critical strikes and unmatched mobility.",
                "stat_modifiers": {
                    "strength": -2,
                    "dexterity": 3,
                    "constitution": -2,
                    "intelligence": 2,
                    "wisdom": -1,
                    "charisma": -1
                },
                "hit_die": "d6",
                "base_attack_speed": 2.0,
                "critical_hit_range": 19
            },
            "knight": {
                "name": "Knight",
                "difficulty": 3,
                "description": "Stalwart defenders and front-line fighters. Easy to play with excellent survivability and straightforward combat mechanics.",
                "stat_modifiers": {
                    "strength": 3,
                    "dexterity": 1,
                    "constitution": 2,
                    "intelligence": -1,
                    "wisdom": -1,
                    "charisma": 1
                },
                "hit_die": "d10",
                "base_attack_speed": 4.0,
                "critical_hit_range": 20
            },
            "mage": {
                "name": "Mage",
                "difficulty": 9,
                "description": "Wielders of arcane power with devastating magical abilities. High difficulty glass cannons with complex resource management.",
                "stat_modifiers": {
                    "strength": -2,
                    "dexterity": 0,
                    "constitution": -3,
                    "intelligence": 3,
                    "wisdom": 2,
                    "charisma": 0
                },
                "hit_die": "d4",
                "base_attack_speed": 6.0,
                "critical_hit_range": 20
            },
            "mystic": {
                "name": "Mystic",
                "difficulty": 6,
                "description": "Balanced warriors who blend physical and spiritual training. Moderate difficulty with unique evasion abilities and versatile combat options.",
                "stat_modifiers": {
                    "strength": -1,
                    "dexterity": 4,
                    "constitution": -1,
                    "intelligence": -2,
                    "wisdom": 2,
                    "charisma": 1
                },
                "hit_die": "d8",
                "base_attack_speed": 3.0,
                "critical_hit_range": 20
            },
            "warrior": {
                "name": "Warrior",
                "difficulty": 2,
                "description": "Pure combat specialist with weapon mastery and multiple attacks. Simple but effective melee fighter.",
                "experience_penalty": 5,
                "stat_modifiers": {
                    "strength": 3,
                    "dexterity": 1,
                    "constitution": 2,
                    "intelligence": -2,
                    "wisdom": 0,
                    "charisma": -1
                },
                "hit_die": "d10",
                "base_attack_speed": 3.5,
                "critical_hit_range": 20
            },
            "ranger": {
                "name": "Ranger",
                "difficulty": 5,
                "description": "Wilderness scout with bow mastery, tracking, and nature magic. Versatile outdoorsman and archer.",
                "experience_penalty": 20,
                "stat_modifiers": {
                    "strength": 1,
                    "dexterity": 3,
                    "constitution": 1,
                    "intelligence": 0,
                    "wisdom": 2,
                    "charisma": -1
                },
                "hit_die": "d8",
                "base_attack_speed": 3.0,
                "critical_hit_range": 20
            },
            "paladin": {
                "name": "Paladin",
                "difficulty": 7,
                "description": "Holy warrior with divine magic, healing, and undead turning. Good-aligned knight with divine powers.",
                "experience_penalty": 35,
                "stat_modifiers": {
                    "strength": 2,
                    "dexterity": 0,
                    "constitution": 2,
                    "intelligence": -1,
                    "wisdom": 2,
                    "charisma": 2
                },
                "hit_die": "d10",
                "base_attack_speed": 4.0,
                "critical_hit_range": 20
            },
            "barbarian": {
                "name": "Barbarian",
                "difficulty": 4,
                "description": "Berserker with rage abilities and damage resistance. High HP warrior with fury-based combat.",
                "experience_penalty": 15,
                "stat_modifiers": {
                    "strength": 4,
                    "dexterity": 1,
                    "constitution": 3,
                    "intelligence": -3,
                    "wisdom": -1,
                    "charisma": -1
                },
                "hit_die": "d12",
                "base_attack_speed": 3.0,
                "critical_hit_range": 20
            },
            "thief": {
                "name": "Thief",
                "difficulty": 6,
                "description": "Classic burglar with lockpicking, trap detection, and stealth. Utility-focused rogue variant.",
                "experience_penalty": 20,
                "stat_modifiers": {
                    "strength": -1,
                    "dexterity": 4,
                    "constitution": -1,
                    "intelligence": 2,
                    "wisdom": 1,
                    "charisma": 0
                },
                "hit_die": "d6",
                "base_attack_speed": 2.5,
                "critical_hit_range": 19
            },
            "spellsword": {
                "name": "Spellsword",
                "difficulty": 8,
                "description": "Warrior-mage hybrid combining melee combat with battle magic. Balanced fighter-caster.",
                "experience_penalty": 40,
                "stat_modifiers": {
                    "strength": 2,
                    "dexterity": 1,
                    "constitution": 0,
                    "intelligence": 2,
                    "wisdom": 1,
                    "charisma": -1
                },
                "hit_die": "d8",
                "base_attack_speed": 3.5,
                "critical_hit_range": 20
            },
            "priest": {
                "name": "Priest",
                "difficulty": 7,
                "description": "Divine spellcaster with healing, blessing, and protective magic. Support-focused holy caster.",
                "experience_penalty": 30,
                "stat_modifiers": {
                    "strength": -1,
                    "dexterity": 0,
                    "constitution": 1,
                    "intelligence": 1,
                    "wisdom": 4,
                    "charisma": 2
                },
                "hit_die": "d8",
                "base_attack_speed": 5.0,
                "critical_hit_range": 20
            },
            "ninja": {
                "name": "Ninja",
                "difficulty": 9,
                "description": "Shadow warrior with death strikes, eastern weapons, and honor code. Expert assassin with exotic abilities.",
                "experience_penalty": 50,
                "stat_modifiers": {
                    "strength": -2,
                    "dexterity": 3,
                    "constitution": 1,
                    "intelligence": -2,
                    "wisdom": 2,
                    "charisma": -1
                },
                "hit_die": "d6",
                "base_attack_speed": 2.0,
                "critical_hit_range": 18
            },
            "warlock": {
                "name": "Warlock",
                "difficulty": 10,
                "description": "Battle mage with eldritch blast and weapon enchantment. Spellsword with dark magical abilities.",
                "experience_penalty": 55,
                "stat_modifiers": {
                    "strength": 1,
                    "dexterity": 1,
                    "constitution": 0,
                    "intelligence": 3,
                    "wisdom": 1,
                    "charisma": 1
                },
                "hit_die": "d8",
                "base_attack_speed": 3.5,
                "critical_hit_range": 20
            },
            "necromancer": {
                "name": "Necromancer",
                "difficulty": 11,
                "description": "Death magic master with undead minions and life drain. Evil-aligned specialist in necromantic arts.",
                "experience_penalty": 65,
                "stat_modifiers": {
                    "strength": -2,
                    "dexterity": 0,
                    "constitution": 1,
                    "intelligence": 4,
                    "wisdom": 2,
                    "charisma": -1
                },
                "hit_die": "d6",
                "base_attack_speed": 5.0,
                "critical_hit_range": 20
            },
            "witchhunter": {
                "name": "Witchhunter",
                "difficulty": 12,
                "description": "Anti-magic zealot with supreme spell immunity and magic item destruction. Ultimate anti-caster specialist.",
                "experience_penalty": 70,
                "stat_modifiers": {
                    "strength": 2,
                    "dexterity": -1,
                    "constitution": 3,
                    "intelligence": -3,
                    "wisdom": 2,
                    "charisma": -2
                },
                "hit_die": "d10",
                "base_attack_speed": 3.5,
                "critical_hit_range": 19
            }
        }
        
    def backup_save_file(self, character_name: str) -> bool:
        """Create backup of character save file"""
        try:
            save_path = self.save_directory / f"{character_name}.json"
            
            if not save_path.exists():
                return False
                
            backup_path = save_path.with_suffix(f'.json.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            shutil.copy2(save_path, backup_path)
            
            return True
            
        except Exception as e:
            print(f"Error creating backup for '{character_name}': {e}")
            return False
            
    def restore_from_backup(self, character_name: str, backup_timestamp: str = None) -> bool:
        """Restore character from backup file"""
        try:
            if backup_timestamp:
                backup_path = self.save_directory / f"{character_name}.json.backup_{backup_timestamp}"
            else:
                # Find most recent backup
                backup_files = list(self.save_directory.glob(f"{character_name}.json.backup_*"))
                if not backup_files:
                    return False
                backup_path = max(backup_files, key=lambda p: p.stat().st_mtime)
                
            if not backup_path.exists():
                return False
                
            save_path = self.save_directory / f"{character_name}.json"
            shutil.copy2(backup_path, save_path)
            
            return True
            
        except Exception as e:
            print(f"Error restoring backup for '{character_name}': {e}")
            return False
            
    def _create_character_data(self, character) -> Dict[str, Any]:
        """Create character data dictionary from character object"""
        return character.to_dict()
        
    def _load_character_data(self, character_name: str) -> Optional[Dict[str, Any]]:
        """Load character data dictionary from file"""
        try:
            save_path = self.save_directory / f"{character_name}.json"
            
            if not save_path.exists():
                return None
                
            with open(save_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"Error loading character data for '{character_name}': {e}")
            return None
        
    def _save_character_data(self, character_name: str, character_data: Dict[str, Any]) -> bool:
        """Save character data dictionary to file"""
        try:
            save_path = self.save_directory / f"{character_name}.json"
            
            # Create backup if file exists
            if save_path.exists():
                backup_path = save_path.with_suffix('.json.bak')
                shutil.copy2(save_path, backup_path)
                
            # Add timestamp
            character_data['save_timestamp'] = datetime.now().isoformat()
            
            # Write to file with pretty formatting
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(character_data, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Error saving character data for '{character_name}': {e}")
            return False
            
    def validate_character_save(self, save_data: Dict[str, Any]) -> bool:
        """Validate character save data integrity"""
        try:
            # Check required fields
            required_fields = ['character_name', 'character_class', 'level', 'stats', 'derived_stats']
            for field in required_fields:
                if field not in save_data:
                    return False
                    
            # Check stats structure
            required_stats = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
            stats = save_data.get('stats', {})
            for stat in required_stats:
                if stat not in stats or not isinstance(stats[stat], int):
                    return False
                if stats[stat] < 1 or stats[stat] > 30:  # Reasonable stat range
                    return False
                    
            # Check derived stats
            derived = save_data.get('derived_stats', {})
            required_derived = ['max_hp', 'current_hp', 'armor_class', 'base_attack_bonus']
            for stat in required_derived:
                if stat not in derived or not isinstance(derived[stat], int):
                    return False
                    
            # Validate character class (accept all implemented classes)
            valid_classes = [
                'rogue','knight','mage','mystic','warrior','ranger','paladin','barbarian','thief',
                'spellsword','priest','ninja','warlock','necromancer','witchhunter','druid','bard',
                'missionary','gypsy'
            ]
            if str(save_data.get('character_class')).lower() not in valid_classes:
                return False
                
            return True
            
        except Exception:
            return False