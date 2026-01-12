"""
Unit - Base class for all units in the game.
"""
from zatikon import constants


class Unit:
    """
    Base class for all units in Zatikon.
    Provides core functionality for stats, state, and battlefield integration.
    """
    
    def __init__(self, castle):
        """
        Initialize a new unit.
        
        Args:
            castle: Castle that owns this unit
        """
        self.castle = castle
        self.battlefield = None
        
        # Basic stats
        self.life = 0
        self.life_max = 0
        self.armor = 0
        self.damage = 0
        self.actions_left = 0
        self.actions_max = 0
        
        # Location
        self.location = -1
        self.last_location = -1
        
        # Team
        self.team = constants.TEAM_NONE
        
        # State flags
        self.dead = False
        self._deployed = False  # Internal flag
        self.stunned = False
        self.organic = True
        
        # Unit properties
        self.unit_id = None
        self.name = ""
        self.deploy_cost = 0  # Cost to deploy (in commands)
        self.can_win = True  # Can this unit capture enemy castle?
        
        # Actions (will be populated by subclasses)
        self.actions = []
        self.move_action = None
        self.attack_action = None
        
        # Events (organized by event type)
        self.events = {}  # Dict[int, List[Event]]
        
        # Sequence number for event ordering
        self.sequence = -1
    
    def get_targets(self, target_type: int) -> list:
        """
        Get bonus targets for this unit (override in subclasses).
        
        Args:
            target_type: Type of targeting
            
        Returns:
            List of bonus target locations
        """
        return []
    
    def targetable(self, looker) -> bool:
        """
        Check if this unit can be targeted by another unit.
        
        Args:
            looker: Unit trying to target this unit
            
        Returns:
            True if targetable
        """
        if self.dead:
            return False
        return True
    
    def set_life(self, life: int):
        """Set unit's current life."""
        self.life = life
    
    def set_life_max(self, life_max: int):
        """Set unit's maximum life."""
        self.life_max = life_max
    
    def set_armor(self, armor: int):
        """Set unit's base armor."""
        self.armor = armor
    
    def set_damage(self, damage: int):
        """Set unit's base damage."""
        self.damage = damage
    
    def get_armor(self) -> int:
        """
        Get unit's armor (base + castle modifier, max 2).
        
        Returns:
            Total armor value
        """
        if not self.organic:
            return max(0, self.armor)
        
        # Organic units get castle armor modifier
        total_armor = self.armor
        if self.castle:
            total_armor += self.castle.armor
        
        # Cap at 2
        return max(0, min(2, total_armor))
    
    def get_damage(self) -> int:
        """
        Get unit's damage (base + castle modifier).
        
        Returns:
            Total damage value
        """
        if not self.organic:
            return self.damage
        
        # Organic units get castle power modifier
        total_damage = self.damage
        if self.castle:
            total_damage += self.castle.power
        
        return max(0, total_damage)
    
    def set_location(self, location: int):
        """
        Set unit's location on the board.
        
        Args:
            location: Location number (0-120)
        """
        self.last_location = self.location
        self.location = location
    
    def set_team(self, team: int):
        """
        Set unit's team.
        
        Args:
            team: Team number (TEAM_1 or TEAM_2)
        """
        self.team = team
    
    def is_dead(self) -> bool:
        """
        Check if unit is dead.
        
        Returns:
            True if unit is dead
        """
        return self.dead
    
    def deployed(self) -> bool:
        """
        Check if unit is deployed (not stunned).
        
        Returns:
            True if unit is deployed and not stunned
        """
        return self._deployed and not self.stunned
    
    def stun(self):
        """Stun the unit (prevents actions)."""
        self.stunned = True
    
    def deduct_actions(self, amount: int):
        """
        Deduct actions from the unit.
        
        Args:
            amount: Number of actions to deduct
        """
        self.actions_left -= amount
        if self.actions_left < 0:
            self.actions_left = 0
    
    def refresh(self):
        """
        Refresh the unit at the start of a new turn.
        Resets actions, sets deployed flag, clears stun.
        """
        self._deployed = True
        self.stunned = False
        self.actions_left = self.actions_max
        
        # Refresh all actions
        for action in self.actions:
            if hasattr(action, 'refresh'):
                action.refresh()
    
    def set_battlefield(self, battlefield):
        """
        Set the battlefield reference.
        
        Args:
            battlefield: BattleField instance
        """
        self.battlefield = battlefield
        # Get sequence number when added to battlefield
        if battlefield:
            self.sequence = battlefield.get_sequence()
    
    def add_event(self, event):
        """
        Add an event to this unit.
        
        Args:
            event: Event instance
        """
        event_type = event.get_event_type()
        if event_type not in self.events:
            self.events[event_type] = []
        self.events[event_type].append(event)
    
    def remove_event(self, event):
        """
        Remove an event from this unit.
        
        Args:
            event: Event instance to remove
        """
        event_type = event.get_event_type()
        if event_type in self.events:
            if event in self.events[event_type]:
                self.events[event_type].remove(event)
    
    def get_events(self, event_type: int):
        """
        Get all events of a specific type.
        
        Args:
            event_type: Event type constant
            
        Returns:
            List of events of that type, or empty list if none
        """
        return self.events.get(event_type, [])
    
    def take_damage(self, source, raw_amount: int) -> int:
        """
        Deal damage to this unit.
        Applies armor reduction and checks for death.
        
        Args:
            source: Unit dealing the damage
            raw_amount: Raw damage amount before armor
            
        Returns:
            Actual damage dealt (after armor)
        """
        # Fire PREVIEW_DAMAGE event
        if self.battlefield:
            modified_amount = self.battlefield.event(
                constants.EVENT_PREVIEW_DAMAGE,
                source,
                self,
                constants.EVENT_NONE,
                constants.EVENT_NONE,
                raw_amount
            )
            
            # If cancelled, no damage
            if modified_amount == constants.EVENT_CANCEL:
                return 0
            
            raw_amount = modified_amount
        
        # Calculate damage after armor
        armor = self.get_armor()
        old_life = self.life
        damage_dealt = max(0, raw_amount - armor)
        
        # Apply damage
        self.life -= damage_dealt
        
        # Check for death
        if self.life <= 0:
            self.die(True, source)
        
        # Fire WITNESS_DAMAGE event
        if self.battlefield:
            # Amount witnessed is actual life lost (may be less than damage if unit died)
            witness_amount = min(damage_dealt, old_life)
            self.battlefield.event(
                constants.EVENT_WITNESS_DAMAGE,
                source,
                self,
                witness_amount,
                constants.EVENT_NONE,
                constants.EVENT_OK
            )
        
        return damage_dealt
    
    def die(self, death: bool, source):
        """
        Kill the unit.
        
        Args:
            death: True if this is a real death (creates grave)
            source: Unit that caused the death
        """
        self.dead = True
        
        # Fire PREVIEW_DEATH event (can cancel death)
        if death and self.battlefield:
            result = self.battlefield.event(
                constants.EVENT_PREVIEW_DEATH,
                self,
                source,
                constants.EVENT_NONE,
                constants.EVENT_NONE,
                constants.EVENT_OK
            )
            
            # If cancelled, un-die
            if result == constants.EVENT_CANCEL:
                self.dead = False
                return
        
        if self.battlefield:
            # Remove from battlefield
            self.battlefield.remove_unit(self)
            
            # Add grave if organic and real death
            if death and self.organic:
                self.battlefield.add_grave(self.location)
        
        if self.castle:
            # Remove from castle's units_out
            if self in self.castle.units_out:
                self.castle.units_out.remove(self)
            
            # Add to graveyard if organic and real death
            if death and self.organic:
                self.castle.add_graveyard(self)
        
        # Fire WITNESS_DEATH event
        if self.battlefield:
            death_type = constants.EVENT_TRUE if death else constants.EVENT_FALSE
            self.battlefield.event(
                constants.EVENT_WITNESS_DEATH,
                self,
                source,
                death_type,
                constants.EVENT_NONE,
                constants.EVENT_OK
            )

