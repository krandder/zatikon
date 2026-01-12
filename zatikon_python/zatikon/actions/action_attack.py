"""
ActionAttack - Attack action for units.
"""
from typing import List
from zatikon import constants
from zatikon.action import Action


class ActionAttack(Action):
    """
    Attack action allowing units to attack enemies.
    """
    
    def __init__(self, owner, max_attacks: int, cost: int, target_type: int, 
                 range_val: int, attack_type: int = constants.ATTACK_MELEE):
        """
        Initialize an attack action.
        
        Args:
            owner: Unit that owns this action
            max_attacks: Maximum attacks per turn (0 = unlimited)
            cost: Action cost (actions consumed per attack)
            target_type: Target type (TARGET_UNIT_LINE, etc.)
            range_val: Attack range
            attack_type: Type of attack (ATTACK_MELEE, ATTACK_ARROW, etc.)
        """
        super().__init__(owner, constants.ACTION_ATTACK)
        self.max = max_attacks
        self.remaining = max_attacks
        self.cost = cost
        self.target_type = target_type
        self.range = range_val
        self.attack_type = attack_type
    
    def get_remaining(self) -> int:
        """
        Get remaining attacks.
        
        Returns:
            Number of remaining attacks
        """
        # If unit can't act, no attacks available
        if not self.owner.deployed():
            return 0
        
        # If no commands left, no attacks available
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
        Validate if the attack can be performed.
        
        Args:
            target: Target location
            
        Returns:
            True if attack is valid
        """
        # Check if any attacks remaining
        if self.get_remaining() <= 0:
            return False
        
        # Check if unit is deployed
        if not self.owner.deployed():
            return False
        
        # If no target type, all is well (shouldn't happen for attack)
        if self.target_type == constants.TARGET_NONE:
            return True
        
        # Check if target is in valid targets list
        targets = self.get_targets()
        return target in targets
    
    def get_targets(self) -> List[int]:
        """
        Get valid attack targets.
        
        Returns:
            List of valid target locations
        """
        if not self.owner.battlefield or self.owner.location == -1:
            return []
        
        # Use BattleField.get_targets for proper targeting
        # Attacks target enemy units only
        return self.owner.battlefield.get_targets(
            self.owner,
            self.target_type,
            self.range,
            include_empty=False,  # Attacks don't target empty spaces
            organic=True,
            inorganic=True,
            selection_type=constants.SELECTION_ENEMY,  # Enemy units only
            castle=self.owner.castle
        )
    
    def perform(self, target: int) -> str:
        """
        Perform the attack.
        
        Args:
            target: Target location
            
        Returns:
            Result message
        """
        if not self.validate(target):
            return "Invalid action"
        
        # Get the victim
        if not self.owner.battlefield:
            return "Invalid action"
        
        victim = self.owner.battlefield.get_unit_at(target)
        if victim is None:
            return "Invalid action"
        
        # Deduct costs
        self.owner.deduct_actions(self.cost)
        self.remaining -= 1
        if self.owner.castle:
            self.owner.castle.deduct_commands(1)
        
        # Fire PREVIEW_ACTION event
        outcome = self.owner.battlefield.event(
            constants.EVENT_PREVIEW_ACTION,
            self.owner,
            victim,
            constants.ACTION_ATTACK,
            constants.EVENT_NONE,
            constants.EVENT_OK
        )
        
        damage_dealt = 0
        
        # If event cancelled or ended, don't deal damage
        if outcome == constants.EVENT_END:
            return ""
        
        if outcome == constants.EVENT_OK:
            # Deal damage
            damage_dealt = victim.take_damage(self.owner, self.owner.get_damage())
        
        # If cancelled or parried, return early
        if outcome in [constants.EVENT_CANCEL, constants.EVENT_PARRY]:
            return f"{self.owner.name} attacked {victim.name}"
        
        # Fire WITNESS_ACTION event
        self.owner.battlefield.event(
            constants.EVENT_WITNESS_ACTION,
            self.owner,
            victim,
            constants.ACTION_ATTACK,
            constants.EVENT_NONE,
            constants.EVENT_OK
        )
        
        # Return result message
        if victim.is_dead():
            return f"{self.owner.name} killed {victim.name}"
        else:
            return f"{self.owner.name} attacked {victim.name} for {damage_dealt} damage"
    
    def refresh(self):
        """Refresh remaining attacks at start of turn."""
        self.remaining = self.max
    
    def get_name(self) -> str:
        """Get action name."""
        return "Attack"

