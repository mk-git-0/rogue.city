import os
import sys
import types

# Basic smoke tests to ensure modules import and critical methods exist

def test_import_engine():
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from core.game_engine import GameEngine
    engine = GameEngine()
    assert hasattr(engine, 'initialize')


def test_combat_module():
    from core.combat_system import CombatSystem
    from core.timer_system import TimerSystem
    from core.dice_system import DiceSystem

    class MockUI:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None

    cs = CombatSystem(TimerSystem(), DiceSystem(show_rolls=False), MockUI())
    assert hasattr(cs, 'start_combat') and hasattr(cs, 'attack_enemy')
