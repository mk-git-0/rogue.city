#!/usr/bin/env python3
"""
Basic data validation for Rogue City JSON assets.

Validates structure and required fields for:
- data/classes/class_definitions.json
- data/items/weapons.json, armor.json, consumables.json (if present)
- data/quests/quest_definitions.json (if present)
- data/areas/* (basic sanity)

Exit code: 0 on success, 1 on any validation error.
"""
import json
import os
import sys
from typing import Dict, Any
try:
    from jsonschema import Draft202012Validator  # type: ignore
    HAS_JSONSCHEMA = True
except Exception:
    Draft202012Validator = None  # type: ignore
    HAS_JSONSCHEMA = False

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_json(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_class_definitions() -> None:
    path = os.path.join(PROJECT_ROOT, 'data', 'classes', 'class_definitions.json')
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError('class_definitions.json must be an object mapping class ids to definitions')
    if HAS_JSONSCHEMA:
        schema = load_json(os.path.join(PROJECT_ROOT, 'schemas', 'class_definitions.schema.json'))
        Draft202012Validator(schema).validate(data)
    else:
        # Fallback minimal checks
        required_fields = [
            'name', 'difficulty', 'stat_modifiers', 'hit_die', 'base_attack_speed', 'critical_hit_range'
        ]
        for cls_id, cls in data.items():
            for field in required_fields:
                if field not in cls:
                    raise ValueError(f'class {cls_id}: missing required field {field}')
            if not isinstance(cls.get('stat_modifiers', {}), dict):
                raise ValueError(f'class {cls_id}: stat_modifiers must be an object')


def validate_items(filename: str, required_fields: Dict[str, list]) -> None:
    path = os.path.join(PROJECT_ROOT, 'data', 'items', filename)
    if not os.path.exists(path):
        return  # optional file
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f'{filename} must be an object mapping item ids to definitions')
    if HAS_JSONSCHEMA:
        # Build a simple schema on the fly
        reqs = required_fields.get(filename, [])
        schema = {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "required": reqs
            }
        }
        Draft202012Validator(schema).validate(data)
    else:
        reqs = required_fields.get(filename, [])
        for item_id, item in data.items():
            for field in reqs:
                if field not in item:
                    raise ValueError(f'{filename} {item_id}: missing required field {field}')


def validate_quests() -> None:
    path = os.path.join(PROJECT_ROOT, 'data', 'quests', 'quest_definitions.json')
    if not os.path.exists(path):
        return  # optional
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError('quest_definitions.json must be an object')
    if HAS_JSONSCHEMA:
        schema = load_json(os.path.join(PROJECT_ROOT, 'schemas', 'quest_definitions.schema.json'))
        Draft202012Validator(schema).validate(data)
    else:
        for qid, q in data.items():
            for field in ['name', 'description', 'quest_giver', 'alignment_requirement', 'level_requirement', 'steps', 'rewards']:
                if field not in q:
                    raise ValueError(f'quest {qid}: missing required field {field}')
            steps = q.get('steps', [])
            if not isinstance(steps, list) or not steps:
                raise ValueError(f'quest {qid}: steps must be a non-empty list')


def validate_areas_directory() -> None:
    areas_dir = os.path.join(PROJECT_ROOT, 'data', 'areas')
    if not os.path.isdir(areas_dir):
        return  # optional if areas are code-defined
    # Basic sanity: ensure JSON files parse
    for fname in os.listdir(areas_dir):
        if fname.endswith('.json'):
            _ = load_json(os.path.join(areas_dir, fname))


def main() -> int:
    try:
        print('Validating class definitions...')
        validate_class_definitions()

        print('Validating items...')
        validate_items('weapons.json', {
            'weapons.json': ['name', 'damage_dice']
        })
        validate_items('armor.json', {
            'armor.json': ['name', 'ac_bonus', 'armor_type']
        })
        validate_items('consumables.json', {
            'consumables.json': ['name']
        })

        print('Validating quests...')
        validate_quests()

        print('Validating areas data...')
        validate_areas_directory()

        print('All data validations passed.')
        return 0
    except Exception as e:
        print(f'Data validation failed: {e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
