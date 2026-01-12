# Debugging Summary: Invalid Actions and Turn Completion

## Problem Identified

Turns were sometimes ending without `END_TURN` action, causing:
1. Turns with 0 actions
2. Turns that don't properly end
3. Inconsistent turn counting

## Root Cause

Actions become invalid during turn generation because:
- **Action points are consumed** as moves are performed
- When a unit runs out of action points, subsequent moves become invalid
- When an invalid action is detected, the loop breaks **without adding `END_TURN`**

Additionally, there were other exit conditions that also didn't add `END_TURN`:
- Terminal state reached (`tv is not None`)
- No legal actions available (`not legals`)

## Solution Implemented

### 1. Fix Invalid Action Handling
When an invalid action is detected:
```python
if "Invalid" in result:
    # Invalid action detected - ensure turn ends properly
    if not turn_actions or turn_actions[-1][0] != ACTION_END_TURN:
        turn_actions.append((ACTION_END_TURN, 0, 0))
    break
```

### 2. Fix Terminal State Exit
When terminal state is reached:
```python
if tv is not None:
    # Terminal state reached - ensure turn ends properly
    if not turn_actions or turn_actions[-1][0] != ACTION_END_TURN:
        turn_actions.append((ACTION_END_TURN, 0, 0))
    break
```

### 3. Fix No Legal Actions Exit
When no legal actions are available:
```python
if not legals:
    # No legal actions - ensure turn ends properly
    if not turn_actions or turn_actions[-1][0] != ACTION_END_TURN:
        turn_actions.append((ACTION_END_TURN, 0, 0))
    break
```

### 4. Safety Check After Loop
Added a final safety check after the loop:
```python
# Ensure turn always ends with END_TURN (safety check)
if not turn_actions or turn_actions[-1][0] != ACTION_END_TURN:
    turn_actions.append((ACTION_END_TURN, 0, 0))
```

## Tests Created

1. **`test_turn_always_ends.py`** - Main test suite:
   - `test_turn_generation_always_includes_end_turn` - Tests turn generation logic directly
   - `test_self_play_game_turns_always_end_with_end_turn` - Tests actual self_play_game function
   - `test_self_play_game_with_display_turns_always_end` - Tests display version

2. **`test_invalid_action_tracking.py`** - Investigation tests:
   - `test_track_invalid_actions_during_turn_generation` - Tracks when/why invalid actions occur
   - `test_track_policy_values_for_invalid_actions` - Tracks policy values
   - `test_track_state_changes_causing_invalid_actions` - Tracks state changes
   - `test_verify_action_index_mapping` - Verifies action encoding
   - `test_track_mcts_policy_contains_only_legal_actions` - Verifies MCTS policy

3. **`test_move_action_invalidation.py`** - Move-specific tests:
   - `test_track_why_move_actions_become_invalid` - Tracks why moves become invalid
   - `test_simulate_turn_generation_to_find_invalidation` - Simulates turn generation

4. **`test_action_points_exhaustion.py`** - Action point tracking:
   - `test_track_action_points_during_turn` - Tracks action point consumption
   - `test_verify_get_remaining_changes_during_turn` - Verifies get_remaining() changes

## Key Insights

1. **Action points are consumed during turn generation** - Units start with action points, but as they move, action points decrease, making later moves invalid.

2. **Invalid actions were legal when checked** - Actions are checked for legality before sampling, but become invalid when applied due to state changes (action point exhaustion).

3. **END_TURN is always legal** - `get_legal_actions()` always includes `END_TURN`, so we can safely add it when needed.

4. **Multiple exit conditions** - Not just invalid actions, but also terminal states and no legal actions can cause early exit without `END_TURN`.

## Files Modified

- `zatikon_python/zatikon/alphazero.py` - Fixed turn generation in both `self_play_game` and `self_play_game_with_display`
- `zatikon_python/tests/test_turn_always_ends.py` - Updated test to match fixed logic

## Verification

All tests pass:
- ✅ `test_turn_generation_always_includes_end_turn`
- ✅ `test_self_play_game_turns_always_end_with_end_turn`
- ✅ `test_self_play_game_with_display_turns_always_end`

The fix ensures that **every turn always ends with `END_TURN`**, regardless of how the turn generation loop exits.

