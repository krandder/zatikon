# Shogi Encoding in AlphaZero - Reference

## Key Findings

Based on research and typical AlphaZero implementations:

### Input Encoding (Board State)

**Standard Approach:**
- **One plane per piece type per color** (unpromoted pieces)
- **One plane per piece type per color** (promoted pieces)
- **Planes for pieces in hand** (captured pieces available to drop)
- **Planes for game state** (side to move, etc.)
- **History planes** (last N positions)

### Shogi-Specific Details

Shogi has:
- **8 basic piece types**: Pawn, Lance, Knight, Silver, Gold, Bishop, Rook, King
- **Promoted versions** of most pieces (except Gold and King)
- **Pieces in hand** (captured pieces that can be dropped)

**Typical Encoding:**
- **~14 planes** for piece types on board (8 types × 2 colors, minus King which doesn't promote)
- **~14 planes** for promoted pieces
- **~14 planes** for pieces in hand (counts or presence)
- **~1 plane** for side to move
- **History**: Last 8 positions × above = **~8 × 30 = 240 planes**

**Total: ~240-250 input planes** (9×9 board)

### Chess Comparison (for reference)

Chess uses:
- **6 piece types** × **2 colors** = **12 planes** for pieces on board
- **History**: Last 8 positions = **8 × 12 = 96 planes**
- **~1 plane** for side to move
- **~1 plane** for castling rights
- **~1 plane** for en passant

**Total: ~100-110 input planes** (8×8 board)

### Key Principles

1. **One plane per piece type per color** - Simple, direct encoding
2. **Binary values** - 1.0 if piece present, 0.0 otherwise
3. **History encoding** - Last N positions to capture move sequence
4. **Separate planes for promoted pieces** - Important for shogi
5. **Pieces in hand** - Separate encoding for captured pieces

### For Zatikon Adaptation

**Key Differences:**
- Zatikon has **50+ unit types** (vs Shogi's 8)
- Zatikon has **unit stats** (life, armor, damage) - Shogi doesn't
- Zatikon has **unit states** (stunned, inactive) - Shogi doesn't
- Zatikon has **barracks** (undeployed units) - Similar to pieces in hand
- Zatikon has **larger board** (11×11 vs 9×9)

**Adaptation Strategy:**
- Can't use "one plane per type" for all 50+ types (too many planes)
- Need to use **bucketing** or **top-N + buckets** approach
- Need **additional planes** for stats and states
- Can use **history** if needed (but Zatikon is less history-dependent)

## Recommended Approach for Zatikon

Given Shogi's approach but adapted for Zatikon's complexity:

1. **Unit Type Encoding:**
   - Top 15-20 most common types: dedicated planes (30-40 planes)
   - Remaining types: category buckets (8 planes)
   - Total: ~40-50 planes for unit types

2. **Unit Stats:**
   - Life, armor, damage, actions (8 planes)
   - Normalized values [0, 1]

3. **Unit States:**
   - Stunned, inactive, organic flags (6 planes)

4. **Game State:**
   - Castle locations, commands, turn, side to move (5 planes)

5. **Barracks:**
   - Similar to "pieces in hand" in Shogi
   - Category counts + top types (8 planes)

6. **History (optional):**
   - Last 2-4 positions if needed (multiply above by 2-4)

**Total without history: ~70-80 planes**
**Total with history (2 positions): ~140-160 planes**

This is comparable to Shogi's ~240 planes when accounting for:
- Shogi's 8 positions vs Zatikon's 2-4
- Shogi's simpler piece representation vs Zatikon's stats/states

