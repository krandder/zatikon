"""
Test that catches the bug where games incorrectly report "Draw" when there's a winner,
even when the game ends BEFORE reaching the turn limit.

The bug: When a unit captures the enemy castle, check_victory() returns the winner
and sets _over=True. But terminal_value() calls check_victory() again, which
returns None because _over is already True, causing it to report a draw.
"""
import pytest
from zatikon import constants
from zatikon.game import Game
from zatikon.alphazero import (
    terminal_value,
)
from zatikon.unit_factory import UnitFactory


def test_game_ending_with_winner_should_not_report_draw():
    """
    Test that when a game ends with a winner (unit on enemy castle),
    terminal_value() should return the correct value, not 0.0 (draw).
    
    This reproduces the bug from the user's report:
    - Game ends at turn 182 (not turn limit)
    - Unit is on enemy castle (winner exists)
    - But game reports "Result: Draw"
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
    
    # Place unit on enemy castle (this should trigger victory)
    game.battlefield.remove_unit(team1_unit)
    team1_unit.set_location(castle2_location)
    game.battlefield.add_unit(team1_unit)
    
    # Verify unit is on enemy castle
    unit_at_castle = game.battlefield.get_unit_at(castle2_location)
    assert unit_at_castle is not None, "Unit should be at castle location"
    assert unit_at_castle.castle == game.castle1, "Unit should belong to Team 1"
    
    # First call to check_victory() - this should detect the winner and set _over=True
    winner_first = game.check_victory()
    assert winner_first == game.castle1, f"First check_victory() should return Team 1, got {winner_first}"
    assert game.is_over(), "Game should be over after first check_victory()"
    
    # Second call to check_victory() - this is what terminal_value() does
    # BUG: This returns None because _over is already True
    winner_second = game.check_victory()
    print(f"\nFirst check_victory(): {winner_first}")
    print(f"Second check_victory(): {winner_second}")
    print(f"is_over(): {game.is_over()}")
    
    # This is the bug: check_victory() returns None on second call
    # even though there's a winner
    assert winner_second is not None, \
        f"BUG: check_victory() returns None on second call even though winner exists! " \
        f"First call returned {winner_first}, is_over()={game.is_over()}. " \
        f"This causes terminal_value() to report a draw."
    
    # Now test terminal_value() - this is where the bug manifests
    # terminal_value() calls check_victory(), which returns None because _over is True
    tv = terminal_value(game)
    
    # This assertion will FAIL until the bug is fixed
    assert tv != 0.0, \
        f"BUG: terminal_value() returned 0.0 (draw) even though Team 1 won! " \
        f"check_victory() first call returned {winner_first}, " \
        f"second call returned {winner_second}, is_over()={game.is_over()}. " \
        f"This is the bug - when a game ends with a winner (not turn limit), " \
        f"it should not report a draw."
    
    # If the bug is fixed, terminal_value should return non-zero
    if game.current_player == constants.TEAM_1:
        assert tv == 1.0, f"terminal_value should be 1.0 for winning Team 1, got {tv}"
    else:
        assert tv == -1.0, f"terminal_value should be -1.0 for Team 2 when Team 1 won, got {tv}"


def test_check_victory_returns_none_after_game_over():
    """
    Test that demonstrates the bug: check_victory() returns None
    when called after _over is already True, even if there's a winner.
    
    This is the root cause of the draw bug.
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
    
    # Place unit on enemy castle
    game.battlefield.remove_unit(team1_unit)
    team1_unit.set_location(castle2_location)
    game.battlefield.add_unit(team1_unit)
    
    # First call: should detect winner and set _over=True
    winner1 = game.check_victory()
    assert winner1 == game.castle1, "First call should return winner"
    assert game.is_over(), "Game should be over"
    
    # Second call: BUG - returns None because _over is True
    winner2 = game.check_victory()
    
    # This test documents the bug
    # The assertion will FAIL until check_victory() is fixed to return the winner
    # even when _over is already True
    assert winner2 == game.castle1, \
        f"BUG: check_victory() should return the winner even when called after _over=True. " \
        f"First call: {winner1}, Second call: {winner2}, is_over(): {game.is_over()}. " \
        f"The game should remember who won, not return None."

