"""
Tests for Action base class and ActionMove.
"""
import pytest
from zatikon import constants
from zatikon.action import Action
from zatikon.actions.action_move import ActionMove
from zatikon.unit import Unit
from zatikon.castle import Castle
from zatikon.battlefield import BattleField


class TestActionBase:
    """Test Action base class interface."""

    def test_action_has_required_methods(self):
        """Test Action has all required interface methods."""
        # Action is an abstract base class, so we test via ActionMove
        castle = Castle()
        unit = Unit(castle)
        action = ActionMove(unit, 1, 0, constants.TARGET_LOCATION_LINE, 1)
        
        assert hasattr(action, 'perform')
        assert hasattr(action, 'validate')
        assert hasattr(action, 'get_targets')
        assert hasattr(action, 'get_remaining')
        assert hasattr(action, 'refresh')
        assert hasattr(action, 'start_turn')
        assert hasattr(action, 'get_name')
        assert hasattr(action, 'get_type')


class TestActionMove:
    """Test ActionMove implementation."""

    def test_action_move_initialization(self):
        """Test ActionMove can be initialized."""
        castle = Castle()
        unit = Unit(castle)
        action = ActionMove(unit, 1, 0, constants.TARGET_LOCATION_LINE, 1)
        
        assert action.owner == unit
        assert action.max == 1
        assert action.remaining == 1
        assert action.cost == 0
        assert action.target_type == constants.TARGET_LOCATION_LINE
        assert action.range == 1

    def test_action_move_get_remaining(self):
        """Test getting remaining moves."""
        castle = Castle()
        unit = Unit(castle)
        unit.actions_left = 2
        unit.actions_max = 2
        unit._deployed = True
        
        action = ActionMove(unit, 1, 0, constants.TARGET_LOCATION_LINE, 1)
        assert action.get_remaining() == 1
        
        action.remaining = 0
        assert action.get_remaining() == 0

    def test_action_move_get_remaining_with_cost(self):
        """Test remaining moves calculation with action cost."""
        castle = Castle()
        unit = Unit(castle)
        unit.actions_left = 4
        unit.actions_max = 4
        unit._deployed = True
        
        # Move costs 1 action, max 0 means unlimited
        action = ActionMove(unit, 0, 1, constants.TARGET_LOCATION_LINE, 1)
        # With 4 actions and cost 1, should have 4 remaining
        assert action.get_remaining() == 4

    def test_action_move_get_remaining_when_not_deployed(self):
        """Test remaining moves is 0 when unit not deployed."""
        castle = Castle()
        unit = Unit(castle)
        unit._deployed = False
        
        action = ActionMove(unit, 1, 0, constants.TARGET_LOCATION_LINE, 1)
        assert action.get_remaining() == 0

    def test_action_move_get_remaining_when_no_commands(self):
        """Test remaining moves is 0 when castle has no commands."""
        castle = Castle()
        castle.commands_left = 0
        unit = Unit(castle)
        unit._deployed = True
        
        action = ActionMove(unit, 1, 0, constants.TARGET_LOCATION_LINE, 1)
        assert action.get_remaining() == 0

    def test_action_move_refresh(self):
        """Test refresh resets remaining moves."""
        castle = Castle()
        unit = Unit(castle)
        action = ActionMove(unit, 2, 0, constants.TARGET_LOCATION_LINE, 1)
        
        action.remaining = 0
        action.refresh()
        assert action.remaining == 2

    def test_action_move_get_type(self):
        """Test action type is MOVE."""
        castle = Castle()
        unit = Unit(castle)
        action = ActionMove(unit, 1, 0, constants.TARGET_LOCATION_LINE, 1)
        
        assert action.get_type() == constants.ACTION_MOVE

    def test_action_move_get_name(self):
        """Test action has a name."""
        castle = Castle()
        unit = Unit(castle)
        action = ActionMove(unit, 1, 0, constants.TARGET_LOCATION_LINE, 1)
        
        name = action.get_name()
        assert isinstance(name, str)
        assert len(name) > 0


class TestActionMoveValidation:
    """Test ActionMove validation."""

    def test_validate_with_no_remaining(self):
        """Test validation fails when no moves remaining."""
        castle = Castle()
        unit = Unit(castle)
        unit._deployed = True
        action = ActionMove(unit, 1, 0, constants.TARGET_LOCATION_LINE, 1)
        action.remaining = 0
        
        assert action.validate(10) == False

    def test_validate_when_not_deployed(self):
        """Test validation fails when unit not deployed."""
        castle = Castle()
        unit = Unit(castle)
        unit._deployed = False
        action = ActionMove(unit, 1, 0, constants.TARGET_LOCATION_LINE, 1)
        
        assert action.validate(10) == False

    def test_validate_target_in_range(self):
        """Test validation succeeds when target is in range."""
        castle = Castle()
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        unit = Unit(castle)
        unit.battlefield = battlefield
        unit.location = 60
        unit._deployed = True
        
        action = ActionMove(unit, 1, 0, constants.TARGET_LOCATION_LINE, 1)
        
        # Target should be adjacent (within range 1)
        # Location 60 is center (5,5), so 61 (6,5) should be valid
        assert action.validate(61) == True

    def test_validate_target_out_of_range(self):
        """Test validation fails when target is out of range."""
        castle = Castle()
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        unit = Unit(castle)
        unit.battlefield = battlefield
        unit.location = 60
        unit._deployed = True
        
        action = ActionMove(unit, 1, 0, constants.TARGET_LOCATION_LINE, 1)
        
        # Location 0 is far away, should be invalid
        assert action.validate(0) == False


class TestActionMoveGetTargets:
    """Test ActionMove target collection."""

    def test_get_targets_returns_list(self):
        """Test get_targets returns a list."""
        castle = Castle()
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        unit = Unit(castle)
        unit.battlefield = battlefield
        unit.location = 60
        unit._deployed = True
        
        action = ActionMove(unit, 1, 0, constants.TARGET_LOCATION_LINE, 1)
        targets = action.get_targets()
        
        assert isinstance(targets, list)

    def test_get_targets_includes_adjacent_locations(self):
        """Test get_targets includes adjacent empty locations."""
        castle = Castle()
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        unit = Unit(castle)
        unit.battlefield = battlefield
        unit.location = 60  # Center (5,5)
        unit._deployed = True
        
        action = ActionMove(unit, 1, 0, constants.TARGET_LOCATION_LINE, 1)
        targets = action.get_targets()
        
        # Should include adjacent locations (59, 61, 49, 51, 50, 70, 71, 60)
        # Actually, location 60 itself might not be included
        assert len(targets) > 0
        # Should include at least some adjacent squares
        assert 61 in targets or 59 in targets or 50 in targets or 70 in targets

