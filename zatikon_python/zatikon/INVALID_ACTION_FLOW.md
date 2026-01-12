# Invalid Action Flow Analysis

## Current Flow When Network Proposes Invalid Action

### Step-by-Step Process

1. **MCTS generates policy** (line 669):
   ```python
   pi, _, _ = mcts.run(game)
   ```
   - `pi` is a raw policy over all 31,703 actions
   - Network may assign high probability to invalid actions
   - Policy is NOT masked at this stage

2. **Get legal actions** (line 686):
   ```python
   legals = get_legal_actions(game_copy)
   ```
   - Returns list of legal actions (always includes END_TURN)

3. **Create legal mask** (lines 691-694):
   ```python
   legal_mask = np.zeros(ACTION_SIZE, dtype=np.float32)
   for action in legals:
       idx = action_to_index(*action)
       legal_mask[idx] = 1.0
   ```
   - Sets 1.0 for legal actions, 0.0 for illegal actions

4. **Mask the policy** (line 697):
   ```python
   masked_pi = pi * legal_mask
   ```
   - Invalid actions get probability 0.0
   - Legal actions keep their network-assigned probabilities

5. **Normalize masked policy** (lines 698-702):
   ```python
   if masked_pi.sum() > 0:
       masked_pi /= masked_pi.sum()
   else:
       # Fallback: uniform over legal actions
       masked_pi = legal_mask / legal_mask.sum()
   ```
   - If network assigned 0 probability to ALL legal actions → fallback to uniform
   - Otherwise, normalize so probabilities sum to 1.0

6. **Sample action** (lines 705-710):
   ```python
   if temp == 0.0:
       action_idx = np.argmax(masked_pi)  # Greedy
   else:
       temp_pi = masked_pi ** (1.0 / temp)
       temp_pi /= temp_pi.sum()
       action_idx = np.random.choice(ACTION_SIZE, p=temp_pi)
   ```
   - Samples from `masked_pi` (only legal actions have non-zero probability)
   - **Should only sample legal actions**

7. **Convert to action** (line 712):
   ```python
   action = index_to_action(action_idx)
   ```

8. **Record training data** (line 715):
   ```python
   turn_training_data.append((state_before, pi, action))
   ```
   - Records **RAW policy `pi`**, not masked policy
   - This is important: network learns from its raw policy, even if action was masked

9. **Apply action** (line 718):
   ```python
   result = apply_action(game_copy, *action)
   ```

10. **Check if invalid** (line 719):
    ```python
    if "Invalid" in result:
        break  # <-- Problem: no END_TURN added
    ```

## Key Observations

### Can Invalid Actions Be Sampled?

**Theoretically NO**, because:
- We mask out invalid actions (set probability to 0)
- We sample from the masked distribution
- Only legal actions have non-zero probability

**But practically YES**, because:
- There might be a bug in `action_to_index` / `index_to_action` mapping
- The action might become invalid between checking legality and applying
- Edge cases in action validation

### What Happens When Invalid Action is Detected?

1. **Training data is still recorded** (line 715):
   - Records `(state_before, pi, action)` where `action` is invalid
   - Network learns that this state → invalid action (with raw policy `pi`)

2. **Turn breaks without END_TURN** (line 720):
   - Loop exits immediately
   - No END_TURN added to `turn_actions`
   - Turn is incomplete

3. **Raw policy `pi` is recorded**:
   - Network's raw policy over all actions (including invalid ones)
   - This is what gets used for training
   - Network learns: "In this state, I assigned probabilities X to actions, and action Y was selected (but was invalid)"

### Policy Learning Implications

When an invalid action is proposed and detected:

1. **Raw policy `pi`** contains probabilities for:
   - Valid actions (some probability)
   - Invalid actions (some probability, possibly high)

2. **Masked policy `masked_pi`** contains:
   - Only valid actions (normalized probabilities)
   - Invalid actions have 0 probability

3. **Training data records**:
   - State: `state_before`
   - Policy: `pi` (raw, includes invalid action probabilities)
   - Action: The invalid action that was sampled
   - Value: Turn value (if turn completes)

4. **Network learns**:
   - "In this state, I should assign probability X to this invalid action"
   - But the action was invalid, so the network gets a negative signal
   - Over time, network should learn to assign low probability to invalid actions

### Potential Issues

1. **Action becomes invalid between check and apply**:
   - Legal action checked at time T
   - Game state changes
   - Action applied at time T+1 → now invalid
   - This can happen if game state changes during turn generation

2. **Index mapping bug**:
   - `action_to_index` and `index_to_action` might not be perfect inverses
   - Could map to wrong action

3. **No END_TURN on invalid action**:
   - Turn breaks without completing
   - Game state might be inconsistent

## Questions to Answer

1. **How often does this happen?**
   - Need to add logging to track invalid action frequency

2. **Why does the network propose invalid actions?**
   - Network hasn't learned legality constraints yet
   - MCTS policy might not perfectly mask invalid actions
   - Policy extraction might include invalid actions

3. **Should we record the masked policy instead?**
   - Currently recording raw `pi`
   - Could record `masked_pi` to teach network about legal actions

4. **What should happen when invalid action is detected?**
   - Add END_TURN to complete turn?
   - Retry with different action?
   - Use fallback (END_TURN)?

