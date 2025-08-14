"""
Ancient Ruins Dungeon for Rogue City
Multi-zone dungeon with 8-directional navigation and vertical transitions.
"""

from typing import Dict, Any
from .base_area import BaseArea, Room, ExitDirection


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

            # Enemies (none yet in Session 1)
            self.add_room(room)

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
