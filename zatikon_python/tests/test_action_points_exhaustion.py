"""
Test to track action points exhaustion causing invalid moves.
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


class TestActionPointsExhaustion:
    """Test how action points affect move validity."""
    
    def test_track_action_points_during_turn(self):
        """
        Track how action points change during a turn and affect move validity.
        """
        game = Game()
        
        # Add initial units
        for _ in range(3):
            footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
            game.castle1.add_unit(footman)
        bear = UnitFactory.create_unit(constants.UNIT_BEAR, game.castle1)
        game.castle1.add_unit(bear)
        
        game.start_turn()
        
        # Deploy a unit
        deploy_targets = game._get_castle_targets(game.castle1)
        if deploy_targets:
            game.handle_action(constants.ACTION_DEPLOY, 0, deploy_targets[0])
        
        # Find a unit on the board
        unit = None
        for u in game.battlefield.units:
            if u.castle == game.castle1 and not u.dead:
                unit = u
                break
        
        if not unit:
            pytest.skip("No unit on board to test")
        
        print(f"\n=== Action Points Tracking ===")
        print(f"Unit: {unit.name} at location {unit.location}")
        print(f"Initial actions_left: {unit.actions_left}")
        print(f"Initial move_action.remaining: {unit.move_action.remaining}")
        print(f"Initial move_action.get_remaining(): {unit.move_action.get_remaining()}")
        
        # Get legal moves
        legals = get_legal_actions(game)
        move_actions = [a for a in legals if a[0] == ACTION_MOVE and a[1] == unit.location]
        
        print(f"\nLegal move actions: {len(move_actions)}")
        for i, move_action in enumerate(move_actions[:5]):  # Show first 5
            print(f"  {i+1}. Move from {move_action[1]} to {move_action[2]}")
        
        # Try to perform moves and track action points
        action_point_log = []
        
        for move_num in range(5):
            print(f"\n--- Move Attempt {move_num + 1} ---")
            print(f"Actions left: {unit.actions_left}")
            print(f"Move remaining: {unit.move_action.get_remaining()}")
            print(f"Commands left: {game.get_current_castle().commands_left}")
            
            # Get legal moves again
            legals = get_legal_actions(game)
            move_actions = [a for a in legals if a[0] == ACTION_MOVE and a[1] == unit.location]
            
            if not move_actions:
                print("No legal moves available")
                break
            
            move_action = move_actions[0]
            from_loc = move_action[1]
            to_loc = move_action[2]
            
            print(f"Attempting move: from {from_loc} to {to_loc}")
            print(f"Move is in legal list: {move_action in legals}")
            
            # Check validation before applying
            is_valid_before = unit.move_action.validate(to_loc)
            print(f"Move validates before apply: {is_valid_before}")
            
            # Apply move
            result = apply_action(game, *move_action)
            print(f"Result: {result}")
            
            is_invalid = "Invalid" in result
            
            action_point_log.append({
                'move_num': move_num + 1,
                'actions_left_before': unit.actions_left + 1 if not is_invalid else unit.actions_left,  # +1 because it was deducted
                'actions_left_after': unit.actions_left,
                'move_remaining_before': unit.move_action.get_remaining() + 1 if not is_invalid else unit.move_action.get_remaining(),
                'move_remaining_after': unit.move_action.get_remaining(),
                'commands_before': game.get_current_castle().commands_left + 1 if not is_invalid else game.get_current_castle().commands_left,
                'commands_after': game.get_current_castle().commands_left,
                'is_invalid': is_invalid,
                'result': result,
            })
            
            if is_invalid:
                print(f"Move became invalid!")
                print(f"Actions left: {unit.actions_left}")
                print(f"Move remaining: {unit.move_action.get_remaining()}")
                break
            
            # Update unit reference (location might have changed)
            unit = game.battlefield.get_unit_at(to_loc)
            if not unit:
                print("Unit not found at target location")
                break
        
        # Summary
        print(f"\n=== Action Points Summary ===")
        for log_entry in action_point_log:
            print(f"Move {log_entry['move_num']}:")
            print(f"  Actions: {log_entry['actions_left_before']} -> {log_entry['actions_left_after']}")
            print(f"  Move Remaining: {log_entry['move_remaining_before']} -> {log_entry['move_remaining_after']}")
            print(f"  Commands: {log_entry['commands_before']} -> {log_entry['commands_after']}")
            print(f"  Invalid: {log_entry['is_invalid']}")
        
        assert True  # Test for investigation
    
    def test_verify_get_remaining_changes_during_turn(self):
        """
        Verify that get_remaining() changes as actions are performed.
        """
        game = Game()
        
        # Add and deploy a unit
        footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(footman)
        game.start_turn()
        
        deploy_targets = game._get_castle_targets(game.castle1)
        if deploy_targets:
            game.handle_action(constants.ACTION_DEPLOY, 0, deploy_targets[0])
        
        # End turn and start next turn to activate unit
        game.handle_action(constants.ACTION_END_TURN, 0, 0)
        # Now it's Team 2's turn, end it to get back to Team 1
        game.handle_action(constants.ACTION_END_TURN, 0, 0)
        
        # Find the unit
        unit = None
        for u in game.battlefield.units:
            if u.castle == game.castle1 and not u.dead:
                unit = u
                break
        
        if not unit:
            pytest.skip("No unit on board")
        
        print(f"\n=== get_remaining() Changes ===")
        print(f"Unit: {unit.name}")
        print(f"Deployed: {unit.deployed()}")
        print(f"Initial actions_left: {unit.actions_left}")
        print(f"Initial get_remaining(): {unit.move_action.get_remaining()}")
        print(f"Commands left: {game.get_current_castle().commands_left}")
        
        # Perform moves and track get_remaining()
        for move_num in range(5):
            remaining_before = unit.move_action.get_remaining()
            actions_before = unit.actions_left
            
            # Get legal moves
            legals = get_legal_actions(game)
            move_actions = [a for a in legals if a[0] == ACTION_MOVE and a[1] == unit.location]
            
            if not move_actions:
                print(f"\nMove {move_num + 1}: No legal moves")
                break
            
            move_action = move_actions[0]
            result = apply_action(game, *move_action)
            
            remaining_after = unit.move_action.get_remaining()
            actions_after = unit.actions_left
            
            print(f"\nMove {move_num + 1}:")
            print(f"  get_remaining() before: {remaining_before}")
            print(f"  get_remaining() after: {remaining_after}")
            print(f"  actions_left before: {actions_before}")
            print(f"  actions_left after: {actions_after}")
            print(f"  Result: {result}")
            
            if "Invalid" in result:
                print(f"  *** Move became invalid! ***")
                print(f"  get_remaining() was: {remaining_before}")
                print(f"  actions_left was: {actions_before}")
                break
            
            # Update unit reference
            unit = game.battlefield.get_unit_at(move_action[2])
            if not unit:
                break
        
        assert True  # Test for investigation

