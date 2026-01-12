"""
Main game loop for Zatikon terminal client.
"""
from zatikon.game import Game
from zatikon.terminal_client import TerminalClient
from zatikon import constants
from zatikon.unit_factory import UnitFactory


def setup_game():
    """
    Set up a new game with initial units.
    
    Returns:
        Game instance
    """
    game = Game()
    
    # Add some units to each castle's barracks
    # Player 1
    for _ in range(2):
        footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(footman)
    
    bear = UnitFactory.create_unit(constants.UNIT_BEAR, game.castle1)
    game.castle1.add_unit(bear)
    
    # Player 2
    for _ in range(2):
        footman = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle2)
        game.castle2.add_unit(footman)
    
    bear = UnitFactory.create_unit(constants.UNIT_BEAR, game.castle2)
    game.castle2.add_unit(bear)
    
    # Start first turn
    game.start_turn()
    
    return game


def main():
    """Main game loop."""
    print("=" * 60)
    print("Welcome to Zatikon!")
    print("=" * 60)
    print()
    
    game = setup_game()
    client = TerminalClient(game)
    
    # Main game loop
    while not game.is_over():
        # Clear screen (optional, can be removed if not desired)
        print("\n" * 2)
        print("=" * 60)
        
        # Display board
        print(client.render_board())
        print()
        
        # Display status
        print(client.render_status())
        print()
        
        # Display barracks
        print(client.render_barracks())
        print()
        
        # Get command
        try:
            command = input("> ").strip()
            
            if not command:
                continue
            
            # Parse and execute command
            result = client.parse_command(command)
            if result:
                print(result)
            
            # Check for victory after each command
            if game.check_victory():
                print("\n" + "=" * 60)
                winner = game.check_victory()
                winner_name = "Player 1" if winner == game.castle1 else "Player 2"
                print(f"*** GAME OVER - {winner_name} WINS! ***")
                print("=" * 60)
                break
        
        except KeyboardInterrupt:
            print("\n\nGame interrupted. Goodbye!")
            break
        except EOFError:
            print("\n\nGame ended. Goodbye!")
            break
    
    # Final board state
    print("\n" * 2)
    print("=" * 60)
    print("Final Board State:")
    print("=" * 60)
    print(client.render_board())


if __name__ == "__main__":
    main()

