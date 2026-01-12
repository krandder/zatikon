"""
Tests for deployment inactive state - units cannot move immediately after deployment.
"""
import pytest
from zatikon import constants
from zatikon.game import Game
from zatikon.unit_factory import UnitFactory


class TestDeploymentInactive:
    """Test that deployed units start inactive."""

    def test_deployed_unit_cannot_move_immediately(self):
        """Test deployed unit cannot move on the same turn it was deployed."""
        game = Game()
        
        # Get valid deployment location
        targets = game._get_castle_targets(game.castle1)
        assert len(targets) > 0
        deploy_location = targets[0]
        
        # Add unit to barracks
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(unit)
        
        # Deploy the unit
        result = game.handle_action(constants.ACTION_DEPLOY, 0, deploy_location)
        assert "Invalid" not in result
        
        # Unit should be deployed but inactive
        deployed_unit = game.battlefield.get_unit_at(deploy_location)
        assert deployed_unit is not None
        assert deployed_unit._deployed == False  # Units start inactive when deployed
        
        # Should not be able to move (inactive)
        assert deployed_unit.deployed() == False  # Cannot act yet
        
        # Try to move - should fail (get a nearby location for move attempt)
        if deployed_unit.move_action:
            move_targets = deployed_unit.move_action.get_targets()
            if move_targets:
                move_target = move_targets[0]
                move_result = game.handle_action(constants.ACTION_MOVE, deploy_location, move_target)
                assert "Invalid" in move_result or "inactive" in move_result.lower() or "deployed" in move_result.lower()

    def test_deployed_unit_can_move_after_turn_end(self):
        """Test deployed unit can move after turn ends and next turn starts."""
        from zatikon.battlefield import BattleField
        
        game = Game()
        
        # Get valid deployment location
        targets = game._get_castle_targets(game.castle1)
        assert len(targets) > 0
        deploy_location = targets[0]
        
        # Deploy unit
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(unit)
        game.handle_action(constants.ACTION_DEPLOY, 0, deploy_location)
        
        # Unit should be inactive
        deployed_unit = game.battlefield.get_unit_at(deploy_location)
        assert deployed_unit.deployed() == False
        
        # End turn (switches to player 2)
        game.end_turn()
        
        # End turn again (back to player 1)
        game.end_turn()
        
        # Now unit should be active and can move
        assert deployed_unit.deployed() == True
        
        # Get valid move targets
        if deployed_unit.move_action:
            move_targets = deployed_unit.move_action.get_targets()
            if move_targets:
                move_target = move_targets[0]
                move_result = game.handle_action(constants.ACTION_MOVE, deploy_location, move_target)
                assert "Invalid" not in move_result or deployed_unit.location == move_target

    def test_deployed_unit_cannot_attack_immediately(self):
        """Test deployed unit cannot attack on the same turn it was deployed."""
        game = Game()
        
        # Get valid deployment location for Castle 1
        targets1 = game._get_castle_targets(game.castle1)
        assert len(targets1) > 0
        deploy_location1 = targets1[0]
        
        # Deploy attacker on turn 1
        attacker = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(attacker)
        game.handle_action(constants.ACTION_DEPLOY, 0, deploy_location1)
        
        # Attacker should be inactive
        attacker_unit = game.battlefield.get_unit_at(deploy_location1)
        assert attacker_unit is not None
        assert attacker_unit.deployed() == False
        
        # Try to attack - should fail (unit inactive)
        # Get a nearby location for attack attempt
        if attacker_unit.attack_action:
            attack_targets = attacker_unit.attack_action.get_targets()
            if attack_targets:
                attack_target = attack_targets[0]
                attack_result = game.handle_action(constants.ACTION_ATTACK, deploy_location1, attack_target)
                assert "Invalid" in attack_result or "deployed" in attack_result.lower() or "inactive" in attack_result.lower()
        
        # End turn and come back - attacker should now be active
        game.end_turn()
        game.end_turn()
        
        # Attacker should now be active (after turn refresh)
        attacker_unit = game.battlefield.get_unit_at(deploy_location1)
        assert attacker_unit is not None
        assert attacker_unit.deployed() == True
        
        # Now the unit can attempt attacks (even if no valid target, error should be different)
        # The key point is: unit was inactive when deployed, now it's active

    def test_unit_refresh_activates_deployed_units(self):
        """Test unit refresh activates deployed units."""
        game = Game()
        
        # Get valid deployment location
        targets = game._get_castle_targets(game.castle1)
        assert len(targets) > 0
        deploy_location = targets[0]
        
        # Deploy unit
        unit = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(unit)
        game.handle_action(constants.ACTION_DEPLOY, 0, deploy_location)
        
        deployed_unit = game.battlefield.get_unit_at(deploy_location)
        assert deployed_unit.deployed() == False  # Inactive
        
        # Refresh unit (happens at start of next turn)
        deployed_unit.refresh()
        
        # Should now be active
        assert deployed_unit.deployed() == True

    def test_multiple_deployed_units_all_inactive(self):
        """Test multiple units deployed in same turn are all inactive."""
        game = Game()
        
        # Get valid deployment locations
        targets = game._get_castle_targets(game.castle1)
        assert len(targets) >= 2
        
        # Deploy two units
        unit1 = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(unit1)
        game.handle_action(constants.ACTION_DEPLOY, 0, targets[0])
        
        unit2 = UnitFactory.create_unit(constants.UNIT_FOOTMAN, game.castle1)
        game.castle1.add_unit(unit2)
        game.handle_action(constants.ACTION_DEPLOY, 0, targets[1])
        
        # Both should be inactive
        deployed1 = game.battlefield.get_unit_at(targets[0])
        deployed2 = game.battlefield.get_unit_at(targets[1])
        
        assert deployed1.deployed() == False
        assert deployed2.deployed() == False

