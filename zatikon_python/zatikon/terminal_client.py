"""
TerminalClient - Terminal-based client for playing Zatikon.
"""
from zatikon import constants
from zatikon.battlefield import BattleField
from zatikon.game import Game


class TerminalClient:
    """
    Terminal-based client for playing Zatikon.
    Provides board display, command parsing, and game interaction.
    """
    
    def __init__(self, game: Game):
        """
        Initialize terminal client.
        
        Args:
            game: Game instance to interact with
        """
        self.game = game
        self.selected_unit = None
    
    def render_board(self) -> str:
        """
        Render the game board as ASCII art.

        Returns:
            String representation of the board
        """
        lines = []

        # Title with turn number
        lines.append("=" * 50)
        lines.append(f"Turn {self.game.turn_number + 1}/300 | Player: {'Team 1' if self.game.current_player == constants.TEAM_1 else 'Team 2'}")
        lines.append("=" * 50)

        # Header with column numbers
        header = "   "
        for x in range(constants.BOARD_SIZE):
            header += f" {x:2}"
        lines.append(header)
        lines.append("   " + "-" * (constants.BOARD_SIZE * 3 + 1))
        
        # Board rows
        for y in range(constants.BOARD_SIZE):
            row = f"{y:2}|"
            for x in range(constants.BOARD_SIZE):
                location = BattleField.get_location(x, y)
                cell = self._get_cell_symbol(location)
                row += f" {cell}"
            row += " |"
            lines.append(row)
        
        lines.append("   " + "-" * (constants.BOARD_SIZE * 3 + 1))
        
        return "\n".join(lines)
    
    def _get_cell_symbol(self, location: int) -> str:
        """
        Get symbol for a cell.
        
        Args:
            location: Location to get symbol for
            
        Returns:
            Symbol string (exactly 2 characters)
        """
        # Check for castle
        if location == self.game.castle1.location:
            return "C1"
        if location == self.game.castle2.location:
            return "C2"
        
        # Check for unit
        unit = self.game.battlefield.get_unit_at(location)
        if unit:
            return self._get_cell_symbol_for_unit(unit)
        
        # Empty cell
        return " ."
    
    def _get_cell_symbol_for_unit(self, unit) -> str:
        """
        Get symbol for a unit (always 2 characters).
        
        Args:
            unit: Unit to get symbol for
            
        Returns:
            Symbol string (exactly 2 characters)
        """
        # Get unit symbol (first letter of name)
        if unit.name:
            symbol_char = unit.name[0].upper()
        else:
            symbol_char = "U"
        
        # Player 1 uses uppercase, Player 2 uses lowercase
        if unit.castle == self.game.castle1:
            symbol_char = symbol_char.upper()
        else:
            symbol_char = symbol_char.lower()
        
        # Always return 2 characters (pad with space)
        return f" {symbol_char}" if len(symbol_char) == 1 else symbol_char[:2].ljust(2)
    
    def render_status(self) -> str:
        """
        Render game status information.
        
        Returns:
            Status string
        """
        castle = self.game.get_current_castle()
        player_name = "Player 1" if self.game.current_player == constants.TEAM_1 else "Player 2"
        
        status = []
        status.append(f"=== {player_name}'s Turn ===")
        status.append(f"Turn: {self.game.turn_number + 1}")
        status.append(f"Commands: {castle.commands_left}/{castle.commands_max}")
        
        if self.selected_unit:
            status.append(f"Selected: {self.selected_unit.name} at location {self.selected_unit.location}")
            status.append(f"  Life: {self.selected_unit.life}/{self.selected_unit.life_max}")
            status.append(f"  Actions: {self.selected_unit.actions_left}/{self.selected_unit.actions_max}")
        
        if self.game.is_over():
            winner = self.game.check_victory()
            if winner:
                winner_name = "Player 1" if winner == self.game.castle1 else "Player 2"
                status.append(f"*** GAME OVER - {winner_name} WINS! ***")
        
        return "\n".join(status)
    
    def render_barracks(self) -> str:
        """
        Render barracks (undeployed units).
        
        Returns:
            Barracks string
        """
        castle = self.game.get_current_castle()
        
        if not castle.barracks:
            return "Barracks: (empty)"
        
        lines = ["Barracks:"]
        for i, unit in enumerate(castle.barracks):
            deploy_cost = getattr(unit, 'deploy_cost', 0)
            lines.append(f"  [{i}] {unit.name} (deploy cost: {deploy_cost})")
        
        return "\n".join(lines)
    
    def parse_command(self, command: str) -> str:
        """
        Parse and execute a command.
        
        Args:
            command: Command string
            
        Returns:
            Result message
        """
        if not command or not command.strip():
            return ""
        
        parts = command.strip().split()
        if not parts:
            return ""
        
        cmd = parts[0].lower()
        
        if cmd == "deploy":
            if len(parts) < 3:
                return "Usage: deploy <barracks_index> <location>"
            try:
                barracks_index = int(parts[1])
                location = self.parse_location(parts[2])
                if location is None:
                    return "Invalid location"
                return self.game.handle_action(constants.ACTION_DEPLOY, barracks_index, location)
            except (ValueError, IndexError):
                return "Invalid deploy command"
        
        elif cmd == "select":
            if len(parts) < 2:
                return "Usage: select <location>"
            location = self.parse_location(parts[1])
            if location is None:
                return "Invalid location"
            unit = self.game.battlefield.get_unit_at(location)
            if not unit:
                return "No unit at location"
            if unit.castle != self.game.get_current_castle():
                return "Not your unit"
            self.selected_unit = unit
            return f"Selected {unit.name} at location {location}"
        
        elif cmd == "move":
            if not self.selected_unit:
                return "No unit selected. Use 'select <location>' first."
            if len(parts) < 2:
                return "Usage: move <location>"
            location = self.parse_location(parts[1])
            if location is None:
                return "Invalid location"
            return self.game.handle_action(constants.ACTION_MOVE, self.selected_unit.location, location)
        
        elif cmd == "attack":
            if not self.selected_unit:
                return "No unit selected. Use 'select <location>' first."
            if len(parts) < 2:
                return "Usage: attack <location>"
            location = self.parse_location(parts[1])
            if location is None:
                return "Invalid location"
            return self.game.handle_action(constants.ACTION_ATTACK, self.selected_unit.location, location)
        
        elif cmd == "end":
            return self.game.handle_action(constants.ACTION_END_TURN, 0, 0)
        
        elif cmd == "help":
            return self._get_help_text()
        
        else:
            return f"Unknown command: {cmd}. Type 'help' for available commands."
    
    def parse_location(self, location_str: str) -> int:
        """
        Parse location from string (supports "x,y" or number).
        
        Args:
            location_str: Location string ("5,5" or "60")
            
        Returns:
            Location number, or None if invalid
        """
        # Try comma-separated coordinates
        if ',' in location_str:
            try:
                parts = location_str.split(',')
                x = int(parts[0])
                y = int(parts[1])
                if x < 0 or x >= constants.BOARD_SIZE:
                    return None
                if y < 0 or y >= constants.BOARD_SIZE:
                    return None
                return BattleField.get_location(x, y)
            except (ValueError, IndexError):
                return None
        
        # Try as direct location number
        try:
            location = int(location_str)
            if location < 0 or location >= constants.BOARD_SIZE * constants.BOARD_SIZE:
                return None
            return location
        except ValueError:
            return None
    
    def _get_help_text(self) -> str:
        """Get help text."""
        return """
Available Commands:
  deploy <index> <location>  - Deploy unit from barracks
  select <location>          - Select a unit
  move <location>            - Move selected unit
  attack <location>          - Attack with selected unit
  end                        - End turn
  help                       - Show this help

Location format: "x,y" (e.g., "5,5") or location number (e.g., "60")
"""

