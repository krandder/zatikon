"""
Test to verify that turn numbers are displayed correctly in training display.

The issue: Turn numbers in headers don't match the board display, or turns
show the same number multiple times.
"""
import pytest
from unittest.mock import patch
from zatikon.alphazero import self_play_game_with_display, ZatikonNet


class TestTurnNumberDisplay:
    """Test turn number display consistency."""

    @pytest.fixture
    def net(self):
        """Create a neural network for testing."""
        return ZatikonNet()

    def test_turn_numbers_increment_correctly_in_display(self, net):
        """
        Test that turn numbers increment correctly and headers match board display.

        This test reproduces the bug where turn headers show incorrect numbers
        or the same turn number appears multiple times.
        """
        captured_output = []

        def mock_print(*args, **kwargs):
            """Capture print output for analysis."""
            output = ' '.join(str(arg) for arg in args)
            captured_output.append(output)

        with patch('builtins.print', side_effect=mock_print):
            try:
                # Run a short game with display
                game_data, winner = self_play_game_with_display(
                    net, mcts_sims=2, max_turns=5, game_number=1
                )
            except Exception as e:
                # Game might end early, that's fine
                pass

        # Analyze captured output for turn number consistency
        turn_headers = []
        board_turns = []

        for i, line in enumerate(captured_output):
            if 'GAME 1 - TURN' in line:
                # Extract turn number from header like "GAME 1 - TURN 123"
                try:
                    turn_num = int(line.split('TURN')[1].strip())
                    turn_headers.append(turn_num)
                except (IndexError, ValueError):
                    continue
            elif 'Turn' in line and 'Player:' in line:
                # Extract turn number from board like "Turn 123/300 | Player: Team 1"
                try:
                    # Find the turn number in the line
                    turn_start = line.find('Turn ')
                    if turn_start >= 0:
                        # Extract from "Turn X/300" pattern
                        turn_part = line[turn_start:turn_start+20]  # Get next 20 chars
                        if '/' in turn_part:
                            # Format: "Turn 123/300"
                            turn_num_str = turn_part.split('/')[0].split()[1]
                        else:
                            # Format: "Turn 123"
                            turn_num_str = turn_part.split()[1]
                        turn_num = int(turn_num_str)
                        board_turns.append(turn_num)
                except (IndexError, ValueError, AttributeError):
                    continue

        print(f"\nCaptured headers: {turn_headers}")
        print(f"Captured board turns: {board_turns}")

        # Verify we captured some data
        assert len(turn_headers) > 0, "Should have captured at least one turn header"
        assert len(board_turns) > 0, "Should have captured at least one board turn"

        # Check that headers and board turns are consistent
        # Both should show the same turn number now (1-indexed)
        min_length = min(len(turn_headers), len(board_turns))
        for i in range(min_length):
            header_turn = turn_headers[i]
            board_turn = board_turns[i]
            print(f"Turn {i+1}: Header={header_turn}, Board={board_turn}")

            # Both header and board should show the same turn number
            assert header_turn == board_turn, \
                f"Turn {i+1}: Header turn {header_turn} should match board turn {board_turn}"

        # The main bug: turn numbers should not be duplicated
        # This reproduces the user's issue where the same turn number appears multiple times

        # Check for duplicate headers during active game (exclude last one which might be from display_game_summary)
        if len(turn_headers) > 1:
            header_counts = {}
            for h in turn_headers[:-1]:  # Exclude last header
                header_counts[h] = header_counts.get(h, 0) + 1

            duplicates = [turn for turn, count in header_counts.items() if count > 1]
            assert len(duplicates) == 0, \
                f"BUG: Duplicate turn headers found during active game! " \
                f"Headers: {turn_headers[:-1]}, Duplicate turns: {duplicates}. " \
                f"This matches the user's report of seeing the same turn number multiple times."

        # Check for duplicate board turns during active game (exclude last one which might be from display_game_summary)
        if len(board_turns) > 1:
            board_counts = {}
            for b in board_turns[:-1]:  # Exclude last board turn
                board_counts[b] = board_counts.get(b, 0) + 1

            duplicates = [turn for turn, count in board_counts.items() if count > 1]
            assert len(duplicates) == 0, \
                f"BUG: Duplicate board turn numbers found during active game! " \
                f"Board turns: {board_turns[:-1]}, Duplicate turns: {duplicates}"
