"""
Tests for UnitFactory - creating unit instances.
"""
import pytest
from zatikon import constants
from zatikon.unit_factory import UnitFactory
from zatikon.castle import Castle


class TestUnitFactory:
    """Test UnitFactory functionality."""

    def test_create_footman(self):
        """Test creating a Footman unit."""
        castle = Castle()
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, castle)
        
        assert unit is not None
        assert unit.unit_id == constants.UNIT_FOOTMAN
        assert unit.castle == castle
        assert unit.name == "Footman"
        assert unit.life > 0
        assert unit.life_max > 0
        assert unit.damage >= 0
        assert unit.armor >= 0

    def test_create_bear(self):
        """Test creating a Bear unit."""
        castle = Castle()
        unit = UnitFactory.create_unit(constants.UNIT_BEAR, castle)
        
        assert unit is not None
        assert unit.unit_id == constants.UNIT_BEAR
        assert unit.castle == castle
        assert unit.name == "Bear"
        assert unit.life > 0
        assert unit.life_max > 0

    def test_create_unit_with_different_castles(self):
        """Test creating units for different castles."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        
        unit1 = UnitFactory.create_unit(constants.UNIT_FOOTMAN, castle1)
        unit2 = UnitFactory.create_unit(constants.UNIT_FOOTMAN, castle2)
        
        assert unit1.castle == castle1
        assert unit2.castle == castle2
        assert unit1.unit_id == unit2.unit_id

    def test_unit_has_move_action(self):
        """Test created unit has move action."""
        castle = Castle()
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, castle)
        
        assert unit.move_action is not None
        assert unit.move_action.get_type() == constants.ACTION_MOVE

    def test_unit_has_attack_action(self):
        """Test created unit has attack action."""
        castle = Castle()
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, castle)
        
        assert unit.attack_action is not None
        assert unit.attack_action.get_type() == constants.ACTION_ATTACK

    def test_unit_actions_in_actions_list(self):
        """Test unit actions are in actions list."""
        castle = Castle()
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, castle)
        
        assert len(unit.actions) > 0
        assert unit.move_action in unit.actions
        assert unit.attack_action in unit.actions

    def test_invalid_unit_id(self):
        """Test creating unit with invalid ID raises error."""
        castle = Castle()
        
        with pytest.raises(ValueError):
            UnitFactory.create_unit(99999, castle)


class TestUnitStats:
    """Test unit stats are correctly set."""

    def test_footman_stats(self):
        """Test Footman has correct stats."""
        castle = Castle()
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, castle)
        
        # Footman should have basic melee stats
        assert unit.life > 0
        assert unit.life == unit.life_max
        assert unit.damage >= 0
        assert unit.armor >= 0
        assert unit.actions_max > 0

    def test_bear_stats(self):
        """Test Bear has correct stats."""
        castle = Castle()
        unit = UnitFactory.create_unit(constants.UNIT_BEAR, castle)
        
        # Bear should be stronger than Footman
        assert unit.life > 0
        assert unit.life == unit.life_max
        assert unit.organic == True

