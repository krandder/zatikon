# Policy Behavior When Network Proposes Invalid Actions

## Current Flow

### 1. MCTS Policy Generation (lines 434-500)

```python
pi, _, _ = mcts.run(game)
```

**What `pi` contains:**
- Full ACTION_SIZE vector (31,703 actions)
- Probabilities are set ONLY for legal actions (lines 487-491)
- Illegal actions have probability 0.0
- Policy is normalized: `pi = counts / counts.sum()` (line 500)

**Key point:** MCTS policy extraction already filters to legal actions only.

### 2. Turn Generation Loop (lines 676-726)

For each action in the turn:

**a) Get legal actions** (line 686):
```python
legals = get_legal_actions(game_copy)
```
- Returns current legal actions
- Always includes END_TURN

**b) Create legal mask** (lines 691-694):
```python
legal_mask = np.zeros(ACTION_SIZE)
for action in legals:
    idx = action_to_index(*action)
    legal_mask[idx] = 1.0
```
- Sets 1.0 for legal actions, 0.0 for illegal

**c) Mask the policy** (line 697):
```python
masked_pi = pi * legal_mask
```
- Invalid actions → 0.0 probability
- Legal actions → keep their `pi` values

**d) Normalize** (lines 698-702):
```python
if masked_pi.sum() > 0:
    masked_pi /= masked_pi.sum()
else:
    masked_pi = legal_mask / legal_mask.sum()  # Fallback: uniform
```

**e) Sample** (lines 705-710):
```python
action_idx = np.random.choice(ACTION_SIZE, p=masked_pi)
action = index_to_action(action_idx)
```
- Samples from `masked_pi` (only legal actions have non-zero probability)
- **Should only sample legal actions**

**f) Record training data** (line 715):
```python
turn_training_data.append((state_before, pi, action))
```
- Records **raw policy `pi`** (not masked_pi)
- This is the MCTS policy over legal actions

**g) Apply action** (line 718):
```python
result = apply_action(game_copy, *action)
```

**h) Check if invalid** (line 719):
```python
if "Invalid" in result:
    break  # <-- Problem: no END_TURN
```

## Key Questions

### Q1: Can the network propose invalid actions?

**In the policy `pi`:**
- MCTS policy extraction (lines 487-491) only sets counts for legal actions
- So `pi` should have 0 probability for invalid actions
- **Answer: The policy `pi` should NOT contain invalid actions**

### Q2: Can we sample an invalid action?

**Theoretically NO**, because:
- We mask `pi` with `legal_mask` (line 697)
- Only legal actions have non-zero probability in `masked_pi`
- We sample from `masked_pi`

**But practically YES**, if:
1. **Action becomes invalid between check and apply:**
   - `get_legal_actions()` checks at time T
   - Game state changes during turn generation
   - Action applied at time T+1 → now invalid
   - Example: Unit moves, then we try to move it again from old location

2. **Index mapping bug:**
   - `action_to_index()` and `index_to_action()` might not be perfect inverses
   - Could map to wrong action

3. **Race condition:**
   - Multiple actions in turn change game state
   - Later actions become invalid due to earlier actions

### Q3: What policy is recorded for invalid actions?

**Current behavior (line 715):**
```python
turn_training_data.append((state_before, pi, action))
```

- **State:** `state_before` (state before the invalid action)
- **Policy:** `pi` (MCTS policy - should only have legal actions)
- **Action:** The invalid action that was sampled

**Problem:** We're recording the raw `pi`, but the action was invalid. This means:
- Network learns: "In this state, I assigned probabilities X, and action Y was selected"
- But action Y was invalid, so the network gets a confusing signal
- The policy `pi` might not even have probability for this action (if it became invalid)

### Q4: What should happen?

**Option A: Record masked policy**
```python
turn_training_data.append((state_before, masked_pi, action))
```
- Records the policy that was actually used for sampling
- More accurate representation of what happened

**Option B: Don't record invalid actions**
```python
if "Invalid" not in result:
    turn_training_data.append((state_before, pi, action))
```
- Skip recording invalid actions
- Network doesn't learn from invalid action attempts

**Option C: Record with special flag**
```python
turn_training_data.append((state_before, pi, action, is_valid))
```
- Record but mark as invalid
- Network can learn to avoid invalid actions

## Current Issue

When an invalid action is detected:
1. **Training data is recorded** with raw `pi` (line 715)
2. **Turn breaks** without END_TURN (line 720)
3. **Network learns** from invalid action, but signal is confusing

The network's policy `pi` should already exclude invalid actions (from MCTS), but the action becomes invalid between policy generation and application.

## Recommendations

1. **Add logging** to track how often invalid actions occur
2. **Record masked policy** instead of raw policy for more accurate learning
3. **Ensure END_TURN** is always added, even when invalid action detected
4. **Investigate** why actions become invalid (state changes during turn?)

