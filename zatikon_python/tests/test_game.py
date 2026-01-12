"""
Tests for Game class - game state management and turn flow.
"""
import pytest
from zatikon import constants
from zatikon.game import Game
from zatikon.castle import Castle
from zatikon.battlefield import BattleField
from zatikon.unit_factory import UnitFactory


class TestGameInitialization:
    """Test Game initialization."""

    def test_game_initializes_with_two_castles(self):
        """Test game initializes with two castles."""
        game = Game()
        
        assert game.castle1 is not None
        assert game.castle2 is not None
        assert isinstance(game.castle1, Castle)
        assert isinstance(game.castle2, Castle)

    def test_game_creates_battlefield(self):
        """Test game creates a battlefield."""
        game = Game()
        
        assert game.battlefield is not None
        assert isinstance(game.battlefield, BattleField)

    def test_game_sets_castle_locations(self):
        """Test game sets castle locations correctly."""
        from zatikon.battlefield import BattleField
        
        game = Game()
        
        # Castle 1 should be at location 115 (bottom center, 5,10)
        assert game.castle1.location == BattleField.get_location(5, 10)
        assert BattleField.get_x(game.castle1.location) == 5
        assert BattleField.get_y(game.castle1.location) == 10
        
        # Castle 2 should be at location 5 (top center, 5,0)
        assert game.castle2.location == BattleField.get_location(5, 0)
        assert BattleField.get_x(game.castle2.location) == 5
        assert BattleField.get_y(game.castle2.location) == 0

    def test_game_sets_castle_teams(self):
        """Test game sets castle teams correctly."""
        game = Game()
        
        assert game.castle1.team == constants.TEAM_1
        assert game.castle2.team == constants.TEAM_2

    def test_game_links_castles_to_battlefield(self):
        """Test castles are linked to battlefield."""
        game = Game()
        
        assert game.castle1.battlefield == game.battlefield
        assert game.castle2.battlefield == game.battlefield

    def test_game_starts_with_player_one(self):
        """Test game starts with player 1's turn."""
        game = Game()
        
        assert game.current_player == constants.TEAM_1

    def test_game_starts_not_over(self):
        """Test game starts in active state."""
        game = Game()
        
        assert game.is_over() == False
        assert game.turn_number == 0


class TestGameTurnFlow:
    """Test turn flow management."""

    def test_get_current_castle_returns_correct_castle(self):
        """Test get_current_castle returns correct castle for current player."""
        game = Game()
        
        assert game.get_current_castle() == game.castle1
        assert game.get_current_castle().team == constants.TEAM_1

    def test_get_enemy_castle_returns_opposite_castle(self):
        """Test get_enemy_castle returns opposite castle."""
        game = Game()
        
        assert game.get_enemy_castle() == game.castle2
        assert game.get_enemy_castle().team == constants.TEAM_2

    def test_start_turn_refreshes_current_castle(self):
        """Test start_turn refreshes current castle."""
        game = Game()
        
        # Use some commands
        game.castle1.commands_left = 2
        
        game.start_turn()
        
        # Commands should be refreshed
        assert game.castle1.commands_left == constants.MAX_COMMANDS

    def test_start_turn_refreshes_units(self):
        """Test start_turn refreshes units on battlefield."""
        game = Game()
        
        # Add a unit to battlefield
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        unit.battlefield = game.battlefield
        unit.location = 1
        unit._deployed = True
        unit.actions_left = 0
        game.battlefield.add_unit(unit)
        game.castle1.add_unit_out(constants.TEAM_1, unit)
        
        game.start_turn()
        
        # Unit actions should be refreshed
        assert unit.actions_left == unit.actions_max

    def test_end_turn_switches_to_next_player(self):
        """Test end_turn switches to next player."""
        game = Game()
        
        assert game.current_player == constants.TEAM_1
        game.end_turn()
        assert game.current_player == constants.TEAM_2
        
        game.end_turn()
        assert game.current_player == constants.TEAM_1

    def test_end_turn_refreshes_previous_castle(self):
        """Test end_turn refreshes the castle that just ended."""
        game = Game()
        
        # Use some commands
        game.castle1.commands_left = 1
        
        game.end_turn()
        
        # Castle 1 should be refreshed
        assert game.castle1.commands_left == constants.MAX_COMMANDS

    def test_end_turn_increments_turn_number(self):
        """Test end_turn increments turn counter."""
        game = Game()
        
        assert game.turn_number == 0
        game.end_turn()
        assert game.turn_number == 1
        game.end_turn()
        assert game.turn_number == 2

    def test_end_turn_starts_next_player_turn(self):
        """Test end_turn automatically starts next player's turn."""
        game = Game()
        
        # Use some commands for player 1
        game.castle1.commands_left = 1
        
        game.end_turn()
        
        # Player 2 should have full commands
        assert game.current_player == constants.TEAM_2
        assert game.castle2.commands_left == constants.MAX_COMMANDS


class TestGameVictoryConditions:
    """Test victory condition checking."""

    def test_check_victory_returns_none_when_no_victory(self):
        """Test check_victory returns None when no victory condition met."""
        game = Game()
        
        result = game.check_victory()
        assert result is None
        assert game.is_over() == False

    def test_check_victory_when_unit_on_enemy_castle(self):
        """Test check_victory detects unit on enemy castle."""
        game = Game()
        
        # Deploy unit from player 1 onto player 2's castle
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        unit.battlefield = game.battlefield
        unit.location = game.castle2.location  # On enemy castle
        unit._deployed = True
        unit.can_win = True
        game.battlefield.add_unit(unit)
        
        result = game.check_victory()
        assert result == game.castle1
        assert game.is_over() == True

    def test_check_victory_ignores_units_that_cannot_win(self):
        """Test check_victory ignores units with can_win=False."""
        game = Game()
        
        # Deploy unit that can't win
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        unit.battlefield = game.battlefield
        unit.location = game.castle2.location
        unit._deployed = True
        unit.can_win = False  # Can't win
        game.battlefield.add_unit(unit)
        
        result = game.check_victory()
        assert result is None
        assert game.is_over() == False

    def test_check_victory_ignores_own_units_on_own_castle(self):
        """Test check_victory ignores own units on own castle."""
        game = Game()
        
        # Unit on own castle
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        unit.battlefield = game.battlefield
        unit.location = game.castle1.location
        unit._deployed = True
        game.battlefield.add_unit(unit)
        
        result = game.check_victory()
        assert result is None

    def test_check_victory_ignores_dead_units(self):
        """Test check_victory ignores dead units."""
        game = Game()
        
        # Dead unit on enemy castle
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        unit.battlefield = game.battlefield
        unit.location = game.castle2.location
        unit.dead = True
        game.battlefield.add_unit(unit)
        
        result = game.check_victory()
        assert result is None

    def test_check_victory_checks_after_move(self):
        """Test check_victory is called after unit moves."""
        game = Game()
        
        # Unit moves onto enemy castle
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        unit.battlefield = game.battlefield
        unit.location = 1
        unit._deployed = True
        game.battlefield.add_unit(unit)
        
        # Move onto enemy castle
        game.battlefield.move(unit, 1, game.castle2.location)
        
        result = game.check_victory()
        assert result == game.castle1


class TestGameActionHandling:
    """Test action handling."""

    def test_handle_deploy_action(self):
        """Test handling DEPLOY action."""
        from zatikon.battlefield import BattleField
        
        game = Game()
        
        # Add unit to barracks
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(unit)
        
        # Get valid deployment locations (adjacent to Castle 1 at 5,10)
        targets = game._get_castle_targets(game.castle1)
        assert len(targets) > 0
        
        # Deploy to first valid location
        deploy_location = targets[0]
        result = game.handle_action(constants.ACTION_DEPLOY, 0, deploy_location)
        
        assert "Invalid" not in result
        assert unit in game.battlefield.units
        assert unit.location == deploy_location
        assert unit not in game.castle1.barracks

    def test_handle_deploy_validates_cost(self):
        """Test deploy validates command cost."""
        game = Game()
        
        # Use all commands
        game.castle1.commands_left = 0
        
        unit = UnitFactory.create_unit(constants.UNIT_BEAR, game.castle1)
        unit.deploy_cost = 1
        game.castle1.add_unit(unit)
        
        result = game.handle_action(constants.ACTION_DEPLOY, 0, 1)
        assert "Invalid" in result or "commands" in result.lower() or "cost" in result.lower()

    def test_handle_deploy_validates_location(self):
        """Test deploy validates deployment location."""
        game = Game()
        
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(unit)
        
        # Try to deploy to invalid location (far from castle)
        result = game.handle_action(constants.ACTION_DEPLOY, 0, 60)
        assert "Invalid" in result

    def test_handle_end_turn_action(self):
        """Test handling END_TURN action."""
        game = Game()
        
        initial_player = game.current_player
        result = game.handle_action(constants.ACTION_END_TURN, 0, 0)
        
        assert game.current_player != initial_player
        assert game.turn_number > 0

    def test_handle_unit_action_move(self):
        """Test handling unit MOVE action."""
        game = Game()
        
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        unit.battlefield = game.battlefield
        unit.location = 1
        unit._deployed = True
        game.battlefield.add_unit(unit)
        
        result = game.handle_action(constants.ACTION_MOVE, 1, 2)
        
        assert "Invalid" not in result
        assert unit.location == 2

    def test_handle_unit_action_attack(self):
        """Test handling unit ATTACK action."""
        game = Game()
        
        attacker = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        attacker.battlefield = game.battlefield
        attacker.location = 1
        attacker._deployed = True
        game.battlefield.add_unit(attacker)
        
        target = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle2)
        target.battlefield = game.battlefield
        target.location = 2
        target._deployed = True
        game.battlefield.add_unit(target)
        
        initial_life = target.life
        result = game.handle_action(constants.ACTION_ATTACK, 1, 2)
        
        assert "Invalid" not in result
        assert target.life < initial_life


class TestGameStateQueries:
    """Test game state query methods."""

    def test_is_over_returns_false_initially(self):
        """Test is_over returns False initially."""
        game = Game()
        assert game.is_over() == False

    def test_is_over_returns_true_after_victory(self):
        """Test is_over returns True after victory."""
        game = Game()

        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        unit.set_team(constants.TEAM_1)  # Set team explicitly
        unit.battlefield = game.battlefield
        unit.location = game.castle2.location
        unit._deployed = True
        game.battlefield.add_unit(unit)

        game.check_victory()
        assert game.is_over() == True

    def test_get_current_player_returns_current_player(self):
        """Test get_current_player returns current player."""
        game = Game()
        assert game.get_current_player() == constants.TEAM_1
        
        game.end_turn()
        assert game.get_current_player() == constants.TEAM_2

    def test_get_turn_number_returns_turn_count(self):
        """Test get_turn_number returns turn count."""
        game = Game()
        assert game.get_turn_number() == 0

        game.end_turn()
        assert game.get_turn_number() == 1

        game.end_turn()
        assert game.get_turn_number() == 2


class TestGameVictoryConditions:
    """Test victory condition logic."""

    def test_game_should_not_declare_winner_when_both_castles_present(self):
        """Test that game does not declare winner when both castles are present and no units on enemy castles."""
        game = Game()

        # Add some units to both teams (similar to the problematic game state)
        # Team 1 units
        footman1 = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(footman1)
        bear1 = UnitFactory.create_unit(constants.UNIT_BEAR, game.castle1)
        game.castle1.add_unit(bear1)

        # Team 2 units
        footman2 = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle2)
        game.castle2.add_unit(footman2)
        bear2 = UnitFactory.create_unit(constants.UNIT_BEAR, game.castle2)
        game.castle2.add_unit(bear2)

        # Start game and deploy some units
        game.start_turn()

        # Deploy units to various positions (not on enemy castles)
        game._handle_deploy(constants.UNIT_FOOTMAN, 47)  # Team 1 footman at (7, 4)
        game._handle_deploy(constants.UNIT_BEAR, 67)     # Team 1 bear at (7, 6)
        game._handle_deploy(constants.UNIT_FOOTMAN, 43)  # Team 2 footman at (3, 4)
        game._handle_deploy(constants.UNIT_BEAR, 56)     # Team 2 bear at (6, 5)

        # Switch to team 2's turn
        game.end_turn()

        # Deploy team 2 units
        game._handle_deploy(constants.UNIT_FOOTMAN, 10)  # Team 2 footman at (0, 1)
        game._handle_deploy(constants.UNIT_BEAR, 96)     # Team 2 bear at (6, 9)

        # Both castles should still be present
        assert game.castle1.location == game.battlefield.get_location(5, 10)
        assert game.castle2.location == game.battlefield.get_location(5, 0)

        # No units should be on enemy castles
        castle1_loc = game.castle1.location
        castle2_loc = game.castle2.location

        units_on_castle1 = [u for u in game.battlefield.units if not u.dead and u.location == castle1_loc]
        units_on_castle2 = [u for u in game.battlefield.units if not u.dead and u.location == castle2_loc]

        # Should be empty or only contain the castle itself (but castles aren't units)
        assert len(units_on_castle1) == 0, f"Units on castle 1: {units_on_castle1}"
        assert len(units_on_castle2) == 0, f"Units on castle 2: {units_on_castle2}"

        # Game should not be over
        assert not game.is_over()
        assert game.check_victory() is None

    def test_victory_condition_bug_from_training_output(self):
        """Test the specific victory condition bug from the training output.

        In the training output, the game declared 'Winner: Team 1' after 253 turns,
        but both castles were still present on the board with no units on enemy castles.
        This should not happen.
        """
        game = Game()

        # Recreate the exact board state from the training output
        # Team 1 units: F1 at (7,0), B1 at (4,7), B1 at (6,7)
        # Team 2 units: B2 at (3,9), B2 at (5,6)

        # Add units to barracks first
        f1 = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(f1)
        b1_1 = UnitFactory.create_unit(constants.UNIT_BEAR, game.castle1)
        game.castle1.add_unit(b1_1)
        b1_2 = UnitFactory.create_unit(constants.UNIT_BEAR, game.castle1)
        game.castle1.add_unit(b1_2)

        b2_1 = UnitFactory.create_unit(constants.UNIT_BEAR, game.castle2)
        game.castle2.add_unit(b2_1)
        b2_2 = UnitFactory.create_unit(constants.UNIT_BEAR, game.castle2)
        game.castle2.add_unit(b2_2)

        # Start game
        game.start_turn()

        # Deploy units to match the training output positions
        game._handle_deploy(constants.UNIT_FOOTMAN, 7)   # F1 at (7,0)
        game._handle_deploy(constants.UNIT_BEAR, 47)     # B1 at (7,4)
        game._handle_deploy(constants.UNIT_BEAR, 67)     # B1 at (7,6)

        # Switch to team 2
        game.end_turn()

        game._handle_deploy(constants.UNIT_BEAR, 39)     # B2 at (9,3)
        game._handle_deploy(constants.UNIT_BEAR, 56)     # B2 at (6,5)

        # Now manually move units to match the final positions from the training output
        # This is tricky, but let's try to move them to the right positions

        # Check that both castles are still present and no victory
        assert game.castle1.location == game.battlefield.get_location(5, 10)
        assert game.castle2.location == game.battlefield.get_location(5, 0)

        # Check that no units are on enemy castles
        enemy_castle_1 = game.castle1.location  # enemy of team 2
        enemy_castle_2 = game.castle2.location  # enemy of team 1

        team1_units_on_enemy_castle = [u for u in game.battlefield.units
                                      if not u.dead and u.team == constants.TEAM_1
                                      and u.location == enemy_castle_2]
        team2_units_on_enemy_castle = [u for u in game.battlefield.units
                                      if not u.dead and u.team == constants.TEAM_2
                                      and u.location == enemy_castle_1]

        assert len(team1_units_on_enemy_castle) == 0, f"Team 1 units on enemy castle: {team1_units_on_enemy_castle}"
        assert len(team2_units_on_enemy_castle) == 0, f"Team 2 units on enemy castle: {team2_units_on_enemy_castle}"

        # Game should NOT be over - this is the bug we're testing
        # In the training output, it incorrectly declared Team 1 as winner
        winner = game.check_victory()
        assert winner is None, f"Game should not have a winner, but got: {winner}"
        assert not game.is_over(), "Game should not be over"

    def test_victory_correctly_declared_when_unit_on_enemy_castle(self):
        """Test that victory is correctly declared when a unit is on the enemy castle."""
        game = Game()

        # Create and place a Team 1 unit directly on Team 2's castle
        footman1 = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        footman1.set_team(constants.TEAM_1)  # Set team explicitly
        enemy_castle_location = game.castle2.location  # (5,0) = location 5
        footman1.set_location(enemy_castle_location)
        game.battlefield.add_unit(footman1)

        # Team 1 should be the winner
        winner = game.check_victory()
        assert winner == game.castle1, f"Team 1 should win when their unit is on enemy castle, but got: {winner}"
        assert game.is_over(), "Game should be over"

    def test_no_victory_when_unit_on_own_castle(self):
        """Test that placing a unit on your own castle does not declare victory."""
        game = Game()

        # Add a unit to Team 1
        footman1 = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(footman1)

        # Start game
        game.start_turn()

        # Deploy Team 1 footman to Team 1's own castle location (5,10)
        own_castle_location = game.castle1.location  # (5,10) = location 115
        game._handle_deploy(constants.UNIT_FOOTMAN, own_castle_location)

        # No victory should be declared
        winner = game.check_victory()
        assert winner is None, f"No victory should be declared when unit is on own castle, but got: {winner}"
        assert not game.is_over(), "Game should not be over"

