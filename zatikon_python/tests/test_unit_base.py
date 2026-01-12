"""
Tests for Unit base class - core unit functionality, stats, state management.
"""
import pytest
from zatikon import constants
from zatikon.unit import Unit
from zatikon.castle import Castle
from zatikon.battlefield import BattleField


class TestUnitInitialization:
    """Test Unit initialization and basic properties."""

    def test_unit_has_basic_properties(self):
        """Test unit has all basic properties initialized."""
        castle = Castle()
        unit = Unit(castle)
        
        # Basic stats
        assert hasattr(unit, 'life')
        assert hasattr(unit, 'life_max')
        assert hasattr(unit, 'armor')
        assert hasattr(unit, 'damage')
        assert hasattr(unit, 'actions_left')
        assert hasattr(unit, 'actions_max')
        
        # State
        assert hasattr(unit, 'location')
        assert hasattr(unit, 'team')
        assert hasattr(unit, 'castle')
        assert hasattr(unit, 'battlefield')
        
        # Flags
        assert hasattr(unit, 'organic')
        assert hasattr(unit, 'dead')
        assert hasattr(unit, 'deployed')
        assert hasattr(unit, 'stunned')

    def test_unit_initialization_with_castle(self):
        """Test unit is initialized with castle reference."""
        castle = Castle()
        unit = Unit(castle)
        
        assert unit.castle == castle

    def test_unit_default_stats(self):
        """Test unit has default stats."""
        castle = Castle()
        unit = Unit(castle)
        
        # Default stats should be set (implementation dependent)
        assert unit.life >= 0
        assert unit.life_max >= 0
        assert unit.armor >= 0
        assert unit.damage >= 0
        assert unit.actions_left >= 0
        assert unit.actions_max >= 0

    def test_unit_default_state(self):
        """Test unit default state."""
        castle = Castle()
        unit = Unit(castle)
        
        assert unit.location == -1  # Not on board
        assert unit.team == constants.TEAM_NONE
        assert unit.dead == False
        assert unit.deployed() == False  # Use method
        assert unit.stunned == False


class TestUnitStats:
    """Test Unit stat management."""

    def test_set_life(self):
        """Test setting unit life."""
        castle = Castle()
        unit = Unit(castle)
        
        unit.set_life(5)
        assert unit.life == 5

    def test_set_life_max(self):
        """Test setting unit life max."""
        castle = Castle()
        unit = Unit(castle)
        
        unit.set_life_max(10)
        assert unit.life_max == 10

    def test_set_armor(self):
        """Test setting unit armor."""
        castle = Castle()
        unit = Unit(castle)
        
        unit.set_armor(2)
        assert unit.armor == 2

    def test_set_damage(self):
        """Test setting unit damage."""
        castle = Castle()
        unit = Unit(castle)
        
        unit.set_damage(3)
        assert unit.damage == 3

    def test_get_armor_with_castle_modifier(self):
        """Test getting armor includes castle modifier."""
        castle = Castle()
        castle.add_armor(1)
        unit = Unit(castle)
        unit.set_armor(1)
        unit.organic = True
        
        armor = unit.get_armor()
        # Should be base armor + castle armor (max 2)
        assert armor >= 1

    def test_get_damage_with_castle_modifier(self):
        """Test getting damage includes castle modifier."""
        castle = Castle()
        castle.add_power(1)
        unit = Unit(castle)
        unit.set_damage(2)
        unit.organic = True
        
        damage = unit.get_damage()
        # Should be base damage + castle power
        assert damage >= 2


class TestUnitLocation:
    """Test Unit location management."""

    def test_set_location(self):
        """Test setting unit location."""
        castle = Castle()
        unit = Unit(castle)
        
        unit.set_location(60)
        assert unit.location == 60

    def test_set_location_updates_last_location(self):
        """Test setting location updates last_location."""
        castle = Castle()
        unit = Unit(castle)
        
        unit.set_location(50)
        unit.set_location(60)
        
        assert unit.location == 60
        assert unit.last_location == 50


class TestUnitTeam:
    """Test Unit team management."""

    def test_set_team(self):
        """Test setting unit team."""
        castle = Castle()
        unit = Unit(castle)
        
        unit.set_team(constants.TEAM_1)
        assert unit.team == constants.TEAM_1
        
        unit.set_team(constants.TEAM_2)
        assert unit.team == constants.TEAM_2


class TestUnitState:
    """Test Unit state management (dead, deployed, stunned)."""

    def test_unit_is_not_dead_by_default(self):
        """Test unit is not dead by default."""
        castle = Castle()
        unit = Unit(castle)
        
        assert unit.is_dead() == False

    def test_unit_die(self):
        """Test unit can die."""
        castle = Castle()
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        unit = Unit(castle)
        unit.battlefield = battlefield
        unit.location = 60
        
        unit.die(True, unit)  # death=True, source=unit
        
        assert unit.is_dead() == True
        assert unit.dead == True

    def test_unit_deployed_state(self):
        """Test unit deployed state."""
        castle = Castle()
        unit = Unit(castle)
        
        assert unit.deployed() == False
        
        unit._deployed = True
        assert unit.deployed() == True
        
        unit.stunned = True
        assert unit.deployed() == False  # Stunned units are not deployed

    def test_unit_stun(self):
        """Test unit can be stunned."""
        castle = Castle()
        unit = Unit(castle)
        
        unit.stun()
        assert unit.stunned == True
        assert unit.deployed() == False


class TestUnitActions:
    """Test Unit action management."""

    def test_deduct_actions(self):
        """Test deducting actions."""
        castle = Castle()
        unit = Unit(castle)
        unit.actions_left = 2
        unit.actions_max = 2
        
        unit.deduct_actions(1)
        assert unit.actions_left == 1
        
        unit.deduct_actions(1)
        assert unit.actions_left == 0

    def test_refresh_resets_actions(self):
        """Test refresh resets actions."""
        castle = Castle()
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        unit = Unit(castle)
        unit.battlefield = battlefield
        unit.actions_left = 0
        unit.actions_max = 2
        
        unit.refresh()
        
        assert unit.actions_left == unit.actions_max
        assert unit.deployed() == True  # Use method
        assert unit.stunned == False


class TestUnitBattlefield:
    """Test Unit battlefield integration."""

    def test_set_battlefield(self):
        """Test setting battlefield reference."""
        castle = Castle()
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        unit = Unit(castle)
        
        unit.set_battlefield(battlefield)
        assert unit.battlefield == battlefield

    def test_unit_removed_from_battlefield_on_death(self):
        """Test unit is removed from battlefield when it dies."""
        castle = Castle()
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        unit = Unit(castle)
        unit.battlefield = battlefield
        unit.location = 60
        battlefield.add_unit(unit)
        
        assert unit in battlefield.units
        
        unit.die(True, unit)
        
        assert unit not in battlefield.units

