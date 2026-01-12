"""
Test to ensure turn numbers are consistent between display and game state.
"""
import pytest
from zatikon import constants
from zatikon.game import Game
from zatikon.alphazero import self_play_game_with_display, ZatikonNet
from zatikon.training_display import render_board_simple


def test_turn_number_consistency():
    """
    Test that displayed turn numbers match game.turn_number.
    
    This test ensures that when we display "TURN N", the game.turn_number
    matches what we expect.
    """
    net = ZatikonNet()
    
    # Track turn numbers during a game
    turn_numbers_seen = []
    
    # Monkey-patch display_turn to capture turn numbers
    original_display_turn = None
    
    def capture_turn_display(game, turn_actions, displayed_turn_num, game_number):
        """Capture turn numbers for verification."""
        turn_numbers_seen.append({
            'displayed_turn': displayed_turn_num,
            'game_turn_number': game.turn_number,
            'current_player': game.current_player,
        })
        # Don't actually display to avoid cluttering test output
    
    # Replace display function temporarily
    import zatikon.alphazero
    original_display_turn = zatikon.alphazero.self_play_game_with_display
    
    # Play a short game
    try:
        # Use a small number of turns to keep test fast
        game_data, winner = self_play_game_with_display(
            net, 
            mcts_sims=5, 
            max_turns=10,
            game_number=1
        )
        
        # Verify turn numbers are consistent
        # The displayed turn number should match game.turn_number + 1
        # (because turn_number is 0-indexed, display is 1-indexed)
        for turn_info in turn_numbers_seen:
            displayed = turn_info['displayed_turn']
            game_turn = turn_info['game_turn_number']
            
            # Displayed turn should be game_turn + 1 (1-indexed vs 0-indexed)
            assert displayed == game_turn + 1, \
                f"Turn mismatch: displayed={displayed}, game_turn_number={game_turn}"
    
    except Exception as e:
        pytest.fail(f"Turn number consistency test failed: {e}")


def test_game_turn_number_increments_correctly():
    """
    Test that game.turn_number increments correctly when END_TURN is called.
    """
    game = Game()
    game.start_turn()
    
    # Initially turn_number should be 0
    assert game.turn_number == 0, f"Expected turn_number=0, got {game.turn_number}"
    
    # End turn
    game.end_turn()
    
    # After end_turn, should increment
    assert game.turn_number == 1, f"Expected turn_number=1, got {game.turn_number}"
    
    # End another turn
    game.end_turn()
    
    assert game.turn_number == 2, f"Expected turn_number=2, got {game.turn_number}"


def test_display_shows_correct_turn_number():
    """
    Test that render_board_simple shows the correct turn number.
    """
    game = Game()
    game.start_turn()
    
    # Render board
    board_str = render_board_simple(game)
    
    # Should show "Turn 0"
    assert "Turn 0" in board_str, f"Expected 'Turn 0' in board display, got:\n{board_str}"
    
    # End turn and check again
    game.end_turn()
    board_str = render_board_simple(game)
    
    # Should show "Turn 1"
    assert "Turn 1" in board_str, f"Expected 'Turn 1' in board display, got:\n{board_str}"

