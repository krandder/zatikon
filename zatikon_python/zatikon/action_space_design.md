# Action Space vs Turn Space - Design Discussion

## Key Distinction

### Traditional Games (Chess, Shogi, Go)
- **One action per turn**
- After each action, player switches
- Turn = Action

### Zatikon
- **Multiple actions per turn**
- Actions: Deploy, Move, Attack (can do multiple)
- Turn ends only when player explicitly ends it (END_TURN action)
- Turn ≠ Action

## Current Implementation Issues

### Problem 1: MCTS Assumes Alternating Players

**Current Code (line 416 in alphazero.py):**
```python
v = -self._simulate(game)  # Negate because opponent's perspective
```

**Issue**: This assumes the player switches after every action, but in Zatikon:
- After DEPLOY → same player's turn
- After MOVE → same player's turn  
- After ATTACK → same player's turn
- After END_TURN → opponent's turn

### Problem 2: Value Function Perspective

**Question**: Should value be evaluated:
- After each action? (action-level)
- Only at turn boundaries? (turn-level)

**Current**: Evaluates after each action, but assumes player switch.

### Problem 3: Training Data Collection

**Current**: Records state after each action
**Question**: Should we record:
- Every action? (action-level policy)
- Only at turn start? (turn-level policy)
- Both?

## Proposed Solution: Action-Based MCTS

### Core Principle
**MCTS operates on actions, not turns.**
- Each node in MCTS tree = one action
- Player only switches after END_TURN action
- Value function evaluates from current player's perspective

### Modified MCTS Algorithm

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
        # Get network evaluation from CURRENT player's perspective
        v = self._evaluate_state(game)
        self.P[sk] = self._get_policy(game, legals)
        self.V[sk] = v
        return v
    
    # Selection
    best_action = self._select_action(sk, legals)
    
    # Apply action
    result = apply_action(game, *best_action)
    
    if "Invalid" in result:
        v = -1.0
    else:
        # Check if action ended the turn
        action_type = best_action[0]
        if action_type == ACTION_END_TURN:
            # Player switched - negate value for opponent's perspective
            v = -self._simulate(game)
        else:
            # Same player continues - keep same perspective
            v = self._simulate(game)
    
    # Backup
    self._backup(sk, best_action, v)
    return v
```

### Key Changes

1. **Conditional Value Negation**:
   - Only negate after END_TURN (player switch)
   - Keep same perspective for other actions

2. **Value Function**:
   - Always evaluates from current player's perspective
   - No assumption about player switching

3. **State Key**:
   - Should include current player (already does)
   - Should distinguish between same-turn states

## Action Space Encoding

### Current Action Space (31,703 actions)
- Deploy: 2,420 actions (20 barracks × 121 locations)
- Move: 14,641 actions (121 × 121)
- Attack: 14,641 actions (121 × 121)
- End Turn: 1 action

**Total: 31,703 actions**

### Is This Correct?

**Yes** - This is the action space, not turn space.

**Each action is independent**:
- Can deploy unit A, then deploy unit B (2 actions)
- Can move unit 1, then move unit 2 (2 actions)
- Can attack with unit 1, then move unit 2 (2 actions)
- Must eventually END_TURN (1 action)

## Training Data Structure

### Option A: Action-Level (Recommended)
```python
# Record every action
for action in turn:
    state = encode_game_state(game)
    pi = mcts.get_policy()  # Policy over actions
    # z will be determined at game end
    history.append((state, pi, current_player))
```

**Pros**:
- More training data
- Learns action-level patterns
- Matches MCTS structure

**Cons**:
- More data to store
- Need to handle turn boundaries

### Option B: Turn-Level
```python
# Record only at turn start
state = encode_game_state(game)  # At turn start
pi = aggregate_action_policies()  # Aggregate over turn
history.append((state, pi, current_player))
```

**Pros**:
- Less data
- Simpler structure

**Cons**:
- Loses action-level information
- Harder to learn action sequences

### Recommendation: **Action-Level**

Record every action, but:
- Use turn boundaries to aggregate value
- Learn action-level policy
- Value is backpropagated from game end

## Value Function Design

### Question: When to Evaluate?

**Option A: After Every Action**
- Evaluate state after deploy/move/attack/end_turn
- Value represents "how good is this state for current player"
- More granular, more training data

**Option B: Only at Turn Boundaries**
- Evaluate only after END_TURN
- Value represents "how good is this turn for the player"
- Less granular, but matches turn structure

### Recommendation: **After Every Action**

**Reasoning**:
- MCTS explores action sequences
- Value should guide action selection
- More training data helps learning
- Can still aggregate at turn boundaries if needed

## Modified MCTS Implementation

### State Key Enhancement

Current state key includes:
- Current player
- Turn number
- Commands left
- Unit positions

**Enhancement**: Should also track:
- Actions taken this turn (for turn boundary detection)
- Or: Just rely on current_player staying same until END_TURN

### Value Backpropagation

**After END_TURN**:
- Player switches
- Negate value: `v = -opponent_value`

**After other actions**:
- Player stays same
- Keep value: `v = current_value`

### Policy Learning

**Action-level policy**:
- Network outputs policy over 31,703 actions
- Each action gets probability
- END_TURN is just another action

**Turn-level aggregation** (optional):
- Can aggregate action policies within a turn
- But primary learning is action-level

## Example MCTS Tree Structure

```
Root: Player 1's turn
├─ Action: Deploy Footman
│  └─ Still Player 1's turn (no negation)
│     ├─ Action: Move Footman
│     │  └─ Still Player 1's turn
│     │     ├─ Action: Attack
│     │     │  └─ Still Player 1's turn
│     │     └─ Action: END_TURN
│     │        └─ Player 2's turn (negate value)
│     └─ Action: END_TURN
│        └─ Player 2's turn (negate value)
└─ Action: END_TURN
   └─ Player 2's turn (negate value)
```

## Implementation Checklist

- [ ] Modify `_simulate` to check action type
- [ ] Only negate value after END_TURN
- [ ] Keep same perspective for other actions
- [ ] Update state key if needed
- [ ] Modify training data collection (action-level)
- [ ] Update value backpropagation logic
- [ ] Test with simple game sequences

## Questions to Resolve

1. **State Key**: Do we need to track "actions taken this turn" or is current_player sufficient?

2. **Value Evaluation**: Should we evaluate after every action or only at turn boundaries?

3. **Training Data**: Action-level or turn-level? (Recommendation: action-level)

4. **Policy Aggregation**: Should we aggregate action policies within a turn for learning?

5. **Turn Boundaries**: How to handle turn boundaries in value backpropagation?

