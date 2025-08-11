#!/usr/bin/env python3
"""
Quick profiling for combat loop hot paths.

Runs a simulated combat and prints timing stats. Use to spot regressions and
bottlenecks. For deeper analysis, run with cProfile: `python -m cProfile -o prof.out scripts/profile_combat.py`.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.combat_system import CombatSystem
from core.timer_system import TimerSystem
from core.dice_system import DiceSystem


class MockUI:
    def __getattr__(self, name):
        return lambda *args, **kwargs: None


class MockCharacter:
    def __init__(self, name="Profiler"):
        self.name = name
        self.current_hp = 100
        self.max_hp = 100
        self.armor_class = 12
        self.base_attack_bonus = 4
        self.level = 5
        self.stats = {"strength": 14, "dexterity": 12, "constitution": 12,
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
        self.current_hp = max(0, self.current_hp - amount)
        return amount

    def gain_experience(self, amount):
        pass


class MockEnemy:
    def __init__(self, name="Dummy", hp=30):
        self.name = name
        self.current_hp = hp
        self.max_hp = hp
        self.armor_class = 12
        self.attack_bonus = 2
        self.damage_dice = "1d4+1"
        self.experience_value = 25

    def is_alive(self):
        return self.current_hp > 0

    def take_damage(self, amount):
        self.current_hp = max(0, self.current_hp - amount)
        return amount

    def get_loot(self):
        return []


def main():
    ui = MockUI()
    cs = CombatSystem(TimerSystem(), DiceSystem(show_rolls=False), ui)
    hero = MockCharacter()
    enemies = [MockEnemy() for _ in range(3)]

    t0 = time.perf_counter()
    cs.start_combat(hero, enemies)

    rounds = 0
    while cs.is_active() and rounds < 100:
        cs.attack_enemy()
        rounds += 1
    t1 = time.perf_counter()

    print(f"Completed {rounds} rounds in {t1 - t0:.4f}s")


if __name__ == '__main__':
    main()
