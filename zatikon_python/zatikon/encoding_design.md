# Zatikon Encoding Design - Combination Flags & Exact Numerics

## 1. Combination Encoding for Rare Units

### Concept
Instead of one plane per unit type, use **N planes** to encode unit types via **binary combinations**.

**Example:**
- With 10 planes, we can represent 2^10 = 1024 different unit types
- Common units get "simple" encodings (few flags set)
- Rare units use combinations of flags

### Performance Impact Analysis

**Potential Issues:**
1. **Learning Complexity**: Network must learn combinations rather than direct features
2. **Sparse Activation**: Most combinations unused, sparse representation
3. **Semantic Loss**: No direct "this is a Footman" signal

**Potential Benefits:**
1. **Efficiency**: Far fewer planes needed
2. **Scalability**: Can handle unlimited unit types
3. **Feature Learning**: Network might learn meaningful combinations

### Research Findings
- Shogi uses **362 planes** total (with history)
- Most implementations use **one plane per type** for common pieces
- Binary encoding is used for **numeric values** (counts, etc.) but less common for piece types

### Recommendation: **Hybrid Approach**

**Strategy:**
1. **Top 10-15 common types**: Dedicated planes (20-30 planes)
2. **Remaining types**: Binary combination encoding (10 planes = 1024 types)
3. **Category buckets**: 4 planes for fallback (melee/ranged/magic/special)

**Total: ~44 planes for unit types** (vs 100+ for one-per-type)

**Encoding Scheme:**
```
Planes 0-9:   Top 10 unit types (Team 1) - dedicated
Planes 10-19: Top 10 unit types (Team 2) - dedicated
Planes 20-29: Binary encoding (10 planes) for rare types (Team 1)
Planes 30-39: Binary encoding (10 planes) for rare types (Team 2)
Planes 40-43: Category buckets (4 categories × 2 teams)
```

**Example:**
- Footman (common): Plane 0 = 1.0 (Team 1)
- RareUnit123: Planes 20-29 = [1,0,1,1,0,0,1,0,1,0] (binary encoding)

### Performance Impact Estimate
- **Minimal degradation** if:
  - Common types (80%+ of units) use dedicated planes
  - Rare types (<20%) use combinations
  - Network can learn that "many flags set" = rare unit
- **Moderate degradation** if:
  - Too many types use combinations (>30%)
  - Encoding is random/unstructured
- **Solution**: Use **semantic encoding** - group related units with similar binary patterns

---

## 2. Exact Numeric Representation

### Requirements
- **Exact HP values** (not normalized/bucketed)
- **Exact action counts** (0, 1, 2, etc.)
- **Exact armor/damage** values

### Option A: Binary Encoding (Recommended)

**Concept**: Encode numbers in binary across multiple planes.

**Example for HP (0-15 range):**
```
HP = 6 → Binary: 0110
Plane 0 (2^0): 0
Plane 1 (2^1): 1
Plane 2 (2^2): 1
Plane 3 (2^3): 0
```

**Advantages:**
- Exact representation
- Efficient (4 planes for 0-15, 5 planes for 0-31)
- Works well with CNNs
- Standard approach in neural networks

**Disadvantages:**
- Multiple planes per value
- Network must learn binary patterns

**Implementation:**
```python
# HP encoding (0-15 range, 4 planes)
hp_planes = [
    (hp >> 0) & 1,  # Bit 0
    (hp >> 1) & 1,  # Bit 1
    (hp >> 2) & 1,  # Bit 2
    (hp >> 3) & 1,  # Bit 3
]

# Actions encoding (0-7 range, 3 planes)
actions_planes = [
    (actions >> 0) & 1,
    (actions >> 1) & 1,
    (actions >> 2) & 1,
]
```

### Option B: One-Hot Encoding

**Concept**: One plane per possible value.

**Example for HP (0-15 range):**
```
HP = 6 → Plane 6 = 1.0, all others = 0.0
```

**Advantages:**
- Very explicit
- Easy to interpret
- Direct feature learning

**Disadvantages:**
- Many planes needed (16 planes for 0-15)
- Very sparse
- Doesn't scale well

### Option C: Multi-Scale Encoding

**Concept**: Separate planes for units, tens, hundreds.

**Example for HP (0-99 range):**
```
HP = 47
Plane 0 (units): 7
Plane 1 (tens): 4
```

**Advantages:**
- Compact (2 planes for 0-99)
- Exact representation
- Network learns digit patterns

**Disadvantages:**
- Network must learn place value
- Less direct than binary

### Option D: Direct Float (Not Recommended)

**Concept**: Single plane with normalized float value.

**Example:**
```
HP = 6, max_HP = 10 → Plane = 0.6
```

**Advantages:**
- Single plane
- Simple

**Disadvantages:**
- **Not exact** - loses precision
- Network sees 0.6, doesn't know if it's 6/10 or 3/5
- **Doesn't meet requirement**

### Recommendation: **Binary Encoding**

**For each numeric value:**
- **HP**: 5 planes (0-31 range, covers most units)
- **Armor**: 3 planes (0-7 range, armor capped at 2-3)
- **Damage**: 4 planes (0-15 range)
- **Actions**: 3 planes (0-7 range, most units have 0-3 actions)

**Total: 15 planes for exact numeric stats**

**Encoding Example:**
```python
# Unit with HP=6, Armor=2, Damage=3, Actions=2

HP planes (5):     [0, 1, 1, 0, 0]  # Binary: 00110
Armor planes (3):  [0, 1, 0]        # Binary: 010
Damage planes (4): [1, 1, 0, 0]     # Binary: 0011
Actions planes (3):[0, 1, 0]        # Binary: 010
```

---

## Complete Encoding Proposal

### Total Plane Count: ~80-90 planes

**Unit Types (44 planes):**
- Top 10 types × 2 teams = 20 planes
- Binary encoding × 2 teams = 20 planes
- Category buckets × 2 teams = 4 planes

**Unit Stats - Exact (15 planes):**
- HP: 5 planes (binary, 0-31)
- Armor: 3 planes (binary, 0-7)
- Damage: 4 planes (binary, 0-15)
- Actions: 3 planes (binary, 0-7)

**Unit States (6 planes):**
- Stunned (Team 1, Team 2) = 2 planes
- Inactive (Team 1, Team 2) = 2 planes
- Organic (Team 1, Team 2) = 2 planes

**Game State (5 planes):**
- Castle locations (2 planes)
- Commands left (1 plane, normalized)
- Turn number (1 plane, normalized)
- Side to move (1 plane)

**Barracks (10 planes):**
- Binary encoding for unit counts (5 planes × 2 teams)

**Total: ~80 planes** (without history)

### Performance Considerations

**Combination Encoding:**
- **Low impact** if <20% of units use it
- **Medium impact** if 20-40% use it
- Use semantic grouping to minimize impact

**Binary Numeric Encoding:**
- **Standard approach** - well-tested
- **No performance degradation** expected
- Networks learn binary patterns easily

### Implementation Notes

1. **Unit Type Mapping**: Create mapping from unit_id to encoding
   - Common types → dedicated plane index
   - Rare types → binary combination

2. **Binary Encoding Helper**:
```python
def encode_binary(value: int, num_bits: int) -> List[float]:
    """Encode integer as binary across planes."""
    return [float((value >> i) & 1) for i in range(num_bits)]
```

3. **Semantic Grouping**: Group related rare units with similar binary patterns
   - Similar units get similar encodings
   - Helps network learn patterns

