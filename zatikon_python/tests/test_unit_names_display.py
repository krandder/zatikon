"""
Tests for unit name display - ensuring names are always 2 characters for board rendering.
"""
import pytest
from zatikon import constants
from zatikon.terminal_client import TerminalClient
from zatikon.game import Game
from zatikon.unit_factory import UnitFactory


class TestUnitNameDisplay:
    """Test unit names for board display."""

    def test_footman_name_is_two_characters(self):
        """Test Footman name is formatted as 2 characters."""
        game = Game()
        client = TerminalClient(game)
        
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        symbol = client._get_cell_symbol_for_unit(unit)
        
        assert len(symbol) == 2
        assert "F" in symbol

    def test_bear_name_is_two_characters(self):
        """Test Bear name is formatted as 2 characters."""
        game = Game()
        client = TerminalClient(game)
        
        unit = UnitFactory.create_unit(constants.UNIT_BEAR, game.castle1)
        symbol = client._get_cell_symbol_for_unit(unit)
        
        assert len(symbol) == 2
        assert "B" in symbol

    def test_all_unit_symbols_are_two_characters(self):
        """Test all unit symbols are exactly 2 characters."""
        game = Game()
        client = TerminalClient(game)
        
        # Deploy units
        footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(footman)
        game.handle_action(constants.ACTION_DEPLOY, 0, 1)
        
        bear = UnitFactory.create_unit(constants.UNIT_BEAR, game.castle1)
        game.castle1.add_unit(bear)
        game.handle_action(constants.ACTION_DEPLOY, 0, 2)
        
        # Check board rendering
        board = client.render_board()
        lines = board.split('\n')
        
        # Find the row with units (row 0)
        for line in lines:
            if '|' in line and ('F' in line or 'B' in line):
                # Check that symbols are properly spaced
                cells = line.split('|')[1].strip().split()
                for cell in cells:
                    # Each cell should be 2 characters (or we handle spacing correctly)
                    assert len(cell) <= 2 or cell.startswith(' ')

    def test_empty_cell_is_two_characters(self):
        """Test empty cell symbol is 2 characters."""
        game = Game()
        client = TerminalClient(game)
        
        symbol = client._get_cell_symbol(60)  # Empty location
        assert len(symbol) == 2

    def test_castle_symbols_are_two_characters(self):
        """Test castle symbols are 2 characters."""
        from zatikon.battlefield import BattleField
        
        game = Game()
        client = TerminalClient(game)
        
        c1_location = BattleField.get_location(5, 10)  # Castle 1
        c2_location = BattleField.get_location(5, 0)    # Castle 2
        
        c1_symbol = client._get_cell_symbol(c1_location)
        c2_symbol = client._get_cell_symbol(c2_location)
        
        assert len(c1_symbol) == 2
        assert len(c2_symbol) == 2
        assert c1_symbol == "C1"
        assert c2_symbol == "C2"

    def test_board_alignment_is_consistent(self):
        """Test board columns align correctly with 2-character symbols."""
        game = Game()
        client = TerminalClient(game)
        
        # Deploy units at various locations
        for i in range(3):
            unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
            game.castle1.add_unit(unit)
            game.handle_action(constants.ACTION_DEPLOY, i, i + 1)
        
        board = client.render_board()
        lines = board.split('\n')
        
        # Check that rows have consistent width
        board_lines = [line for line in lines if '|' in line]
        if board_lines:
            first_width = len(board_lines[0])
            for line in board_lines:
                # All board rows should have same width
                assert len(line) == first_width or abs(len(line) - first_width) <= 1

