"""
ActionMove - Movement action for units.
"""
from typing import List
from zatikon import constants
from zatikon.action import Action
from zatikon.battlefield import BattleField


class ActionMove(Action):
    """
    Movement action allowing units to move on the board.
    """
    
    def __init__(self, owner, max_moves: int, cost: int, target_type: int, range_val: int):
        """
        Initialize a movement action.
        
        Args:
            owner: Unit that owns this action
            max_moves: Maximum moves per turn (0 = unlimited based on actions)
            cost: Action cost (actions consumed per move)
            target_type: Target type (TARGET_LOCATION_LINE, etc.)
            range_val: Movement range
        """
        super().__init__(owner, constants.ACTION_MOVE)
        self.max = max_moves
        self.remaining = max_moves
        self.cost = cost
        self.target_type = target_type
        self.range = range_val
    
    def get_remaining(self) -> int:
        """
        Get remaining moves.
        
        Returns:
            Number of remaining moves
        """
        # If unit can't act, no moves available
        if not self.owner.deployed():
            return 0
        
        # If no commands left, no moves available
        if self.owner.castle and self.owner.castle.get_commands_left() <= 0:
            return 0
        
        # If max is 0, calculate based on actions_left
        if self.max <= 0:
            if self.cost > 0:
                return self.owner.actions_left // self.cost
            return self.owner.actions_left
        
        return self.remaining
    
    def validate(self, target: int) -> bool:
        """
        Validate if the move can be performed.
        
        Args:
            target: Target location
            
        Returns:
            True if move is valid
        """
        # Check if any moves remaining
        if self.get_remaining() <= 0:
            return False
        
        # Check if unit is deployed
        if not self.owner.deployed():
            return False
        
        # If no target type, all is well (shouldn't happen for move)
        if self.target_type == constants.TARGET_NONE:
            return True
        
        # Check if target is in valid targets list
        targets = self.get_targets()
        return target in targets
    
    def get_targets(self) -> List[int]:
        """
        Get valid movement targets.
        
        Returns:
            List of valid target locations
        """
        if not self.owner.battlefield or self.owner.location == -1:
            return []
        
        # Use BattleField.get_targets for proper targeting
        return self.owner.battlefield.get_targets(
            self.owner,
            self.target_type,
            self.range,
            include_empty=True,  # Movement can target empty spaces
            organic=True,
            inorganic=True,
            selection_type=constants.SELECTION_MOVE,
            castle=self.owner.castle
        )
    
    def perform(self, target: int) -> str:
        """
        Perform the movement.
        
        Args:
            target: Target location
            
        Returns:
            Result message
        """
        if not self.validate(target):
            return "Invalid move"
        
        # Deduct cost
        self.owner.deduct_actions(self.cost)
        self.remaining -= 1
        if self.owner.castle:
            self.owner.castle.deduct_commands(1)
        
        # Move the unit via battlefield
        if self.owner.battlefield:
            result = self.owner.battlefield.move(self.owner, self.owner.location, target)
            if result == constants.EVENT_CANCEL:
                return "Move cancelled"
        else:
            self.owner.set_location(target)
        
        # Check for powerup pickup
        unit_at = self.owner.battlefield.get_unit_at(target) if self.owner.battlefield else None
        if unit_at and hasattr(unit_at, 'is_powerup') and unit_at.is_powerup():
            # Powerup pickup logic will be implemented later
            pass
        
        # Check for victory (unit on enemy castle)
        if self.owner.battlefield:
            enemy_castle = self.owner.battlefield.castle2 if self.owner.castle == self.owner.battlefield.castle1 else self.owner.battlefield.castle1
            if target == enemy_castle.location:
                # Victory logic will be implemented later
                return f"{self.owner.name} captured the enemy castle!"
        
        x = BattleField.get_x(target)
        y = BattleField.get_y(target)
        return f"{self.owner.name} moved to ({x+1}, {y+1})"
    
    def refresh(self):
        """Refresh remaining moves at start of turn."""
        self.remaining = self.max
    
    def get_name(self) -> str:
        """Get action name."""
        return "Move"

