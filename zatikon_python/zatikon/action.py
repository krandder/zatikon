"""
Action - Base class for all unit actions (move, attack, spell, skill).
"""
from abc import ABC, abstractmethod
from typing import List
from zatikon import constants


class Action(ABC):
    """
    Abstract base class for all unit actions.
    Actions include: Move, Attack, Spell, Skill
    """
    
    def __init__(self, owner, action_type: int):
        """
        Initialize an action.
        
        Args:
            owner: Unit that owns this action
            action_type: Type of action (ACTION_MOVE, ACTION_ATTACK, etc.)
        """
        self.owner = owner
        self.action_type = action_type
    
    @abstractmethod
    def perform(self, target: int) -> str:
        """
        Perform the action on a target.
        
        Args:
            target: Target location or unit ID
            
        Returns:
            Result message string
        """
        pass
    
    @abstractmethod
    def validate(self, target: int) -> bool:
        """
        Validate if the action can be performed on the target.
        
        Args:
            target: Target location or unit ID
            
        Returns:
            True if action is valid
        """
        pass
    
    @abstractmethod
    def get_targets(self) -> List[int]:
        """
        Get list of valid targets for this action.
        
        Returns:
            List of target locations/IDs
        """
        pass
    
    @abstractmethod
    def get_remaining(self) -> int:
        """
        Get remaining uses of this action.
        
        Returns:
            Number of remaining uses
        """
        pass
    
    def refresh(self):
        """
        Refresh the action at the start of a new turn.
        Override in subclasses if needed.
        """
        pass
    
    def start_turn(self):
        """
        Called at the start of a turn.
        Override in subclasses if needed.
        """
        pass
    
    def get_type(self) -> int:
        """
        Get the action type.
        
        Returns:
            Action type constant
        """
        return self.action_type
    
    def get_name(self) -> str:
        """
        Get the action name.
        
        Returns:
            Action name string
        """
        return "Action"

