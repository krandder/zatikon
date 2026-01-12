# Action-Based MCTS for Zatikon

## The Problem

### Current Implementation (WRONG)
```python
# Line 416 in alphazero.py
v = -self._simulate(game)  # Always negates - ASSUMES player switch
```

**Issue**: This assumes player switches after EVERY action, but in Zatikon:
- Deploy → Same player continues
- Move → Same player continues  
- Attack → Same player continues
- **END_TURN → Player switches** ✓

### Correct Behavior Needed

```python
action_type = best_action[0]
if action_type == ACTION_END_TURN:
    v = -self._simulate(game)  # Negate - player switched
else:
    v = self._simulate(game)   # Keep same - same player
```

## Action Space Structure

### Current Action Space: 31,703 actions
- **Deploy**: 2,420 actions (barracks_index × location)
- **Move**: 14,641 actions (from_location × to_location)
- **Attack**: 14,641 actions (from_location × to_location)
- **END_TURN**: 1 action

**This is correct** - these are the atomic actions.

### Turn Structure
A turn consists of a sequence of actions:
```
Turn 1 (Player 1):
  Action 1: Deploy Footman
  Action 2: Deploy Bear
  Action 3: Move Footman
  Action 4: Attack with Bear
  Action 5: END_TURN  ← Only this switches players

Turn 2 (Player 2):
  Action 1: Deploy Archer
  Action 2: END_TURN
```

## MCTS Tree Structure

### Traditional Games (Chess)
```
Root (White)
├─ Move 1 (White → Black)
│  └─ Move 2 (Black → White)
│     └─ Move 3 (White → Black)
```

**Every node switches players**

### Zatikon (Action-Based)
```
Root (Player 1's turn)
├─ Action: Deploy (Player 1 continues)
│  ├─ Action: Move (Player 1 continues)
│  │  ├─ Action: Attack (Player 1 continues)
│  │  │  └─ Action: END_TURN (→ Player 2)
│  │  └─ Action: END_TURN (→ Player 2)
│  └─ Action: END_TURN (→ Player 2)
└─ Action: END_TURN (→ Player 2)
```

**Only END_TURN nodes switch players**

## Modified MCTS Algorithm

### Key Changes

1. **Conditional Value Negation**:
   - Check action type before negating
   - Only negate after END_TURN

2. **Value Perspective**:
   - Value always from current player's perspective
   - Network evaluates "how good is this state for current player"
   - No assumption about player switching

3. **State Key**:
   - Already includes `current_player` ✓
   - This is sufficient - no need to track "actions taken this turn"

### Implementation

```python
def _simulate(self, game: Game) -> float:
    """
    Perform one MCTS simulation.
    
    Returns:
        Value from current player's perspective
    """
    sk = self.state_key(game)
    tv = terminal_value(game)
    
    if tv is not None:
        return tv
    
    legals = get_legal_actions(game)
    if not legals:
        return -1.0  # No legal moves = loss
    
    # Leaf node: expand
    if sk not in self.P:
        # Evaluate from CURRENT player's perspective
        with torch.no_grad():
            x_np = encode_game_state(game)
            x = torch.tensor(x_np[None, :, :, :], dtype=torch.float32)
            self.net.eval()
            logits, v = self.net(x)
            logits = logits[0].cpu().numpy()
            v = float(v.item())  # Value from current player's perspective
        
        # Mask illegal moves
        mask = np.full(ACTION_SIZE, -1e9, dtype=np.float32)
        for action in legals:
            a_idx = action_to_index(*action)
            mask[a_idx] = logits[a_idx]
        
        probs = np.exp(mask - np.max(mask))
        probs /= probs.sum()
        
        self.P[sk] = probs
        self.V[sk] = v
        return v
    
    # Selection
    best_a_idx = None
    best_ucb = -1e9
    sum_Ns = self.Ns[sk] + 1e-8
    
    for action in legals:
        a_idx = action_to_index(*action)
        Nsa = self.Nsa[(sk, a_idx)]
        Wsa = self.Wsa[(sk, a_idx)]
        Qsa = Wsa / Nsa if Nsa > 0 else 0.0
        Psa = self.P[sk][a_idx]
        u = Qsa + CPUCT * Psa * math.sqrt(sum_Ns) / (1 + Nsa)
        
        if u > best_ucb:
            best_ucb = u
            best_a_idx = a_idx
    
    # Apply action
    action = index_to_action(best_a_idx)
    action_type = action[0]
    result = apply_action(game, *action)
    
    if "Invalid" in result:
        v = -1.0
    else:
        # KEY CHANGE: Only negate if player switched
        if action_type == ACTION_END_TURN:
            # Player switched - value from opponent's perspective
            v = -self._simulate(game)
        else:
            # Same player continues - keep same perspective
            v = self._simulate(game)
    
    # Backup
    self.Nsa[(sk, best_a_idx)] += 1
    self.Wsa[(sk, best_a_idx)] += v
    self.Ns[sk] += 1
    
    return v
```

## Training Data Collection

### Action-Level Recording (Recommended)

Record every action, not just turn boundaries:

```python
def self_play_game(...):
    history = []
    
    while not game.is_over():
        # Get action from MCTS
        action, pi, _, _ = azero_choose_move(net, game, mcts_sims, temp)
        
        # Record BEFORE applying action
        state = encode_game_state(game)
        history.append((state, pi, game.current_player))
        
        # Apply action
        apply_action(game, *action)
        
        # Check if game ended
        if terminal_value(game) is not None:
            break
```

**Value Assignment**:
- At game end, assign value to all positions
- Value from perspective of player who made the action
- Winner's actions get +1.0, loser's get -1.0

## Value Function Design

### Question: When to Evaluate Value?

**Option A: After Every Action** (Recommended)
- Evaluate state after deploy/move/attack/end_turn
- Value = "how good is this state for current player"
- More training data
- More granular learning

**Option B: Only at Turn Boundaries**
- Evaluate only after END_TURN
- Value = "how good was this turn"
- Less training data
- Matches turn structure better

### Recommendation: **After Every Action**

**Reasoning**:
1. MCTS explores action sequences, not turn sequences
2. Value should guide action selection
3. More training data = better learning
4. Can still aggregate at turn boundaries if needed

## State Key Considerations

### Current State Key
```python
key_parts = [
    str(game.current_player),      # ✓ Distinguishes players
    str(game.turn_number),          # ✓ Distinguishes turns
    str(game.castle1.commands_left),
    str(game.castle2.commands_left),
    str(tuple(unit_positions)),
]
```

### Question: Do we need "actions taken this turn"?

**Answer: Probably not**

**Reasoning**:
- `current_player` already distinguishes whose turn it is
- `commands_left` changes with each action (implicit turn tracking)
- Unit positions change with each action
- State is already unique enough

**However**: Two states with same unit positions but different action sequences within a turn would have the same key. But this is probably fine - the state is what matters, not the history.

## Example: MCTS Simulation

```
Initial: Player 1, 5 commands, units at [A, B]

Simulation 1:
  Action: Deploy C (Player 1, 4 commands, units at [A, B, C])
    Action: Move A (Player 1, 3 commands, units at [A', B, C])
      Action: END_TURN (Player 2, ...)
        → Evaluate from Player 2's perspective
        → Negate: -v2
      → Backprop: v = -v2 (from Player 1's perspective)
    → Backprop: v = -v2
  → Backprop: v = -v2

Simulation 2:
  Action: END_TURN (Player 2, ...)
    → Evaluate from Player 2's perspective
    → Negate: -v2
  → Backprop: v = -v2 (from Player 1's perspective)
```

## Implementation Checklist

- [x] Action space correctly defined (31,703 actions)
- [ ] Modify `_simulate` to check action type
- [ ] Only negate value after END_TURN
- [ ] Keep same perspective for other actions
- [ ] Update training data collection (action-level)
- [ ] Test with simple sequences
- [ ] Verify value backpropagation

## Questions to Resolve

1. **Value Evaluation**: After every action or only at turn boundaries?
   - **Recommendation**: After every action

2. **Training Data**: Record every action or only turn starts?
   - **Recommendation**: Record every action

3. **State Key**: Need to track "actions taken this turn"?
   - **Recommendation**: No, current_player + commands_left is sufficient

4. **Policy Learning**: Action-level or turn-level?
   - **Recommendation**: Action-level (matches MCTS structure)

5. **Value Perspective**: Always from current player?
   - **Recommendation**: Yes, network learns "value for current player"

