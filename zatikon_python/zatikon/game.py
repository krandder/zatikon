"""
Game - Main game controller managing turn flow and game state.
"""
from zatikon import constants
from zatikon.castle import Castle
from zatikon.battlefield import BattleField


class Game:
    """
    Main game controller.
    Manages turn flow, game state, and action handling.
    """
    
    def __init__(self):
        """Initialize a new game."""
        # Create castles
        self.castle1 = Castle(constants.TEAM_1)
        self.castle2 = Castle(constants.TEAM_2)
        
        # Create battlefield
        self.battlefield = BattleField(self.castle1, self.castle2)
        
        # Set castle locations (matching Java implementation)
        # Castle 1: bottom center (5, 10) = location 115
        # Castle 2: top center (5, 0) = location 5
        self.castle1.set_location(BattleField.get_location(5, 10))
        self.castle2.set_location(BattleField.get_location(5, 0))
        
        # Game state
        self.current_player = constants.TEAM_1
        self.turn_number = 0
        self._over = False
        self._winner = None  # Store the winning castle when game ends
    
    def get_current_castle(self) -> Castle:
        """
        Get the castle for the current player.
        
        Returns:
            Current player's castle
        """
        if self.current_player == constants.TEAM_1:
            return self.castle1
        else:
            return self.castle2
    
    def get_enemy_castle(self) -> Castle:
        """
        Get the enemy castle.
        
        Returns:
            Enemy player's castle
        """
        if self.current_player == constants.TEAM_1:
            return self.castle2
        else:
            return self.castle1
    
    def start_turn(self):
        """Start the current player's turn."""
        castle = self.get_current_castle()
        
        # Refresh castle (commands, modifiers)
        castle.refresh(self.current_player)
        
        # Start turn (sets armor/power to permanent values)
        castle.start_turn(self.current_player)
        
        # Refresh all units on battlefield
        for unit in castle.units_out:
            if hasattr(unit, 'refresh'):
                unit.refresh()
    
    def end_turn(self):
        """
        End the current player's turn and switch to next player.
        """
        # Refresh the castle that just ended
        castle = self.get_current_castle()
        castle.refresh(self.current_player)
        
        # Switch to next player
        if self.current_player == constants.TEAM_1:
            self.current_player = constants.TEAM_2
        else:
            self.current_player = constants.TEAM_1
        
        # Increment turn counter
        self.turn_number += 1
        
        # Start next player's turn
        self.start_turn()
    
    def check_victory(self):
        """
        Check if victory condition is met.
        
        Returns:
            Winning castle if victory, None otherwise
        """
        # If game is already over, return stored winner
        if self._over:
            return self._winner
        
        # Check all units on battlefield
        for unit in self.battlefield.units:
            if unit.dead:
                continue

            if not unit.can_win:
                continue

            # Check if unit is on enemy castle
            # Enemy castle is the one NOT owned by this unit's team
            enemy_castle = self.castle2 if unit.team == constants.TEAM_1 else self.castle1
            if unit.location == enemy_castle.location:
                # Store the winner and mark game as over
                self._winner = unit.castle
                self._over = True
                return self._winner
        
        return None
    
    def is_over(self) -> bool:
        """
        Check if game is over.
        
        Returns:
            True if game is over
        """
        return self._over
    
    def get_current_player(self) -> int:
        """
        Get current player team.
        
        Returns:
            Current player team (TEAM_1 or TEAM_2)
        """
        return self.current_player
    
    def get_turn_number(self) -> int:
        """
        Get current turn number.
        
        Returns:
            Turn number (starts at 0)
        """
        return self.turn_number
    
    def handle_action(self, action_type: int, actor_location: int, target_location: int) -> str:
        """
        Handle a game action.
        
        Args:
            action_type: Type of action (ACTION_DEPLOY, ACTION_MOVE, etc.)
            actor_location: Location of acting unit (or barracks index for deploy)
            target_location: Target location
            
        Returns:
            Result message
        """
        if self._over:
            return "Game is over"
        
        if action_type == constants.ACTION_DEPLOY:
            return self._handle_deploy(actor_location, target_location)
        elif action_type == constants.ACTION_END_TURN:
            self.end_turn()
            return "Turn ended"
        elif action_type == constants.ACTION_MOVE:
            return self._handle_move(actor_location, target_location)
        elif action_type == constants.ACTION_ATTACK:
            return self._handle_attack(actor_location, target_location)
        else:
            return "Unknown action"
    
    def _handle_deploy(self, barracks_index: int, location: int) -> str:
        """Handle deployment action."""
        castle = self.get_current_castle()
        
        # Validate barracks index
        if barracks_index < 0 or barracks_index >= len(castle.barracks):
            return "Invalid unit index"
        
        unit = castle.barracks[barracks_index]
        
        # Get valid deployment locations
        targets = self._get_castle_targets(castle)
        if location not in targets:
            return "Invalid deployment location"
        
        # Check deploy cost
        deploy_cost = getattr(unit, 'deploy_cost', 0)
        if castle.commands_left < deploy_cost:
            return "Not enough commands"
        
        # Deploy the unit
        castle.remove_unit(unit)
        unit.battlefield = self.battlefield
        unit.location = location
        unit._deployed = False  # Units start inactive when deployed
        self.battlefield.add_unit(unit)
        castle.add_unit_out(self.current_player, unit)
        castle.deduct_commands(deploy_cost)
        
        # Check for victory
        self.check_victory()
        
        return f"Deployed {unit.name} to location {location}"
    
    def _handle_move(self, from_location: int, to_location: int) -> str:
        """Handle move action."""
        unit = self.battlefield.get_unit_at(from_location)
        if not unit:
            return "No unit at location"
        
        if unit.castle != self.get_current_castle():
            return "Not your unit"
        
        if not unit.deployed():
            return "Unit not deployed"
        
        # Use move action
        if not unit.move_action:
            return "Unit has no move action"
        
        result = unit.move_action.perform(to_location)
        
        # Check for victory
        self.check_victory()
        
        return result
    
    def _handle_attack(self, attacker_location: int, target_location: int) -> str:
        """Handle attack action."""
        attacker = self.battlefield.get_unit_at(attacker_location)
        if not attacker:
            return "No unit at location"
        
        if attacker.castle != self.get_current_castle():
            return "Not your unit"
        
        if not attacker.deployed():
            return "Unit not deployed"
        
        # Use attack action
        if not attacker.attack_action:
            return "Unit has no attack action"
        
        result = attacker.attack_action.perform(target_location)
        
        # Check for victory
        self.check_victory()
        
        return result
    
    def _get_castle_targets(self, castle: Castle):
        """
        Get valid deployment locations for a castle.
        
        Args:
            castle: Castle to get targets for
            
        Returns:
            List of valid deployment locations
        """
        if not castle.battlefield:
            return []
        
        targets = []
        castle_location = castle.location
        castle_x = BattleField.get_x(castle_location)
        castle_y = BattleField.get_y(castle_location)
        
        # Get locations within range 1 (adjacent)
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue  # Skip castle location itself
                
                x = castle_x + dx
                y = castle_y + dy
                
                # Check bounds
                if x < 0 or x >= constants.BOARD_SIZE:
                    continue
                if y < 0 or y >= constants.BOARD_SIZE:
                    continue
                
                location = BattleField.get_location(x, y)
                
                # Check if location is empty (or has powerup)
                unit_at = self.battlefield.get_unit_at(location)
                if unit_at is None:
                    targets.append(location)
        
        return targets

