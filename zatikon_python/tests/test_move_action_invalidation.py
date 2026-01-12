"""
Test to understand why MOVE actions become invalid.
"""
import pytest
from zatikon import constants
from zatikon.game import Game
from zatikon.alphazero import (
    get_legal_actions,
    action_to_index,
    index_to_action,
    apply_action,
    ACTION_MOVE,
    ACTION_END_TURN,
)
from zatikon.unit_factory import UnitFactory
from zatikon.battlefield import BattleField


class TestMoveActionInvalidation:
    """Test why MOVE actions become invalid."""
    
    def test_track_why_move_actions_become_invalid(self):
        """
        Track exactly why MOVE actions become invalid.
        
        This test will help us understand:
        - Does the source unit move/die?
        - Does the target location change?
        - Do action points get exhausted?
        """
        game = Game()
        
        # Add initial units
        for _ in range(3):
            footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
            game.castle1.add_unit(footman)
        bear = UnitFactory.create_unit(constants.UNIT_BEAR, game.castle1)
        game.castle1.add_unit(bear)
        
        for _ in range(3):
            footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle2)
            game.castle2.add_unit(footman)
        bear = UnitFactory.create_unit(constants.UNIT_BEAR, game.castle2)
        game.castle2.add_unit(bear)
        
        game.start_turn()
        
        import copy
        
        # Deploy a unit to have something to move
        deploy_targets = game._get_castle_targets(game.castle1)
        if deploy_targets:
            game.handle_action(constants.ACTION_DEPLOY, 0, deploy_targets[0])
        
        invalid_move_details = []
        
        for attempt in range(10):
            game_copy = copy.deepcopy(game)
            
            # Get legal actions
            legals = get_legal_actions(game_copy)
            move_actions = [a for a in legals if a[0] == ACTION_MOVE]
            
            if not move_actions:
                # No move actions available, end turn and try again
                apply_action(game, ACTION_END_TURN, 0, 0)
                continue
            
            # Pick a move action
            move_action = move_actions[0]
            from_loc = move_action[1]
            to_loc = move_action[2]
            
            # Capture state before action
            unit_before = game_copy.battlefield.get_unit_at(from_loc)
            target_before = game_copy.battlefield.get_unit_at(to_loc)
            
            if unit_before:
                unit_state_before = {
                    'location': unit_before.location,
                    'actions': unit_before.actions,
                    'dead': unit_before.dead,
                    'deployed': unit_before.deployed(),
                }
            else:
                unit_state_before = None
            
            # Check if action is in legal list
            is_legal = move_action in legals
            
            # Apply action
            result = apply_action(game_copy, *move_action)
            is_invalid = "Invalid" in result
            
            if is_invalid:
                # Capture state after (failed) action
                unit_after = game_copy.battlefield.get_unit_at(from_loc)
                target_after = game_copy.battlefield.get_unit_at(to_loc)
                
                if unit_after:
                    unit_state_after = {
                        'location': unit_after.location,
                        'actions': unit_after.actions,
                        'dead': unit_after.dead,
                        'deployed': unit_after.deployed(),
                    }
                else:
                    unit_state_after = None
                
                invalid_move_details.append({
                    'attempt': attempt,
                    'action': move_action,
                    'from_loc': from_loc,
                    'to_loc': to_loc,
                    'was_legal': is_legal,
                    'result': result,
                    'unit_before': unit_state_before,
                    'unit_after': unit_state_after,
                    'target_before': target_before is not None,
                    'target_after': target_after is not None,
                    'unit_moved': unit_state_before and unit_state_after and unit_state_before['location'] != unit_state_after['location'],
                    'unit_died': unit_state_before and (not unit_state_after or unit_state_after['dead']),
                })
            
            # Apply END_TURN to advance
            apply_action(game, ACTION_END_TURN, 0, 0)
            
            if game.is_over():
                break
        
        # Analyze results
        print(f"\n=== Move Action Invalidation Analysis ===")
        print(f"Invalid move actions found: {len(invalid_move_details)}")
        
        for detail in invalid_move_details:
            print(f"\nInvalid Move {detail['attempt']}:")
            print(f"  Action: {detail['action']}")
            print(f"  From: {detail['from_loc']}, To: {detail['to_loc']}")
            print(f"  Was Legal: {detail['was_legal']}")
            print(f"  Result: {detail['result']}")
            print(f"  Unit Before: {detail['unit_before']}")
            print(f"  Unit After: {detail['unit_after']}")
            print(f"  Unit Moved: {detail['unit_moved']}")
            print(f"  Unit Died: {detail['unit_died']}")
            print(f"  Target Before: {detail['target_before']}")
            print(f"  Target After: {detail['target_after']}")
        
        # This test is for investigation, always passes
        assert True
    
    def test_simulate_turn_generation_to_find_invalidation(self):
        """
        Simulate the exact turn generation process to find when actions become invalid.
        """
        game = Game()
        
        # Add initial units
        for _ in range(3):
            footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
            game.castle1.add_unit(footman)
        bear = UnitFactory.create_unit(constants.UNIT_BEAR, game.castle1)
        game.castle1.add_unit(bear)
        
        for _ in range(3):
            footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle2)
            game.castle2.add_unit(footman)
        bear = UnitFactory.create_unit(constants.UNIT_BEAR, game.castle2)
        game.castle2.add_unit(bear)
        
        game.start_turn()
        
        import copy
        import numpy as np
        
        # Simulate turn generation with uniform policy
        pi = np.ones(31703) / 31703  # Uniform policy
        
        for turn_num in range(5):
            if game.is_over():
                break
            
            game_copy = copy.deepcopy(game)
            turn_actions = []
            action_log = []
            
            while True:
                # Get legal actions
                legals = get_legal_actions(game_copy)
                if not legals:
                    break
                
                # Create mask and sample (simulating the process)
                legal_mask = np.zeros(31703, dtype=np.float32)
                for action in legals:
                    idx = action_to_index(*action)
                    legal_mask[idx] = 1.0
                
                masked_pi = pi * legal_mask
                if masked_pi.sum() > 0:
                    masked_pi /= masked_pi.sum()
                else:
                    masked_pi = legal_mask / legal_mask.sum()
                
                action_idx = np.random.choice(31703, p=masked_pi)
                action = index_to_action(action_idx)
                
                # Capture detailed state
                action_detail = {
                    'action': action,
                    'action_type': action[0],
                    'was_legal': action in legals,
                    'legal_count': len(legals),
                }
                
                # If it's a move action, capture unit state
                if action[0] == ACTION_MOVE:
                    from_loc = action[1]
                    unit = game_copy.battlefield.get_unit_at(from_loc)
                    if unit:
                        action_detail['unit_state'] = {
                            'location': unit.location,
                            'actions': unit.actions,
                            'dead': unit.dead,
                            'deployed': unit.deployed(),
                        }
                    else:
                        action_detail['unit_state'] = None
                        action_detail['unit_missing'] = True
                
                # Apply action
                result = apply_action(game_copy, *action)
                action_detail['result'] = result
                action_detail['is_invalid'] = "Invalid" in result
                
                action_log.append(action_detail)
                
                if "Invalid" in result:
                    # Found an invalid action - log details
                    print(f"\n=== Invalid Action Found (Turn {turn_num}) ===")
                    print(f"Action: {action_detail['action']}")
                    print(f"Was Legal: {action_detail['was_legal']}")
                    print(f"Result: {action_detail['result']}")
                    if 'unit_state' in action_detail:
                        print(f"Unit State: {action_detail['unit_state']}")
                    if 'unit_missing' in action_detail:
                        print(f"Unit Missing: {action_detail['unit_missing']}")
                    
                    # Show previous actions in this turn
                    print(f"\nPrevious actions in this turn:")
                    for i, prev_action in enumerate(action_log[:-1]):
                        print(f"  {i+1}. {prev_action['action']} -> {prev_action['result']}")
                    break
                
                turn_actions.append(action)
                
                if action[0] == ACTION_END_TURN:
                    break
            
            # Apply turn to actual game
            for action in turn_actions:
                apply_action(game, *action)
            
            if game.is_over():
                break
        
        assert True  # Test for investigation

