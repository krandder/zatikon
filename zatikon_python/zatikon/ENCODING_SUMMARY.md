# Zatikon AlphaZero Encoding Summary

## Complete Encoding Scheme

**Total Planes: 327**

### Plane Breakdown

#### 1. Unit Type Encoding (Planes 0-57) - 58 planes
- **Common Types (0-29)**: Top 15 unit types × 2 teams = 30 planes
- **Rare Types (30-57)**: Binary encoding (10 bits) + categories (4) × 2 teams = 28 planes

#### 2. Unit Numeric Stats - RNS (Planes 58-233) - 176 planes per unit location
- **HP**: 26 planes (bases [3,5,7,11])
- **HP Max**: 26 planes (bases [3,5,7,11])
- **Base Armor**: 15 planes (bases [3,5,7])
- **Effective Armor**: 15 planes (bases [3,5,7])
- **Base Damage**: 15 planes (bases [3,5,7])
- **Effective Damage**: 15 planes (bases [3,5,7])
- **Current Actions**: 15 planes (bases [3,5,7])
- **Max Actions**: 15 planes (bases [3,5,7])
- **Reserved Unit Value**: 26 planes (for future properties)
- **HP Thresholds**: 4 planes (>=3, >=5, >=7, >=11)
- **HP Max Thresholds**: 4 planes (>=3, >=5, >=7, >=11)

#### 3. Unit State Flags (Planes 234-239) - 6 planes
- Stunned (Team 1, Team 2): 2 planes
- Inactive (Team 1, Team 2): 2 planes
- Organic (Team 1, Team 2): 2 planes

#### 4. Game State (Planes 240-288) - 49 planes
- Castle locations: 2 planes
- Turn number: 1 plane (normalized)
- Side to move: 1 plane
- Commands left: 15 planes (RNS, bases [3,5,7])
- Max commands: 15 planes (RNS, bases [3,5,7])
- Deploy cost: 15 planes (RNS, bases [3,5,7])

#### 5. Barracks (Planes 289-326) - 38 planes
- Category counts (Team 1): 4 planes (melee, ranged, magic, special)
- Category counts (Team 2): 4 planes
- Top unit types (Team 1): 15 planes (one-hot for common types)
- Top unit types (Team 2): 15 planes

## Key Features

### RNS Encoding
- **Exact numeric representation** - no precision loss
- **Redundant encoding** - multiple moduli provide robustness
- **Threshold encoding** - additional redundancy for HP values
- **Handles large numbers** - no sparse high-order bit problem

### Unit Type Encoding
- **Common types**: Direct plane assignment (fast, interpretable)
- **Rare types**: Binary combination encoding (scalable)
- **Category buckets**: Fallback for unknown types

### Encoding Properties
- **Spatial encoding**: Unit stats encoded at unit's board location
- **Board-wide encoding**: Game state and barracks encoded across entire board
- **Team separation**: Separate planes for Team 1 and Team 2

## Usage

```python
from zatikon.state_encoder import encode_game_state, get_total_plane_count
from zatikon.game import Game

game = Game()
# ... setup game ...

planes = encode_game_state(game)
# planes.shape = (327, 11, 11)

total_planes = get_total_plane_count()
# Returns: 327
```

## Integration with Neural Network

The `ZatikonNet` class in `alphazero.py` has been updated to use 327 input planes:

```python
N_PLANES = get_total_plane_count()  # 327
```

The network architecture processes these planes through convolutional layers to learn game patterns.

