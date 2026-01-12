"""
RandomAI - AI that makes random valid moves.
"""
import random
from zatikon import constants
from zatikon.game import Game


class RandomAI:
    """
    Random AI that makes random valid moves.
    """
    
    def __init__(self, game: Game, max_moves_per_turn: int = 10):
        """
        Initialize RandomAI.
        
        Args:
            game: Game instance
            max_moves_per_turn: Maximum moves to make per turn
        """
        self.game = game
        self.max_moves_per_turn = max_moves_per_turn
    
    def execute_turn(self):
        """
        Execute a full turn for the current player.
        Makes random valid moves until turn ends.
        
        Returns:
            List of command descriptions executed
        """
        return self.execute_turn_with_log()
    
    def execute_turn_with_log(self):
        """
        Execute a full turn for the current player with logging.
        Makes random valid moves until turn ends.
        
        Returns:
            List of command descriptions executed
        """
        commands_executed = []
        moves_made = 0
        
        while moves_made < self.max_moves_per_turn and not self.game.is_over():
            # Get all valid moves
            moves = self.get_all_valid_moves()
            
            if not moves:
                # No moves available, end turn
                commands_executed.append("END TURN (no moves available)")
                self.game.handle_action(constants.ACTION_END_TURN, 0, 0)
                break
            
            # Choose random move
            move = random.choice(moves)
            
            # Execute move and log it
            if move['action'] == constants.ACTION_DEPLOY:
                unit = self.game.get_current_castle().barracks[move['barracks_index']]
                cmd_desc = f"DEPLOY {unit.name} to location {move['location']}"
                result = self.game.handle_action(
                    constants.ACTION_DEPLOY,
                    move['barracks_index'],
                    move['location']
                )
                if "Invalid" not in result:
                    commands_executed.append(cmd_desc)
            elif move['action'] == constants.ACTION_MOVE:
                unit = self.game.battlefield.get_unit_at(move['from_location'])
                unit_name = unit.name if unit else "Unit"
                cmd_desc = f"MOVE {unit_name} from {move['from_location']} to {move['to_location']}"
                result = self.game.handle_action(
                    constants.ACTION_MOVE,
                    move['from_location'],
                    move['to_location']
                )
                if "Invalid" not in result:
                    commands_executed.append(cmd_desc)
            elif move['action'] == constants.ACTION_ATTACK:
                unit = self.game.battlefield.get_unit_at(move['from_location'])
                target = self.game.battlefield.get_unit_at(move['to_location'])
                unit_name = unit.name if unit else "Unit"
                target_name = target.name if target else "target"
                cmd_desc = f"ATTACK {target_name} at {move['to_location']} with {unit_name}"
                result = self.game.handle_action(
                    constants.ACTION_ATTACK,
                    move['from_location'],
                    move['to_location']
                )
                if "Invalid" not in result:
                    commands_executed.append(cmd_desc)
            elif move['action'] == constants.ACTION_END_TURN:
                commands_executed.append("END TURN")
                self.game.handle_action(constants.ACTION_END_TURN, 0, 0)
                break
            else:
                break
            
            moves_made += 1
            
            # Check if game ended
            if self.game.is_over():
                break
            
            # Random chance to end turn early (but only if we've made some moves)
            if moves_made > 0 and random.random() < 0.2:  # 20% chance to end turn
                commands_executed.append("END TURN (early)")
                self.game.handle_action(constants.ACTION_END_TURN, 0, 0)
                break
        
        return commands_executed
    
    def get_all_valid_moves(self):
        """
        Get all valid moves for current player.
        
        Returns:
            List of move dictionaries
        """
        moves = []
        
        # Check if we can deploy
        deploy_moves = self.get_deploy_moves()
        moves.extend(deploy_moves)
        
        # Check if we can move/attack with deployed units
        unit_moves = self.get_unit_moves()
        moves.extend(unit_moves)
        
        # Always can end turn
        moves.append({'action': constants.ACTION_END_TURN})
        
        return moves
    
    def get_deploy_moves(self):
        """
        Get all valid deploy moves.
        
        Returns:
            List of deploy move dictionaries
        """
        moves = []
        castle = self.game.get_current_castle()
        
        if not castle.barracks:
            return moves
        
        # Get valid deployment locations
        targets = self.game._get_castle_targets(castle)
        
        if not targets:
            return moves
        
        # For each unit in barracks, try each valid location
        for barracks_index, unit in enumerate(castle.barracks):
            deploy_cost = getattr(unit, 'deploy_cost', 0)
            if castle.commands_left >= deploy_cost:
                for location in targets:
                    moves.append({
                        'action': constants.ACTION_DEPLOY,
                        'barracks_index': barracks_index,
                        'location': location
                    })
        
        return moves
    
    def get_unit_moves(self):
        """
        Get all valid moves for deployed units.
        
        Returns:
            List of unit move dictionaries
        """
        moves = []
        castle = self.game.get_current_castle()
        
        # Get all deployed units for current player
        for unit in self.game.battlefield.units:
            if unit.castle != castle:
                continue
            
            if not unit.deployed():
                continue  # Skip inactive units
            
            if unit.dead:
                continue
            
            # Get move targets
            if unit.move_action:
                move_targets = unit.move_action.get_targets()
                for target in move_targets:
                    moves.append({
                        'action': constants.ACTION_MOVE,
                        'from_location': unit.location,
                        'to_location': target
                    })
            
            # Get attack targets
            if unit.attack_action:
                attack_targets = unit.attack_action.get_targets()
                for target in attack_targets:
                    moves.append({
                        'action': constants.ACTION_ATTACK,
                        'from_location': unit.location,
                        'to_location': target
                    })
        
        return moves
    
    def get_random_deploy_move(self):
        """
        Get a random deploy move.
        
        Returns:
            Deploy move dictionary or None
        """
        moves = self.get_deploy_moves()
        if moves:
            return random.choice(moves)
        return None
    
    def get_random_unit_move(self, unit_location: int):
        """
        Get a random move for a unit at a location.
        
        Args:
            unit_location: Location of the unit
            
        Returns:
            Move dictionary or None
        """
        unit = self.game.battlefield.get_unit_at(unit_location)
        if not unit:
            return None
        
        castle = self.game.get_current_castle()
        if unit.castle != castle:
            return None
        
        if not unit.deployed():
            return None
        
        moves = []
        
        # Get move targets
        if unit.move_action:
            move_targets = unit.move_action.get_targets()
            for target in move_targets:
                moves.append({
                    'action': constants.ACTION_MOVE,
                    'from_location': unit.location,
                    'to_location': target
                })
        
        # Get attack targets
        if unit.attack_action:
            attack_targets = unit.attack_action.get_targets()
            for target in attack_targets:
                moves.append({
                    'action': constants.ACTION_ATTACK,
                    'from_location': unit.location,
                    'to_location': target
                })
        
        if moves:
            return random.choice(moves)
        return None

