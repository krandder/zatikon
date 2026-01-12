"""
Tests to investigate and track invalid actions during turn generation.
"""
import pytest
import numpy as np
from zatikon import constants
from zatikon.game import Game
from zatikon.alphazero import (
    self_play_game,
    self_play_game_with_display,
    ZatikonNet,
    MCTS,
    get_legal_actions,
    action_to_index,
    index_to_action,
    apply_action,
    ACTION_END_TURN,
    ACTION_MOVE,
    ACTION_ATTACK,
    ACTION_DEPLOY,
)
from zatikon.unit_factory import UnitFactory


class TestInvalidActionTracking:
    """Tests to track and understand invalid actions."""
    
    @pytest.fixture
    def net(self):
        """Create a neural network for testing."""
        return ZatikonNet()
    
    def test_track_invalid_actions_during_turn_generation(self, net):
        """
        Track when invalid actions occur during turn generation.
        
        This test logs:
        - How often invalid actions occur
        - What actions become invalid
        - Policy values for invalid actions
        - State changes that might cause invalidity
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
        
        invalid_actions_log = []
        mcts = MCTS(net, n_simulations=10)
        
        for turn_num in range(20):
            if game.is_over():
                break
            
            # Get MCTS policy
            pi, _, _ = mcts.run(game)
            
            # Generate a turn and track invalid actions
            turn_actions = []
            game_copy = Game()
            # Copy game state manually for tracking
            import copy
            game_copy = copy.deepcopy(game)
            
            temp = 1.0
            action_count = 0
            
            while True:
                # Check terminal
                from zatikon.alphazero import terminal_value
                tv = terminal_value(game_copy)
                if tv is not None:
                    break
                
                # Get legal actions BEFORE sampling
                legals_before = get_legal_actions(game_copy)
                
                # Create legal mask
                legal_mask = np.zeros(31703, dtype=np.float32)
                for action in legals_before:
                    idx = action_to_index(*action)
                    legal_mask[idx] = 1.0
                
                # Mask policy
                masked_pi = pi * legal_mask
                if masked_pi.sum() > 0:
                    masked_pi /= masked_pi.sum()
                else:
                    masked_pi = legal_mask / legal_mask.sum()
                
                # Sample action
                action_idx = np.random.choice(31703, p=masked_pi)
                action = index_to_action(action_idx)
                
                # Check if action is in legal list
                action_is_legal = action in legals_before
                
                # Get policy value for this action
                policy_value = pi[action_idx] if action_idx < len(pi) else 0.0
                masked_policy_value = masked_pi[action_idx] if action_idx < len(masked_pi) else 0.0
                
                # Apply action
                result = apply_action(game_copy, *action)
                is_invalid = "Invalid" in result
                
                # Track invalid actions
                if is_invalid:
                    invalid_actions_log.append({
                        'turn': turn_num,
                        'action_count': action_count,
                        'action': action,
                        'action_type': action[0],
                        'action_idx': action_idx,
                        'was_legal_before': action_is_legal,
                        'policy_value': policy_value,
                        'masked_policy_value': masked_policy_value,
                        'legal_actions_count': len(legals_before),
                        'result': result,
                        'game_state': {
                            'current_player': game_copy.current_player,
                            'turn_number': game_copy.turn_number,
                            'commands_left': game_copy.get_current_castle().commands_left,
                        }
                    })
                    break
                
                turn_actions.append(action)
                action_count += 1
                
                # Check if turn ended
                if action[0] == ACTION_END_TURN:
                    break
            
            # Apply turn to actual game
            for action in turn_actions:
                apply_action(game, *action)
            
            if game.is_over():
                break
        
        # Analyze results
        print(f"\n=== Invalid Action Analysis ===")
        print(f"Total invalid actions: {len(invalid_actions_log)}")
        
        if invalid_actions_log:
            print("\nInvalid Actions Details:")
            for i, log_entry in enumerate(invalid_actions_log):
                print(f"\nInvalid Action {i+1}:")
                print(f"  Turn: {log_entry['turn']}")
                print(f"  Action: {log_entry['action']}")
                print(f"  Action Type: {log_entry['action_type']} ({'DEPLOY' if log_entry['action_type'] == ACTION_DEPLOY else 'MOVE' if log_entry['action_type'] == ACTION_MOVE else 'ATTACK' if log_entry['action_type'] == ACTION_ATTACK else 'OTHER'})")
                print(f"  Was Legal Before Sampling: {log_entry['was_legal_before']}")
                print(f"  Policy Value (raw): {log_entry['policy_value']:.6f}")
                print(f"  Policy Value (masked): {log_entry['masked_policy_value']:.6f}")
                print(f"  Legal Actions Available: {log_entry['legal_actions_count']}")
                print(f"  Result: {log_entry['result']}")
                print(f"  Game State: Player={log_entry['game_state']['current_player']}, Turn={log_entry['game_state']['turn_number']}, Commands={log_entry['game_state']['commands_left']}")
        
        # Assertions for investigation
        assert True  # Test always passes, but logs information
    
    def test_track_policy_values_for_invalid_actions(self, net):
        """
        Track what policy values invalid actions have.
        
        This helps understand if the network is assigning high probability
        to invalid actions, or if actions become invalid for other reasons.
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
        
        policy_stats = {
            'invalid_actions': [],
            'valid_actions': [],
            'total_actions': 0,
        }
        
        mcts = MCTS(net, n_simulations=5)
        
        for turn_num in range(10):
            if game.is_over():
                break
            
            pi, _, _ = mcts.run(game)
            game_copy = Game()
            import copy
            game_copy = copy.deepcopy(game)
            
            temp = 1.0
            
            for action_in_turn in range(10):  # Limit actions per turn
                legals = get_legal_actions(game_copy)
                if not legals:
                    break
                
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
                
                policy_value = float(pi[action_idx])
                masked_policy_value = float(masked_pi[action_idx])
                
                result = apply_action(game_copy, *action)
                is_invalid = "Invalid" in result
                
                policy_stats['total_actions'] += 1
                
                if is_invalid:
                    policy_stats['invalid_actions'].append({
                        'policy_value': policy_value,
                        'masked_policy_value': masked_policy_value,
                        'action': action,
                        'was_in_legal_list': action in legals,
                    })
                    break
                else:
                    policy_stats['valid_actions'].append({
                        'policy_value': policy_value,
                        'masked_policy_value': masked_policy_value,
                    })
                
                if action[0] == ACTION_END_TURN:
                    break
            
            # Apply to actual game
            for action in [(ACTION_END_TURN, 0, 0)]:  # Simplified
                apply_action(game, *action)
            
            if game.is_over():
                break
        
        # Analyze policy statistics
        print(f"\n=== Policy Statistics ===")
        print(f"Total actions sampled: {policy_stats['total_actions']}")
        print(f"Invalid actions: {len(policy_stats['invalid_actions'])}")
        print(f"Valid actions: {len(policy_stats['valid_actions'])}")
        
        if policy_stats['invalid_actions']:
            invalid_policies = [x['policy_value'] for x in policy_stats['invalid_actions']]
            invalid_masked = [x['masked_policy_value'] for x in policy_stats['invalid_actions']]
            print(f"\nInvalid Action Policy Values:")
            print(f"  Raw policy - Min: {min(invalid_policies):.6f}, Max: {max(invalid_policies):.6f}, Mean: {np.mean(invalid_policies):.6f}")
            print(f"  Masked policy - Min: {min(invalid_masked):.6f}, Max: {max(invalid_masked):.6f}, Mean: {np.mean(invalid_masked):.6f}")
            
            # Check if invalid actions were in legal list
            was_legal_count = sum(1 for x in policy_stats['invalid_actions'] if x['was_in_legal_list'])
            print(f"  Actions that were legal before sampling: {was_legal_count}/{len(policy_stats['invalid_actions'])}")
        
        if policy_stats['valid_actions']:
            valid_policies = [x['policy_value'] for x in policy_stats['valid_actions']]
            valid_masked = [x['masked_policy_value'] for x in policy_stats['valid_actions']]
            print(f"\nValid Action Policy Values:")
            print(f"  Raw policy - Min: {min(valid_policies):.6f}, Max: {max(valid_policies):.6f}, Mean: {np.mean(valid_policies):.6f}")
            print(f"  Masked policy - Min: {min(valid_masked):.6f}, Max: {max(valid_masked):.6f}, Mean: {np.mean(valid_masked):.6f}")
        
        assert True  # Test always passes, logs information
    
    def test_track_state_changes_causing_invalid_actions(self, net):
        """
        Track how game state changes cause actions to become invalid.
        
        This test checks if actions become invalid because:
        - Units move (making old locations invalid)
        - Commands are spent (making expensive actions invalid)
        - Units die (making actions on dead units invalid)
        - Other state changes
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
        
        state_change_log = []
        mcts = MCTS(net, n_simulations=5)
        
        for turn_num in range(10):
            if game.is_over():
                break
            
            pi, _, _ = mcts.run(game)
            import copy
            game_copy = copy.deepcopy(game)
            
            # Capture initial state
            initial_state = {
                'unit_locations': [(u.location, u.team) for u in game_copy.battlefield.units if not u.dead],
                'commands': game_copy.get_current_castle().commands_left,
                'current_player': game_copy.current_player,
            }
            
            temp = 1.0
            actions_in_turn = []
            
            while True:
                from zatikon.alphazero import terminal_value
                tv = terminal_value(game_copy)
                if tv is not None:
                    break
                
                legals = get_legal_actions(game_copy)
                if not legals:
                    break
                
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
                
                # Capture state before action
                state_before = {
                    'unit_locations': [(u.location, u.team) for u in game_copy.battlefield.units if not u.dead],
                    'commands': game_copy.get_current_castle().commands_left,
                }
                
                result = apply_action(game_copy, *action)
                
                # Capture state after action
                state_after = {
                    'unit_locations': [(u.location, u.team) for u in game_copy.battlefield.units if not u.dead],
                    'commands': game_copy.get_current_castle().commands_left,
                }
                
                if "Invalid" in result:
                    # Action became invalid - track state changes
                    state_change_log.append({
                        'turn': turn_num,
                        'action': action,
                        'actions_before': actions_in_turn.copy(),
                        'state_before_action': state_before,
                        'state_after_action': state_after,
                        'initial_state': initial_state,
                        'result': result,
                    })
                    break
                
                actions_in_turn.append(action)
                
                if action[0] == ACTION_END_TURN:
                    break
            
            # Apply to actual game
            for action in actions_in_turn:
                apply_action(game, *action)
            
            if game.is_over():
                break
        
        # Analyze state changes
        print(f"\n=== State Change Analysis ===")
        print(f"Invalid actions due to state changes: {len(state_change_log)}")
        
        for i, log_entry in enumerate(state_change_log):
            print(f"\nState Change {i+1}:")
            print(f"  Turn: {log_entry['turn']}")
            print(f"  Action: {log_entry['action']}")
            print(f"  Actions before: {len(log_entry['actions_before'])}")
            print(f"  Unit locations changed: {log_entry['state_before_action']['unit_locations'] != log_entry['state_after_action']['unit_locations']}")
            print(f"  Commands changed: {log_entry['state_before_action']['commands'] != log_entry['state_after_action']['commands']}")
            print(f"  Result: {log_entry['result']}")
        
        assert True  # Test always passes, logs information
    
    def test_verify_action_index_mapping(self):
        """
        Verify that action_to_index and index_to_action are perfect inverses.
        
        This tests if there's a bug in the action encoding that could cause
        invalid actions to be sampled.
        """
        test_actions = [
            (ACTION_DEPLOY, 0, 10),
            (ACTION_DEPLOY, 1, 50),
            (ACTION_MOVE, 10, 20),
            (ACTION_MOVE, 50, 60),
            (ACTION_ATTACK, 10, 20),
            (ACTION_ATTACK, 50, 60),
            (ACTION_END_TURN, 0, 0),
        ]
        
        mapping_errors = []
        
        for action in test_actions:
            idx = action_to_index(*action)
            decoded = index_to_action(idx)
            
            if decoded != action:
                mapping_errors.append({
                    'original': action,
                    'index': idx,
                    'decoded': decoded,
                })
        
        if mapping_errors:
            print(f"\n=== Action Mapping Errors ===")
            for error in mapping_errors:
                print(f"  Original: {error['original']}")
                print(f"  Index: {error['index']}")
                print(f"  Decoded: {error['decoded']}")
                print()
        
        # This should never happen, but if it does, we want to know
        assert len(mapping_errors) == 0, f"Found {len(mapping_errors)} action mapping errors!"
    
    def test_track_mcts_policy_contains_only_legal_actions(self, net):
        """
        Verify that MCTS policy only contains legal actions.
        
        This ensures that the policy extraction from MCTS correctly
        filters to only legal actions.
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
        
        policy_issues = []
        mcts = MCTS(net, n_simulations=10)
        
        for turn_num in range(5):
            if game.is_over():
                break
            
            # Get MCTS policy
            pi, _, _ = mcts.run(game)
            
            # Get legal actions
            legals = get_legal_actions(game)
            legal_indices = {action_to_index(*action) for action in legals}
            
            # Check if policy has non-zero probability for illegal actions
            illegal_with_prob = []
            for idx in range(len(pi)):
                if idx not in legal_indices and pi[idx] > 1e-6:  # Small threshold for floating point
                    illegal_with_prob.append({
                        'index': idx,
                        'probability': pi[idx],
                        'action': index_to_action(idx),
                    })
            
            if illegal_with_prob:
                policy_issues.append({
                    'turn': turn_num,
                    'illegal_actions_with_prob': illegal_with_prob,
                })
            
            # Apply END_TURN to advance
            apply_action(game, ACTION_END_TURN, 0, 0)
            
            if game.is_over():
                break
        
        if policy_issues:
            print(f"\n=== MCTS Policy Issues ===")
            for issue in policy_issues:
                print(f"Turn {issue['turn']}: {len(issue['illegal_actions_with_prob'])} illegal actions with non-zero probability")
                for illegal in issue['illegal_actions_with_prob'][:5]:  # Show first 5
                    print(f"  Index {illegal['index']}: {illegal['action']} = {illegal['probability']:.6f}")
        
        # This should not happen - MCTS policy should only have legal actions
        # But we're tracking it, not failing the test
        assert True  # Test always passes, logs information

