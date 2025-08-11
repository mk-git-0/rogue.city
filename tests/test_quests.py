import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.quest_system import QuestSystem
from core.quest_manager import CharacterQuestManager
from characters.base_character import BaseCharacter
from core.alignment_system import Alignment


class DummyChar(BaseCharacter):
    def get_hit_die_value(self):
        return 8
    def get_hit_die_type(self):
        return "1d8"
    def get_attack_speed(self):
        return 3.0
    def get_base_attack_speed(self):
        return 3.0
    def get_critical_range(self):
        return 20
    def get_experience_penalty(self):
        return 0


def test_quest_accept_complete_flow():
    game = type('G', (), {"get_game_time": lambda self: "now"})()
    qs = QuestSystem(game)

    # Build a tiny in-memory quest
    quest_id = 'test_quest_1'
    qs.quest_definitions[quest_id] = type('Q', (), {
        '__init__': lambda self: None,
        'quest_id': quest_id,
        'name': 'Test Quest',
        'description': 'Do a thing',
        'quest_giver': 'annora',
        'alignment_requirement': 'any',
        'level_requirement': 1,
        'prerequisites': [],
        'steps': [{'objective': 'Do it'}],
        'rewards': {'experience': 10, 'gold': 1, 'items': []},
        'failure_consequences': {},
        'abandon_consequences': {}
    })()

    ch = DummyChar('Questy', 'warrior', alignment=Alignment.NEUTRAL)
    ch.initialize_item_systems()

    qm = CharacterQuestManager(ch, qs)
    assert qm.accept_quest(quest_id)
    assert quest_id in qm.active_quests

    assert qm.complete_quest(quest_id)
    assert quest_id in qm.completed_quests
