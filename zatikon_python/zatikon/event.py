"""
Event - Base interface for game events.
"""
from abc import ABC, abstractmethod
from zatikon import constants


class Event(ABC):
    """
    Base interface for all game events.
    Events can intercept and modify game actions (PREVIEW) or react to them (WITNESS).
    """
    
    @abstractmethod
    def get_event_type(self) -> int:
        """
        Get the type of event this is.
        
        Returns:
            Event type constant (EVENT_PREVIEW_MOVE, etc.)
        """
        pass
    
    @abstractmethod
    def perform(self, source, target, val1: int, val2: int, default_result: int) -> int:
        """
        Perform the event.
        
        Args:
            source: Unit that triggered the event
            target: Unit that is the target (may be None)
            val1: First value (action type, etc.)
            val2: Second value (damage amount, etc.)
            default_result: Default result if event doesn't modify
            
        Returns:
            Event result (may modify default_result)
        """
        pass
    
    @abstractmethod
    def get_owner(self):
        """
        Get the unit that owns this event.
        
        Returns:
            Unit that owns this event
        """
        pass
    
    @abstractmethod
    def get_priority(self) -> int:
        """
        Get the priority of this event (higher = processed first).
        
        Returns:
            Priority value
        """
        pass

