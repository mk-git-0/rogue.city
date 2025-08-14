"""
Enemy Factory for Rogue City
Creates and manages enemy instances from data definitions.
"""

import json
import os
from typing import Dict, List, Optional, Any, Type
from .base_enemy import BaseEnemy, TutorialEnemy


class TutorialGoblin(TutorialEnemy):
    """Tutorial goblin enemy - weak but aggressive"""
    
    def __init__(self, name: str = "goblin"):
        super().__init__(name, "goblin")
        
        # Combat stats
        self.level = 1
        self.max_hp = 8
        self.current_hp = 8
        self.armor_class = 12
        self.attack_bonus = 2
        self.damage_dice = "1d4+1"
        
        # Combat properties
        self.attack_speed = 3.0
        self.experience_value = 50
        self.difficulty_rating = 1
        
        # Loot
        self.loot_table = [
            {'name': 'Rusty Dagger', 'type': 'weapon', 'chance': 25},
            {'name': 'Goblin Ear', 'type': 'misc', 'chance': 80}
        ]
        self.gold_min = 1
        self.gold_max = 3
        
        # AI behavior
        self.ai_aggressive = True
        self.ai_intelligent = False
        
    def get_attack_speed(self) -> float:
        """Goblins attack every 3 seconds"""
        return self.attack_speed
        
    def get_special_abilities(self) -> List[str]:
        """No special abilities for tutorial goblins"""
        return []


class TutorialRat(TutorialEnemy):
    """Tutorial rat enemy - very weak but fast"""
    
    def __init__(self, name: str = "rat"):
        super().__init__(name, "rat")
        
        # Combat stats
        self.level = 1
        self.max_hp = 4
        self.current_hp = 4
        self.armor_class = 13  # Small and quick
        self.attack_bonus = 1
        self.damage_dice = "1d3"
        
        # Combat properties
        self.attack_speed = 2.0  # Faster than goblins
        self.experience_value = 25
        self.difficulty_rating = 1
        
        # Loot
        self.loot_table = [
            {'name': 'Rat Tail', 'type': 'misc', 'chance': 60}
        ]
        self.gold_min = 0
        self.gold_max = 1
        
        # AI behavior
        self.ai_aggressive = True
        self.ai_intelligent = False
        
    def get_attack_speed(self) -> float:
        """Rats attack every 2 seconds"""
        return self.attack_speed
        
    def get_special_abilities(self) -> List[str]:
        """No special abilities for tutorial rats"""
        return []


class TutorialBoss(TutorialEnemy):
    """Tutorial boss enemy - stronger with simple special ability"""
    
    def __init__(self, name: str = "orc warrior"):
        super().__init__(name, "orc")
        
        # Combat stats
        self.level = 3
        self.max_hp = 25
        self.current_hp = 25
        self.armor_class = 14
        self.attack_bonus = 4
        self.damage_dice = "1d8+2"
        
        # Combat properties
        self.attack_speed = 4.0  # Slower but hits harder
        self.experience_value = 150
        self.difficulty_rating = 3
        
        # Special ability tracking
        self.last_special_round = 0
        self.special_cooldown = 3  # Can use special every 3 rounds
        
        # Loot
        self.loot_table = [
            {'name': 'Orcish Axe', 'type': 'weapon', 'chance': 80},
            {'name': 'Chain Mail Vest', 'type': 'armor', 'chance': 60},
            {'name': 'Health Potion', 'type': 'consumable', 'chance': 40}
        ]
        self.gold_min = 5
        self.gold_max = 15
        
        # AI behavior
        self.ai_aggressive = True
        self.ai_intelligent = True  # Can use special abilities
        
    def get_attack_speed(self) -> float:
        """Boss attacks every 4 seconds"""
        return self.attack_speed
        
    def get_special_abilities(self) -> List[str]:
        """Boss has a power attack ability"""
        return ['power_attack']
        
    def choose_combat_action(self, target, allies: List[BaseEnemy] = None) -> str:
        """
        Smart AI that uses special abilities when available.
        
        Args:
            target: The target to attack
            allies: Other enemies (unused for tutorial boss)
            
        Returns:
            Action to perform
        """
        # Use power attack if available and at low health
        if (self.get_hp_percentage() < 0.5 and 
            hasattr(self, 'combat_round') and
            self.combat_round - self.last_special_round >= self.special_cooldown):
            return 'power_attack'
        
        return 'attack'
        
    def use_power_attack(self, target) -> Dict[str, Any]:
        """
        Execute power attack special ability.
        
        Args:
            target: Target to attack
            
        Returns:
            Action result data
        """
        self.last_special_round = getattr(self, 'combat_round', 0)
        
        return {
            'damage_dice': '2d8+4',  # Double damage
            'attack_bonus_modifier': 2,  # +2 to hit
            'message': f"The {self.name} roars and makes a powerful attack!"
        }


class EnemyFactory:
    """
    Factory class for creating enemies from data definitions and templates.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize enemy factory.
        
        Args:
            data_path: Path to enemy data directory (defaults to data/enemies/)
        """
        if data_path is None:
            # Default to data/enemies/ relative to project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            data_path = os.path.join(project_root, "data", "enemies")
            
        self.data_path = data_path
        self.enemy_templates: Dict[str, Dict[str, Any]] = {}
        self.enemy_classes: Dict[str, Type[BaseEnemy]] = {}
        
        # Register built-in enemy types
        self._register_builtin_enemies()
        
        # Load enemy data if available
        self._load_enemy_data()
        
    def _register_builtin_enemies(self) -> None:
        """Register built-in enemy classes"""
        self.enemy_classes.update({
            'tutorial_goblin': TutorialGoblin,
            'tutorial_rat': TutorialRat,
            'tutorial_boss': TutorialBoss,
            'goblin': TutorialGoblin,  # Alias
            'rat': TutorialRat,        # Alias
            'orc': TutorialBoss        # Alias
        })
        
    def _load_enemy_data(self) -> None:
        """Load enemy templates from JSON files"""
        if not os.path.exists(self.data_path):
            return
            
        for filename in os.listdir(self.data_path):
            if filename.endswith('.json'):
                filepath = os.path.join(self.data_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # Store enemy templates
                    if isinstance(data, dict):
                        for enemy_id, enemy_data in data.items():
                            self.enemy_templates[enemy_id] = enemy_data
                            
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Warning: Could not load enemy data from {filename}: {e}")
                    
    def create_enemy(self, enemy_type: str, **kwargs) -> Optional[BaseEnemy]:
        """
        Create an enemy instance of the specified type.
        
        Args:
            enemy_type: Type/ID of enemy to create
            **kwargs: Additional parameters to override defaults
            
        Returns:
            Enemy instance or None if type not found
        """
        # Check for built-in enemy class
        if enemy_type in self.enemy_classes:
            enemy_class = self.enemy_classes[enemy_type]
            
            # Create instance with any provided name
            name = kwargs.get('name', enemy_type)
            enemy = enemy_class(name)
            
            # Apply any stat overrides
            self._apply_stat_overrides(enemy, kwargs)
            
            return enemy
            
        # Check for template-based enemy
        if enemy_type in self.enemy_templates:
            return self._create_from_template(enemy_type, kwargs)
            
        print(f"Warning: Unknown enemy type '{enemy_type}'")
        return None
        
    def _create_from_template(self, enemy_type: str, overrides: Dict[str, Any]) -> Optional[BaseEnemy]:
        """
        Create enemy from JSON template data.
        
        Args:
            enemy_type: Enemy type identifier
            overrides: Stat overrides
            
        Returns:
            Configured enemy instance
        """
        template = self.enemy_templates[enemy_type]
        
        # Create base enemy
        name = overrides.get('name', template.get('name', enemy_type))
        enemy = TutorialEnemy(name, template.get('enemy_type', 'generic'))
        
        # Apply template stats
        enemy.level = template.get('level', 1)
        enemy.max_hp = template.get('max_hp', 10)
        enemy.current_hp = enemy.max_hp
        enemy.armor_class = template.get('armor_class', 10)
        enemy.attack_bonus = template.get('attack_bonus', 0)
        enemy.damage_dice = template.get('damage_dice', '1d4')
        enemy.attack_speed = template.get('attack_speed', 3.0)
        enemy.experience_value = template.get('experience_value', 10)
        enemy.difficulty_rating = template.get('difficulty_rating', 1)
        
        # Loot table
        enemy.loot_table = template.get('loot_table', [])
        # Add tiered loot entry if defined via economy override
        try:
            econ_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'economy', 'loot_tables.json')
            if os.path.exists(econ_path):
                with open(econ_path, 'r') as f:
                    econ = json.load(f)
                tiers = econ.get('enemy_overrides', {}).get(enemy_type, {}).get('tiers')
                if tiers:
                    # Roll one tier according to weights to drop as placeholder; conversion handled in combat system
                    import random
                    total = sum(tiers.values())
                    r = random.randint(1, max(1, total))
                    acc = 0
                    chosen = None
                    for tier, weight in tiers.items():
                        acc += int(weight)
                        if r <= acc:
                            chosen = tier
                            break
                    if chosen:
                        enemy.loot_table.append({'name': chosen, 'type': 'tier', 'chance': 100, 'quantity': 1})
        except Exception:
            pass
        enemy.gold_min = template.get('gold_min', 0)
        enemy.gold_max = template.get('gold_max', 0)
        
        # AI flags
        ai_flags = template.get('ai_flags', {})
        enemy.ai_aggressive = ai_flags.get('aggressive', True)
        enemy.ai_intelligent = ai_flags.get('intelligent', False)
        enemy.ai_pack_hunter = ai_flags.get('pack_hunter', False)
        
        # Apply overrides
        self._apply_stat_overrides(enemy, overrides)
        
        return enemy
        
    def _apply_stat_overrides(self, enemy: BaseEnemy, overrides: Dict[str, Any]) -> None:
        """Apply stat overrides to an enemy instance"""
        for key, value in overrides.items():
            if key == 'name':
                continue  # Already handled
            if hasattr(enemy, key):
                setattr(enemy, key, value)
                
        # Ensure current HP doesn't exceed max HP
        if enemy.current_hp > enemy.max_hp:
            enemy.current_hp = enemy.max_hp
            
    def create_encounter(self, encounter_type: str) -> List[BaseEnemy]:
        """
        Create a pre-defined encounter with multiple enemies.
        
        Args:
            encounter_type: Type of encounter to create
            
        Returns:
            List of enemy instances
        """
        encounters = {
            'tutorial_start': [
                self.create_enemy('tutorial_rat'),
            ],
            'tutorial_goblin': [
                self.create_enemy('tutorial_goblin'),
            ],
            'tutorial_multi': [
                self.create_enemy('tutorial_rat', name='large rat'),
                self.create_enemy('tutorial_goblin'),
            ],
            'tutorial_boss': [
                self.create_enemy('tutorial_boss'),
            ],
            'goblin_pack': [
                self.create_enemy('tutorial_goblin', name='goblin warrior'),
                self.create_enemy('tutorial_goblin', name='goblin scout'),
            ],
            'rat_swarm': [
                self.create_enemy('tutorial_rat', name='sewer rat'),
                self.create_enemy('tutorial_rat', name='cave rat'),
                self.create_enemy('tutorial_rat', name='giant rat'),
            ]
        }
        
        encounter = encounters.get(encounter_type, [])
        # Filter out any None values in case enemy creation failed
        return [enemy for enemy in encounter if enemy is not None]
        
    def list_available_enemies(self) -> List[str]:
        """Get list of all available enemy types"""
        available = list(self.enemy_classes.keys())
        available.extend(self.enemy_templates.keys())
        return sorted(list(set(available)))  # Remove duplicates and sort
        
    def list_available_encounters(self) -> List[str]:
        """Get list of all available encounter types"""
        return [
            'tutorial_start',
            'tutorial_goblin', 
            'tutorial_multi',
            'tutorial_boss',
            'goblin_pack',
            'rat_swarm'
        ]
        
    def get_enemy_info(self, enemy_type: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an enemy type.
        
        Args:
            enemy_type: Enemy type to get info for
            
        Returns:
            Enemy information dictionary or None
        """
        if enemy_type in self.enemy_classes:
            # Create temporary instance to get stats
            temp_enemy = self.create_enemy(enemy_type)
            if temp_enemy:
                return {
                    'name': temp_enemy.name,
                    'type': temp_enemy.enemy_type,
                    'level': temp_enemy.level,
                    'hp': temp_enemy.max_hp,
                    'ac': temp_enemy.armor_class,
                    'attack_bonus': temp_enemy.attack_bonus,
                    'damage': temp_enemy.damage_dice,
                    'speed': temp_enemy.attack_speed,
                    'experience': temp_enemy.experience_value,
                    'difficulty': temp_enemy.difficulty_rating
                }
                
        elif enemy_type in self.enemy_templates:
            return self.enemy_templates[enemy_type].copy()
            
        return None


# Test function for enemy factory
def _test_enemy_factory():
    """Test enemy factory functionality."""
    factory = EnemyFactory()
    
    # Test enemy creation
    goblin = factory.create_enemy('tutorial_goblin')
    assert goblin is not None
    assert goblin.name == 'goblin'
    assert goblin.max_hp == 8
    assert goblin.is_alive()
    
    # Test enemy with custom name
    named_goblin = factory.create_enemy('tutorial_goblin', name='Big Goblin')
    assert named_goblin.name == 'Big Goblin'
    
    # Test encounter creation
    encounter = factory.create_encounter('tutorial_multi')
    assert len(encounter) == 2
    assert any(enemy.name == 'large rat' for enemy in encounter)
    assert any(enemy.name == 'goblin' for enemy in encounter)
    
    # Test listing
    enemies = factory.list_available_enemies()
    assert 'tutorial_goblin' in enemies
    assert 'tutorial_rat' in enemies
    
    encounters = factory.list_available_encounters()
    assert 'tutorial_start' in encounters
    assert 'tutorial_boss' in encounters
    
    # Test enemy info
    info = factory.get_enemy_info('tutorial_goblin')
    assert info is not None
    assert info['hp'] == 8
    assert info['experience'] == 50
    
    print("Enemy factory tests passed!")


if __name__ == "__main__":
    _test_enemy_factory()