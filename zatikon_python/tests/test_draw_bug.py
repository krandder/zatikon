"""
Test that catches the bug where games incorrectly report "Draw" when there's a winner.

The bug: When max_turns is reached in self_play_game_with_display, it calls
display_game_summary with winner=None without checking if there's actually a winner.
"""
import pytest
from zatikon import constants
from zatikon.game import Game
from zatikon.alphazero import (
    terminal_value,
)
from zatikon.unit_factory import UnitFactory


def test_game_with_winner_should_not_report_draw():
    """
    Test that when a unit is on the enemy castle, the game should report
    the winner, not a draw.
    
    This test reproduces the bug from the user's report where a game
    incorrectly shows "Result: Draw" even when there's a winner.
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
    
    # Deploy a unit for Team 1
    deploy_targets = game._get_castle_targets(game.castle1)
    if deploy_targets:
        game.handle_action(constants.ACTION_DEPLOY, 0, deploy_targets[0])
    
    # Find Team 1 unit and place it on Team 2's castle
    team1_unit = None
    for u in game.battlefield.units:
        if u.castle == game.castle1 and not u.dead:
            team1_unit = u
            break
    
    if not team1_unit:
        pytest.skip("No Team 1 unit on board")
    
    castle2_location = game.castle2.location
    
    # Place unit on enemy castle (simulating victory)
    game.battlefield.remove_unit(team1_unit)
    team1_unit.set_location(castle2_location)
    game.battlefield.add_unit(team1_unit)
    
    # Verify unit is on enemy castle
    unit_at_castle = game.battlefield.get_unit_at(castle2_location)
    assert unit_at_castle is not None, "Unit should be at castle location"
    assert unit_at_castle.castle == game.castle1, "Unit should belong to Team 1"
    
    # Check victory - this should detect Team 1 as winner
    winner = game.check_victory()
    assert winner == game.castle1, f"Team 1 should be the winner, got {winner}"
    assert game.is_over(), "Game should be over"
    
    # Now test terminal_value - this is where the bug manifests
    # The bug: terminal_value returns 0.0 (draw) even when there's a winner
    tv = terminal_value(game)
    
    # This assertion will FAIL until the bug is fixed
    assert tv != 0.0, \
        f"BUG: terminal_value() returned 0.0 (draw) even though Team 1 won! " \
        f"check_victory() returned {winner}, is_over()={game.is_over()}. " \
        f"This is the bug - when a game ends with a winner, it should not report a draw."
    
    # If the bug is fixed, terminal_value should return non-zero
    if game.current_player == constants.TEAM_1:
        assert tv == 1.0, f"terminal_value should be 1.0 for winning Team 1, got {tv}"
    else:
        assert tv == -1.0, f"terminal_value should be -1.0 for Team 2 when Team 1 won, got {tv}"

