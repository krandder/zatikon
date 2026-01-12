# MCTS Turn-Based Design - Clarifications Needed

## Your Answers Summary

1. **Turn Generation**: Option B - Sample from network policy (stochastic)
2. **Multiple Turns**: Each node = state after turn. Recalculate for exploration. Same child = same state (deterministic)
3. **Turn Representation**: Option C - Store both (sequence + final state)
4. **Value Evaluation**: Not sure why it matters
5. **Action Recording**: (start, sequence, end) - turn boundaries
6. **Policy Storage**: Store action sequence (question why store policy)

## Clarifying Questions

### Question 1: Deterministic vs Stochastic Turn Generation

**Your answer #2**: "If picking same child based on MCTS heuristics, needs to go to same state"

**This implies**:
- When **exploring new** → Generate turn stochastically (different turns possible)
- When **revisiting** → Generate same turn (deterministic, cached?)

**How to implement?**

**Option A: Cache Turns**
```python
# First visit: Generate turn stochastically, cache it
if state not in turn_cache:
    turn = generate_turn_stochastic(state)
    turn_cache[state] = turn
else:
    turn = turn_cache[state]  # Reuse cached turn
```

**Option B: Deterministic Turn Generation for Revisits**
```python
# Use temperature=0 (greedy) when revisiting
# Use temperature>0 when exploring new
```

**Option C: Seed-Based**
```python
# Use state hash as seed for random number generator
# Same state → same seed → same turn sequence
```

**Which approach do you prefer?**

### Question 2: Value Evaluation Timing

**Your answer #4**: "Not sure why this matters"

**Let me clarify**:

**Scenario**: Player 1's turn
- Action 1: Deploy (state S1)
- Action 2: Move (state S2)  
- Action 3: Attack (state S3)
- Action 4: END_TURN (state S4, now Player 2's turn)

**Question**: When do we evaluate the value?

**Option A: Only at S4 (turn end)**
- Evaluate S4 from Player 2's perspective
- Negate: -v2 = value for Player 1
- Use this value for the entire turn

**Option B: After each action, aggregate**
- Evaluate S1, S2, S3, S4
- Aggregate (average? weighted?)
- More information but complex

**My recommendation**: Option A (evaluate only at turn end)
- Simple
- Value represents "how good was this turn"
- Matches turn structure

**Does this make sense? Or do you have a preference?**

### Question 3: Action-Level Learning vs Turn Boundary Recording

**Your earlier requirement**: "Action-level policy learning"

**Your answer #5**: Record (start, sequence, end) - turn boundaries

**Clarification needed**:

**Option A: Record Turn Boundaries Only**
```python
# Training data:
(state_at_turn_start, turn_sequence, state_at_turn_end, value)
```
- Less data
- Learn turn-level patterns
- But you said "action-level learning"...

**Option B: Record Every Action in Turn**
```python
# Training data (for each action in turn):
(state_before_action, action, policy_at_action, turn_value)
```
- More data
- Learn action-level patterns
- Matches "action-level learning"

**Option C: Hybrid**
```python
# MCTS: Work with turn boundaries
# Training: Record every action, use turn's value
(state_before_action, action, policy, turn_value)
```
- MCTS explores turns
- But we learn from individual actions
- Each action gets the turn's final value

**Which matches your intent?**

**My interpretation**: Option C
- MCTS nodes = turns (for exploration efficiency)
- Training data = actions (for learning granularity)
- Each action in a turn gets the turn's final value

**Is this correct?**

### Question 4: MCTS Node Structure

**Your answer #3**: Store both sequence and final state

**Proposed structure**:
```python
class TurnNode:
    state_start: Game  # State at turn start
    action_sequence: List[Tuple]  # Actions taken in turn
    state_end: Game  # State after turn (opponent's turn)
    value: float  # Value from turn-start player's perspective
    visits: int
    total_value: float
```

**Questions**:
- Do we need `state_start` stored, or can we reconstruct from parent?
- Should `state_end` be the actual Game object or just encoded state?

**My proposal**:
```python
# Node stores:
- action_sequence: List[Tuple]  # Actions to get from parent to this node
- state_end_encoded: np.ndarray  # Encoded state after turn
- value: float  # Cached value
- visits: int
- total_value: float
```

**Parent's state_end becomes this node's state_start** (implicit)

**Does this work?**

### Question 5: MCTS Selection with Turn Nodes

**Scenario**: 
- Parent node: Player 1's turn end (state S1)
- Child nodes: Different Player 2 turns
  - Child A: Turn [Deploy, Move, END_TURN] → State S2
  - Child B: Turn [END_TURN] → State S3

**MCTS Selection**:
- UCB selects Child A
- We need to **replay** the turn sequence to get to state S2
- Then continue simulation from S2

**Implementation**:
```python
def select_child(node):
    # UCB selects child
    child = ucb_select(node.children)
    
    # Replay turn to get to child's state
    game = copy_game(node.state_end)  # Start from parent's end state
    for action in child.action_sequence:
        apply_action(game, *action)
    
    # Now game is at child's state_end
    return child, game
```

**Is this the right approach?**

### Question 6: Turn Generation Caching

**Your answer #2**: "If picking same child, needs to go to same state"

**This means**: When MCTS selects the same child node, we must replay the same turn sequence.

**But**: If turn generation is stochastic, how do we ensure same child = same sequence?

**Options**:

**A. Cache turn sequences per state**
```python
turn_cache[(state_hash, player)] = action_sequence
```

**B. Deterministic turn generation**
```python
# Use state hash as random seed
random.seed(hash(state))
turn = generate_turn()  # Deterministic
```

**C. Store turn in child node**
```python
# When creating child, generate and store turn
# Reuse stored turn when revisiting
```

**Which do you prefer?**

## Proposed Implementation Plan

Based on your answers, here's what I understand:

1. **MCTS Structure**:
   - Node = (action_sequence, state_after_turn)
   - Each node represents a complete turn
   - Children = different turns from same start state

2. **Turn Generation**:
   - Stochastic when exploring new
   - Deterministic when revisiting (cached or seeded)

3. **Value Evaluation**:
   - Evaluate at turn end only
   - From opponent's perspective, then negate

4. **Training Data**:
   - Record (start_state, action_sequence, end_state, value)
   - But also record individual actions for action-level learning?

5. **Policy Storage**:
   - Store action sequence in node
   - Don't store policy (network provides it on demand)

**Please confirm or correct these interpretations!**

