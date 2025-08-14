"""
Ancient Ruins Dungeon for Rogue City
Multi-zone dungeon with 8-directional navigation and vertical transitions.
"""

from typing import Dict, Any
from .base_area import BaseArea, Room, ExitDirection
import time


class AncientRuinsArea(BaseArea):
    """
    Ancient underground complex accessible from the Forest's Deep Forest.
    Organized in three zones: Entrance Hall, Central Chambers, Deep Vaults.
    """

    def __init__(self):
        super().__init__(
            area_id="ancient_ruins",
            name="Ancient Ruins",
            description=(
                "An ancient subterranean complex of crumbling halls and forgotten vaults. "
                "Faint glyphs mark the stone and stale air carries whispers of the past."
            ),
        )
        # Chest respawn tracking: chest_id -> next_available_epoch
        self._chest_respawns: Dict[str, float] = {}
        # First-visit bonuses and lore fragment tracking
        self._first_visit_bonus_awarded: set[str] = set()
        self._secret_rooms: set[str] = {
            'waterfall_hollow', 'puzzle_vault', 'class_chamber', 'star_chamber'
        }
        self._lore_fragments_required: set[str] = {
            'lore_star_1', 'lore_star_2', 'lore_star_3'
        }
        self._lore_fragments_collected: set[str] = set()

    def _load_area_data(self) -> None:
        data = self._load_json_data("ancient_ruins.json")
        if not data:
            self._create_minimal_fallback()
            return

        rooms_data: Dict[str, Any] = data.get("rooms", {})
        for room_id, room_data in rooms_data.items():
            room = Room(
                room_id=room_id,
                name=room_data["name"],
                description=room_data["description"],
                coords=tuple(room_data.get("coords")) if room_data.get("coords") else None,
                room_type=room_data.get("room_type", "normal"),
                lighting=room_data.get("lighting", "dim"),
                scent=room_data.get("scent", ""),
                temperature=room_data.get("temperature", ""),
            )

            # Properties
            room.is_safe = room_data.get("is_safe", room.room_type == "safe_zone")
            room.ambient_sound = room_data.get("ambient_sound", "")
            if "special_actions" in room_data:
                room.special_actions = room_data["special_actions"]

            # Exits
            for direction_str, exit_data in room_data.get("exits", {}).items():
                try:
                    direction = ExitDirection(direction_str)
                except ValueError:
                    continue
                room.add_exit(
                    direction=direction,
                    destination_room=exit_data["destination"],
                    destination_area=exit_data.get("destination_area"),
                    is_locked=exit_data.get("is_locked", False),
                    lock_message=exit_data.get("lock_message", "That way is blocked."),
                    hidden=exit_data.get("hidden", False),
                )

            # Items
            for item_id, item in room_data.get("items", {}).items():
                room.add_item(
                    item_id=item_id,
                    name=item["name"],
                    description=item["description"],
                    can_take=item.get("can_take", True),
                    quantity=item.get("quantity", 1),
                )

            # Examinables
            for key, value in room_data.get("examinables", {}).items():
                room.examinables[key.lower()] = value

            # Enemies
            for enemy_id, enemy in room_data.get("enemies", {}).items():
                room.add_enemy(
                    enemy_id=enemy_id,
                    enemy_type=enemy.get("enemy_type", enemy_id),
                    quantity=enemy.get("quantity", 1),
                    encounter_name=enemy.get("encounter_name", enemy.get("enemy_type", enemy_id)),
                    respawn=enemy.get("respawn", False),
                    respawn_delay=enemy.get("respawn_delay", 0),
                )

            # Enemies (none yet in Session 1)
            self.add_room(room)

        # Initialize chest cooldowns based on economy config (default 30 minutes)
        try:
            import json, os
            econ_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'economy', 'loot_tables.json')
            cooldown = 30
            if os.path.exists(econ_file):
                with open(econ_file, 'r') as f:
                    econ = json.load(f)
                cooldown = int(econ.get('chests', {}).get('ruins_common', {}).get('cooldown_minutes', 30))
            now = time.time()
            for rid, room in self.rooms.items():
                for item_id, item in room.items.items():
                    if 'chest' in item_id:
                        self._chest_respawns[item_id] = now
            self._chest_cooldown_minutes = cooldown
        except Exception:
            self._chest_cooldown_minutes = 30

        # Area meta
        info = data.get("area_info", {})
        self.starting_room = info.get("starting_room", "entrance_hall")

        # Optional map
        if map_file := info.get("map_file"):
            self._load_map_data(map_file)

        self.map_legend = {
            "[*]": "Your current location",
            "EH": "Entrance Hall",
            "CC": "Central Chambers",
            "DV": "Deep Vaults",
        }

    def _create_minimal_fallback(self) -> None:
        """In case JSON is missing, create a tiny 3-room stub."""
        r1 = Room(
            "entrance_hall",
            "Entrance Hall",
            "Sand-choked steps descend into a dim hall lined with cracked columns.",
            coords=(0, 0, 0),
            room_type="transition",
            lighting="dim",
        )
        r1.add_exit(ExitDirection.SOUTH, "forest_clearing", "forest_path")
        r1.add_exit(ExitDirection.EAST, "antechamber")
        self.add_room(r1)

        r2 = Room(
            "antechamber",
            "Antechamber",
            "Dusty stone benches and faded wall-script hint at ritual purpose.",
            coords=(1, 0, 0),
            lighting="dim",
        )
        r2.add_exit(ExitDirection.WEST, "entrance_hall")
        r2.add_exit(ExitDirection.DOWN, "grand_crossing")
        self.add_room(r2)

        r3 = Room(
            "grand_crossing",
            "Grand Crossing",
            "A wide junction where four corridors meet, the air colder below.",
            coords=(1, 0, -1),
            lighting="dark",
        )
        r3.add_exit(ExitDirection.UP, "antechamber")
        self.add_room(r3)

    def get_starting_room(self) -> str:
        return self.starting_room

    def on_item_taken(self, item_id: str, room_id: str) -> list[str]:
        """Handle chest respawn scheduling and lore hooks."""
        messages = []
        if 'chest' in item_id:
            # Schedule chest respawn
            cooldown = getattr(self, '_chest_cooldown_minutes', 30)
            self._chest_respawns[item_id] = time.time() + cooldown * 60
            messages.append("You empty the chest. It will take time to reset.")
        # Lore fragment collection
        if item_id in self._lore_fragments_required:
            if item_id not in self._lore_fragments_collected:
                self._lore_fragments_collected.add(item_id)
                messages.append("You recover a lore fragment etched with star glyphs.")
            # Unlock final secret if all collected
            if self._lore_fragments_required.issubset(self._lore_fragments_collected):
                gate = self.get_room('archive_gate')
                if gate and 'star_unlocked' not in getattr(self, '_flags', set()):
                    from .base_area import ExitDirection
                    gate.add_exit(ExitDirection.UP, 'star_chamber')
                    if not hasattr(self, '_flags'):
                        self._flags = set()
                    self._flags.add('star_unlocked')
                    messages.append("A resonance hum builds in the Archive Gate. A passage opens above!")
        return messages

    def on_room_enter(self, room_id: str, character) -> list[str]:
        messages = []
        room = self.get_room(room_id)
        if not room:
            return messages
        # Chest respawn check
        try:
            now = time.time()
            to_respawn = []
            for item_id, item in list(room.items.items()):
                # If chest missing but cooldown passed, re-add
                if 'chest' in item_id and item.quantity <= 0:
                    next_at = self._chest_respawns.get(item_id, 0)
                    if now >= next_at:
                        item.quantity = 1
                        messages.append("You hear a click as an ancient mechanism resets a chest." )
            return messages
        except Exception:
            return messages

        # First-visit exploration bonuses
        if room_id not in self._first_visit_bonus_awarded:
            self._first_visit_bonus_awarded.add(room_id)
            bonus_xp = 50 if room_id in self._secret_rooms else 15
            try:
                if character and hasattr(character, 'gain_experience'):
                    character.gain_experience(bonus_xp)
                    messages.append(f"You gain {bonus_xp} bonus experience for discovering this area.")
            except Exception:
                pass
        # Context hints for quest Session 7.1
        if room_id == 'entrance_hall':
            messages.append("Objective: Investigate the disturbance deeper in the Entrance Hall zone.")
        if room_id == 'ancient_library':
            messages.append("Objective: The Keeper's Journal fragments may be scattered here.")
        # Auto-offer Ruins Q1 if available
        try:
            if character and hasattr(character, 'quest_manager') and character.quest_manager:
                qm = character.quest_manager
                available = [q.quest_id for q in qm.get_available_quests()]
                if room_id == 'entrance_hall' and 'ruins_q1_investigate' in available:
                    messages.append("A quest is available: 'Investigate the Disturbance'. Use 'accept Investigate the Disturbance' to begin.")
        except Exception:
            pass
        return messages
