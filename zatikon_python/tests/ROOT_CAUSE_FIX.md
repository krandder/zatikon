# Root Cause Fix: Stale Action Locations

## The Real Problem

Actions were becoming invalid because **`get_legal_actions` captures `unit.location` at call time**, but units can move during turn generation, making the `from_location` in the action stale.

### Example:
1. `get_legal_actions()` called → unit at location A
2. Returns action: `(MOVE, A, B)`
3. Unit moves: `(MOVE, A, C)` is applied → unit now at location C
4. Try to apply `(MOVE, A, B)` → **INVALID** because unit is no longer at A!

### Why This Happens:
- `get_legal_actions()` encodes actions as `(ACTION_MOVE, unit.location, target)` 
- `unit.location` is captured **at the time `get_legal_actions()` is called**
- But by the time we apply the action, the unit may have moved
- `apply_action()` calls `_handle_move()` which does `get_unit_at(from_location)`
- If unit moved, `get_unit_at(from_location)` returns `None` → "No unit at location" → "Invalid move"

## The Fix

**Re-validate actions against the CURRENT game state right before applying:**

```python
action = index_to_action(action_idx)

# CRITICAL: Re-validate action against CURRENT state
# Actions may become invalid if unit moved or state changed
current_legals = get_legal_actions(game_copy)
if action not in current_legals:
    # Action is no longer legal - skip it and try again
    continue

# Now safe to apply
result = apply_action(game_copy, *action)
```

This ensures that:
1. We only apply actions that are legal in the **current** state
2. Stale actions (with old `from_location`) are skipped
3. We don't waste time trying to apply invalid actions

## Why This Is Better Than the Workaround

The previous "fix" was a workaround that added `END_TURN` when invalid actions were detected. This:
- ✅ Fixed the symptom (turns not ending)
- ❌ Didn't fix the root cause (stale actions)
- ❌ Still wasted computation trying to apply invalid actions
- ❌ Created confusing training data (invalid actions in policy)

The new fix:
- ✅ Fixes the root cause (prevents stale actions from being applied)
- ✅ More efficient (skips invalid actions immediately)
- ✅ Cleaner training data (only valid actions)
- ✅ Still has safety nets for edge cases (terminal state, no legal actions)

## Safety Nets Still in Place

We still have safety checks for other exit conditions:
1. Terminal state reached → add `END_TURN`
2. No legal actions → add `END_TURN`
3. Final safety check after loop → ensure `END_TURN` is present

But these should rarely trigger now that we prevent stale actions.

## Testing

All tests pass:
- ✅ `test_turn_generation_always_includes_end_turn`
- ✅ `test_self_play_game_turns_always_end_with_end_turn`
- ✅ `test_self_play_game_with_display_turns_always_end`

The fix prevents stale actions from being applied, which was the root cause of invalid actions.

