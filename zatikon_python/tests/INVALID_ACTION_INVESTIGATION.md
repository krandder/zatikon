# Invalid Action Investigation Results

## Test Results Summary

From `test_track_invalid_actions_during_turn_generation`:

### Key Findings

1. **All invalid actions are MOVE actions**
   - Pattern: `(1, from_location, to_location)` 
   - Example: `(1, 91, 92)`, `(1, 91, 101)`, `(1, 114, 103)`

2. **Actions were legal before sampling**
   - `Was Legal Before Sampling: True` for all cases
   - This means `get_legal_actions()` returned these actions as valid

3. **Actions become invalid when applied**
   - Result: "Invalid move"
   - This happens during `apply_action()`, not during sampling

4. **Policy values are uniform**
   - Policy Value (raw): 0.000000 or 0.045455
   - Policy Value (masked): 0.045455 (1/22, suggesting uniform over 22 legal actions)
   - This suggests MCTS hasn't learned much yet (untrained network)

5. **Game state shows Commands=0**
   - All invalid actions occur when `Commands=0`
   - This might be a clue, but MOVE actions don't cost commands

## Hypothesis

**Actions become invalid because game state changes during turn generation:**

1. Turn generation happens on `game_copy` (a copy of the game)
2. Actions are applied sequentially to `game_copy`
3. When we check legality: `get_legal_actions(game_copy)` - actions are legal
4. When we apply: `apply_action(game_copy, *action)` - action becomes invalid

**Possible causes:**
- Unit at `from_location` moved earlier in the turn
- Unit at `from_location` died earlier in the turn  
- Target location `to_location` became occupied
- Unit's action points were exhausted
- Some other state change

## Next Steps

1. **Track unit locations** - See if units move/die between legality check and application
2. **Track action points** - See if units run out of actions
3. **Compare game_copy state** - Before and after each action
4. **Check ActionMove validation** - What exactly makes a move invalid?

## Test Coverage

- ✅ `test_track_invalid_actions_during_turn_generation` - Tracks when/why invalid actions occur
- ✅ `test_track_policy_values_for_invalid_actions` - Tracks policy values
- ✅ `test_track_state_changes_causing_invalid_actions` - Tracks state changes
- ✅ `test_verify_action_index_mapping` - Verifies action encoding
- ✅ `test_track_mcts_policy_contains_only_legal_actions` - Verifies MCTS policy

## Questions to Answer

1. Why do MOVE actions become invalid?
2. Is it because the source unit moved/died?
3. Is it because the target location changed?
4. Is it because the unit ran out of action points?
5. Should we re-check legality right before applying?

