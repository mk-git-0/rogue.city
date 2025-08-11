#!/usr/bin/env python3
"""
Data lint: detect unused or unknown references across datasets.
- Checks that item IDs referenced in areas/quests exist in item databases or item classes.
- Checks that class IDs in class_definitions.json have corresponding character class files.

Note: This is a heuristic lint and may report false positives for code-defined items.
"""
import json
import os
import re
import sys
from typing import Dict, Set

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_json(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def collect_item_ids() -> Set[str]:
    ids: Set[str] = set()
    items_dir = os.path.join(PROJECT_ROOT, 'data', 'items')
    if not os.path.isdir(items_dir):
        return ids
    for fname in ('weapons.json', 'armor.json', 'consumables.json'):
        path = os.path.join(items_dir, fname)
        if os.path.exists(path):
            data = load_json(path)
            ids.update(data.keys())
    # Add class-coded items known to ItemFactory
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from core.item_factory import ItemFactory
    ids.update(ItemFactory().item_classes.keys())
    return ids


def collect_class_ids_from_code() -> Set[str]:
    chars_dir = os.path.join(PROJECT_ROOT, 'characters')
    ids: Set[str] = set()
    for fname in os.listdir(chars_dir):
        m = re.match(r'class_(.+)\.py$', fname)
        if m:
            ids.add(m.group(1).lower())
    return ids


def lint_area_item_refs(item_ids: Set[str]) -> None:
    areas_dir = os.path.join(PROJECT_ROOT, 'data', 'areas')
    if not os.path.isdir(areas_dir):
        return
    for fname in os.listdir(areas_dir):
        if not fname.endswith('.json'):
            continue
        data = load_json(os.path.join(areas_dir, fname))
        rooms = data.get('rooms', {})
        for room_id, room in rooms.items():
            items = (room or {}).get('items', {})
            for iid in items.keys():
                if iid not in item_ids:
                    print(f"WARN: Area {fname}:{room_id} references unknown item '{iid}'")


def lint_quests_item_refs(item_ids: Set[str]) -> None:
    qpath = os.path.join(PROJECT_ROOT, 'data', 'quests', 'quest_definitions.json')
    if not os.path.exists(qpath):
        return
    data = load_json(qpath)
    for qid, q in data.items():
        rewards = (q or {}).get('rewards', {})
        items = rewards.get('items', [])
        for iid in items:
            if iid not in item_ids:
                print(f"WARN: Quest {qid} rewards unknown item '{iid}'")


def lint_class_defs() -> None:
    cpath = os.path.join(PROJECT_ROOT, 'data', 'classes', 'class_definitions.json')
    data = load_json(cpath)
    code_ids = collect_class_ids_from_code()
    for cls_id in data.keys():
        if cls_id.lower() not in code_ids:
            print(f"WARN: Class '{cls_id}' defined but no characters/class_{cls_id}.py present")


def main() -> int:
    items = collect_item_ids()
    lint_area_item_refs(items)
    lint_quests_item_refs(items)
    lint_class_defs()
    return 0


if __name__ == '__main__':
    sys.exit(main())
