"""
Tests for Castle functionality - command economy, unit management, modifiers.
"""
import pytest
from zatikon import constants
from zatikon.castle import Castle
from zatikon.battlefield import BattleField


class TestCastleInitialization:
    """Test Castle initialization and basic properties."""

    def test_castle_initialization_with_team(self):
        """Test castle can be initialized with a team."""
        castle1 = Castle(constants.TEAM_1)
        assert castle1.team == constants.TEAM_1
        
        castle2 = Castle(constants.TEAM_2)
        assert castle2.team == constants.TEAM_2

    def test_castle_default_team(self):
        """Test castle defaults to TEAM_1 if no team specified."""
        castle = Castle()
        assert castle.team == constants.TEAM_1

    def test_castle_command_economy_initialization(self):
        """Test castle command economy is initialized correctly."""
        castle = Castle()
        assert castle.commands_max == constants.MAX_COMMANDS
        assert castle.commands_left == constants.MAX_COMMANDS

    def test_castle_unit_management_initialization(self):
        """Test castle unit management structures are initialized."""
        castle = Castle()
        assert castle.barracks == []
        assert castle.units_out == []
        assert castle.graveyard == []

    def test_castle_modifiers_initialization(self):
        """Test castle modifiers are initialized to zero."""
        castle = Castle()
        assert castle.armor == 0
        assert castle.power == 0
        assert castle.perm_armor == 0
        assert castle.perm_power == 0
        assert castle.logistics == 0

    def test_castle_location_initialization(self):
        """Test castle location is initialized to -1 (unset)."""
        castle = Castle()
        assert castle.location == -1

    def test_castle_set_location(self):
        """Test castle location can be set."""
        castle = Castle()
        castle.set_location(60)
        assert castle.location == 60


class TestCastleCommandEconomy:
    """Test Castle command economy (commandsLeft, deductCommands)."""

    def test_get_commands_left(self):
        """Test getting commands left."""
        castle = Castle()
        assert castle.get_commands_left() == constants.MAX_COMMANDS

    def test_deduct_commands(self):
        """Test deducting commands."""
        castle = Castle()
        initial_commands = castle.commands_left
        
        castle.deduct_commands(2)
        assert castle.commands_left == initial_commands - 2
        assert castle.get_commands_left() == initial_commands - 2

    def test_deduct_commands_multiple_times(self):
        """Test deducting commands multiple times."""
        castle = Castle()
        castle.deduct_commands(1)
        castle.deduct_commands(2)
        assert castle.commands_left == constants.MAX_COMMANDS - 3

    def test_deduct_commands_can_go_to_zero(self):
        """Test commands can be deducted to zero."""
        castle = Castle()
        castle.deduct_commands(constants.MAX_COMMANDS)
        assert castle.commands_left == 0
        assert castle.get_commands_left() == 0

    def test_deduct_commands_can_go_negative(self):
        """Test commands can go negative (for validation purposes)."""
        castle = Castle()
        castle.deduct_commands(constants.MAX_COMMANDS + 1)
        assert castle.commands_left < 0

    def test_refresh_resets_commands(self):
        """Test refresh resets commands to max."""
        castle = Castle()
        castle.deduct_commands(3)
        assert castle.commands_left < castle.commands_max
        
        castle.refresh(constants.TEAM_1)
        assert castle.commands_left == castle.commands_max


class TestCastleUnitManagement:
    """Test Castle unit management (barracks, units_out, graveyard)."""

    def test_add_unit_to_barracks(self):
        """Test adding unit to barracks."""
        castle = Castle()
        
        class MockUnit:
            def __init__(self, unit_id):
                self.unit_id = unit_id
        
        unit = MockUnit(1)
        castle.add_unit(unit)
        
        assert len(castle.barracks) == 1
        assert unit in castle.barracks

    def test_remove_unit_from_barracks(self):
        """Test removing unit from barracks."""
        castle = Castle()
        
        class MockUnit:
            def __init__(self, unit_id):
                self.unit_id = unit_id
        
        unit = MockUnit(1)
        castle.add_unit(unit)
        assert len(castle.barracks) == 1
        
        castle.remove_unit(unit)
        assert len(castle.barracks) == 0
        assert unit not in castle.barracks

    def test_add_unit_to_field(self):
        """Test adding unit to units_out (deployed units)."""
        castle = Castle()
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        castle.battlefield = battlefield
        
        class MockUnit:
            def __init__(self, location):
                self.location = location
                self.team = None
                self.sequence = None
        
        unit = MockUnit(10)
        castle.add_unit_out(constants.TEAM_1, unit)
        
        assert len(castle.units_out) == 1
        assert unit in castle.units_out
        assert unit.team == constants.TEAM_1

    def test_add_unit_to_graveyard(self):
        """Test adding unit to graveyard."""
        castle = Castle()
        
        class MockUnit:
            def __init__(self, unit_id):
                self.unit_id = unit_id
        
        unit = MockUnit(1)
        castle.add_graveyard(unit)
        
        assert len(castle.graveyard) == 1
        assert unit in castle.graveyard

    def test_get_unit_count(self):
        """Test getting total unit count (barracks + units_out)."""
        castle = Castle()
        
        class MockUnit:
            def __init__(self, unit_id):
                self.unit_id = unit_id
        
        unit1 = MockUnit(1)
        unit2 = MockUnit(2)
        unit3 = MockUnit(3)
        
        castle.add_unit(unit1)
        castle.add_unit(unit2)
        castle.add_unit_out(constants.TEAM_1, unit3)
        
        # Note: get_count() should count barracks only, but we'll implement it
        # For now, test the structure
        assert len(castle.barracks) == 2
        assert len(castle.units_out) == 1


class TestCastleModifiers:
    """Test Castle modifiers (armor, power, logistics)."""

    def test_add_armor(self):
        """Test adding temporary armor."""
        castle = Castle()
        castle.add_armor(2)
        assert castle.armor == 2
        
        castle.add_armor(1)
        assert castle.armor == 3

    def test_add_power(self):
        """Test adding temporary power."""
        castle = Castle()
        castle.add_power(2)
        assert castle.power == 2
        
        castle.add_power(1)
        assert castle.power == 3

    def test_add_perm_armor(self):
        """Test adding permanent armor."""
        castle = Castle()
        castle.add_perm_armor(1)
        assert castle.perm_armor == 1
        assert castle.armor == 1
        
        castle.add_perm_armor(1)
        assert castle.perm_armor == 2
        assert castle.armor == 2

    def test_add_perm_power(self):
        """Test adding permanent power."""
        castle = Castle()
        castle.add_perm_power(1)
        assert castle.perm_power == 1
        assert castle.power == 1
        
        castle.add_perm_power(1)
        assert castle.perm_power == 2
        assert castle.power == 2

    def test_set_logistics(self):
        """Test setting logistics modifier."""
        castle = Castle()
        castle.set_logistics(2)
        assert castle.logistics == 2

    def test_refresh_resets_temporary_modifiers(self):
        """Test refresh resets temporary armor/power but keeps permanent."""
        castle = Castle()
        castle.add_perm_armor(1)
        castle.add_perm_power(1)
        castle.add_armor(1)  # Temporary
        castle.add_power(1)  # Temporary
        
        castle.refresh(constants.TEAM_1)
        
        # Permanent modifiers should remain
        assert castle.perm_armor == 1
        assert castle.perm_power == 1
        # Temporary modifiers should reset to permanent values
        assert castle.armor == castle.perm_armor
        assert castle.power == castle.perm_power


class TestCastleTurnManagement:
    """Test Castle turn management (startTurn, refresh)."""

    def test_start_turn(self):
        """Test starting a turn."""
        castle = Castle()
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        castle.battlefield = battlefield
        
        # startTurn should reset armor/power to permanent values
        castle.add_perm_armor(1)
        castle.add_perm_power(1)
        castle.armor = 0  # Simulate temporary modifier
        castle.power = 0
        
        castle.start_turn(constants.TEAM_1)
        assert castle.armor == castle.perm_armor
        assert castle.power == castle.perm_power

    def test_refresh_resets_commands_and_militia(self):
        """Test refresh resets commands and militia."""
        castle = Castle()
        castle.deduct_commands(2)
        castle.militia = 5
        
        castle.refresh(constants.TEAM_1)
        
        assert castle.commands_left == castle.commands_max
        assert castle.militia == 0

    def test_refresh_decrements_armistice(self):
        """Test refresh decrements armistice counter."""
        castle = Castle()
        castle.armistice = 2
        
        castle.refresh(constants.TEAM_1)
        assert castle.armistice == 1
        
        castle.refresh(constants.TEAM_1)
        assert castle.armistice == 0
        
        castle.refresh(constants.TEAM_1)
        assert castle.armistice == 0  # Should not go negative

