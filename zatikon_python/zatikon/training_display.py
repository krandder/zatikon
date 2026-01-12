"""
Display utilities for training visualization.
"""
import os
from zatikon import constants
from zatikon.battlefield import BattleField
from zatikon.alphazero import action_to_index, index_to_action, ACTION_DEPLOY, ACTION_MOVE, ACTION_ATTACK, ACTION_END_TURN


def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')


def render_board_simple(game) -> str:
    """
    Render a simple board representation.
    
    Args:
        game: Game instance
        
    Returns:
        String representation of the board
    """
    lines = []
    lines.append("=" * 50)
    # Show the player who just played (before END_TURN switched to the next player)
    player_who_played = 'Team 2' if game.current_player == constants.TEAM_1 else 'Team 1'
    lines.append(f"Turn {game.turn_number + 1}/300 | Player: {player_who_played}")
    lines.append("=" * 50)
    
    # Board
    header = "   "
    for x in range(constants.BOARD_SIZE):
        header += f" {x:2}"
    lines.append(header)
    lines.append("   " + "-" * (constants.BOARD_SIZE * 3 + 1))
    
    for y in range(constants.BOARD_SIZE):
        row = f"{y:2}|"
        for x in range(constants.BOARD_SIZE):
            location = BattleField.get_location(x, y)
            cell = _get_cell_symbol(game, location)
            row += f" {cell}"
        row += " |"
        lines.append(row)
    
    lines.append("   " + "-" * (constants.BOARD_SIZE * 3 + 1))
    
    # Status
    castle1 = game.castle1
    castle2 = game.castle2
    lines.append(f"Team 1: {castle1.commands_left} commands | Units: {len([u for u in castle1.units_out if not u.dead])}")
    lines.append(f"Team 2: {castle2.commands_left} commands | Units: {len([u for u in castle2.units_out if not u.dead])}")
    
    return "\n".join(lines)


def _get_cell_symbol(game, location: int) -> str:
    """Get symbol for a cell."""
    # Check for castle
    if location == game.castle1.location:
        return "C1"
    if location == game.castle2.location:
        return "C2"

    # Check for unit
    unit = game.battlefield.get_unit_at(location)
    if unit:
        if unit.castle == game.castle1:
            # Team 1 units
            if unit.unit_id == constants.UNIT_FOOTMAN:
                return "F1"  # Footman
            else:  # UNIT_BEAR
                return "B1"  # Bear
        else:
            # Team 2 units
            if unit.unit_id == constants.UNIT_FOOTMAN:
                return "F2"  # Footman
            else:  # UNIT_BEAR
                return "B2"  # Bear

    # Empty cell
    return " ."


def format_action(action) -> str:
    """
    Format an action for display.
    
    Args:
        action: (action_type, param1, param2) tuple
        
    Returns:
        Formatted string
    """
    action_type, param1, param2 = action
    
    if action_type == ACTION_DEPLOY:
        x = BattleField.get_x(param2)
        y = BattleField.get_y(param2)
        return f"Deploy unit {param1} to ({x}, {y})"
    elif action_type == ACTION_MOVE:
        x1 = BattleField.get_x(param1)
        y1 = BattleField.get_y(param1)
        x2 = BattleField.get_x(param2)
        y2 = BattleField.get_y(param2)
        return f"Move from ({x1}, {y1}) to ({x2}, {y2})"
    elif action_type == ACTION_ATTACK:
        x1 = BattleField.get_x(param1)
        y1 = BattleField.get_y(param1)
        x2 = BattleField.get_x(param2)
        y2 = BattleField.get_y(param2)
        return f"Attack from ({x1}, {y1}) to ({x2}, {y2})"
    elif action_type == ACTION_END_TURN:
        return "End Turn"
    else:
        return f"Unknown action {action_type}"


def display_turn(game, turn_actions, turn_number, game_number, clear=False, value_estimate=None):
    """
    Display a turn during training.

    Args:
        game: Game instance (game.turn_number is the source of truth)
        turn_actions: List of actions in the turn
        turn_number: Turn number passed in (should match game.turn_number + 1)
        game_number: Current game number
        clear: If True, clear screen before displaying (default: False, append to history)
        value_estimate: Neural network's value estimate [win_prob, lose_prob, draw_prob] or None
    """
    if clear:
        clear_screen()
    else:
        # Add separator for readability when scrolling
        print("\n" + "="*60)
    
    # Use game.turn_number as source of truth (0-indexed, so +1 for display)
    actual_turn = game.turn_number + 1
    print(f"\n{'='*60}")
    print(f"GAME {game_number} - TURN {actual_turn}")
    print(f"{'='*60}\n")

    # Warn if mismatch
    if turn_number != actual_turn:
        print(f"[WARNING] Turn number mismatch: passed={turn_number}, game.turn_number={game.turn_number}, actual={actual_turn}")

    print(f"Actions in this turn ({len(turn_actions)}):")
    for i, action in enumerate(turn_actions, 1):
        print(f"  {i}. {format_action(action)}")
    print()

    # Use render_board_simple which uses game.turn_number directly
    print(render_board_simple(game))
    print()

    # Display neural network value estimate if provided
    if value_estimate is not None:
        if isinstance(value_estimate, (list, tuple)) and len(value_estimate) == 3:
            win_prob, lose_prob, draw_prob = value_estimate
            expected_value = win_prob * 1.0 + lose_prob * (-1.0) + draw_prob * 0.0
            print(f"Neural Network Value (Player 1 perspective): Win={win_prob:.3f}, Lose={lose_prob:.3f}, Draw={draw_prob:.3f} (EV={expected_value:.3f})")
        else:
            print(f"Neural Network Value: {value_estimate} (unexpected format)")
        print()

    # Flush output to ensure it's visible immediately
    import sys
    sys.stdout.flush()


def display_game_summary(game, game_number, winner, turn_count, game_time, clear=False):
    """
    Display game summary.
    
    Args:
        game: Game instance
        game_number: Game number
        winner: Winner team or None
        turn_count: Number of turns
        game_time: Time taken for game
        clear: If True, clear screen before displaying (default: False)
    """
    if clear:
        clear_screen()
    else:
        print("\n" + "="*60)
    
    print(f"\n{'='*60}")
    print(f"GAME {game_number} COMPLETE")
    print(f"{'='*60}\n")
    
    print(render_board_simple(game))
    print()
    
    if winner:
        winner_name = "Team 1" if winner == constants.TEAM_1 else "Team 2"
        print(f"Winner: {winner_name}")
    else:
        print("Result: Draw")
    
    print(f"Turns: {turn_count}")
    print(f"Time: {game_time:.2f}s")
    print(f"\n{'='*60}\n")
    import sys
    sys.stdout.flush()

