"""
Complete game state encoder for AlphaZero.

Integrates:
- Unit type encoding (combination encoding)
- RNS numeric encoding (HP, armor, damage, actions, etc.)
- Unit state flags
- Game state
- Barracks
"""

import numpy as np
from typing import List, Dict, Tuple

from zatikon import constants
from zatikon.game import Game
from zatikon.battlefield import BattleField

BOARD_SIZE = constants.BOARD_SIZE
from zatikon.rns_encoding import (
    encode_hp, encode_hp_max, encode_armor, encode_damage,
    encode_actions, encode_actions_max, encode_effective_armor,
    encode_effective_damage, encode_reserved_unit_value,
    encode_thresholds, encode_commands, encode_commands_max,
    encode_deploy_cost, HP_BASES, STAT_BASES, get_rns_plane_counts
)


# ---------- Unit Type Encoding ----------

# Top 15 most common unit types (get dedicated planes)
COMMON_UNIT_TYPES = [
    constants.UNIT_FOOTMAN,      # 0
    constants.UNIT_BEAR,          # -8
    constants.UNIT_ARCHER,        # 3
    constants.UNIT_KNIGHT,        # 5
    constants.UNIT_WIZARD,        # 17
    constants.UNIT_PRIEST,        # 11
    constants.UNIT_RANGER,        # 6
    constants.UNIT_WARRIOR,       # 14
    constants.UNIT_SCOUT,         # 18
    constants.UNIT_PALADIN,       # 62
    constants.UNIT_DRAGON,        # 35
    constants.UNIT_NECROMANCER,   # 26
    constants.UNIT_BERSERKER,     # 70
    constants.UNIT_GOLEM,         # 57
    constants.UNIT_TOWER,         # 38
]

# Unit type to index mapping
UNIT_TYPE_TO_INDEX = {unit_id: idx for idx, unit_id in enumerate(COMMON_UNIT_TYPES)}
COMMON_TYPE_COUNT = len(COMMON_UNIT_TYPES)

# Binary encoding for rare types (10 planes = 1024 types)
RARE_TYPE_BITS = 10
MAX_RARE_TYPES = 2 ** RARE_TYPE_BITS

# Category buckets
CATEGORY_MELEE = 0
CATEGORY_RANGED = 1
CATEGORY_MAGIC = 2
CATEGORY_SPECIAL = 3


def get_unit_category(unit_id: int) -> int:
    """
    Categorize unit by type.
    
    Returns:
        0: Melee, 1: Ranged, 2: Magic, 3: Special
    """
    # Melee units
    melee_types = [
        constants.UNIT_FOOTMAN, constants.UNIT_KNIGHT, constants.UNIT_WARRIOR,
        constants.UNIT_BERSERKER, constants.UNIT_PALADIN, constants.UNIT_SWORDSMAN,
        constants.UNIT_SHIELD_MAIDEN
    ]
    if unit_id in melee_types:
        return CATEGORY_MELEE
    
    # Ranged units
    ranged_types = [
        constants.UNIT_ARCHER, constants.UNIT_RANGER, constants.UNIT_SCOUT,
        constants.UNIT_CROSSBOWMAN, constants.UNIT_FIRE_ARCHER, constants.UNIT_MOUNTED_ARCHER
    ]
    if unit_id in ranged_types:
        return CATEGORY_RANGED
    
    # Magic units
    magic_types = [
        constants.UNIT_WIZARD, constants.UNIT_PRIEST, constants.UNIT_NECROMANCER,
        constants.UNIT_ENCHANTER, constants.UNIT_WARLOCK, constants.UNIT_ABJURER,
        constants.UNIT_DRUID, constants.UNIT_CHANNELER, constants.UNIT_MAGUS,
        constants.UNIT_SHAMAN, constants.UNIT_DIABOLIST
    ]
    if unit_id in magic_types:
        return CATEGORY_MAGIC
    
    # Special/Other
    return CATEGORY_SPECIAL


def encode_unit_type(unit_id: int, team: int) -> Tuple[int, List[float]]:
    """
    Encode unit type.
    
    Returns:
        (plane_offset, encoding) where encoding is list of plane values
    """
    if unit_id in UNIT_TYPE_TO_INDEX:
        # Common type - dedicated plane
        plane_idx = UNIT_TYPE_TO_INDEX[unit_id]
        if team == constants.TEAM_1:
            return (plane_idx, [1.0])
        else:
            return (COMMON_TYPE_COUNT + plane_idx, [1.0])
    else:
        # Rare type - binary encoding
        # Map unit_id to binary (handle negative IDs)
        unit_id_normalized = abs(unit_id) % MAX_RARE_TYPES
        
        # Binary encoding
        binary_encoding = []
        for i in range(RARE_TYPE_BITS):
            binary_encoding.append(1.0 if (unit_id_normalized >> i) & 1 else 0.0)
        
        # Category bucket
        category = get_unit_category(unit_id)
        category_encoding = [0.0] * 4
        category_encoding[category] = 1.0
        
        if team == constants.TEAM_1:
            # Team 1 rare types: planes after common types
            offset = 2 * COMMON_TYPE_COUNT
            return (offset, binary_encoding + category_encoding)
        else:
            # Team 2 rare types: after Team 1 rare types
            offset = 2 * COMMON_TYPE_COUNT + RARE_TYPE_BITS + 4
            return (offset, binary_encoding + category_encoding)


# ---------- Complete State Encoding ----------

def get_total_plane_count() -> int:
    """
    Calculate total number of planes needed.
    
    Returns:
        Total plane count
    """
    # Unit type planes
    unit_type_planes = (
        2 * COMMON_TYPE_COUNT +  # Common types (Team 1 + Team 2)
        2 * (RARE_TYPE_BITS + 4)  # Rare types + categories (Team 1 + Team 2)
    )  # = 2*15 + 2*(10+4) = 30 + 28 = 58 planes
    
    # Unit numeric stats (per unit, but we encode at each unit's location)
    rns_counts = get_rns_plane_counts()
    unit_stats_planes = rns_counts['total_unit_stats']  # 176 planes
    
    # Unit state flags
    unit_state_planes = 6  # stunned, inactive, organic (×2 teams)
    
    # Game state planes
    game_state_planes = (
        2 +  # Castle locations (2)
        1 +  # Turn number (normalized)
        1 +  # Side to move
        rns_counts['total_game_stats']  # Commands, commands_max, deploy_cost (45)
    )  # = 2 + 1 + 1 + 45 = 49 planes
    
    # Barracks planes
    barracks_planes = (
        4 +  # Category counts (Team 1)
        4 +  # Category counts (Team 2)
        2 * COMMON_TYPE_COUNT  # Top unit types in barracks (Team 1 + Team 2)
    )  # = 4 + 4 + 30 = 38 planes
    
    total = (
        unit_type_planes +
        unit_stats_planes +
        unit_state_planes +
        game_state_planes +
        barracks_planes
    )
    
    return total


def encode_game_state(game: Game) -> np.ndarray:
    """
    Encode complete game state into neural network input planes.
    
    Returns:
        (N_PLANES, BOARD_SIZE, BOARD_SIZE) numpy array
    """
    rns_counts = get_rns_plane_counts()
    total_planes = get_total_plane_count()
    
    planes = np.zeros((total_planes, BOARD_SIZE, BOARD_SIZE), dtype=np.float32)
    plane_idx = 0
    
    # ---------- Unit Type Encoding (Planes 0-57) ----------
    unit_type_start = plane_idx
    
    # Initialize unit type planes
    for unit in game.battlefield.units:
        if unit.dead:
            continue
        
        x = BattleField.get_x(unit.location)
        y = BattleField.get_y(unit.location)
        unit_id = unit.unit_id if unit.unit_id is not None else constants.UNIT_NONE
        
        offset, encoding = encode_unit_type(unit_id, unit.team)
        for i, value in enumerate(encoding):
            planes[unit_type_start + offset + i, y, x] = value
    
    plane_idx += (2 * COMMON_TYPE_COUNT + 2 * (RARE_TYPE_BITS + 4))
    
    # ---------- Unit Numeric Stats (RNS) (Planes 58-233) ----------
    unit_stats_start = plane_idx
    
    for unit in game.battlefield.units:
        if unit.dead:
            continue
        
        x = BattleField.get_x(unit.location)
        y = BattleField.get_y(unit.location)
        stats_idx = unit_stats_start
        
        # HP (26 planes)
        hp_encoded = encode_hp(unit.life)
        for i, val in enumerate(hp_encoded):
            planes[stats_idx + i, y, x] = val
        stats_idx += len(hp_encoded)
        
        # HP Max (26 planes)
        hp_max_encoded = encode_hp_max(unit.life_max)
        for i, val in enumerate(hp_max_encoded):
            planes[stats_idx + i, y, x] = val
        stats_idx += len(hp_max_encoded)
        
        # Base Armor (15 planes)
        armor_base_encoded = encode_armor(unit.armor)
        for i, val in enumerate(armor_base_encoded):
            planes[stats_idx + i, y, x] = val
        stats_idx += len(armor_base_encoded)
        
        # Effective Armor (15 planes)
        armor_eff_encoded = encode_effective_armor(unit.get_armor())
        for i, val in enumerate(armor_eff_encoded):
            planes[stats_idx + i, y, x] = val
        stats_idx += len(armor_eff_encoded)
        
        # Base Damage (15 planes)
        damage_base_encoded = encode_damage(unit.damage)
        for i, val in enumerate(damage_base_encoded):
            planes[stats_idx + i, y, x] = val
        stats_idx += len(damage_base_encoded)
        
        # Effective Damage (15 planes)
        damage_eff_encoded = encode_effective_damage(unit.get_damage())
        for i, val in enumerate(damage_eff_encoded):
            planes[stats_idx + i, y, x] = val
        stats_idx += len(damage_eff_encoded)
        
        # Current Actions (15 planes)
        actions_encoded = encode_actions(unit.actions_left)
        for i, val in enumerate(actions_encoded):
            planes[stats_idx + i, y, x] = val
        stats_idx += len(actions_encoded)
        
        # Max Actions (15 planes)
        actions_max_encoded = encode_actions_max(unit.actions_max)
        for i, val in enumerate(actions_max_encoded):
            planes[stats_idx + i, y, x] = val
        stats_idx += len(actions_max_encoded)
        
        # Reserved Unit Value (26 planes)
        reserved_encoded = encode_reserved_unit_value(0)  # Reserved for future
        for i, val in enumerate(reserved_encoded):
            planes[stats_idx + i, y, x] = val
        stats_idx += len(reserved_encoded)
        
        # HP Thresholds (4 planes)
        hp_thresholds = encode_thresholds(unit.life)
        for i, val in enumerate(hp_thresholds):
            planes[stats_idx + i, y, x] = val
        stats_idx += len(hp_thresholds)
        
        # HP Max Thresholds (4 planes)
        hp_max_thresholds = encode_thresholds(unit.life_max)
        for i, val in enumerate(hp_max_thresholds):
            planes[stats_idx + i, y, x] = val
        stats_idx += len(hp_max_thresholds)
    
    plane_idx += rns_counts['total_unit_stats']
    
    # ---------- Unit State Flags (Planes 234-239) ----------
    unit_state_start = plane_idx
    
    for unit in game.battlefield.units:
        if unit.dead:
            continue
        
        x = BattleField.get_x(unit.location)
        y = BattleField.get_y(unit.location)
        
        if unit.team == constants.TEAM_1:
            if unit.stunned:
                planes[unit_state_start, y, x] = 1.0
            if not unit.deployed():
                planes[unit_state_start + 1, y, x] = 1.0
            if unit.organic:
                planes[unit_state_start + 2, y, x] = 1.0
        else:
            if unit.stunned:
                planes[unit_state_start + 3, y, x] = 1.0
            if not unit.deployed():
                planes[unit_state_start + 4, y, x] = 1.0
            if unit.organic:
                planes[unit_state_start + 5, y, x] = 1.0
    
    plane_idx += 6
    
    # ---------- Game State (Planes 240-288) ----------
    game_state_start = plane_idx
    
    # Castle locations
    c1_x = BattleField.get_x(game.castle1.location)
    c1_y = BattleField.get_y(game.castle1.location)
    planes[game_state_start, c1_y, c1_x] = 1.0
    
    c2_x = BattleField.get_x(game.castle2.location)
    c2_y = BattleField.get_y(game.castle2.location)
    planes[game_state_start + 1, c2_y, c2_x] = 1.0
    
    # Turn number (normalized)
    turn_norm = min(game.turn_number / 300.0, 1.0)
    planes[game_state_start + 2, :, :] = turn_norm
    
    # Side to move
    if game.current_player == constants.TEAM_1:
        planes[game_state_start + 3, :, :] = 1.0
    else:
        planes[game_state_start + 3, :, :] = -1.0
    
    # Commands (RNS encoded)
    commands_start = game_state_start + 4
    current_castle = game.get_current_castle()
    enemy_castle = game.get_enemy_castle()
    
    # Commands left (current player)
    commands_encoded = encode_commands(current_castle.commands_left)
    for i, val in enumerate(commands_encoded):
        planes[commands_start + i, :, :] = val
    
    # Max commands (current player)
    commands_max_encoded = encode_commands_max(current_castle.commands_max)
    for i, val in enumerate(commands_max_encoded):
        planes[commands_start + len(commands_encoded) + i, :, :] = val
    
    # Deploy cost (for barracks units - encode as 0 for now, will be per-barracks)
    deploy_cost_encoded = encode_deploy_cost(0)
    for i, val in enumerate(deploy_cost_encoded):
        planes[commands_start + 2 * len(commands_encoded) + i, :, :] = val
    
    plane_idx += (2 + 1 + 1 + rns_counts['total_game_stats'])
    
    # ---------- Barracks (Planes 289-326) ----------
    barracks_start = plane_idx
    
    # Count units in barracks by category
    def count_barracks_by_category(castle):
        counts = [0, 0, 0, 0]  # melee, ranged, magic, special
        for unit in castle.barracks:
            unit_id = unit.unit_id if unit.unit_id is not None else constants.UNIT_NONE
            category = get_unit_category(unit_id)
            counts[category] += 1
        return counts
    
    # Team 1 barracks
    barracks1_counts = count_barracks_by_category(game.castle1)
    for i, count in enumerate(barracks1_counts):
        planes[barracks_start + i, :, :] = min(count / MAX_BARRACKS, 1.0)
    
    # Team 2 barracks
    barracks2_counts = count_barracks_by_category(game.castle2)
    for i, count in enumerate(barracks2_counts):
        planes[barracks_start + 4 + i, :, :] = min(count / MAX_BARRACKS, 1.0)
    
    # Top unit types in barracks (one-hot for first unit of each common type)
    barracks_types_start = barracks_start + 8
    for i, unit_type in enumerate(COMMON_UNIT_TYPES):
        # Team 1
        has_type = any(u.unit_id == unit_type for u in game.castle1.barracks)
        if has_type:
            planes[barracks_types_start + i, :, :] = 1.0
        
        # Team 2
        has_type = any(u.unit_id == unit_type for u in game.castle2.barracks)
        if has_type:
            planes[barracks_types_start + COMMON_TYPE_COUNT + i, :, :] = 1.0
    
    return planes


# Constants
MAX_BARRACKS = 20

