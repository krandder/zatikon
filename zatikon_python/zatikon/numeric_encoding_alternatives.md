# Alternative Numeric Encodings with Redundancy

## Problem with Binary Encoding

**Issue**: High-order bits are rarely activated, making them hard to learn.
- HP = 17 → Binary: `10001` (bits: 16, 8, 4, 2, 1)
- HP = 1 → Binary: `00001` (only bit 1)
- The "16" bit is rarely set, so network struggles to learn its meaning

**Solution**: Use encodings with **redundancy** - multiple ways to represent the same number.

---

## Option 1: Unary/Thermometer Encoding (Most Redundant)

### Concept
Each plane represents "value >= N". Very redundant - many planes active for large numbers.

**Example for HP (0-20 range):**
```
HP = 6:
Plane 0: 1 (>= 0) ✓
Plane 1: 1 (>= 1) ✓
Plane 2: 1 (>= 2) ✓
Plane 3: 1 (>= 3) ✓
Plane 4: 1 (>= 4) ✓
Plane 5: 1 (>= 5) ✓
Plane 6: 1 (>= 6) ✓
Plane 7: 0 (>= 7) ✗
Plane 8: 0 (>= 8) ✗
...
Plane 20: 0 (>= 20) ✗
```

**Advantages:**
- **Highly redundant** - large numbers activate many planes
- **Easy to learn** - pattern is simple (cumulative)
- **Robust** - even if some planes are noisy, value is recoverable
- **Natural for CNNs** - spatial patterns are clear

**Disadvantages:**
- **Many planes needed** (N+1 planes for range 0-N)
- **Less efficient** than binary
- **But**: Redundancy helps generalization!

**Implementation:**
```python
def encode_unary(value: int, max_value: int) -> List[float]:
    """Unary/thermometer encoding."""
    return [1.0 if value >= i else 0.0 for i in range(max_value + 1)]

# HP = 6, max_HP = 20
# Returns: [1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
```

**For HP 0-31**: 32 planes (but very redundant and robust!)

---

## Option 2: Multi-Scale Redundant Encoding

### Concept
Encode the same value at multiple scales/resolutions simultaneously.

**Example for HP (0-31 range):**
```
HP = 17

Scale 1 (coarse, 0-31 in steps of 8):
  Plane 0: 1 if HP >= 0  (always 1)
  Plane 1: 1 if HP >= 8  (17 >= 8) ✓
  Plane 2: 1 if HP >= 16 (17 >= 16) ✓
  Plane 3: 1 if HP >= 24 (17 < 24) ✗
  → Tells us: HP is in [16, 24)

Scale 2 (medium, 0-31 in steps of 4):
  Plane 4: 1 if HP >= 0
  Plane 5: 1 if HP >= 4
  Plane 6: 1 if HP >= 8
  Plane 7: 1 if HP >= 12
  Plane 8: 1 if HP >= 16 (17 >= 16) ✓
  Plane 9: 1 if HP >= 20 (17 < 20) ✗
  → Tells us: HP is in [16, 20)

Scale 3 (fine, 0-31 in steps of 1):
  Plane 10-41: Unary encoding for remainder
  → Tells us: HP = 16 + 1 = 17
```

**Advantages:**
- **Redundant** - value encoded at multiple scales
- **Efficient** - fewer planes than pure unary
- **Robust** - can recover value from any scale
- **Generalizes well** - coarse scales help with rare high values

**Disadvantages:**
- More complex to implement
- Still more planes than binary

**Implementation:**
```python
def encode_multiscale(value: int, max_value: int) -> List[float]:
    """Multi-scale encoding."""
    planes = []
    
    # Coarse scale (steps of 8)
    for threshold in range(0, max_value + 1, 8):
        planes.append(1.0 if value >= threshold else 0.0)
    
    # Medium scale (steps of 4)
    for threshold in range(0, max_value + 1, 4):
        planes.append(1.0 if value >= threshold else 0.0)
    
    # Fine scale (remainder, unary)
    remainder = value % 4
    planes.extend([1.0] * remainder + [0.0] * (4 - remainder))
    
    return planes

# HP = 17, max = 31
# Coarse: [1,1,1,0,0] (>=0, >=8, >=16, >=24, >=32)
# Medium: [1,1,1,1,1,0,0,0,0] (>=0,4,8,12,16,20,24,28,32)
# Fine: [1,1,0,0] (remainder 1 from 16)
# Total: ~18 planes
```

---

## Option 3: Residue Number System (RNS)

### Concept
Encode value modulo different bases. Very redundant and robust.

**Example for HP (0-31 range):**
```
HP = 17

Modulo 3: 17 % 3 = 2 → Planes [0,0,1] (one-hot)
Modulo 5: 17 % 5 = 2 → Planes [0,0,1,0,0] (one-hot)
Modulo 7: 17 % 7 = 3 → Planes [0,0,0,1,0,0,0] (one-hot)
Modulo 11: 17 % 11 = 6 → Planes [0,0,0,0,0,0,1,0,0,0,0] (one-hot)

Total: 3 + 5 + 7 + 11 = 26 planes
```

**Advantages:**
- **Highly redundant** - value encoded multiple ways
- **Robust** - can recover value even if some moduli are wrong
- **Distributed** - no single "high-order bit" problem
- **Mathematically elegant**

**Disadvantages:**
- More planes than binary
- Requires Chinese Remainder Theorem to decode (but network learns it)
- Need to choose coprime bases

**Implementation:**
```python
def encode_rns(value: int, bases: List[int]) -> List[float]:
    """Residue Number System encoding."""
    planes = []
    for base in bases:
        residue = value % base
        # One-hot encode residue
        planes.extend([1.0 if i == residue else 0.0 for i in range(base)])
    return planes

# HP = 17, bases = [3, 5, 7, 11]
# Returns: [0,0,1, 0,0,1,0,0, 0,0,0,1,0,0,0, 0,0,0,0,0,0,1,0,0,0,0]
```

---

## Option 4: Hybrid Binary + Unary

### Concept
Combine binary (efficient) with unary (redundant) for robustness.

**Example for HP (0-31 range):**
```
HP = 17

Binary part (5 planes): [1,0,0,0,1] (16 + 1)
Unary part (8 planes for high values): 
  Plane 0: 1 if HP >= 16
  Plane 1: 1 if HP >= 17
  Plane 2: 1 if HP >= 18
  ...
  Plane 7: 1 if HP >= 23

Total: 5 + 8 = 13 planes
```

**Advantages:**
- **Efficient** - binary for low values
- **Redundant** - unary for high values (where we need robustness)
- **Best of both worlds**

**Disadvantages:**
- Still more planes than pure binary
- Need to decide threshold

**Implementation:**
```python
def encode_hybrid(value: int, max_value: int, unary_threshold: int = 16) -> List[float]:
    """Hybrid binary + unary encoding."""
    planes = []
    
    # Binary encoding (always)
    num_bits = int(np.ceil(np.log2(max_value + 1)))
    planes.extend([float((value >> i) & 1) for i in range(num_bits)])
    
    # Unary encoding for high values (redundant)
    if value >= unary_threshold:
        for i in range(unary_threshold, max_value + 1):
            planes.append(1.0 if value >= i else 0.0)
    else:
        # Zero padding
        planes.extend([0.0] * (max_value - unary_threshold + 1))
    
    return planes
```

---

## Option 5: Distributed Representation (Learned Embeddings)

### Concept
Use learned embeddings - each number gets a distributed representation across planes.

**Example:**
```
HP = 17 → Embedding vector of length 8
[0.2, 0.8, 0.1, 0.9, 0.3, 0.7, 0.0, 0.5]

These embeddings are learned during training.
```

**Advantages:**
- **Very flexible** - can learn optimal representations
- **Compact** - fixed number of planes
- **Can capture relationships** - similar numbers have similar embeddings

**Disadvantages:**
- **Not exact** - requires training to learn
- **May not generalize** to unseen values
- **Less interpretable**

**Not recommended** for exact representation requirement.

---

## Option 6: Overlapping Buckets with Redundancy

### Concept
Use overlapping buckets where each value appears in multiple buckets.

**Example for HP (0-31 range):**
```
HP = 17

Bucket set 1 (size 4, stride 2):
  Bucket 0: [0-3]   → 0
  Bucket 1: [2-5]   → 0
  Bucket 2: [4-7]   → 0
  ...
  Bucket 7: [14-17] → 1 ✓ (17 is in this bucket)
  Bucket 8: [16-19] → 1 ✓ (17 is in this bucket)
  Bucket 9: [18-21] → 0

Bucket set 2 (size 8, stride 4):
  Bucket 0: [0-7]   → 0
  Bucket 1: [4-11]  → 0
  Bucket 2: [8-15]  → 0
  Bucket 3: [12-19] → 1 ✓ (17 is in this bucket)
  Bucket 4: [16-23] → 1 ✓ (17 is in this bucket)

Fine-grained remainder:
  HP % 4 = 1 → [0,1,0,0]
```

**Advantages:**
- **Redundant** - value appears in multiple buckets
- **Robust** - can recover from partial information
- **Efficient** - fewer planes than unary

**Disadvantages:**
- More complex
- Need to design bucket structure

---

## Recommendation: **Unary/Thermometer Encoding**

### Why Unary?

1. **Maximum Redundancy**: Large numbers activate many planes
2. **Simple Pattern**: Easy for network to learn (cumulative)
3. **Robust**: Even if some planes are wrong, value is recoverable
4. **No Sparse High-Order Bits**: All planes are used frequently
5. **Proven**: Used in some neural network applications

### Implementation for Zatikon

**For HP (0-31 range):**
- **32 planes** (unary encoding)
- HP = 17 → First 18 planes = 1, rest = 0

**For Armor (0-7 range):**
- **8 planes** (unary encoding)
- Armor = 3 → First 4 planes = 1, rest = 0

**For Damage (0-15 range):**
- **16 planes** (unary encoding)
- Damage = 6 → First 7 planes = 1, rest = 0

**For Actions (0-7 range):**
- **8 planes** (unary encoding)
- Actions = 2 → First 3 planes = 1, rest = 0

**Total: 32 + 8 + 16 + 8 = 64 planes for exact numeric stats**

### Alternative: **Hybrid Binary + Unary** (More Efficient)

If 64 planes is too many, use hybrid:

**For HP (0-31 range):**
- **5 planes** (binary, 0-31)
- **8 planes** (unary for HP >= 16)
- **Total: 13 planes** (vs 32 for pure unary)

**For other stats**: Similar approach

**Total: ~30-35 planes for exact numeric stats** (vs 64 for pure unary)

---

## Comparison Table

| Encoding | Planes (HP 0-31) | Redundancy | Robustness | Efficiency |
|----------|------------------|------------|------------|------------|
| Binary | 5 | Low | Low (sparse high bits) | High |
| Unary | 32 | Very High | Very High | Low |
| Multi-Scale | ~18 | High | High | Medium |
| RNS | ~26 | Very High | Very High | Medium |
| Hybrid | 13 | Medium-High | High | Medium-High |

**Recommendation**: **Unary** for maximum robustness, or **Hybrid** for balance.

