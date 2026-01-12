"""
Test to verify that actions with stale from_location become invalid.
"""
import pytest
from zatikon import constants
from zatikon.game import Game
from zatikon.alphazero import (
    get_legal_actions,
    apply_action,
    ACTION_MOVE,
    ACTION_END_TURN,
)
from zatikon.unit_factory import UnitFactory


def test_stale_location_causes_invalid_action():
    """
    Test that an action with a stale from_location becomes invalid.
    
    This reproduces the bug:
    1. Get legal actions - unit at location A, action is (MOVE, A, B)
    2. Unit moves from A to C
    3. Try to apply (MOVE, A, B) - INVALID because unit is no longer at A
    """
    game = Game()
    
    # Add and deploy a unit
    footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
    game.castle1.add_unit(footman)
    game.start_turn()
    
    # Deploy unit
    deploy_targets = game._get_castle_targets(game.castle1)
    if deploy_targets:
        game.handle_action(constants.ACTION_DEPLOY, 0, deploy_targets[0])
    
    # End turn to activate unit
    game.handle_action(constants.ACTION_END_TURN, 0, 0)
    game.start_turn()
    
    # Find the unit
    unit = None
    for u in game.battlefield.units:
        if u.castle == game.castle1 and not u.dead:
            unit = u
            break
    
    if not unit:
        pytest.skip("No unit on board")
    
    initial_location = unit.location
    print(f"\nUnit at initial location: {initial_location}")
    
    # Get legal actions - this encodes (MOVE, initial_location, target)
    legals = get_legal_actions(game)
    move_actions = [a for a in legals if a[0] == ACTION_MOVE and a[1] == initial_location]
    
    if not move_actions:
        pytest.skip("No move actions available")
    
    # Pick a move action
    stale_action = move_actions[0]
    print(f"Stale action: {stale_action}")
    print(f"  from_location: {stale_action[1]} (unit is currently at {initial_location})")
    print(f"  to_location: {stale_action[2]}")
    
    # Move the unit to a different location
    # Get a different target
    other_targets = [a[2] for a in move_actions if a[2] != stale_action[2]]
    if other_targets:
        first_move_target = other_targets[0]
        print(f"\nMoving unit from {initial_location} to {first_move_target}")
        result1 = apply_action(game, ACTION_MOVE, initial_location, first_move_target)
        print(f"First move result: {result1}")
        
        # Check unit's new location
        unit_after_move = game.battlefield.get_unit_at(first_move_target)
        if unit_after_move:
            print(f"Unit is now at: {unit_after_move.location}")
        
        # Now try to apply the stale action (from old location)
        print(f"\nTrying to apply stale action: {stale_action}")
        result2 = apply_action(game, *stale_action)
        print(f"Stale action result: {result2}")
        
        # This should be invalid because unit is no longer at stale_action[1]
        assert "Invalid" in result2 or "No unit" in result2, \
            f"Stale action should be invalid! Unit moved from {initial_location} to {first_move_target}, " \
            f"but action still references {stale_action[1]}"
    else:
        pytest.skip("Need at least 2 move targets to test")

