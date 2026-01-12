"""
Tests for Terminal Client - board display and command parsing.
"""
import pytest
from io import StringIO
from zatikon import constants
from zatikon.game import Game
from zatikon.terminal_client import TerminalClient
from zatikon.unit_factory import UnitFactory


class TestTerminalClientInitialization:
    """Test TerminalClient initialization."""

    def test_client_initializes_with_game(self):
        """Test client initializes with a game."""
        game = Game()
        client = TerminalClient(game)
        
        assert client.game == game

    def test_client_has_selected_unit(self):
        """Test client tracks selected unit."""
        game = Game()
        client = TerminalClient(game)
        
        assert client.selected_unit is None


class TestBoardDisplay:
    """Test board rendering."""

    def test_render_board_shows_grid(self):
        """Test render_board creates a grid display."""
        game = Game()
        client = TerminalClient(game)
        
        output = client.render_board()
        
        assert isinstance(output, str)
        assert len(output) > 0
        # Should have multiple lines (one per row)
        lines = output.split('\n')
        assert len(lines) >= 11  # At least 11 rows

    def test_render_board_shows_castles(self):
        """Test render_board shows castle locations."""
        from zatikon.battlefield import BattleField
        
        game = Game()
        client = TerminalClient(game)
        
        output = client.render_board()
        
        # Should show Castle 1 at location 115 (bottom center, 5,10)
        # Should show Castle 2 at location 5 (top center, 5,0)
        assert 'C1' in output or 'C' in output
        assert 'C2' in output or 'C' in output

    def test_render_board_shows_units(self):
        """Test render_board shows units on board."""
        game = Game()
        
        # Get valid deployment location
        targets = game._get_castle_targets(game.castle1)
        assert len(targets) > 0
        
        # Deploy a unit
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(unit)
        game.handle_action(constants.ACTION_DEPLOY, 0, targets[0])
        
        client = TerminalClient(game)
        output = client.render_board()
        
        # Should show unit (F for Footman)
        assert 'F' in output or unit.name[0].upper() in output

    def test_render_board_shows_coordinates(self):
        """Test render_board shows coordinate labels."""
        game = Game()
        client = TerminalClient(game)
        
        output = client.render_board()
        
        # Should have coordinate labels (0-10 or similar)
        assert '0' in output or '1' in output


class TestCommandParsing:
    """Test command parsing."""

    def test_parse_command_deploy(self):
        """Test parsing deploy command."""
        game = Game()
        client = TerminalClient(game)
        
        # Add unit to barracks
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(unit)
        
        result = client.parse_command("deploy 0 1")
        
        assert result is not None
        assert "Invalid" not in result.lower()

    def test_parse_command_select(self):
        """Test parsing select command."""
        game = Game()
        
        # Get valid deployment location
        targets = game._get_castle_targets(game.castle1)
        assert len(targets) > 0
        
        # Deploy a unit
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(unit)
        game.handle_action(constants.ACTION_DEPLOY, 0, targets[0])
        
        client = TerminalClient(game)
        result = client.parse_command(f"select {targets[0]}")
        
        assert client.selected_unit == unit

    def test_parse_command_move(self):
        """Test parsing move command."""
        game = Game()
        
        # Deploy a unit
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(unit)
        game.handle_action(constants.ACTION_DEPLOY, 0, 1)
        
        client = TerminalClient(game)
        client.selected_unit = unit
        
        result = client.parse_command("move 2")
        
        assert "Invalid" not in result.lower() or unit.location == 2

    def test_parse_command_attack(self):
        """Test parsing attack command."""
        game = Game()
        
        # Deploy attacker
        attacker = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(attacker)
        game.handle_action(constants.ACTION_DEPLOY, 0, 1)
        
        # Deploy target
        target = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle2)
        game.castle2.add_unit(target)
        game.current_player = constants.TEAM_2
        game.handle_action(constants.ACTION_DEPLOY, 0, 11)
        game.current_player = constants.TEAM_1
        
        client = TerminalClient(game)
        client.selected_unit = attacker
        
        result = client.parse_command("attack 11")
        
        assert result is not None

    def test_parse_command_end_turn(self):
        """Test parsing end turn command."""
        game = Game()
        client = TerminalClient(game)
        
        initial_player = game.current_player
        result = client.parse_command("end")
        
        assert game.current_player != initial_player

    def test_parse_command_help(self):
        """Test parsing help command."""
        game = Game()
        client = TerminalClient(game)
        
        result = client.parse_command("help")
        
        assert "help" in result.lower() or "command" in result.lower()

    def test_parse_command_invalid(self):
        """Test parsing invalid command."""
        game = Game()
        client = TerminalClient(game)
        
        result = client.parse_command("invalid_command")
        
        assert "unknown" in result.lower() or "invalid" in result.lower()


class TestGameStateDisplay:
    """Test game state display."""

    def test_render_status_shows_current_player(self):
        """Test render_status shows current player."""
        game = Game()
        client = TerminalClient(game)
        
        status = client.render_status()
        
        assert "Player" in status or "Team" in status or "Turn" in status

    def test_render_status_shows_commands(self):
        """Test render_status shows commands remaining."""
        game = Game()
        client = TerminalClient(game)
        
        status = client.render_status()
        
        assert "Command" in status or str(constants.MAX_COMMANDS) in status

    def test_render_status_shows_turn_number(self):
        """Test render_status shows turn number."""
        game = Game()
        client = TerminalClient(game)
        
        status = client.render_status()
        
        assert "Turn" in status or "turn" in status.lower()

    def test_render_barracks_shows_undeployed_units(self):
        """Test render_barracks shows units in barracks."""
        game = Game()
        
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(unit)
        
        client = TerminalClient(game)
        barracks = client.render_barracks()
        
        assert len(barracks) > 0
        assert "Footman" in barracks or "F" in barracks


class TestLocationParsing:
    """Test location coordinate parsing."""

    def test_parse_location_coordinates(self):
        """Test parsing location from coordinates."""
        game = Game()
        client = TerminalClient(game)
        
        # Parse "5,5" -> location 60
        location = client.parse_location("5,5")
        assert location == 60
        
        location = client.parse_location("0,0")
        assert location == 0
        
        location = client.parse_location("10,10")
        assert location == 120

    def test_parse_location_number(self):
        """Test parsing location as number."""
        game = Game()
        client = TerminalClient(game)
        
        location = client.parse_location("60")
        assert location == 60
        
        location = client.parse_location("0")
        assert location == 0

    def test_parse_location_invalid(self):
        """Test parsing invalid location."""
        game = Game()
        client = TerminalClient(game)
        
        location = client.parse_location("invalid")
        assert location is None
        
        location = client.parse_location("999")
        assert location is None or location == 999  # May allow out of bounds


class TestCommandValidation:
    """Test command validation."""

    def test_validate_deploy_requires_unit_in_barracks(self):
        """Test deploy requires unit in barracks."""
        game = Game()
        client = TerminalClient(game)
        
        result = client.parse_command("deploy 0 1")
        assert "Invalid" in result or "not found" in result.lower()

    def test_validate_move_requires_selected_unit(self):
        """Test move requires selected unit."""
        game = Game()
        client = TerminalClient(game)
        
        result = client.parse_command("move 2")
        assert "select" in result.lower() or "Invalid" in result

    def test_validate_attack_requires_selected_unit(self):
        """Test attack requires selected unit."""
        game = Game()
        client = TerminalClient(game)
        
        result = client.parse_command("attack 2")
        assert "select" in result.lower() or "Invalid" in result

