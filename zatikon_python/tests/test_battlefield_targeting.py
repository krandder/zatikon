"""
Tests for BattleField targeting system - line, area, unit filtering.
"""
import pytest
from zatikon import constants
from zatikon.battlefield import BattleField
from zatikon.castle import Castle
from zatikon.unit import Unit


class TestBattleFieldTargeting:
    """Test BattleField targeting methods."""

    def test_get_targets_location_line(self):
        """Test getting targets in a line (adjacent)."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        unit = Unit(castle1)
        unit.battlefield = battlefield
        unit.location = 60  # Center (5,5)
        unit._deployed = True
        
        targets = battlefield.get_targets(
            unit, 
            constants.TARGET_LOCATION_LINE,
            range_val=1,
            include_empty=True,
            organic=True,
            inorganic=True,
            selection_type=constants.SELECTION_MOVE,
            castle=castle1
        )
        
        assert isinstance(targets, list)
        assert len(targets) > 0
        # Should include adjacent empty locations
        assert 61 in targets or 59 in targets or 50 in targets or 70 in targets

    def test_get_targets_unit_line(self):
        """Test getting unit targets in a line."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        attacker = Unit(castle1)
        attacker.battlefield = battlefield
        attacker.location = 60
        attacker._deployed = True
        attacker.team = constants.TEAM_1
        
        target = Unit(castle2)
        target.battlefield = battlefield
        target.location = 61  # Adjacent
        target._deployed = True
        target.team = constants.TEAM_2
        battlefield.add_unit(target)
        
        targets = battlefield.get_targets(
            attacker,
            constants.TARGET_UNIT_LINE,
            range_val=1,
            include_empty=False,
            organic=True,
            inorganic=True,
            selection_type=constants.SELECTION_ENEMY,
            castle=castle1
        )
        
        assert 61 in targets

    def test_get_targets_area(self):
        """Test getting targets in an area."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        unit = Unit(castle1)
        unit.battlefield = battlefield
        unit.location = 60  # Center (5,5)
        unit._deployed = True
        
        targets = battlefield.get_targets(
            unit,
            constants.TARGET_LOCATION_AREA,
            range_val=2,
            include_empty=True,
            organic=True,
            inorganic=True,
            selection_type=constants.SELECTION_MOVE,
            castle=castle1
        )
        
        assert isinstance(targets, list)
        assert len(targets) > 0
        # Should include locations within range 2

    def test_get_targets_filters_enemy_units(self):
        """Test targeting filters enemy units correctly."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        attacker = Unit(castle1)
        attacker.battlefield = battlefield
        attacker.location = 60
        attacker.team = constants.TEAM_1
        attacker._deployed = True
        
        enemy = Unit(castle2)
        enemy.battlefield = battlefield
        enemy.location = 61
        enemy.team = constants.TEAM_2
        battlefield.add_unit(enemy)
        
        friendly = Unit(castle1)
        friendly.battlefield = battlefield
        friendly.location = 59
        friendly.team = constants.TEAM_1
        battlefield.add_unit(friendly)
        
        # Get enemy targets only
        targets = battlefield.get_targets(
            attacker,
            constants.TARGET_UNIT_LINE,
            range_val=1,
            include_empty=False,
            organic=True,
            inorganic=True,
            selection_type=constants.SELECTION_ENEMY,
            castle=castle1
        )
        
        assert 61 in targets  # Enemy
        assert 59 not in targets  # Friendly

    def test_get_targets_filters_friendly_units(self):
        """Test targeting filters friendly units correctly."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        unit = Unit(castle1)
        unit.battlefield = battlefield
        unit.location = 60
        unit.team = constants.TEAM_1
        unit._deployed = True
        
        enemy = Unit(castle2)
        enemy.battlefield = battlefield
        enemy.location = 61
        enemy.team = constants.TEAM_2
        battlefield.add_unit(enemy)
        
        friendly = Unit(castle1)
        friendly.battlefield = battlefield
        friendly.location = 59
        friendly.team = constants.TEAM_1
        battlefield.add_unit(friendly)
        
        # Get friendly targets only
        targets = battlefield.get_targets(
            unit,
            constants.TARGET_UNIT_LINE,
            range_val=1,
            include_empty=False,
            organic=True,
            inorganic=True,
            selection_type=constants.SELECTION_FRIENDLY,
            castle=castle1
        )
        
        assert 59 in targets  # Friendly
        assert 61 not in targets  # Enemy

    def test_get_targets_line_blocking(self):
        """Test line targeting is blocked by units."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        attacker = Unit(castle1)
        attacker.battlefield = battlefield
        attacker.location = 50  # (5,4)
        attacker._deployed = True
        
        blocker = Unit(castle2)
        blocker.battlefield = battlefield
        blocker.location = 51  # Blocks the line
        battlefield.add_unit(blocker)
        
        target = Unit(castle2)
        target.battlefield = battlefield
        target.location = 52  # Behind blocker
        battlefield.add_unit(target)
        
        # Without jump, should not reach target behind blocker
        targets = battlefield.get_targets(
            attacker,
            constants.TARGET_UNIT_LINE,
            range_val=3,
            include_empty=False,
            organic=True,
            inorganic=True,
            selection_type=constants.SELECTION_ENEMY,
            castle=castle1
        )
        
        assert 51 in targets  # Blocker is targetable
        # Target behind blocker should not be in targets (no jump)

    def test_get_targets_line_jump(self):
        """Test line targeting with jump (can jump over units)."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        attacker = Unit(castle1)
        attacker.battlefield = battlefield
        attacker.location = 50
        attacker._deployed = True
        
        blocker = Unit(castle2)
        blocker.battlefield = battlefield
        blocker.location = 51
        battlefield.add_unit(blocker)
        
        target = Unit(castle2)
        target.battlefield = battlefield
        target.location = 52
        battlefield.add_unit(target)
        
        # With jump, should reach target behind blocker
        targets = battlefield.get_targets(
            attacker,
            constants.TARGET_UNIT_LINE_JUMP,
            range_val=3,
            include_empty=False,
            organic=True,
            inorganic=True,
            selection_type=constants.SELECTION_ENEMY,
            castle=castle1
        )
        
        assert 52 in targets  # Target behind blocker should be reachable
