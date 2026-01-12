# AlphaZero Game State Encoding for Zatikon

## Design Goals
- Encode all unit types (50+)
- Encode unit stats (life, armor, damage, actions)
- Encode unit states (stunned, inactive, dead, organic)
- Handle many units on board efficiently
- Encode castle/barracks information
- Keep encoding size reasonable for neural network

## Proposed Encoding Scheme

### Plane Structure (Total: ~60-80 planes)

#### Unit Presence & Type (Planes 0-29)
- **Planes 0-9**: Top 10 most common unit types (Team 1)
  - Plane 0: Footman (Team 1)
  - Plane 1: Bear (Team 1)
  - Plane 2: Archer (Team 1)
  - Plane 3: Knight (Team 1)
  - ... (most common types)
- **Planes 10-19**: Top 10 most common unit types (Team 2)
- **Planes 20-21**: Unit type buckets (Team 1, Team 2)
  - Bucket 0: Melee units
  - Bucket 1: Ranged units
  - Bucket 2: Magic units
  - Bucket 3: Special units
- **Planes 22-23**: Any unit presence (Team 1, Team 2) - fallback for rare types

#### Unit Stats (Planes 24-35)
- **Planes 24-25**: Life (normalized) (Team 1, Team 2)
  - Value = life / max_life (clamped to [0, 1])
  - If multiple units at location, use max or average
- **Planes 26-27**: Armor (normalized) (Team 1, Team 2)
  - Value = armor / 3.0 (assuming max armor ~3)
- **Planes 28-29**: Damage (normalized) (Team 1, Team 2)
  - Value = damage / 10.0 (assuming max damage ~10)
- **Planes 30-31**: Actions left (normalized) (Team 1, Team 2)
  - Value = actions_left / actions_max
- **Planes 32-33**: Life buckets (Team 1, Team 2)
  - Bucket 0: 0-25% life
  - Bucket 1: 25-50% life
  - Bucket 2: 50-75% life
  - Bucket 3: 75-100% life

#### Unit States (Planes 34-41)
- **Plane 34**: Stunned units (Team 1)
- **Plane 35**: Stunned units (Team 2)
- **Plane 36**: Inactive units (Team 1) - just deployed
- **Plane 37**: Inactive units (Team 2)
- **Plane 38**: Organic units (Team 1)
- **Plane 39**: Organic units (Team 2)
- **Plane 40**: Units with actions remaining (Team 1)
- **Plane 41**: Units with actions remaining (Team 2)

#### Castle & Game State (Planes 42-50)
- **Plane 42**: Castle 1 location
- **Plane 43**: Castle 2 location
- **Plane 44**: Commands left (normalized) - current player
- **Plane 45**: Commands left (normalized) - opponent
- **Plane 46**: Current player indicator (1.0 = Team 1, -1.0 = Team 2)
- **Plane 47**: Turn number (normalized to [0, 1])
- **Plane 48**: Castle armor modifier (Team 1)
- **Plane 49**: Castle power modifier (Team 2)
- **Plane 50**: Castle armor modifier (Team 2)
- **Plane 51**: Castle power modifier (Team 2)

#### Barracks (Planes 52-60)
- **Planes 52-56**: Barracks unit counts by type bucket (Team 1)
  - Bucket 0: Melee count
  - Bucket 1: Ranged count
  - Bucket 2: Magic count
  - Bucket 3: Special count
  - Bucket 4: Total count (normalized)
- **Planes 57-61**: Barracks unit counts by type bucket (Team 2)
- **Plane 62**: Barracks top unit type (Team 1) - one-hot encoded
- **Plane 63**: Barracks top unit type (Team 2)

#### Additional Features (Planes 64-70)
- **Plane 64**: Graveyard count (Team 1) - normalized
- **Plane 65**: Graveyard count (Team 2) - normalized
- **Plane 66**: Unit density (Team 1) - units per area
- **Plane 67**: Unit density (Team 2)
- **Planes 68-70**: Reserved for future features

## Alternative: Channel-Based Encoding

Instead of planes, we could use channels per location:
- Each location has N channels encoding the unit there
- Channel 0: Unit type ID (normalized)
- Channel 1: Team (1.0 or -1.0)
- Channel 2: Life (normalized)
- Channel 3: Armor (normalized)
- Channel 4: Damage (normalized)
- Channel 5: Actions left (normalized)
- Channel 6: Stunned flag
- Channel 7: Inactive flag
- Channel 8: Organic flag
- Channel 9: Can act flag

This would be (11, 11, 10) = 1210 values vs plane-based (70, 11, 11) = 8470 values.

## Recommendation

**Use plane-based encoding** because:
1. CNNs work well with plane-based features
2. Can encode multiple units per location (stacking)
3. More interpretable
4. Easier to add features
5. Standard in AlphaGo/AlphaZero

## Implementation Considerations

1. **Unit Type Mapping**: Create a mapping from unit_id to plane index
   - Common types get dedicated planes
   - Rare types use bucket planes

2. **Stat Normalization**: 
   - Life: / max_life (per unit)
   - Armor: / 3.0 (global max)
   - Damage: / 10.0 (global max)
   - Actions: / actions_max (per unit)

3. **Multiple Units**: If multiple units at same location (shouldn't happen in Zatikon):
   - Use max values
   - Or use separate planes for unit counts

4. **Sparse Encoding**: For efficiency, only encode non-zero values

5. **Barracks Encoding**: 
   - Count units by type bucket
   - Encode top N unit types in barracks
   - Use normalized counts

## Example Encoding Function Structure

```python
def encode_game_state(game: Game) -> np.ndarray:
    """
    Encode game state into neural network input planes.
    
    Returns:
        (N_PLANES, BOARD_SIZE, BOARD_SIZE) numpy array
    """
    N_PLANES = 70  # Adjust based on final design
    planes = np.zeros((N_PLANES, BOARD_SIZE, BOARD_SIZE), dtype=np.float32)
    
    # 1. Encode units by type (planes 0-23)
    # 2. Encode unit stats (planes 24-33)
    # 3. Encode unit states (planes 34-41)
    # 4. Encode castle/game state (planes 42-51)
    # 5. Encode barracks (planes 52-63)
    # 6. Encode additional features (planes 64-70)
    
    return planes
```

