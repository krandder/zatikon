"""
Tests for Event system - PREVIEW and WITNESS events.
"""
import pytest
from zatikon import constants
from zatikon.event import Event
from zatikon.unit import Unit
from zatikon.castle import Castle
from zatikon.battlefield import BattleField


class TestEvent:
    """Test Event base class."""

    def test_event_has_event_type(self):
        """Test event has an event type."""
        castle = Castle()
        unit = Unit(castle)
        
        class TestEvent(Event):
            def get_event_type(self):
                return constants.EVENT_PREVIEW_MOVE
            
            def perform(self, source, target, val1, val2, default_result):
                return default_result
            
            def get_owner(self):
                return unit
            
            def get_priority(self):
                return 50
        
        event = TestEvent()
        assert event.get_event_type() == constants.EVENT_PREVIEW_MOVE

    def test_event_perform_returns_result(self):
        """Test event perform method returns a result."""
        castle = Castle()
        unit = Unit(castle)
        
        class TestEvent(Event):
            def get_event_type(self):
                return constants.EVENT_PREVIEW_MOVE
            
            def perform(self, source, target, val1, val2, default_result):
                return constants.EVENT_CANCEL
            
            def get_owner(self):
                return unit
            
            def get_priority(self):
                return 50
        
        event = TestEvent()
        result = event.perform(None, None, 0, 0, constants.EVENT_OK)
        assert result == constants.EVENT_CANCEL


class TestBattleFieldEventSystem:
    """Test BattleField event firing system."""

    def test_event_fires_with_default_result(self):
        """Test event fires and returns default result when no handlers."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        unit1 = Unit(castle1)
        unit1.battlefield = battlefield
        battlefield.add_unit(unit1)
        
        result = battlefield.event(
            constants.EVENT_PREVIEW_MOVE,
            unit1,
            None,
            constants.EVENT_NONE,
            constants.EVENT_NONE,
            constants.EVENT_OK
        )
        
        assert result == constants.EVENT_OK

    def test_event_fires_preview_move(self):
        """Test PREVIEW_MOVE event fires and can be cancelled."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        unit1 = Unit(castle1)
        unit1.battlefield = battlefield
        battlefield.add_unit(unit1)
        
        unit2 = Unit(castle2)
        unit2.battlefield = battlefield
        battlefield.add_unit(unit2)
        
        # Create a test event that cancels movement
        class CancelMoveEvent(Event):
            def get_event_type(self):
                return constants.EVENT_PREVIEW_MOVE
            
            def perform(self, source, target, val1, val2, default_result):
                if source == unit1:
                    return constants.EVENT_CANCEL
                return default_result
            
            def get_owner(self):
                return unit2
            
            def get_priority(self):
                return 50
        
        event = CancelMoveEvent()
        unit2.add_event(event)
        
        result = battlefield.event(
            constants.EVENT_PREVIEW_MOVE,
            unit1,
            None,
            constants.EVENT_NONE,
            constants.EVENT_NONE,
            constants.EVENT_OK
        )
        
        assert result == constants.EVENT_CANCEL

    def test_event_fires_preview_action(self):
        """Test PREVIEW_ACTION event fires."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        attacker = Unit(castle1)
        attacker.battlefield = battlefield
        battlefield.add_unit(attacker)
        
        defender = Unit(castle2)
        defender.battlefield = battlefield
        battlefield.add_unit(defender)
        
        # Create a test event that modifies damage
        class ModifyDamageEvent(Event):
            def get_event_type(self):
                return constants.EVENT_PREVIEW_ACTION
            
            def perform(self, source, target, val1, val2, default_result):
                if target == defender and val1 == constants.ACTION_ATTACK:
                    # Modify damage (val2 would be damage amount)
                    return 5  # Return modified damage
                return default_result
            
            def get_owner(self):
                return defender
            
            def get_priority(self):
                return 50
        
        event = ModifyDamageEvent()
        defender.add_event(event)
        
        result = battlefield.event(
            constants.EVENT_PREVIEW_ACTION,
            attacker,
            defender,
            constants.ACTION_ATTACK,
            constants.EVENT_NONE,
            constants.EVENT_OK
        )
        
        assert result == 5

    def test_event_fires_witness_action(self):
        """Test WITNESS_ACTION event fires after action."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        attacker = Unit(castle1)
        attacker.battlefield = battlefield
        battlefield.add_unit(attacker)
        
        defender = Unit(castle2)
        defender.battlefield = battlefield
        battlefield.add_unit(defender)
        
        witness_called = []
        
        class WitnessEvent(Event):
            def get_event_type(self):
                return constants.EVENT_WITNESS_ACTION
            
            def perform(self, source, target, val1, val2, default_result):
                witness_called.append((source, target, val1))
                return default_result
            
            def get_owner(self):
                return defender
            
            def get_priority(self):
                return 50
        
        event = WitnessEvent()
        defender.add_event(event)
        
        result = battlefield.event(
            constants.EVENT_WITNESS_ACTION,
            attacker,
            defender,
            constants.ACTION_ATTACK,
            constants.EVENT_NONE,
            constants.EVENT_OK
        )
        
        assert result == constants.EVENT_OK
        assert len(witness_called) == 1
        assert witness_called[0][0] == attacker
        assert witness_called[0][1] == defender

    def test_event_priority_ordering(self):
        """Test events are processed in priority order."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        unit1 = Unit(castle1)
        unit1.battlefield = battlefield
        battlefield.add_unit(unit1)
        
        results = []
        
        class LowPriorityEvent(Event):
            def get_event_type(self):
                return constants.EVENT_PREVIEW_MOVE
            
            def perform(self, source, target, val1, val2, default_result):
                results.append("low")
                return default_result
            
            def get_owner(self):
                return unit1
            
            def get_priority(self):
                return 10
        
        class HighPriorityEvent(Event):
            def get_event_type(self):
                return constants.EVENT_PREVIEW_MOVE
            
            def perform(self, source, target, val1, val2, default_result):
                results.append("high")
                return constants.EVENT_CANCEL  # Cancel to stop processing
            
            def get_owner(self):
                return unit1
            
            def get_priority(self):
                return 100
        
        unit1.add_event(LowPriorityEvent())
        unit1.add_event(HighPriorityEvent())
        
        result = battlefield.event(
            constants.EVENT_PREVIEW_MOVE,
            unit1,
            None,
            constants.EVENT_NONE,
            constants.EVENT_NONE,
            constants.EVENT_OK
        )
        
        # High priority should run first and cancel
        assert result == constants.EVENT_CANCEL
        assert results == ["high"]  # Low priority shouldn't run

    def test_event_sequence_ordering(self):
        """Test events with same priority are ordered by unit sequence."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        unit1 = Unit(castle1)
        unit1.battlefield = battlefield
        seq1 = battlefield.get_sequence()
        battlefield.add_unit(unit1)
        
        unit2 = Unit(castle2)
        unit2.battlefield = battlefield
        seq2 = battlefield.get_sequence()
        battlefield.add_unit(unit2)
        
        # Make sure unit1 has lower sequence (added first)
        assert seq1 < seq2
        
        results = []
        
        class Event1(Event):
            def get_event_type(self):
                return constants.EVENT_PREVIEW_MOVE
            
            def perform(self, source, target, val1, val2, default_result):
                results.append("unit1")
                return default_result
            
            def get_owner(self):
                return unit1
            
            def get_priority(self):
                return 50
        
        class Event2(Event):
            def get_event_type(self):
                return constants.EVENT_PREVIEW_MOVE
            
            def perform(self, source, target, val1, val2, default_result):
                results.append("unit2")
                return constants.EVENT_CANCEL
            
            def get_owner(self):
                return unit2
            
            def get_priority(self):
                return 50
        
        unit1.add_event(Event1())
        unit2.add_event(Event2())
        
        result = battlefield.event(
            constants.EVENT_PREVIEW_MOVE,
            unit1,
            None,
            constants.EVENT_NONE,
            constants.EVENT_NONE,
            constants.EVENT_OK
        )
        
        # Unit1's event should run first (lower sequence)
        assert results == ["unit1", "unit2"] or results == ["unit1"]  # May stop after unit1

    def test_event_cancel_stops_processing(self):
        """Test EVENT_CANCEL stops further event processing."""
        castle1 = Castle(constants.TEAM_1)
        castle2 = Castle(constants.TEAM_2)
        battlefield = BattleField(castle1, castle2)
        
        unit1 = Unit(castle1)
        unit1.battlefield = battlefield
        battlefield.add_unit(unit1)
        
        results = []
        
        class CancelEvent(Event):
            def get_event_type(self):
                return constants.EVENT_PREVIEW_MOVE
            
            def perform(self, source, target, val1, val2, default_result):
                results.append("cancel")
                return constants.EVENT_CANCEL
            
            def get_owner(self):
                return unit1
            
            def get_priority(self):
                return 50
        
        class LaterEvent(Event):
            def get_event_type(self):
                return constants.EVENT_PREVIEW_MOVE
            
            def perform(self, source, target, val1, val2, default_result):
                results.append("later")
                return default_result
            
            def get_owner(self):
                return unit1
            
            def get_priority(self):
                return 40  # Lower priority, should run after
        
        unit1.add_event(CancelEvent())
        unit1.add_event(LaterEvent())
        
        result = battlefield.event(
            constants.EVENT_PREVIEW_MOVE,
            unit1,
            None,
            constants.EVENT_NONE,
            constants.EVENT_NONE,
            constants.EVENT_OK
        )
        
        assert result == constants.EVENT_CANCEL
        # Later event should not run because cancel stopped processing
        assert "later" not in results

