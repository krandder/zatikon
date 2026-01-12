"""
BattleField - The game board and coordinate system.
"""
from typing import List
from zatikon import constants


class BattleField:
    """
    Represents the game board and handles coordinate conversions.
    The board is an 11x11 grid (121 locations, numbered 0-120).
    """
    
    def __init__(self, castle1, castle2):
        """
        Initialize a new BattleField with two castles.
        
        Args:
            castle1: First player's castle
            castle2: Second player's castle
        """
        self.castle1 = castle1
        self.castle2 = castle2
        self.units = []  # List of units on the battlefield
        self.sequence = 0  # Sequence counter for unit ordering
        self.graves = []  # Locations where units have died
        
        # Set battlefield reference in castles
        castle1.set_battlefield(self)
        castle2.set_battlefield(self)
    
    @staticmethod
    def get_x(location: int) -> int:
        """
        Convert a location number to its x coordinate.
        
        Args:
            location: Location number (0-120)
            
        Returns:
            X coordinate (0-10)
        """
        return location % constants.BOARD_SIZE
    
    @staticmethod
    def get_y(location: int) -> int:
        """
        Convert a location number to its y coordinate.
        
        Args:
            location: Location number (0-120)
            
        Returns:
            Y coordinate (0-10)
        """
        return location // constants.BOARD_SIZE
    
    @staticmethod
    def get_location(x: int, y: int) -> int:
        """
        Convert x,y coordinates to a location number.
        
        Args:
            x: X coordinate (0-10)
            y: Y coordinate (0-10)
            
        Returns:
            Location number (0-120)
        """
        return y * constants.BOARD_SIZE + x
    
    @staticmethod
    def get_distance(location1: int, location2: int) -> int:
        """
        Calculate Chebyshev (chessboard) distance between two locations.
        
        Args:
            location1: First location (0-120)
            location2: Second location (0-120)
            
        Returns:
            Distance (max of x and y differences)
        """
        x1 = BattleField.get_x(location1)
        x2 = BattleField.get_x(location2)
        y1 = BattleField.get_y(location1)
        y2 = BattleField.get_y(location2)
        
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        
        return max(dx, dy)
    
    def get_sequence(self) -> int:
        """
        Get a new sequence number for unit ordering.
        
        Returns:
            Next sequence number
        """
        seq = self.sequence
        self.sequence += 1
        return seq
    
    def add_unit(self, unit):
        """Add a unit to the battlefield."""
        self.units.append(unit)
    
    def remove_unit(self, unit):
        """Remove a unit from the battlefield."""
        if unit in self.units:
            self.units.remove(unit)
    
    def get_unit_at(self, location: int):
        """
        Get the unit at a specific location.
        
        Args:
            location: Location to check
            
        Returns:
            Unit at location, or None if empty
        """
        for unit in self.units:
            if unit.location == location:
                return unit
        return None
    
    def get_units_at(self, location: int):
        """
        Get all units at a specific location (should normally be 0 or 1).
        
        Args:
            location: Location to check
            
        Returns:
            List of units at location
        """
        return [unit for unit in self.units if unit.location == location]
    
    def add_grave(self, location: int):
        """
        Add a grave marker at a location (for organic unit deaths).
        
        Args:
            location: Location where unit died
        """
        if location not in self.graves:
            if location != self.castle1.location and location != self.castle2.location:
                self.graves.append(location)
    
    def remove_grave(self, location: int):
        """
        Remove a grave marker from a location.
        
        Args:
            location: Location to remove grave from
        """
        if location in self.graves:
            self.graves.remove(location)
    
    def move(self, unit, from_location: int, to_location: int) -> int:
        """
        Move a unit from one location to another.
        Fires PREVIEW_MOVE and WITNESS_MOVE events.
        
        Args:
            unit: Unit to move
            from_location: Source location
            to_location: Destination location
            
        Returns:
            Event result (EVENT_OK if successful, EVENT_CANCEL if cancelled)
        """
        # Fire PREVIEW_MOVE event
        result = self.event(
            constants.EVENT_PREVIEW_MOVE,
            unit,
            None,
            from_location,
            to_location,
            constants.EVENT_OK
        )
        
        # If cancelled, don't move
        if result == constants.EVENT_CANCEL:
            return constants.EVENT_CANCEL
        
        # Move the unit
        unit.set_location(to_location)
        
        # Fire WITNESS_MOVE event
        self.event(
            constants.EVENT_WITNESS_MOVE,
            unit,
            None,
            from_location,
            to_location,
            constants.EVENT_OK
        )
        
        return constants.EVENT_OK
    
    def event(self, event_type: int, source, target, val1: int, val2: int, default_result: int) -> int:
        """
        Fire an event and process all registered handlers.
        Events are processed in priority order (higher priority first).
        Events with same priority are ordered by unit sequence.
        
        Args:
            event_type: Type of event to fire
            source: Unit that triggered the event
            target: Target unit (may be None)
            val1: First value (action type, from_location, etc.)
            val2: Second value (damage amount, to_location, etc.)
            default_result: Default result if no events modify it
            
        Returns:
            Event result (may be modified by event handlers)
        """
        result = default_result
        events_to_process = []
        
        # Collect all events of this type from all units
        for unit in self.units:
            unit_events = unit.get_events(event_type)
            for event in unit_events:
                self._add_event_sorted(events_to_process, event)
        
        # Process events in order
        for event in events_to_process:
            result = event.perform(source, target, val1, val2, result)
            
            # Stop processing if event cancels or ends
            if result in [constants.EVENT_CANCEL, constants.EVENT_DEAD, 
                         constants.EVENT_END, constants.EVENT_PARRY]:
                return result
        
        return result
    
    def _add_event_sorted(self, events_list, event):
        """
        Add an event to the list in priority order.
        Higher priority events come first.
        Events with same priority are ordered by unit sequence.
        
        Args:
            events_list: List to add event to
            event: Event to add
        """
        event_priority = event.get_priority()
        event_owner = event.get_owner()
        event_sequence = event_owner.sequence if event_owner else 0
        
        # Find insertion point
        for i, existing_event in enumerate(events_list):
            existing_priority = existing_event.get_priority()
            existing_owner = existing_event.get_owner()
            existing_sequence = existing_owner.sequence if existing_owner else 0
            
            # Higher priority first
            if event_priority > existing_priority:
                events_list.insert(i, event)
                return
            
            # Same priority: lower sequence first
            if event_priority == existing_priority:
                if event_sequence < existing_sequence:
                    events_list.insert(i, event)
                    return
        
        # Add to end if not inserted
        events_list.append(event)
    
    def get_targets(self, unit, target_type: int, range_val: int, 
                    include_empty: bool, organic: bool, inorganic: bool,
                    selection_type: int, castle) -> List[int]:
        """
        Get valid targets for an action.
        
        Args:
            unit: Unit performing the action
            target_type: Type of targeting (TARGET_LOCATION_LINE, etc.)
            range_val: Range of the action
            include_empty: Include empty locations
            organic: Include organic units
            inorganic: Include inorganic units
            selection_type: SELECTION_FRIENDLY, SELECTION_ENEMY, SELECTION_BOTH, SELECTION_MOVE
            castle: Castle of the acting unit
            
        Returns:
            List of valid target locations
        """
        targets = []
        
        if unit.location == -1:
            return targets
        
        # Handle different target types
        # For LOCATION types: include_empty=True, include_units=False (locations only)
        # For UNIT types: include_empty=include_empty param, include_units=True
        if target_type == constants.TARGET_LOCATION_LINE:
            targets = self._get_line_targets(
                unit, unit.location, range_val, False, True, False,
                organic, inorganic, selection_type, castle
            )
        elif target_type == constants.TARGET_UNIT_LINE:
            targets = self._get_line_targets(
                unit, unit.location, range_val, False, include_empty, True,
                organic, inorganic, selection_type, castle
            )
        elif target_type == constants.TARGET_LOCATION_LINE_JUMP:
            targets = self._get_line_targets(
                unit, unit.location, range_val, True, True, False,
                organic, inorganic, selection_type, castle
            )
        elif target_type == constants.TARGET_UNIT_LINE_JUMP:
            targets = self._get_line_targets(
                unit, unit.location, range_val, True, include_empty, True,
                organic, inorganic, selection_type, castle
            )
        elif target_type == constants.TARGET_LOCATION_AREA:
            targets = self._get_area_targets(
                unit, unit.location, range_val, True, False,
                organic, inorganic, selection_type, castle
            )
        elif target_type == constants.TARGET_UNIT_AREA:
            targets = self._get_area_targets(
                unit, unit.location, range_val, include_empty, True,
                organic, inorganic, selection_type, castle
            )
        elif target_type == constants.TARGET_ANY_LINE:
            targets = self._get_all_lines(
                unit, unit.location, range_val, False, True, True,
                organic, inorganic, selection_type, castle
            )
        elif target_type == constants.TARGET_ANY_LINE_JUMP:
            targets = self._get_all_lines(
                unit, unit.location, range_val, True, True, True,
                organic, inorganic, selection_type, castle
            )
        elif target_type == constants.TARGET_ANY_AREA:
            targets = self._get_area_targets(
                unit, unit.location, range_val, True, True,
                organic, inorganic, selection_type, castle
            )
        
        return targets
    
    def _get_line_targets(self, unit, start_location: int, range_val: int,
                          jump: bool, include_empty: bool, include_units: bool,
                          organic: bool, inorganic: bool, selection_type: int,
                          castle) -> List[int]:
        """Get targets in a line in a specific direction."""
        targets = []
        x = BattleField.get_x(start_location)
        y = BattleField.get_y(start_location)
        
        # Try all 8 directions
        directions = [
            (0, -1),   # Up
            (1, -1),   # Up-right
            (1, 0),    # Right
            (1, 1),    # Down-right
            (0, 1),    # Down
            (-1, 1),   # Down-left
            (-1, 0),   # Left
            (-1, -1),  # Up-left
        ]
        
        for dx, dy in directions:
            line_targets = self._get_single_line(
                unit, start_location, range_val, dx, dy, jump,
                include_empty, include_units, organic, inorganic,
                selection_type, castle
            )
            targets.extend(line_targets)
        
        return list(set(targets))  # Remove duplicates
    
    def _get_single_line(self, unit, start_location: int, range_val: int,
                        dx: int, dy: int, jump: bool, include_empty: bool,
                        include_units: bool, organic: bool, inorganic: bool,
                        selection_type: int, castle) -> List[int]:
        """Get targets in a single line direction."""
        targets = []
        x = BattleField.get_x(start_location)
        y = BattleField.get_y(start_location)
        
        for i in range(1, range_val + 1):
            new_x = x + dx * i
            new_y = y + dy * i
            
            # Check bounds
            if new_x < 0 or new_x >= constants.BOARD_SIZE:
                break
            if new_y < 0 or new_y >= constants.BOARD_SIZE:
                break
            
            location = BattleField.get_location(new_x, new_y)
            unit_at = self.get_unit_at(location)
            
            # Check if we should include this location
            if unit_at is None:
                if include_empty:
                    targets.append(location)
                # Don't break on empty space - continue checking
            else:
                # There's a unit here
                if include_units and self._is_valid_target(
                    unit_at, unit, organic, inorganic, selection_type, castle
                ):
                    targets.append(location)
                
                if not jump:
                    break  # Blocked by unit (if not jumping)
        
        return targets
    
    def _get_area_targets(self, unit, start_location: int, range_val: int,
                          include_empty: bool, include_units: bool,
                          organic: bool, inorganic: bool, selection_type: int,
                          castle) -> List[int]:
        """Get targets in an area around a location."""
        targets = []
        x = BattleField.get_x(start_location)
        y = BattleField.get_y(start_location)
        
        for dy in range(-range_val, range_val + 1):
            for dx in range(-range_val, range_val + 1):
                new_x = x + dx
                new_y = y + dy
                
                # Check bounds
                if new_x < 0 or new_x >= constants.BOARD_SIZE:
                    continue
                if new_y < 0 or new_y >= constants.BOARD_SIZE:
                    continue
                
                location = BattleField.get_location(new_x, new_y)
                
                # Skip starting location
                if location == start_location:
                    continue
                
                unit_at = self.get_unit_at(location)
                
                if unit_at is None:
                    if include_empty:
                        targets.append(location)
                else:
                    if include_units and self._is_valid_target(
                        unit_at, unit, organic, inorganic, selection_type, castle
                    ):
                        targets.append(location)
        
        return targets
    
    def _get_all_lines(self, unit, start_location: int, range_val: int,
                       jump: bool, include_empty: bool, include_units: bool,
                       organic: bool, inorganic: bool, selection_type: int,
                       castle) -> List[int]:
        """Get targets in all 8 directions (for ANY_LINE types)."""
        return self._get_line_targets(
            unit, start_location, range_val, jump, include_empty,
            include_units, organic, inorganic, selection_type, castle
        )
    
    def _is_valid_target(self, target_unit, source_unit, organic: bool,
                         inorganic: bool, selection_type: int, castle) -> bool:
        """Check if a unit is a valid target."""
        # Check organic/inorganic filter
        # If organic=True, we want organic units
        # If inorganic=True, we want inorganic units
        # If both True, we want both
        if not organic and not inorganic:
            return False  # No types wanted
        
        if organic and not target_unit.organic:
            if not inorganic:
                return False  # Only organic wanted, but target is inorganic
        if inorganic and target_unit.organic:
            if not organic:
                return False  # Only inorganic wanted, but target is organic
        
        # Check selection type (friendly/enemy/both)
        if selection_type == constants.SELECTION_FRIENDLY:
            return target_unit.castle == castle
        elif selection_type == constants.SELECTION_ENEMY:
            return target_unit.castle != castle
        elif selection_type == constants.SELECTION_BOTH:
            return True
        elif selection_type == constants.SELECTION_MOVE:
            # For movement, can't move onto units (except powerups)
            return False
        
        return False
