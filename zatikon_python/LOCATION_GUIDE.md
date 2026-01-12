# Location System Guide

## Overview

Zatikon uses a **single-number location system** for the 11x11 board. Locations are numbered from **0 to 120**.

## Conversion Formula

```
Location = y * 11 + x
x = Location % 11
y = Location // 11
```

Where:
- `x` is the column (0-10, left to right)
- `y` is the row (0-10, top to bottom)
- `11` is the BOARD_SIZE

## Key Locations

| Location | Coordinates (x,y) | Description |
|----------|------------------|-------------|
| 0 | (0, 0) | **Castle 1** - Top-left corner |
| 1 | (1, 0) | One square right of Castle 1 |
| 11 | (0, 1) | One square down from Castle 1 |
| 60 | (5, 5) | Center of board |
| 120 | (10, 10) | **Castle 2** - Bottom-right corner |

## Visual Map (First 3 Rows)

```
     0   1   2   3   4   5   6   7   8   9  10
   ─────────────────────────────────────────────
 0| C1   1   2   3   4   5   6   7   8   9  10 |
 1| 11  12  13  14  15  16  17  18  19  20  21 |
 2| 22  23  24  25  26  27  28  29  30  31  32 |
```

## Using Locations

### In Commands

You can specify locations in two ways:

1. **Coordinates**: `5,5` → Location 60
   - Format: `x,y`
   - Example: `deploy 0 5,5`

2. **Location Number**: `60` → Location 60
   - Format: Direct number
   - Example: `deploy 0 60`

### Examples

- `deploy 0 1` - Deploy unit to location 1 (coordinates 1,0)
- `select 11` - Select unit at location 11 (coordinates 0,1)
- `move 5,5` - Move to location 60 (center)
- `attack 120` - Attack location 120 (Castle 2)

## Adjacent Locations

For a unit at location `loc`:
- **Right**: `loc + 1` (if not at right edge)
- **Left**: `loc - 1` (if not at left edge)
- **Down**: `loc + 11` (if not at bottom edge)
- **Up**: `loc - 11` (if not at top edge)
- **Diagonals**: `loc + 12`, `loc - 10`, etc.

## Castle Deployment Range

Units deploy within **range 1** of their castle:

- **Castle 1** (location 0) can deploy to: 1, 11, 12
- **Castle 2** (location 120) can deploy to: 109, 110, 119

## Helper Functions

The `BattleField` class provides conversion functions:

```python
from zatikon.battlefield import BattleField

# Convert location to coordinates
x = BattleField.get_x(60)  # Returns 5
y = BattleField.get_y(60)  # Returns 5

# Convert coordinates to location
location = BattleField.get_location(5, 5)  # Returns 60

# Calculate distance
distance = BattleField.get_distance(0, 120)  # Returns 10 (Chebyshev distance)
```

