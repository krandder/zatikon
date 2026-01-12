"""
Tests for UnitFootman - basic melee unit.
"""
import pytest
from zatikon import constants
from zatikon.unit_factory import UnitFactory
from zatikon.castle import Castle
from zatikon.battlefield import BattleField


class TestUnitFootman:
    """Test UnitFootman implementation."""

    def test_footman_initialization(self):
        """Test Footman initializes correctly."""
        castle = Castle()
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, castle)
        
        assert unit.name == "Footman"
        assert unit.unit_id == constants.UNIT_FOOTMAN
        assert unit.organic == True

    def test_footman_has_move_action(self):
        """Test Footman has move action."""
        castle = Castle()
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, castle)
        
        assert unit.move_action is not None
        assert unit.move_action.get_type() == constants.ACTION_MOVE
        assert unit.move_action.range == 1  # Footman moves 1 square

    def test_footman_has_attack_action(self):
        """Test Footman has attack action."""
        castle = Castle()
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, castle)
        
        assert unit.attack_action is not None
        assert unit.attack_action.get_type() == constants.ACTION_ATTACK
        assert unit.attack_action.target_type == constants.TARGET_UNIT_LINE
        assert unit.attack_action.range == 1  # Melee attack

    def test_footman_can_move(self):
        """Test Footman can move."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, castle1)
        unit.battlefield = battlefield
        unit.location = 60
        unit._deployed = True
        battlefield.add_unit(unit)
        
        targets = unit.move_action.get_targets()
        assert len(targets) > 0
        assert 61 in targets or 59 in targets or 50 in targets or 70 in targets

    def test_footman_can_attack(self):
        """Test Footman can attack."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        attacker = UnitFactory.create_unit(constants.UNIT_FOOTMAN, castle1)
        attacker.battlefield = battlefield
        attacker.location = 60
        attacker._deployed = True
        battlefield.add_unit(attacker)
        
        target = UnitFactory.create_unit(constants.UNIT_FOOTMAN, castle2)
        target.battlefield = battlefield
        target.location = 61
        target._deployed = True
        battlefield.add_unit(target)
        
        targets = attacker.attack_action.get_targets()
        assert 61 in targets

