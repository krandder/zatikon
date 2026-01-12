"""
UnitFactory - Factory for creating unit instances.
"""
from zatikon import constants
from zatikon.unit import Unit
from zatikon.actions.action_move import ActionMove
from zatikon.actions.action_attack import ActionAttack


class UnitFactory:
    """
    Factory for creating unit instances.
    """
    
    @staticmethod
    def create_unit(unit_id: int, castle):
        """
        Create a unit of the specified type.
        
        Args:
            unit_id: Unit ID constant (UNIT_FOOTMAN, etc.)
            castle: Castle that owns this unit
            
        Returns:
            Unit instance
            
        Raises:
            ValueError: If unit_id is invalid
        """
        if unit_id == constants.UNIT_FOOTMAN:
            return UnitFootman(castle)
        elif unit_id == constants.UNIT_BEAR:
            return UnitBear(castle)
        else:
            raise ValueError(f"Unknown unit ID: {unit_id}")


class UnitFootman(Unit):
    """
    Footman - Basic melee unit.
    """
    
    def __init__(self, castle):
        super().__init__(castle)
        
        # Set unit properties
        self.unit_id = constants.UNIT_FOOTMAN
        self.name = "Footman"
        
        # Stats
        self.damage = 3
        self.armor = 2
        self.life = 4
        self.life_max = 4
        self.actions_left = 2
        self.actions_max = 2
        
        # Organic unit
        self.organic = True
        
        # Create actions
        self.move_action = ActionMove(
            self,
            max_moves=0,  # 0 = unlimited moves per turn
            cost=1,
            target_type=constants.TARGET_LOCATION_LINE,
            range_val=1
        )
        
        # Footman uses ActionRush (move + attack), but for now use ActionAttack
        # TODO: Implement ActionRush
        self.attack_action = ActionAttack(
            self,
            max_attacks=0,  # 0 = unlimited attacks per turn
            cost=1,
            target_type=constants.TARGET_UNIT_LINE,
            range_val=1,
            attack_type=constants.ATTACK_MELEE
        )
        
        # Add actions to list
        self.actions.append(self.move_action)
        self.actions.append(self.attack_action)
        
        # TODO: Add EventInterference


class UnitBear(Unit):
    """
    Bear - Strong melee unit.
    """
    
    def __init__(self, castle):
        super().__init__(castle)
        
        # Set unit properties
        self.unit_id = constants.UNIT_BEAR
        self.name = "Bear"
        
        # Stats
        self.damage = 4
        self.armor = 1
        self.life = 6
        self.life_max = 6
        self.actions_left = 2
        self.actions_max = 2
        self.deploy_cost = 1  # Bear costs 1 command to deploy
        
        # Organic unit
        self.organic = True
        
        # Create actions
        self.move_action = ActionMove(
            self,
            max_moves=0,
            cost=1,
            target_type=constants.TARGET_LOCATION_LINE,
            range_val=1
        )
        
        self.attack_action = ActionAttack(
            self,
            max_attacks=0,
            cost=1,
            target_type=constants.TARGET_UNIT_LINE,
            range_val=1,
            attack_type=constants.ATTACK_MELEE
        )
        
        # Add actions to list
        self.actions.append(self.move_action)
        self.actions.append(self.attack_action)
        
        # TODO: Add EventStun

