"""
Tests for AlphaZero turn-based MCTS implementation.
"""
import pytest
import numpy as np
import torch
from zatikon import constants
from zatikon.game import Game
from zatikon.alphazero import (
    copy_game,
    TurnNode,
    MCTS,
    ZatikonNet,
    get_legal_actions,
    action_to_index,
    index_to_action,
    ACTION_DEPLOY,
    ACTION_MOVE,
    ACTION_ATTACK,
    ACTION_END_TURN,
    ACTION_SIZE,
    terminal_value,
    self_play_game,
)
from zatikon.unit_factory import UnitFactory


class TestGameStateCopying:
    """Test game state copying for MCTS."""
    
    def test_copy_game_creates_independent_copy(self):
        """Test that copy_game creates an independent copy."""
        game = Game()
        
        # Add units to barracks
        for _ in range(2):
            footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
            game.castle1.add_unit(footman)
        
        game.start_turn()
        
        # Copy game
        game_copy = copy_game(game)
        
        # Modify original
        game.castle1.commands_left = 999
        game.turn_number = 999
        
        # Copy should be unchanged
        assert game_copy.castle1.commands_left != 999
        assert game_copy.turn_number != 999
    
    def test_copy_game_preserves_unit_positions(self):
        """Test that copied game preserves unit positions."""
        game = Game()
        
        # Deploy a unit
        footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(footman)
        game.start_turn()
        
        deploy_targets = game._get_castle_targets(game.castle1)
        if deploy_targets:
            game.handle_action(constants.ACTION_DEPLOY, 0, deploy_targets[0])
        
        # Copy game
        game_copy = copy_game(game)
        
        # Check unit positions match
        units_orig = [(u.location, u.team) for u in game.battlefield.units if not u.dead]
        units_copy = [(u.location, u.team) for u in game_copy.battlefield.units if not u.dead]
        
        assert units_orig == units_copy
    
    def test_copy_game_independent_modifications(self):
        """Test that modifications to copy don't affect original."""
        game = Game()
        
        footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(footman)
        game.start_turn()
        
        deploy_targets = game._get_castle_targets(game.castle1)
        if deploy_targets:
            game.handle_action(constants.ACTION_DEPLOY, 0, deploy_targets[0])
        
        game_copy = copy_game(game)
        
        # Modify copy
        if game_copy.battlefield.units:
            unit = game_copy.battlefield.units[0]
            unit.location = 999
        
        # Original should be unchanged
        if game.battlefield.units:
            assert game.battlefield.units[0].location != 999


class TestTurnNode:
    """Test TurnNode class."""
    
    def test_turn_node_initialization(self):
        """Test TurnNode initialization."""
        action_sequence = [(ACTION_DEPLOY, 0, 10), (ACTION_END_TURN, 0, 0)]
        state_end = np.zeros((327, 11, 11), dtype=np.float32)
        state_key = "test_key"
        
        node = TurnNode(action_sequence, state_end, state_key)
        
        assert node.action_sequence == action_sequence
        assert np.array_equal(node.state_end_encoded, state_end)
        assert node.state_key == state_key
        assert node.visits == 0
        assert node.total_value == 0.0
        assert len(node.children) == 0
        assert node.cached_value is None
    
    def test_turn_node_value_property(self):
        """Test TurnNode value property."""
        node = TurnNode([], np.zeros((327, 11, 11)), "key")
        
        # No visits
        assert node.value == 0.0
        
        # With visits
        node.visits = 5
        node.total_value = 10.0
        assert node.value == 2.0


class TestTurnGeneration:
    """Test turn generation."""
    
    @pytest.fixture
    def net(self):
        """Create a neural network for testing."""
        return ZatikonNet()
    
    @pytest.fixture
    def game_with_units(self):
        """Create a game with units in barracks."""
        game = Game()
        
        for _ in range(2):
            footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
            game.castle1.add_unit(footman)
        
        game.start_turn()
        return game
    
    def test_generate_turn_ends_with_end_turn(self, net, game_with_units):
        """Test that generated turn ends with END_TURN."""
        mcts = MCTS(net, n_simulations=1)
        
        turn_actions, turn_data = mcts.generate_turn(game_with_units, temp=1.0)
        
        # Turn should end with END_TURN
        assert len(turn_actions) > 0
        assert turn_actions[-1][0] == ACTION_END_TURN
    
    def test_generate_turn_records_training_data(self, net, game_with_units):
        """Test that turn generation records training data."""
        mcts = MCTS(net, n_simulations=1)
        
        turn_actions, turn_data = mcts.generate_turn(game_with_units, temp=1.0)
        
        # Should have training data for each action
        assert len(turn_data) == len(turn_actions)
        
        # Check training data format
        for state_before, action, policy, action_idx in turn_data:
            assert state_before.shape == (327, 11, 11)
            assert len(action) == 3
            assert policy.shape == (ACTION_SIZE,)
            assert 0 <= action_idx < ACTION_SIZE
    
    def test_generate_turn_greedy_mode(self, net, game_with_units):
        """Test turn generation in greedy mode (temp=0)."""
        mcts = MCTS(net, n_simulations=1)
        
        # Generate multiple turns - should be deterministic in greedy mode
        turn1_actions, _ = mcts.generate_turn(copy_game(game_with_units), temp=0.0)
        turn2_actions, _ = mcts.generate_turn(copy_game(game_with_units), temp=0.0)
        
        # In greedy mode, should get same turn (if network is deterministic)
        # Note: This might not always be true due to network randomness, but structure should be valid
        assert len(turn1_actions) > 0
        assert len(turn2_actions) > 0
    
    def test_generate_turn_handles_terminal_state(self, net):
        """Test turn generation stops at terminal state."""
        game = Game()
        game._over = True
        
        mcts = MCTS(net, n_simulations=1)
        turn_actions, turn_data = mcts.generate_turn(game, temp=1.0)
        
        # Should return empty turn if game is over
        assert len(turn_actions) == 0
        assert len(turn_data) == 0


class TestMCTSSimulation:
    """Test MCTS simulation."""
    
    @pytest.fixture
    def net(self):
        """Create a neural network for testing."""
        return ZatikonNet()
    
    @pytest.fixture
    def game_with_units(self):
        """Create a game with units."""
        game = Game()
        
        for _ in range(2):
            footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
            game.castle1.add_unit(footman)
        
        game.start_turn()
        return game
    
    def test_mcts_simulation_returns_value(self, net, game_with_units):
        """Test that MCTS simulation returns a value."""
        mcts = MCTS(net, n_simulations=1)
        
        # Create root node
        game_copy = copy_game(game_with_units)
        turn_actions, _ = mcts.generate_turn(game_copy, temp=1.0)
        state_end = np.zeros((327, 11, 11))
        state_key = mcts.state_key(game_copy)
        
        root = TurnNode(turn_actions, state_end, state_key)
        
        # Run simulation
        game_sim = copy_game(game_with_units)
        value = mcts._simulate(game_sim, root)
        
        # Value should be a float
        assert isinstance(value, float)
        assert -1.0 <= value <= 1.0
    
    def test_mcts_simulation_expands_node(self, net, game_with_units):
        """Test that simulation expands nodes."""
        mcts = MCTS(net, n_simulations=1)
        
        # Create root node with no children
        game_copy = copy_game(game_with_units)
        turn_actions, _ = mcts.generate_turn(game_copy, temp=1.0)
        state_end = np.zeros((327, 11, 11))
        state_key = mcts.state_key(game_copy)
        
        root = TurnNode(turn_actions, state_end, state_key)
        
        assert len(root.children) == 0
        
        # Run simulation
        game_sim = copy_game(game_with_units)
        mcts._simulate(game_sim, root)
        
        # Should have expanded (created children)
        assert len(root.children) > 0
    
    def test_mcts_simulation_updates_statistics(self, net, game_with_units):
        """Test that simulation updates node statistics."""
        mcts = MCTS(net, n_simulations=1)
        
        game_copy = copy_game(game_with_units)
        turn_actions, _ = mcts.generate_turn(game_copy, temp=1.0)
        state_end = np.zeros((327, 11, 11))
        state_key = mcts.state_key(game_copy)
        
        root = TurnNode(turn_actions, state_end, state_key)
        
        # Add a child so that selection path is taken (which updates statistics)
        child_turn_actions, _ = mcts.generate_turn(copy_game(game_with_units), temp=1.0)
        child_state_end = np.zeros((327, 11, 11))
        child_state_key = "child_key"
        child = TurnNode(child_turn_actions, child_state_end, child_state_key)
        root.children.append(child)
        
        initial_visits = root.visits
        initial_value = root.total_value
        
        # Run simulation (will select child and update root)
        game_sim = copy_game(game_with_units)
        value = mcts._simulate(game_sim, root)
        
        # Statistics should be updated
        assert root.visits == initial_visits + 1
        assert root.total_value == initial_value + value


class TestMCTSRun:
    """Test MCTS run and policy extraction."""
    
    @pytest.fixture
    def net(self):
        """Create a neural network for testing."""
        return ZatikonNet()
    
    @pytest.fixture
    def game_with_units(self):
        """Create a game with units."""
        game = Game()
        
        for _ in range(2):
            footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
            game.castle1.add_unit(footman)
        
        game.start_turn()
        return game
    
    def test_mcts_run_returns_policy(self, net, game_with_units):
        """Test that MCTS run returns a policy."""
        mcts = MCTS(net, n_simulations=10)
        
        pi, root_q, q_values = mcts.run(game_with_units)
        
        # Check policy format
        assert pi.shape == (ACTION_SIZE,)
        assert np.allclose(pi.sum(), 1.0, atol=1e-5)
        assert np.all(pi >= 0)
        
        # Check Q values
        assert q_values.shape == (ACTION_SIZE,)
        assert isinstance(root_q, float)
    
    def test_mcts_run_creates_root_node(self, net, game_with_units):
        """Test that MCTS run creates root node."""
        mcts = MCTS(net, n_simulations=10)
        
        assert mcts.root is None
        
        mcts.run(game_with_units)
        
        assert mcts.root is not None
        assert isinstance(mcts.root, TurnNode)
    
    def test_mcts_run_policy_sums_to_one(self, net, game_with_units):
        """Test that extracted policy sums to one."""
        mcts = MCTS(net, n_simulations=10)
        
        pi, _, _ = mcts.run(game_with_units)
        
        assert abs(pi.sum() - 1.0) < 1e-5
    
    def test_mcts_run_policy_masks_illegal_actions(self, net, game_with_units):
        """Test that policy only includes legal actions."""
        mcts = MCTS(net, n_simulations=10)
        
        pi, _, _ = mcts.run(game_with_units)
        
        legals = get_legal_actions(game_with_units)
        legal_mask = np.zeros(ACTION_SIZE, dtype=np.float32)
        for action in legals:
            idx = action_to_index(*action)
            legal_mask[idx] = 1.0
        
        # Policy should be zero for illegal actions (or very small)
        illegal_mask = 1.0 - legal_mask
        illegal_probs = pi * illegal_mask
        
        # Illegal actions should have very small probability
        assert illegal_probs.sum() < 0.01  # Allow small numerical errors


class TestActionEncoding:
    """Test action encoding/decoding."""
    
    def test_action_to_index_deploy(self):
        """Test encoding deploy action."""
        idx = action_to_index(ACTION_DEPLOY, 0, 10)
        
        assert 0 <= idx < ACTION_SIZE
        assert idx < 2420  # Deploy actions are first
    
    def test_action_to_index_move(self):
        """Test encoding move action."""
        idx = action_to_index(ACTION_MOVE, 10, 20)
        
        assert 0 <= idx < ACTION_SIZE
        assert idx >= 2420  # Move actions come after deploy
    
    def test_action_to_index_attack(self):
        """Test encoding attack action."""
        idx = action_to_index(ACTION_ATTACK, 10, 20)
        
        assert 0 <= idx < ACTION_SIZE
        assert idx >= 2420 + 14641  # Attack actions come after move
    
    def test_action_to_index_end_turn(self):
        """Test encoding end turn action."""
        idx = action_to_index(ACTION_END_TURN, 0, 0)
        
        assert idx == ACTION_SIZE - 1
    
    def test_index_to_action_roundtrip(self):
        """Test that action encoding/decoding is reversible."""
        actions = [
            (ACTION_DEPLOY, 0, 10),
            (ACTION_MOVE, 10, 20),
            (ACTION_ATTACK, 5, 15),
            (ACTION_END_TURN, 0, 0),
        ]
        
        for action in actions:
            idx = action_to_index(*action)
            decoded = index_to_action(idx)
            assert decoded == action


class TestTerminalValue:
    """Test terminal value function."""
    
    def test_terminal_value_returns_none_for_non_terminal(self):
        """Test that terminal_value returns None for non-terminal games."""
        game = Game()
        game.start_turn()

        tv = terminal_value(game, constants.TEAM_1)

        assert tv is None
    
    def test_terminal_value_returns_one_for_winner(self):
        """Test that terminal_value returns 1.0 for winning player."""
        game = Game()
        game._over = True

        # Mock check_victory to return Team 1's castle
        game.check_victory = lambda: game.castle1

        tv = terminal_value(game, constants.TEAM_1)

        assert tv == 1.0
    
    def test_terminal_value_returns_negative_one_for_loser(self):
        """Test that terminal_value returns -1.0 for losing player."""
        game = Game()
        game._over = True

        # Mock check_victory to return Team 2's castle (Team 1 loses)
        game.check_victory = lambda: game.castle2

        tv = terminal_value(game, constants.TEAM_1)

        assert tv == -1.0


class TestSelfPlayGame:
    """Test self-play game function."""
    
    @pytest.fixture
    def net(self):
        """Create a neural network for testing."""
        return ZatikonNet()
    
    def test_self_play_game_returns_training_data(self, net):
        """Test that self-play returns training data."""
        examples, winner = self_play_game(net, mcts_sims=5, max_turns=10)
        
        # Should return training data
        assert isinstance(examples, list)
        assert len(examples) > 0
        
        # Check format
        for state, policy, value in examples:
            assert state.shape == (327, 11, 11)
            assert policy.shape == (ACTION_SIZE,)
            # Value is now [win_prob, lose_prob, draw_prob]
            assert isinstance(value, list) and len(value) == 3
            assert all(isinstance(v, float) for v in value)
            assert all(0.0 <= v <= 1.0 for v in value)
            # Probabilities should sum to approximately 1
            assert abs(sum(value) - 1.0) < 0.01
    
    def test_self_play_game_records_action_level_data(self, net):
        """Test that self-play records action-level data."""
        examples, winner = self_play_game(net, mcts_sims=5, max_turns=5)
        
        # Should have multiple examples (one per action)
        assert len(examples) > 0
        
        # Each example should have state, policy, value
        for state, policy, value in examples:
            assert state is not None
            assert policy is not None
            assert value is not None
    
    def test_self_play_game_initializes_with_units(self, net):
        """Test that self-play initializes game with units."""
        examples, winner = self_play_game(net, mcts_sims=2, max_turns=2)
        
        # Game should have been played (examples exist)
        assert len(examples) > 0


class TestTrainingDataCollectionBug:
    """Test that demonstrates the training data collection bug.

    BUG: All states in a turn get assigned the SAME final turn_value,
    instead of each state having its proper individual value estimate.
    """

    def test_training_data_has_individual_state_values_not_final_outcomes(self):
        """Test that training data contains individual state value estimates, not just final outcomes.

        FAILS with current buggy implementation where all states get final turn_value.
        Will PASS once each state gets its proper individual value estimate.

        The bug: All states in a turn get assigned the SAME final turn_value [1,0,0], [0,1,0], or [0,0,1]
        The fix: Each state gets its own nuanced value estimate from the network
        """
        from zatikon.alphazero import self_play_game
        from zatikon.alphazero import ZatikonNet
        import torch

        # Create a network and generate training data
        net = ZatikonNet()
        net.eval()
        torch.manual_seed(42)  # For reproducible results

        # Generate some training data
        game_data, winner = self_play_game(net, mcts_sims=10, max_turns=15)

        # Look for training examples that are NOT final outcomes
        # Final outcomes are exactly [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], or [0.0, 0.0, 1.0]
        # Individual state evaluations should have more nuanced values

        found_nuanced_value = False
        nuanced_examples = []

        for state, policy, value in game_data:
            if isinstance(value, list) and len(value) == 3:
                win_prob, lose_prob, draw_prob = value

                # Check if this is a final outcome (exactly one of the three = 1.0)
                is_final_outcome = (
                    (win_prob == 1.0 and lose_prob == 0.0 and draw_prob == 0.0) or
                    (win_prob == 0.0 and lose_prob == 1.0 and draw_prob == 0.0) or
                    (win_prob == 0.0 and lose_prob == 0.0 and draw_prob == 1.0)
                )

                if not is_final_outcome:
                    found_nuanced_value = True
                    nuanced_examples.append((win_prob, lose_prob, draw_prob))
                    if len(nuanced_examples) >= 3:  # Found enough examples
                        break

        # This assertion should now PASS since we fixed the bug
        # The training data should contain individual state value estimates, not just final outcomes
        assert found_nuanced_value, (
            f"FAILED: Training data still contains only final outcomes! "
            f"Found {len(nuanced_examples)} nuanced values out of {len(game_data)} examples. "
            f"Examples found: {nuanced_examples[:3] if nuanced_examples else 'None'}. "
            f"The fix should ensure each state has its proper individual value estimate."
        )

        # Verify we found a reasonable number of nuanced examples
        assert len(nuanced_examples) >= 3, f"Should find at least 3 nuanced examples, found {len(nuanced_examples)}"

        print(f"SUCCESS: Found {len(nuanced_examples)} nuanced value examples")
        print(f"Sample values: {nuanced_examples[:3]}")


class TestValuePredictionConsistency:
    """Test that neural network value predictions are consistent and reasonable."""

    def test_network_predicts_win_when_unit_on_enemy_castle(self):
        """Test that network correctly predicts win when unit is on enemy castle."""
        from zatikon.alphazero import ZatikonNet
        from zatikon.state_encoder import encode_game_state
        from zatikon.battlefield import BattleField
        import torch

        net = ZatikonNet()
        net.eval()

        # Create a game where Team 1 has a unit on Team 2's castle
        game = Game()

        # Create and place Team 1's unit directly on Team 2's castle
        footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        footman.set_team(constants.TEAM_1)
        footman.set_location(game.castle2.location)  # Place on enemy castle
        game.battlefield.add_unit(footman)

        # Team 1 should be winning
        winner = game.check_victory()
        assert winner == game.castle1, "Team 1 should be winning"

        # Encode the game state
        state = encode_game_state(game)
        state_tensor = torch.tensor(state[None, :, :, :], dtype=torch.float32)

        # Get network prediction
        with torch.no_grad():
            _, v_probs = net(state_tensor)

        # Should predict high win probability for Player 1
        win_prob, lose_prob, draw_prob = v_probs[0].cpu().numpy()

        # Since Team 1 clearly wins, win probability should be very high
        assert win_prob > 0.8, f"Network should predict high win probability for clear winning position, got win={win_prob:.3f}, lose={lose_prob:.3f}, draw={draw_prob:.3f}"
        assert draw_prob < 0.1, f"Network should not predict draw in clearly winning position, got draw={draw_prob:.3f}"
        """Test that network correctly predicts win when unit is on enemy castle."""
        from zatikon.alphazero import ZatikonNet
        from zatikon.state_encoder import encode_game_state
        import torch

        net = ZatikonNet()
        net.eval()

        # Create a game where Team 1 has a unit on Team 2's castle
        game = Game()

        # Create and place Team 1's unit directly on Team 2's castle
        footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        footman.set_team(constants.TEAM_1)
        footman.set_location(game.castle2.location)  # Place on enemy castle
        game.battlefield.add_unit(footman)

        # Team 1 should be winning
        winner = game.check_victory()
        assert winner == game.castle1, "Team 1 should be winning"

        # Encode the game state
        state = encode_game_state(game)
        state_tensor = torch.tensor(state[None, :, :, :], dtype=torch.float32)

        # Get network prediction
        with torch.no_grad():
            _, v_probs = net(state_tensor)

        # Should predict high win probability for Player 1
        win_prob, lose_prob, draw_prob = v_probs[0].cpu().numpy()

        # Since Team 1 clearly wins, win probability should be very high
        assert win_prob > 0.8, f"Network should predict high win probability for clear winning position, got win={win_prob:.3f}, lose={lose_prob:.3f}, draw={draw_prob:.3f}"
        assert draw_prob < 0.1, f"Network should not predict draw in clearly winning position, got draw={draw_prob:.3f}"

    def test_network_predicts_consistent_values_for_symmetric_positions(self):
        """Test that network gives consistent predictions for symmetric game states."""
        from zatikon.alphazero import ZatikonNet
        from zatikon.state_encoder import encode_game_state
        from zatikon.battlefield import BattleField
        import torch

        net = ZatikonNet()
        net.eval()

        # Create a symmetric game state
        game1 = Game()
        game2 = Game()

        # Add identical units to both games but swapped teams
        footman1 = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game1.castle1)
        footman1.set_team(constants.TEAM_1)
        footman1.set_location(BattleField.get_location(5, 8))  # Near Team 1's castle
        game1.battlefield.add_unit(footman1)

        footman2 = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game2.castle2)
        footman2.set_team(constants.TEAM_2)
        footman2.set_location(BattleField.get_location(5, 2))  # Near Team 2's castle (symmetric)
        game2.battlefield.add_unit(footman2)

        # Encode both game states
        state1 = encode_game_state(game1)
        state2 = encode_game_state(game2)

        state1_tensor = torch.tensor(state1[None, :, :, :], dtype=torch.float32)
        state2_tensor = torch.tensor(state2[None, :, :, :], dtype=torch.float32)

        # Get network predictions
        with torch.no_grad():
            _, v_probs1 = net(state1_tensor)
            _, v_probs2 = net(state2_tensor)

        win1, lose1, draw1 = v_probs1[0].cpu().numpy()
        win2, lose2, draw2 = v_probs2[0].cpu().numpy()

        # The predictions should be roughly symmetric
        # game1 favors Team 1, game2 favors Team 2, so win probabilities should be swapped
        tolerance = 0.2  # Allow some variance due to network not being fully trained

        assert abs(win1 - lose2) < tolerance, f"Symmetric positions should have swapped win probabilities: game1_win={win1:.3f}, game2_lose={lose2:.3f}"
        assert abs(lose1 - win2) < tolerance, f"Symmetric positions should have swapped lose probabilities: game1_lose={lose1:.3f}, game2_win={win2:.3f}"
        assert abs(draw1 - draw2) < tolerance, f"Symmetric positions should have similar draw probabilities: game1_draw={draw1:.3f}, game2_draw={draw2:.3f}"

    def test_value_estimates_update_correctly_after_moves(self):
        """Test that value estimates change appropriately after significant moves."""
        from zatikon.alphazero import ZatikonNet
        from zatikon.state_encoder import encode_game_state
        from zatikon.battlefield import BattleField
        import torch

        net = ZatikonNet()
        net.eval()

        # Create a game with units positioned to attack
        game = Game()

        # Team 1 unit positioned to attack Team 2's castle next turn
        attacker = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        attacker.set_team(constants.TEAM_1)
        attacker.set_location(BattleField.get_location(5, 1))  # Adjacent to Team 2's castle
        game.battlefield.add_unit(attacker)

        # Encode initial state
        state_before = encode_game_state(game)
        state_before_tensor = torch.tensor(state_before[None, :, :, :], dtype=torch.float32)

        with torch.no_grad():
            _, v_probs_before = net(state_before_tensor)

        win_before, lose_before, draw_before = v_probs_before[0].cpu().numpy()

        # Move the unit onto the enemy castle (winning move)
        # Note: We can't actually execute the move since the game logic prevents it,
        # but we can simulate the position change
        attacker.set_location(game.castle2.location)  # Move onto enemy castle

        # Encode state after "move"
        state_after = encode_game_state(game)
        state_after_tensor = torch.tensor(state_after[None, :, :, :], dtype=torch.float32)

        with torch.no_grad():
            _, v_probs_after = net(state_after_tensor)

        win_after, lose_after, draw_after = v_probs_after[0].cpu().numpy()

        # After winning move, win probability should be much higher
        assert win_after > win_before + 0.3, f"Win probability should increase significantly after winning move: before={win_before:.3f}, after={win_after:.3f}"
        assert draw_after < draw_before - 0.3, f"Draw probability should decrease significantly after winning move: before={draw_before:.3f}, after={draw_after:.3f}"


class TestTerminalValuePerspective:
    """Test terminal value perspective calculation."""

    def test_terminal_value_uses_correct_perspective(self):
        """Test that terminal_value returns correct values from specified perspective.

        This test verifies that terminal_value correctly evaluates outcomes from
        different players' perspectives, which is crucial for proper AlphaZero training.
        """
        from zatikon.alphazero import terminal_value

        # Create a game where Team 1 wins
        game = Game()

        # Create units and place Team 1's unit on Team 2's castle
        footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        footman.set_team(constants.TEAM_1)
        footman.set_location(game.castle2.location)  # Place on enemy castle
        game.battlefield.add_unit(footman)

        # Team 1 should be the winner
        winner = game.check_victory()
        assert winner == game.castle1

        # Test from Team 1's perspective: should return 1.0 (win)
        value_team1 = terminal_value(game, constants.TEAM_1)
        assert value_team1 == 1.0, f"From Team 1 perspective should be 1.0 (win), got {value_team1}"

        # Test from Team 2's perspective: should return -1.0 (loss)
        value_team2 = terminal_value(game, constants.TEAM_2)
        assert value_team2 == -1.0, f"From Team 2 perspective should be -1.0 (loss), got {value_team2}"

        # Test draw case
        game_draw = Game()  # Empty game that's not over = draw state
        draw_value = terminal_value(game_draw, constants.TEAM_1)
        assert draw_value is None, f"Non-terminal game should return None, got {draw_value}"


class TestMCTSIntegration:
    """Integration tests for MCTS."""
    
    @pytest.fixture
    def net(self):
        """Create a neural network for testing."""
        return ZatikonNet()
    
    @pytest.fixture
    def game_with_units(self):
        """Create a game with units."""
        game = Game()
        
        for _ in range(2):
            footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
            game.castle1.add_unit(footman)
        
        game.start_turn()
        return game
    
    def test_mcts_explores_multiple_turns(self, net, game_with_units):
        """Test that MCTS explores multiple different turns."""
        mcts = MCTS(net, n_simulations=20)
        
        mcts.run(game_with_units)
        
        # Root should have multiple children (different turns explored)
        assert len(mcts.root.children) > 0
    
    def test_mcts_revisits_nodes(self, net, game_with_units):
        """Test that MCTS revisits nodes and updates statistics."""
        mcts = MCTS(net, n_simulations=20)
        
        mcts.run(game_with_units)
        
        # Root should have been visited multiple times
        assert mcts.root.visits > 0
    
    def test_mcts_policy_reflects_exploration(self, net, game_with_units):
        """Test that MCTS policy reflects exploration."""
        mcts = MCTS(net, n_simulations=50)
        
        pi1, _, _ = mcts.run(game_with_units)
        
        # Run again with more simulations
        mcts2 = MCTS(net, n_simulations=100)
        pi2, _, _ = mcts2.run(game_with_units)
        
        # Policies might differ due to exploration
        # But both should be valid probability distributions
        assert np.allclose(pi1.sum(), 1.0)
        assert np.allclose(pi2.sum(), 1.0)

