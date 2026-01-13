#!/usr/bin/env python3
"""Minimal command-line version of Zatikon."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

BOARD_SIZE = 11


@dataclass
class Unit:
    name: str
    team: int
    symbol: str
    hp: int
    move_range: int
    attack_range: int
    position: Tuple[int, int]

    def is_enemy(self, other: "Unit") -> bool:
        return self.team != other.team


@dataclass
class Castle:
    team: int
    position: Tuple[int, int]


class Game:
    def __init__(self) -> None:
        self.units: List[Unit] = []
        self.castles: Dict[int, Castle] = {
            1: Castle(team=1, position=(0, BOARD_SIZE // 2)),
            2: Castle(team=2, position=(BOARD_SIZE - 1, BOARD_SIZE // 2)),
        }
        self.current_team = 1
        self._init_units()

    def _init_units(self) -> None:
        self.units = [
            Unit("Soldier", 1, "S", 1, 1, 1, (1, BOARD_SIZE // 2 - 1)),
            Unit("Soldier", 1, "S", 1, 1, 1, (1, BOARD_SIZE // 2)),
            Unit("Archer", 1, "A", 1, 1, 2, (1, BOARD_SIZE // 2 + 1)),
            Unit("Soldier", 2, "s", 1, 1, 1, (BOARD_SIZE - 2, BOARD_SIZE // 2 - 1)),
            Unit("Soldier", 2, "s", 1, 1, 1, (BOARD_SIZE - 2, BOARD_SIZE // 2)),
            Unit("Archer", 2, "a", 1, 1, 2, (BOARD_SIZE - 2, BOARD_SIZE // 2 + 1)),
        ]

    def get_unit_at(self, position: Tuple[int, int]) -> Optional[Unit]:
        for unit in self.units:
            if unit.position == position:
                return unit
        return None

    def in_bounds(self, position: Tuple[int, int]) -> bool:
        x, y = position
        return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

    def distance(self, start: Tuple[int, int], end: Tuple[int, int]) -> int:
        dx = abs(start[0] - end[0])
        dy = abs(start[1] - end[1])
        return max(dx, dy)

    def move_unit(self, start: Tuple[int, int], end: Tuple[int, int]) -> str:
        unit = self.get_unit_at(start)
        if unit is None:
            return "No unit at that position."
        if unit.team != self.current_team:
            return "That unit does not belong to you."
        if not self.in_bounds(end):
            return "Target is out of bounds."
        if self.get_unit_at(end) is not None:
            return "Target position is occupied."
        if end in (self.castles[1].position, self.castles[2].position):
            return "Cannot move onto a castle."
        if self.distance(start, end) > unit.move_range:
            return "Target is out of movement range."
        unit.position = end
        return f"{unit.name} moved to {format_coord(end)}."

    def attack(self, start: Tuple[int, int], target: Tuple[int, int]) -> str:
        attacker = self.get_unit_at(start)
        if attacker is None:
            return "No unit at that position."
        if attacker.team != self.current_team:
            return "That unit does not belong to you."
        if not self.in_bounds(target):
            return "Target is out of bounds."
        if self.distance(start, target) > attacker.attack_range:
            return "Target is out of attack range."

        enemy_castle = self.castles[2 if attacker.team == 1 else 1]
        if target == enemy_castle.position:
            return f"Team {attacker.team} wins by capturing the enemy castle!"

        defender = self.get_unit_at(target)
        if defender is None:
            return "No enemy unit at that position."
        if not attacker.is_enemy(defender):
            return "You can only attack enemy units."

        self.units.remove(defender)
        return f"{attacker.name} defeated {defender.name} at {format_coord(target)}."

    def end_turn(self) -> str:
        self.current_team = 2 if self.current_team == 1 else 1
        return f"Team {self.current_team}'s turn."

    def render_board(self) -> str:
        lines: List[str] = []
        header = "   " + " ".join(f"{i + 1:2d}" for i in range(BOARD_SIZE))
        lines.append(header)
        for y in range(BOARD_SIZE):
            row = ["."] * BOARD_SIZE
            for castle in self.castles.values():
                cx, cy = castle.position
                if cy == y:
                    row[cx] = "C" if castle.team == 1 else "c"
            for unit in self.units:
                ux, uy = unit.position
                if uy == y:
                    row[ux] = unit.symbol
            lines.append(f"{y + 1:2d} " + " ".join(f"{cell:2s}" for cell in row))
        return "\n".join(lines)

    def status(self) -> str:
        lines = [f"Team {self.current_team}'s turn."]
        for unit in self.units:
            lines.append(
                f"{unit.symbol} {unit.name} (Team {unit.team}) at {format_coord(unit.position)}"
            )
        return "\n".join(lines)


def parse_coord(token: str) -> Tuple[int, int]:
    if "," not in token:
        raise ValueError("Coordinates must be in x,y format.")
    x_str, y_str = token.split(",", 1)
    x = int(x_str) - 1
    y = int(y_str) - 1
    return x, y


def format_coord(position: Tuple[int, int]) -> str:
    x, y = position
    return f"{x + 1},{y + 1}"


def command_help() -> str:
    return (
        "Commands:\n"
        "  board                       Show the board\n"
        "  status                      Show units and turn\n"
        "  move x,y x,y                Move a unit\n"
        "  attack x,y x,y              Attack a unit or castle\n"
        "  end                         End your turn\n"
        "  help                        Show this help\n"
        "  quit                        Exit the game\n"
    )


def run_game() -> None:
    game = Game()
    print("Welcome to minimal Zatikon CLI.")
    print(command_help())
    print(game.render_board())

    while True:
        try:
            raw = input("> ").strip()
        except EOFError:
            print("\nGoodbye.")
            return

        if not raw:
            continue

        parts = raw.split()
        command = parts[0].lower()

        if command in {"quit", "exit"}:
            print("Goodbye.")
            return
        if command == "help":
            print(command_help())
            continue
        if command == "board":
            print(game.render_board())
            continue
        if command == "status":
            print(game.status())
            continue
        if command == "end":
            print(game.end_turn())
            continue

        if command in {"move", "attack"}:
            if len(parts) != 3:
                print("Usage: move x,y x,y" if command == "move" else "Usage: attack x,y x,y")
                continue
            try:
                start = parse_coord(parts[1])
                target = parse_coord(parts[2])
            except ValueError as exc:
                print(f"Invalid coordinate: {exc}")
                continue

            if command == "move":
                print(game.move_unit(start, target))
            else:
                outcome = game.attack(start, target)
                print(outcome)
                if outcome.startswith("Team") and "wins" in outcome:
                    print(game.render_board())
                    return
            continue

        print("Unknown command. Type 'help' for instructions.")


if __name__ == "__main__":
    run_game()
