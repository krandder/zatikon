"""
AIClient - Client mode where both sides are controlled by random AIs.
"""
from zatikon.game import Game
from zatikon.random_ai import RandomAI
from zatikon.terminal_client import TerminalClient
from zatikon import constants
from zatikon.unit_factory import UnitFactory
import time


def setup_ai_game():
    """
    Set up a game with initial units for AI vs AI.
    
    Returns:
        Game instance
    """
    game = Game()
    
    # Add units to each castle's barracks
    # Player 1
    for _ in range(5):
        footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(footman)

    for _ in range(5):
        bear = UnitFactory.create_unit(constants.UNIT_BEAR, game.castle1)
        game.castle1.add_unit(bear)

    # Player 2
    for _ in range(5):
        footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle2)
        game.castle2.add_unit(footman)

    for _ in range(5):
        bear = UnitFactory.create_unit(constants.UNIT_BEAR, game.castle2)
        game.castle2.add_unit(bear)
    
    # Start first turn
    game.start_turn()
    
    return game


def main():
    """Main AI vs AI game loop."""
    print("=" * 60)
    print("Zatikon - AI vs AI Mode")
    print("=" * 60)
    print()
    
    game = setup_ai_game()
    client = TerminalClient(game)
    ai1 = RandomAI(game)
    ai2 = RandomAI(game)
    
    max_turns = 300  # Prevent infinite games
    turn_count = 0
    
    # Main game loop
    while not game.is_over() and turn_count < max_turns:
        # Display board
        print("\n" * 2)
        print("=" * 60)
        print(client.render_board())
        print()
        print(client.render_status())
        print()
        
        # Determine which AI to use
        if game.current_player == constants.TEAM_1:
            ai = ai1
            player_name = "AI 1"
        else:
            ai = ai2
            player_name = "AI 2"
        
        print(f"{player_name} is thinking...")
        time.sleep(0.5)  # Small delay for readability
        
        # Execute AI turn and get commands executed
        commands_executed = ai.execute_turn_with_log()
        
        # Display commands executed
        if commands_executed:
            print(f"\n{player_name} executed {len(commands_executed)} commands:")
            for i, cmd in enumerate(commands_executed, 1):
                print(f"  {i}. {cmd}")
        else:
            print(f"\n{player_name} ended turn (no moves available)")
        
        # Check for victory
        winner = game.check_victory()
        if winner:
            print("\n" + "=" * 60)
            winner_name = "AI 1" if winner == game.castle1 else "AI 2"
            print(f"*** GAME OVER - {winner_name} WINS! ***")
            print("=" * 60)
            break
        
        turn_count += 1
    
    # Final board state
    print("\n" * 2)
    print("=" * 60)
    print("Final Board State:")
    print("=" * 60)
    print(client.render_board())
    print()
    print(f"Game ended after {turn_count} turns")


if __name__ == "__main__":
    main()

