# Turn-Based MCTS with Action-Level Learning - Design Questions

## Core Concept

**MCTS Tree Structure**:
- **Node** = Full turn (sequence of actions)
- **Edge** = Transition from one turn to next
- **Policy Learning** = Action-level (record every action)

**MCTS Tree**:
```
Root: Player 1's turn start
├─ Turn 1: [Deploy, Move, Attack, END_TURN] → Player 2's turn start
│  ├─ Turn 2: [Deploy, END_TURN] → Player 1's turn start
│  └─ Turn 2: [END_TURN] → Player 1's turn start
└─ Turn 1: [END_TURN] → Player 2's turn start
```

## Key Questions

### Question 1: How to Generate a Complete Turn?

**Option A: Network-Guided Greedy**
- Use network policy to select actions greedily
- Continue until END_TURN is selected
- Fast, but may not explore well

**Option B: Mini-MCTS Within Turn**
- Run small MCTS to select actions within turn
- More exploration, but expensive
- Turn becomes a "sub-game"

**Option C: Policy Sampling**
- Sample actions from network policy
- Continue until END_TURN sampled
- Balance between exploration and speed

**Option D: Fixed Turn Length**
- Generate N actions per turn
- Then force END_TURN
- Simple but artificial

**Recommendation**: Option C (Policy Sampling) - good balance

### Question 2: How to Evaluate a Turn?

**Option A: Evaluate Only at Turn End**
- Run turn, then evaluate final state
- Value = "how good is state after this turn"
- Simple, matches turn structure

**Option B: Evaluate After Each Action, Aggregate**
- Evaluate after each action in turn
- Aggregate values (average? weighted?)
- More information, but how to aggregate?

**Option C: Evaluate at Turn Start and End**
- Evaluate before and after turn
- Value = difference (end - start)
- Captures turn value

**Recommendation**: Option A (evaluate at turn end) - simplest

### Question 3: How to Learn Action-Level Policies?

**Scenario**: MCTS explores turns, but we want action-level learning.

**Option A: Record Actions During Turn Generation**
- When generating turn, record each action + state
- Use turn's final value for all actions in turn
- Action-level data, turn-level exploration

**Option B: Record Only Turn Boundaries**
- Record state at turn start/end
- Learn turn-level policy
- But you said action-level learning...

**Option C: Hybrid - Turn Exploration, Action Recording**
- MCTS explores turns
- But record every action taken during turn generation
- Use turn's value for all actions in that turn
- This matches your requirement!

**Recommendation**: Option C - MCTS explores turns, but we record every action

### Question 4: Network Architecture - Turn Policy or Action Policy?

**Current**: Network outputs policy over 31,703 actions

**Question**: Should network learn:
- **Action-level policy** (current): P(action | state)
- **Turn-level policy**: P(turn_sequence | state)

**If action-level**:
- Network outputs P(action | state) for each action
- We sample actions to build turn
- We learn action-level policy

**If turn-level**:
- Network outputs P(turn | state) over all possible turns
- But there are exponentially many turns!
- Not feasible

**Recommendation**: Keep action-level network, use it to generate turns

### Question 5: How to Handle Turn Generation in MCTS?

**When expanding a node** (turn start state):
1. Generate a complete turn using network policy
2. Evaluate final state after turn
3. Backpropagate value

**But**: How to explore different turns from same state?

**Option A: Sample Multiple Turns**
- Generate K different turns from same state
- Evaluate each, use best/average
- More exploration

**Option B: Single Turn Per Node**
- Each node = one turn sequence
- Explore by having multiple child nodes (different turns)
- Standard MCTS structure

**Option C: Turn Policy Network**
- Network outputs distribution over "turn strategies"
- But how to represent turn strategies?

**Recommendation**: Option B - each node is one turn, explore multiple turns

### Question 6: Value Backpropagation

**After generating a turn**:
- State: S1 (turn start)
- Actions: [A1, A2, A3, END_TURN]
- State: S2 (turn end, opponent's turn)

**Value**: Evaluate S2 from opponent's perspective, then negate?

**Or**: Evaluate S2 from current player's perspective (how good was my turn)?

**Recommendation**: Evaluate S2 from opponent's perspective, then negate
- Value = "how good is this for opponent" → negate → "how good for me"

### Question 7: Turn Generation - Deterministic or Stochastic?

**When generating a turn from a state**:
- **Deterministic**: Always same turn (no exploration)
- **Stochastic**: Sample actions, get different turns (exploration)

**But**: If stochastic, same state → different turns → different values
- How to handle this in MCTS?

**Option A: Deterministic Turn Generation**
- Use temperature=0 (greedy) for turn generation
- Each state → one turn
- Simple, but less exploration

**Option B: Stochastic with Caching**
- Generate turn stochastically
- Cache turn for this state
- Reuse same turn for this state

**Option C: Multiple Turns Per State**
- Generate multiple turns, create multiple child nodes
- Standard MCTS exploration

**Recommendation**: Option C - generate multiple turns, explore them

## Proposed Architecture

### MCTS Structure
```
Node = (state_at_turn_start, player)
Edge = (turn_sequence, value)
```

### Turn Generation
```python
def generate_turn(game: Game, net: ZatikonNet, temp: float = 1.0) -> List[Tuple]:
    """
    Generate a complete turn (sequence of actions).
    
    Returns:
        List of (action, state_before_action, policy) tuples
    """
    turn_actions = []
    initial_state = encode_game_state(game)
    initial_player = game.current_player
    
    while True:
        # Get network policy
        state = encode_game_state(game)
        with torch.no_grad():
            logits, _ = net(torch.tensor(state[None, ...]))
            policy = F.softmax(logits, dim=1)[0].cpu().numpy()
        
        # Get legal actions
        legals = get_legal_actions(game)
        legal_mask = np.zeros(ACTION_SIZE)
        for action in legals:
            idx = action_to_index(*action)
            legal_mask[idx] = 1.0
        
        # Mask and sample
        masked_policy = policy * legal_mask
        if masked_policy.sum() == 0:
            break
        masked_policy /= masked_policy.sum()
        
        # Sample action
        action_idx = np.random.choice(ACTION_SIZE, p=masked_policy)
        action = index_to_action(action_idx)
        
        # Record action
        turn_actions.append((action, state, masked_policy))
        
        # Apply action
        apply_action(game, *action)
        
        # Check if turn ended
        if action[0] == ACTION_END_TURN:
            break
    
    return turn_actions
```

### MCTS Simulation
```python
def _simulate(self, game: Game) -> float:
    """
    Generate a complete turn and evaluate it.
    """
    sk = self.state_key(game)  # State at turn start
    tv = terminal_value(game)
    
    if tv is not None:
        return tv
    
    # Check if we've explored this turn start state
    if sk not in self.P:
        # Generate a turn
        turn_actions = generate_turn(game, self.net, temp=1.0)
        
        # Evaluate final state (after turn)
        final_state = encode_game_state(game)
        with torch.no_grad():
            x = torch.tensor(final_state[None, ...])
            _, v = self.net(x)
            v = float(v.item())  # Value from current player's perspective
        
        # But final state is opponent's turn, so negate
        v = -v
        
        # Store policy (aggregate over turn actions?)
        # Store value
        self.P[sk] = ...  # How to represent turn policy?
        self.V[sk] = v
        
        return v
    
    # Selection: Choose which turn to explore
    # But we only have one turn per state currently...
    # Need to generate multiple turns?
    
    # For now, generate new turn
    turn_actions = generate_turn(game, self.net, temp=1.0)
    final_state = encode_game_state(game)
    v = -self._evaluate_state(final_state)  # Opponent's perspective
    
    return v
```

## Key Questions for You

1. **Turn Generation**: How should we generate a turn?
   - Greedy from network?
   - Sample from network policy?
   - Mini-MCTS within turn?
   - Fixed number of actions?

2. **Multiple Turns Per State**: Should we explore multiple different turns from the same turn-start state?
   - If yes, how many?
   - How to represent them in MCTS tree?

3. **Turn Policy Representation**: How to represent "turn policy" in MCTS?
   - Aggregate action policies?
   - Just store action sequence?
   - Learn turn-level policy network?

4. **Value Evaluation**: Evaluate turn at:
   - Turn end only?
   - After each action (aggregate)?
   - Turn start and end (difference)?

5. **Action Recording**: When generating a turn, record:
   - Every action with its state?
   - Only turn boundaries?
   - Both?

6. **Exploration**: How to explore different turns from same state?
   - Generate multiple turns, create child nodes?
   - Use temperature to vary turn generation?
   - Something else?

