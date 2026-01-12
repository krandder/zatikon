"""
Tests for RandomAI - AI that makes random valid moves.
"""
import pytest
from zatikon import constants
from zatikon.game import Game
from zatikon.random_ai import RandomAI
from zatikon.unit_factory import UnitFactory


class TestRandomAIInitialization:
    """Test RandomAI initialization."""

    def test_ai_initializes_with_game(self):
        """Test AI initializes with a game."""
        game = Game()
        ai = RandomAI(game)
        
        assert ai.game == game

    def test_ai_has_max_moves_per_turn(self):
        """Test AI has max moves per turn setting."""
        game = Game()
        ai = RandomAI(game)
        
        assert ai.max_moves_per_turn > 0


class TestRandomAIMoves:
    """Test RandomAI move generation."""

    def test_ai_can_deploy_unit(self):
        """Test AI can deploy a unit from barracks."""
        game = Game()
        
        # Add unit to barracks
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(unit)
        
        ai = RandomAI(game)
        move = ai.get_random_deploy_move()
        
        assert move is not None
        assert move['action'] == constants.ACTION_DEPLOY
        assert 'barracks_index' in move
        assert 'location' in move

    def test_ai_deploy_move_is_valid(self):
        """Test AI deploy move is valid."""
        game = Game()
        
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(unit)
        
        ai = RandomAI(game)
        move = ai.get_random_deploy_move()
        
        if move:
            # Should be able to execute the move
            result = game.handle_action(move['action'], move['barracks_index'], move['location'])
            assert "Invalid" not in result or "deployed" in result.lower()

    def test_ai_can_get_unit_move(self):
        """Test AI can get a move for a deployed unit."""
        game = Game()
        
        # Get valid deployment location
        targets = game._get_castle_targets(game.castle1)
        assert len(targets) > 0
        
        # Deploy a unit
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(unit)
        deploy_location = targets[0]
        game.handle_action(constants.ACTION_DEPLOY, 0, deploy_location)
        
        # End turn to activate unit
        game.end_turn()
        game.end_turn()
        
        ai = RandomAI(game)
        move = ai.get_random_unit_move(deploy_location)  # Unit at deployment location
        
        assert move is not None
        assert move['action'] in [constants.ACTION_MOVE, constants.ACTION_ATTACK]
        assert 'from_location' in move
        assert 'to_location' in move

    def test_ai_returns_none_when_no_valid_moves(self):
        """Test AI returns None when no valid moves available."""
        game = Game()
        ai = RandomAI(game)
        
        # No units in barracks
        move = ai.get_random_deploy_move()
        # Should return None or empty dict when no moves available
        assert move is None or move == {}

    def test_ai_can_get_all_valid_moves(self):
        """Test AI can get all valid moves for current turn."""
        game = Game()
        
        # Add units to barracks
        for _ in range(2):
            unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
            game.castle1.add_unit(unit)
        
        ai = RandomAI(game)
        moves = ai.get_all_valid_moves()
        
        assert len(moves) > 0
        # Should have deploy moves
        deploy_moves = [m for m in moves if m['action'] == constants.ACTION_DEPLOY]
        assert len(deploy_moves) > 0


class TestRandomAITurnExecution:
    """Test RandomAI turn execution."""

    def test_ai_can_execute_turn(self):
        """Test AI can execute a full turn."""
        game = Game()
        
        # Add units to both castles
        for _ in range(2):
            unit1 = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
            game.castle1.add_unit(unit1)
            unit2 = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle2)
            game.castle2.add_unit(unit2)
        
        ai1 = RandomAI(game)
        ai2 = RandomAI(game)
        
        initial_turn = game.turn_number
        
        # Execute AI turn
        commands = ai1.execute_turn()
        
        # Should return list of commands
        assert isinstance(commands, list)
        
        # Turn should have progressed or commands used
        assert game.turn_number > initial_turn or game.castle1.commands_left < constants.MAX_COMMANDS

    def test_ai_ends_turn_eventually(self):
        """Test AI eventually ends turn."""
        game = Game()
        
        # Add some units
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(unit)
        
        ai = RandomAI(game)
        
        # Execute turn (should end eventually)
        commands = ai.execute_turn()
        
        # Should return list of commands
        assert isinstance(commands, list)
        
        # Game should still be valid state
        assert not game.is_over() or game.check_victory() is not None

    def test_ai_respects_command_limit(self):
        """Test AI respects command limit."""
        game = Game()
        
        # Add many units
        for _ in range(10):
            unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
            game.castle1.add_unit(unit)
        
        ai = RandomAI(game)
        initial_commands = game.castle1.commands_left
        
        ai.execute_turn()
        
        # Commands should be used but not go negative
        assert game.castle1.commands_left >= 0
        assert game.castle1.commands_left <= initial_commands

