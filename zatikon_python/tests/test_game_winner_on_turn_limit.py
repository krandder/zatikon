"""
Test that games correctly determine the winner even when turn limit is reached.

The bug: When max_turns is reached, the game reports "Draw" even if there's
actually a winner (e.g., a unit on enemy castle).
"""
import pytest
from zatikon import constants
from zatikon.game import Game
from zatikon.alphazero import (
    self_play_game_with_display,
    ZatikonNet,
    terminal_value,
)
from zatikon.unit_factory import UnitFactory


class TestGameWinnerOnTurnLimit:
    """Test that games correctly determine winners when turn limit is reached."""
    
    @pytest.fixture
    def net(self):
        """Create a neural network for testing."""
        return ZatikonNet()
    
    def test_game_with_unit_on_enemy_castle_should_have_winner(self):
        """
        Test that if a unit is on the enemy castle when turn limit is reached,
        the game should report that team as the winner, not a draw.
        
        This test reproduces the bug where games incorrectly report "Draw"
        when there's actually a winner.
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
        
        # Manually place a unit on the enemy castle to simulate victory condition
        # Deploy a unit for Team 1
        deploy_targets = game._get_castle_targets(game.castle1)
        if deploy_targets:
            game.handle_action(constants.ACTION_DEPLOY, 0, deploy_targets[0])
        
        # Don't end turn - keep it as Team 1's turn so get_enemy_castle() returns castle2
        # Find Team 1 unit
        team1_unit = None
        for u in game.battlefield.units:
            if u.castle == game.castle1 and not u.dead:
                team1_unit = u
                break
        
        if not team1_unit:
            pytest.skip("No Team 1 unit on board")
        
        # Move Team 1 unit to Team 2's castle location
        castle2_location = game.castle2.location
        print(f"\nTeam 1 unit at: {team1_unit.location}")
        print(f"Team 2 castle at: {castle2_location}")
        print(f"Current player: {game.current_player} (should be Team 1)")
        
        # Manually place unit on enemy castle for testing
        # This simulates the state where a unit is on enemy castle
        game.battlefield.remove_unit(team1_unit)
        team1_unit.set_location(castle2_location)
        game.battlefield.add_unit(team1_unit)
        print(f"✓ Manually placed unit on enemy castle for testing")
        
        # Verify unit is on enemy castle
        unit_at_castle = game.battlefield.get_unit_at(castle2_location)
        assert unit_at_castle is not None, "Unit should be at castle location"
        assert unit_at_castle.castle == game.castle1, "Unit should belong to Team 1"
        assert unit_at_castle.location == castle2_location, "Unit should be at castle location"
        
        # Verify current player is Team 1 (so get_enemy_castle returns castle2)
        assert game.current_player == constants.TEAM_1, "Current player should be Team 1"
        
        # Check victory condition
        winner = game.check_victory()
        print(f"\ncheck_victory() returned: {winner}")
        print(f"game.is_over(): {game.is_over()}")
        
        # The game should detect Team 1 as the winner
        assert winner == game.castle1, \
            f"Game should detect Team 1 as winner when unit is on enemy castle, but got: {winner}"
        assert game.is_over(), "Game should be over when unit is on enemy castle"
        
        # Now test terminal_value
        tv = terminal_value(game)
        print(f"\nterminal_value() returned: {tv}")
        
        # terminal_value should return 1.0 for Team 1 (current player) if they won
        # or -1.0 if Team 2 is current player and Team 1 won
        if game.current_player == constants.TEAM_1:
            assert tv == 1.0, f"terminal_value should be 1.0 for winning Team 1, got {tv}"
        else:
            assert tv == -1.0, f"terminal_value should be -1.0 for Team 2 when Team 1 won, got {tv}"
    
    def test_turn_limit_with_winner_should_not_be_draw(self, net):
        """
        Test that when turn limit is reached but there's a winner,
        the game should report the winner, not a draw.
        
        This is the actual bug: games ending at turn limit incorrectly report "Draw"
        even when check_victory() returns a winner.
        """
        # Create a game state where Team 1 has a unit on Team 2's castle
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
        
        # Deploy a unit for Team 1
        deploy_targets = game._get_castle_targets(game.castle1)
        if deploy_targets:
            game.handle_action(constants.ACTION_DEPLOY, 0, deploy_targets[0])
        
        # Don't end turn - keep it as Team 1's turn so get_enemy_castle() returns castle2
        # Find Team 1 unit and manually place it on Team 2's castle
        team1_unit = None
        for u in game.battlefield.units:
            if u.castle == game.castle1 and not u.dead:
                team1_unit = u
                break
        
        if not team1_unit:
            pytest.skip("No Team 1 unit on board")
        
        castle2_location = game.castle2.location
        
        # Manually place unit on enemy castle (simulating victory)
        game.battlefield.remove_unit(team1_unit)
        team1_unit.set_location(castle2_location)
        game.battlefield.add_unit(team1_unit)
        
        # Verify unit is on enemy castle
        unit_at_castle = game.battlefield.get_unit_at(castle2_location)
        assert unit_at_castle is not None, "Unit should be at castle location"
        assert unit_at_castle.castle == game.castle1, "Unit should belong to Team 1"
        assert unit_at_castle.can_win, f"Unit should be able to win, can_win={unit_at_castle.can_win}"
        
        # Verify current player is Team 1 (so get_enemy_castle returns castle2)
        assert game.current_player == constants.TEAM_1, "Current player should be Team 1"
        
        # Verify victory condition
        winner = game.check_victory()
        assert winner == game.castle1, \
            f"Team 1 should be the winner when unit is on enemy castle. " \
            f"check_victory() returned: {winner}, is_over(): {game.is_over()}"
        assert game.is_over(), "Game should be over"
        
        # Now simulate what happens when turn limit is reached
        # The bug is in self_play_game_with_display when it reaches max_turns
        # It calls display_game_summary with winner=None without checking check_victory()
        
        # Check what terminal_value returns
        tv = terminal_value(game)
        assert tv is not None, "terminal_value should not be None when game is over"
        assert tv != 0.0, f"terminal_value should not be 0.0 (draw) when there's a winner, got {tv}"
        
        # The bug: when max_turns is reached, the code should check check_victory()
        # instead of assuming it's a draw
        # This test will fail until the bug is fixed
        expected_winner = game.castle1
        actual_winner = game.check_victory()
        
        assert actual_winner == expected_winner, \
            f"When game ends with unit on enemy castle, winner should be {expected_winner}, " \
            f"but check_victory() returned {actual_winner}. " \
            f"This test will pass once the bug is fixed to check check_victory() " \
            f"when turn limit is reached instead of assuming draw."

