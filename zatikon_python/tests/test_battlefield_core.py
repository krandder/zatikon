"""
Tests for BattleField core functionality - initialization, unit management, sequence numbers.
"""
import pytest
from zatikon import constants
from zatikon.battlefield import BattleField
from zatikon.castle import Castle


class TestBattleFieldInitialization:
    """Test BattleField initialization and basic operations."""

    def test_battlefield_creation_with_two_castles(self):
        """Test BattleField can be created with two castles."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        
        battlefield = BattleField(castle1, castle2)
        
        assert battlefield.castle1 == castle1
        assert battlefield.castle2 == castle2
        assert battlefield.units == []
        assert battlefield.sequence == 0
        assert battlefield.graves == []
        
        # Castles should have battlefield reference set
        assert castle1.battlefield == battlefield
        assert castle2.battlefield == battlefield

    def test_sequence_number_generation(self):
        """Test sequence number generation for unit ordering."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        # First sequence should be 0
        seq1 = battlefield.get_sequence()
        assert seq1 == 0
        
        # Subsequent sequences should increment
        seq2 = battlefield.get_sequence()
        assert seq2 == 1
        
        seq3 = battlefield.get_sequence()
        assert seq3 == 2
        
        # Sequence counter should have advanced
        assert battlefield.sequence == 3

    def test_add_unit_to_battlefield(self):
        """Test adding units to the battlefield."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        # Create a mock unit (we'll implement Unit class later)
        class MockUnit:
            def __init__(self, location):
                self.location = location
        
        unit1 = MockUnit(10)
        unit2 = MockUnit(20)
        
        battlefield.add_unit(unit1)
        assert len(battlefield.units) == 1
        assert unit1 in battlefield.units
        
        battlefield.add_unit(unit2)
        assert len(battlefield.units) == 2
        assert unit2 in battlefield.units

    def test_remove_unit_from_battlefield(self):
        """Test removing units from the battlefield."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        class MockUnit:
            def __init__(self, location):
                self.location = location
        
        unit1 = MockUnit(10)
        unit2 = MockUnit(20)
        
        battlefield.add_unit(unit1)
        battlefield.add_unit(unit2)
        assert len(battlefield.units) == 2
        
        battlefield.remove_unit(unit1)
        assert len(battlefield.units) == 1
        assert unit1 not in battlefield.units
        assert unit2 in battlefield.units
        
        battlefield.remove_unit(unit2)
        assert len(battlefield.units) == 0

    def test_get_unit_at_location(self):
        """Test getting unit at a specific location."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        class MockUnit:
            def __init__(self, location):
                self.location = location
        
        unit1 = MockUnit(10)
        unit2 = MockUnit(20)
        
        battlefield.add_unit(unit1)
        battlefield.add_unit(unit2)
        
        assert battlefield.get_unit_at(10) == unit1
        assert battlefield.get_unit_at(20) == unit2
        assert battlefield.get_unit_at(30) is None

    def test_get_units_at_location(self):
        """Test getting all units at a location (for powerups)."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        class MockUnit:
            def __init__(self, location):
                self.location = location
        
        unit1 = MockUnit(10)
        unit2 = MockUnit(10)  # Same location
        
        battlefield.add_unit(unit1)
        battlefield.add_unit(unit2)
        
        units_at_10 = battlefield.get_units_at(10)
        assert len(units_at_10) == 2
        assert unit1 in units_at_10
        assert unit2 in units_at_10
        
        units_at_20 = battlefield.get_units_at(20)
        assert len(units_at_20) == 0

    def test_add_grave(self):
        """Test adding grave markers for dead units."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        castle1.set_location(0)
        castle2.set_location(120)
        
        battlefield = BattleField(castle1, castle2)
        
        # Add grave at valid location
        battlefield.add_grave(60)
        assert 60 in battlefield.graves
        
        # Should not add grave at castle locations
        battlefield.add_grave(0)  # Castle1 location
        assert 0 not in battlefield.graves
        
        battlefield.add_grave(120)  # Castle2 location
        assert 120 not in battlefield.graves

    def test_remove_grave(self):
        """Test removing grave markers."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        battlefield.add_grave(60)
        assert 60 in battlefield.graves
        
        battlefield.remove_grave(60)
        assert 60 not in battlefield.graves
        
        # Removing non-existent grave should not error
        battlefield.remove_grave(70)
        assert 70 not in battlefield.graves

