"""
Tests for ActionAttack - attack actions and damage dealing.
"""
import pytest
from zatikon import constants
from zatikon.actions.action_attack import ActionAttack
from zatikon.unit import Unit
from zatikon.castle import Castle
from zatikon.battlefield import BattleField


class TestActionAttack:
    """Test ActionAttack implementation."""

    def test_action_attack_initialization(self):
        """Test ActionAttack can be initialized."""
        castle = Castle()
        unit = Unit(castle)
        action = ActionAttack(unit, 1, 1, constants.TARGET_UNIT_LINE, 1)
        
        assert action.owner == unit
        assert action.max == 1
        assert action.remaining == 1
        assert action.cost == 1
        assert action.target_type == constants.TARGET_UNIT_LINE
        assert action.range == 1
        assert action.attack_type == constants.ATTACK_MELEE

    def test_action_attack_initialization_with_attack_type(self):
        """Test ActionAttack can be initialized with specific attack type."""
        castle = Castle()
        unit = Unit(castle)
        action = ActionAttack(unit, 1, 1, constants.TARGET_UNIT_LINE, 2, constants.ATTACK_ARROW)
        
        assert action.attack_type == constants.ATTACK_ARROW
        assert action.range == 2

    def test_action_attack_get_remaining(self):
        """Test getting remaining attacks."""
        castle = Castle()
        unit = Unit(castle)
        unit.actions_left = 2
        unit.actions_max = 2
        unit._deployed = True
        
        action = ActionAttack(unit, 1, 1, constants.TARGET_UNIT_LINE, 1)
        assert action.get_remaining() == 1
        
        action.remaining = 0
        assert action.get_remaining() == 0

    def test_action_attack_get_remaining_when_not_deployed(self):
        """Test remaining attacks is 0 when unit not deployed."""
        castle = Castle()
        unit = Unit(castle)
        unit._deployed = False
        
        action = ActionAttack(unit, 1, 1, constants.TARGET_UNIT_LINE, 1)
        assert action.get_remaining() == 0

    def test_action_attack_get_remaining_when_no_commands(self):
        """Test remaining attacks is 0 when castle has no commands."""
        castle = Castle()
        castle.commands_left = 0
        unit = Unit(castle)
        unit._deployed = True
        
        action = ActionAttack(unit, 1, 1, constants.TARGET_UNIT_LINE, 1)
        assert action.get_remaining() == 0

    def test_action_attack_get_type(self):
        """Test action type is ATTACK."""
        castle = Castle()
        unit = Unit(castle)
        action = ActionAttack(unit, 1, 1, constants.TARGET_UNIT_LINE, 1)
        
        assert action.get_type() == constants.ACTION_ATTACK

    def test_action_attack_refresh(self):
        """Test refresh resets remaining attacks."""
        castle = Castle()
        unit = Unit(castle)
        action = ActionAttack(unit, 2, 1, constants.TARGET_UNIT_LINE, 1)
        
        action.remaining = 0
        action.refresh()
        assert action.remaining == 2


class TestActionAttackValidation:
    """Test ActionAttack validation."""

    def test_validate_with_no_remaining(self):
        """Test validation fails when no attacks remaining."""
        castle = Castle()
        unit = Unit(castle)
        unit._deployed = True
        action = ActionAttack(unit, 1, 1, constants.TARGET_UNIT_LINE, 1)
        action.remaining = 0
        
        assert action.validate(10) == False

    def test_validate_when_not_deployed(self):
        """Test validation fails when unit not deployed."""
        castle = Castle()
        unit = Unit(castle)
        unit._deployed = False
        action = ActionAttack(unit, 1, 1, constants.TARGET_UNIT_LINE, 1)
        
        assert action.validate(10) == False

    def test_validate_target_in_range(self):
        """Test validation succeeds when target is in range."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        attacker = Unit(castle1)
        attacker.battlefield = battlefield
        attacker.location = 60
        attacker._deployed = True
        attacker.set_damage(3)
        battlefield.add_unit(attacker)
        
        target = Unit(castle2)
        target.battlefield = battlefield
        target.location = 61  # Adjacent
        target._deployed = True
        battlefield.add_unit(target)
        
        action = ActionAttack(attacker, 1, 1, constants.TARGET_UNIT_LINE, 1)
        
        assert action.validate(61) == True

    def test_validate_target_out_of_range(self):
        """Test validation fails when target is out of range."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        attacker = Unit(castle1)
        attacker.battlefield = battlefield
        attacker.location = 60
        attacker._deployed = True
        battlefield.add_unit(attacker)
        
        target = Unit(castle2)
        target.battlefield = battlefield
        target.location = 0  # Far away
        target._deployed = True
        battlefield.add_unit(target)
        
        action = ActionAttack(attacker, 1, 1, constants.TARGET_UNIT_LINE, 1)
        
        assert action.validate(0) == False


class TestActionAttackPerform:
    """Test ActionAttack perform method."""

    def test_perform_attack_deals_damage(self):
        """Test performing an attack deals damage to target."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        attacker = Unit(castle1)
        attacker.battlefield = battlefield
        attacker.location = 60
        attacker._deployed = True
        attacker.set_damage(3)
        attacker.actions_left = 2
        attacker.actions_max = 2
        battlefield.add_unit(attacker)
        
        target = Unit(castle2)
        target.battlefield = battlefield
        target.location = 61
        target.set_life(5)
        target.set_life_max(5)
        target.set_armor(1)
        battlefield.add_unit(target)
        
        action = ActionAttack(attacker, 1, 1, constants.TARGET_UNIT_LINE, 1)
        
        initial_life = target.life
        result = action.perform(61)
        
        # Target should have taken damage (3 damage - 1 armor = 2 damage)
        assert target.life < initial_life
        assert target.life == 3  # 5 - 2 = 3
        assert "Invalid" not in result

    def test_perform_attack_deducts_actions(self):
        """Test performing attack deducts actions."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        attacker = Unit(castle1)
        attacker.battlefield = battlefield
        attacker.location = 60
        attacker._deployed = True
        attacker.set_damage(3)
        attacker.actions_left = 2
        attacker.actions_max = 2
        battlefield.add_unit(attacker)
        
        target = Unit(castle2)
        target.battlefield = battlefield
        target.location = 61
        target.set_life(5)
        target.set_life_max(5)
        battlefield.add_unit(target)
        
        action = ActionAttack(attacker, 1, 1, constants.TARGET_UNIT_LINE, 1)
        
        initial_actions = attacker.actions_left
        action.perform(61)
        
        assert attacker.actions_left == initial_actions - 1

    def test_perform_attack_deducts_commands(self):
        """Test performing attack deducts castle commands."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        attacker = Unit(castle1)
        attacker.battlefield = battlefield
        attacker.location = 60
        attacker._deployed = True
        attacker.set_damage(3)
        attacker.actions_left = 2
        battlefield.add_unit(attacker)
        
        target = Unit(castle2)
        target.battlefield = battlefield
        target.location = 61
        target.set_life(5)
        battlefield.add_unit(target)
        
        action = ActionAttack(attacker, 1, 1, constants.TARGET_UNIT_LINE, 1)
        
        initial_commands = castle1.commands_left
        action.perform(61)
        
        assert castle1.commands_left == initial_commands - 1

    def test_perform_attack_decrements_remaining(self):
        """Test performing attack decrements remaining count."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        attacker = Unit(castle1)
        attacker.battlefield = battlefield
        attacker.location = 60
        attacker._deployed = True
        attacker.set_damage(3)
        battlefield.add_unit(attacker)
        
        target = Unit(castle2)
        target.battlefield = battlefield
        target.location = 61
        target.set_life(5)
        battlefield.add_unit(target)
        
        action = ActionAttack(attacker, 2, 1, constants.TARGET_UNIT_LINE, 1)
        
        assert action.remaining == 2
        action.perform(61)
        assert action.remaining == 1

    def test_perform_attack_kills_unit(self):
        """Test attack can kill a unit."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        attacker = Unit(castle1)
        attacker.battlefield = battlefield
        attacker.location = 60
        attacker._deployed = True
        attacker.set_damage(10)
        battlefield.add_unit(attacker)
        
        target = Unit(castle2)
        target.battlefield = battlefield
        target.location = 61
        target.set_life(2)
        target.set_life_max(2)
        target.set_armor(0)
        battlefield.add_unit(target)
        
        action = ActionAttack(attacker, 1, 1, constants.TARGET_UNIT_LINE, 1)
        
        action.perform(61)
        
        assert target.is_dead() == True
        assert target not in battlefield.units

    def test_perform_attack_invalid_target(self):
        """Test performing attack on invalid target returns error."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        attacker = Unit(castle1)
        attacker.battlefield = battlefield
        attacker.location = 60
        attacker._deployed = True
        battlefield.add_unit(attacker)
        
        action = ActionAttack(attacker, 1, 1, constants.TARGET_UNIT_LINE, 1)
        
        # Attack empty location
        result = action.perform(62)
        assert "Invalid" in result

    def test_perform_attack_with_armor(self):
        """Test attack damage is reduced by armor."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        attacker = Unit(castle1)
        attacker.battlefield = battlefield
        attacker.location = 60
        attacker._deployed = True
        attacker.set_damage(5)
        battlefield.add_unit(attacker)
        
        target = Unit(castle2)
        target.battlefield = battlefield
        target.location = 61
        target.set_life(10)
        target.set_life_max(10)
        target.set_armor(2)  # Should reduce damage by 2
        battlefield.add_unit(target)
        
        action = ActionAttack(attacker, 1, 1, constants.TARGET_UNIT_LINE, 1)
        
        action.perform(61)
        
        # 5 damage - 2 armor = 3 damage
        assert target.life == 7

    def test_perform_attack_armor_cannot_go_negative(self):
        """Test armor reduction cannot make damage negative."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        attacker = Unit(castle1)
        attacker.battlefield = battlefield
        attacker.location = 60
        attacker._deployed = True
        attacker.set_damage(2)
        battlefield.add_unit(attacker)
        
        target = Unit(castle2)
        target.battlefield = battlefield
        target.location = 61
        target.set_life(10)
        target.set_life_max(10)
        target.set_armor(5)  # More armor than damage
        battlefield.add_unit(target)
        
        action = ActionAttack(attacker, 1, 1, constants.TARGET_UNIT_LINE, 1)
        
        initial_life = target.life
        action.perform(61)
        
        # Life should not decrease (damage reduced to 0)
        assert target.life == initial_life

