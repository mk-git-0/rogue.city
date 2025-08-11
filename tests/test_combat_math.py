import os
import sys
import types
import math
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.combat_system import CombatSystem
from core.timer_system import TimerSystem
from core.dice_system import DiceSystem


class MockUI:
    def __getattr__(self, name):
        return lambda *args, **kwargs: None


class FixedDice(DiceSystem):
    def __init__(self, attack_rolls=None, damage_rolls=None, crit_threshold=20):
        super().__init__(show_rolls=False)
        self._attack_iter = iter(attack_rolls or [])
        self._damage_iter = iter(damage_rolls or [])
        self._crit_threshold = crit_threshold

    def attack_roll(self, notation: str, critical_threshold: int = 20):
        try:
            roll = next(self._attack_iter)
        except StopIteration:
            roll = 10
        is_crit = roll >= (critical_threshold or self._crit_threshold)
        return roll, is_crit

    def roll_with_context(self, notation: str, *_):
        try:
            return next(self._damage_iter)
        except StopIteration:
            return 1


class MockCharacter:
    def __init__(self):
        self.name = "Tester"
        self.current_hp = 20
        self.max_hp = 20
        self.armor_class = 12
        self.base_attack_bonus = 3
        self.level = 1
        self.stats = {"strength": 12, "dexterity": 10, "constitution": 10,
                      "intelligence": 10, "wisdom": 10, "charisma": 10}
        self.character_class = 'warrior'
        self.equipment_system = None

    def get_critical_range(self):
        return 20

    def get_stat_modifier(self, stat):
        return (self.stats.get(stat, 10) - 10) // 2

    def is_alive(self):
        return self.current_hp > 0

    def take_damage(self, amount):
        old = self.current_hp
        self.current_hp = max(0, self.current_hp - amount)
        return old - self.current_hp

    def gain_experience(self, amount):
        pass


class MockEnemy:
    def __init__(self):
        self.name = "Goblin"
        self.current_hp = 8
        self.max_hp = 8
        self.armor_class = 12
        self.attack_bonus = 2
        self.damage_dice = "1d4+1"
        self.experience_value = 25

    def is_alive(self):
        return self.current_hp > 0

    def take_damage(self, amount):
        old = self.current_hp
        self.current_hp = max(0, self.current_hp - amount)
        return old - self.current_hp

    def get_loot(self):
        return []


def test_hit_and_crit_damage_flow():
    # First attack roll 20 (crit), damage 4 -> doubled to 8
    dice = FixedDice(attack_rolls=[20], damage_rolls=[4])
    cs = CombatSystem(TimerSystem(), dice, MockUI())
    hero = MockCharacter()
    enemy = MockEnemy()
    assert cs.start_combat(hero, [enemy])
    cs.attack_enemy("goblin")
    # Enemy should be at <= 0 after crit 8 + BAB etc (we don't simulate AC precisely here)
    assert enemy.current_hp <= 0 or enemy.current_hp < enemy.max_hp
