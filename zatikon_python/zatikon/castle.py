"""
Castle - Represents a player's castle and manages units.
"""
from zatikon import constants


class Castle:
    """
    Represents a player's castle.
    Manages unit deployment, command economy, and castle modifiers.
    """
    
    def __init__(self, team: int = constants.TEAM_1):
        """
        Initialize a new castle.
        
        Args:
            team: Team number (TEAM_1 or TEAM_2)
        """
        self.team = team
        self.location = -1  # Will be set during game setup
        self.battlefield = None
        
        # Command economy
        self.commands_max = constants.MAX_COMMANDS
        self.commands_left = self.commands_max
        
        # Unit management
        self.barracks = []  # Undeployed units
        self.units_out = []  # Units on the battlefield
        self.graveyard = []  # Dead units
        
        # Castle modifiers
        self.armor = 0
        self.power = 0
        self.perm_armor = 0
        self.perm_power = 0
        self.logistics = 0
        
        # Other properties
        self.value = 0  # Total value of units
        self.armistice = 0  # Armistice turns remaining
        self.militia = 0
    
    def set_battlefield(self, battlefield):
        """Set the battlefield reference."""
        self.battlefield = battlefield
    
    def set_location(self, location: int):
        """Set the castle's location on the board."""
        self.location = location
    
    def get_commands_left(self) -> int:
        """
        Get the number of commands remaining.
        
        Returns:
            Number of commands left
        """
        return self.commands_left
    
    def deduct_commands(self, amount: int):
        """
        Deduct commands from the castle.
        
        Args:
            amount: Number of commands to deduct
        """
        self.commands_left -= amount
    
    def add_unit(self, unit):
        """
        Add a unit to the barracks (undeployed units).
        
        Args:
            unit: Unit to add
        """
        self.barracks.append(unit)
    
    def remove_unit(self, unit):
        """
        Remove a unit from the barracks.
        
        Args:
            unit: Unit to remove
        """
        if unit in self.barracks:
            self.barracks.remove(unit)
    
    def add_unit_out(self, team: int, unit):
        """
        Add a unit to the battlefield (deployed units).
        
        Args:
            team: Team number
            unit: Unit to add
        """
        if self.battlefield:
            unit.sequence = self.battlefield.get_sequence()
        unit.team = team
        self.units_out.append(unit)
    
    def add_graveyard(self, unit):
        """
        Add a unit to the graveyard.
        
        Args:
            unit: Dead unit to add
        """
        self.graveyard.append(unit)
    
    def add_armor(self, amount: int):
        """
        Add temporary armor modifier.
        
        Args:
            amount: Amount of armor to add
        """
        self.armor += amount
    
    def add_power(self, amount: int):
        """
        Add temporary power modifier.
        
        Args:
            amount: Amount of power to add
        """
        self.power += amount
    
    def add_perm_armor(self, amount: int):
        """
        Add permanent armor modifier.
        
        Args:
            amount: Amount of permanent armor to add
        """
        self.perm_armor += amount
        self.armor += amount
    
    def add_perm_power(self, amount: int):
        """
        Add permanent power modifier.
        
        Args:
            amount: Amount of permanent power to add
        """
        self.perm_power += amount
        self.power += amount
    
    def set_logistics(self, amount: int):
        """
        Set logistics modifier (reduces deploy costs).
        
        Args:
            amount: Logistics value
        """
        self.logistics = amount
    
    def refresh(self, team: int):
        """
        Refresh the castle at the start of a new turn.
        Resets commands, temporary modifiers, and decrements armistice.
        
        Args:
            team: Team number for the turn
        """
        if self.armistice > 0:
            self.armistice -= 1
        
        # Reset commands
        self.commands_left = self.commands_max
        
        # Reset militia
        self.militia = 0
        
        # Reset temporary modifiers to permanent values
        if team == constants.TEAM_1:
            self.armor = self.perm_armor
            self.power = self.perm_power
    
    def start_turn(self, team: int):
        """
        Start a turn for this castle.
        Resets armor/power to permanent values.
        
        Args:
            team: Team number for the turn
        """
        if team == constants.TEAM_1:
            self.armor = self.perm_armor
            self.power = self.perm_power

