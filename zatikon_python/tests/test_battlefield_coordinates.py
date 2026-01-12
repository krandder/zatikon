"""
Tests for BattleField coordinate system conversion and distance calculations.
These tests ensure the board coordinate system works correctly for the 11x11 grid.
"""
import pytest
from zatikon import constants
from zatikon.battlefield import BattleField


class TestBattleFieldCoordinates:
    """Test coordinate system conversions."""

    def test_get_x_converts_location_to_x_coordinate(self):
        """Test get_x() converts location to x coordinate correctly."""
        # Test various locations
        assert BattleField.get_x(0) == 0, "Location 0 should be x=0"
        assert BattleField.get_x(5) == 5, "Location 5 should be x=5"
        assert BattleField.get_x(10) == 10, "Location 10 should be x=10"
        assert BattleField.get_x(11) == 0, "Location 11 should be x=0 (next row)"
        assert BattleField.get_x(16) == 5, "Location 16 should be x=5"
        assert BattleField.get_x(120) == 10, "Location 120 should be x=10 (last column)"

    def test_get_y_converts_location_to_y_coordinate(self):
        """Test get_y() converts location to y coordinate correctly."""
        # Test various locations
        assert BattleField.get_y(0) == 0, "Location 0 should be y=0"
        assert BattleField.get_y(10) == 0, "Location 10 should be y=0"
        assert BattleField.get_y(11) == 1, "Location 11 should be y=1"
        assert BattleField.get_y(21) == 1, "Location 21 should be y=1"
        assert BattleField.get_y(55) == 5, "Location 55 should be y=5"
        assert BattleField.get_y(120) == 10, "Location 120 should be y=10 (last row)"

    @pytest.mark.parametrize("location,expected_x,expected_y", [
        (0, 0, 0),
        (5, 5, 0),
        (10, 10, 0),
        (11, 0, 1),
        (16, 5, 1),
        (21, 10, 1),
        (55, 0, 5),
        (60, 5, 5),
        (120, 10, 10),
    ])
    def test_coordinate_conversion_roundtrip(self, location, expected_x, expected_y):
        """Test get_location() and coordinate conversion are inverse operations."""
        x = BattleField.get_x(location)
        y = BattleField.get_y(location)
        
        assert x == expected_x, f"X coordinate should match for location {location}"
        assert y == expected_y, f"Y coordinate should match for location {location}"
        
        # Test inverse: get_location should recreate the original location
        reconstructed = BattleField.get_location(expected_x, expected_y)
        assert reconstructed == location, \
            f"get_location(x={expected_x}, y={expected_y}) should recreate location {location}"

    def test_get_location_converts_xy_to_location(self):
        """Test get_location() converts x,y coordinates to location correctly."""
        # Test first row
        assert BattleField.get_location(0, 0) == 0, "x=0,y=0 should be location 0"
        assert BattleField.get_location(5, 0) == 5, "x=5,y=0 should be location 5"
        assert BattleField.get_location(10, 0) == 10, "x=10,y=0 should be location 10"
        
        # Test second row
        assert BattleField.get_location(0, 1) == 11, "x=0,y=1 should be location 11"
        assert BattleField.get_location(5, 1) == 16, "x=5,y=1 should be location 16"
        assert BattleField.get_location(10, 1) == 21, "x=10,y=1 should be location 21"
        
        # Test middle of board
        assert BattleField.get_location(0, 5) == 55, "x=0,y=5 should be location 55"
        assert BattleField.get_location(5, 5) == 60, "x=5,y=5 should be location 60"
        
        # Test last row
        assert BattleField.get_location(0, 10) == 110, "x=0,y=10 should be location 110"
        assert BattleField.get_location(10, 10) == 120, "x=10,y=10 should be location 120"

    def test_get_distance_calculates_chebyshev_distance(self):
        """Test get_distance() calculates Chebyshev distance correctly."""
        # Same location
        assert BattleField.get_distance(0, 0) == 0, "Distance to self should be 0"
        assert BattleField.get_distance(60, 60) == 0, "Distance to self should be 0"
        
        # Adjacent horizontally
        assert BattleField.get_distance(0, 1) == 1, "Adjacent horizontally should be distance 1"
        assert BattleField.get_distance(5, 6) == 1, "Adjacent horizontally should be distance 1"
        
        # Adjacent vertically
        assert BattleField.get_distance(0, 11) == 1, "Adjacent vertically should be distance 1"
        assert BattleField.get_distance(5, 16) == 1, "Adjacent vertically should be distance 1"
        
        # Adjacent diagonally
        assert BattleField.get_distance(0, 12) == 1, "Adjacent diagonally should be distance 1"
        assert BattleField.get_distance(60, 71) == 1, "Adjacent diagonally should be distance 1"
        
        # Multiple squares away
        assert BattleField.get_distance(0, 2) == 2, "Two squares horizontally should be distance 2"
        assert BattleField.get_distance(0, 22) == 2, "Two squares vertically should be distance 2"
        assert BattleField.get_distance(0, 5) == 5, "Five squares horizontally should be distance 5"
        assert BattleField.get_distance(0, 55) == 5, "Five squares vertically should be distance 5"
        
        # Diagonal distance (Chebyshev uses max of x and y differences)
        assert BattleField.get_distance(0, 33) == 3, "3x3 diagonal should be distance 3"
        assert BattleField.get_distance(0, 60) == 5, "5x5 diagonal should be distance 5"
        
        # Distance is symmetric
        assert BattleField.get_distance(0, 60) == BattleField.get_distance(60, 0), \
            "Distance should be symmetric"

    def test_board_boundaries(self):
        """Test board boundaries are correct (11x11 grid)."""
        # Board should be 11x11 = 121 locations (0-120)
        min_location = 0
        max_location = constants.BOARD_SIZE * constants.BOARD_SIZE - 1
        
        assert min_location == 0, "Minimum location should be 0"
        assert max_location == 120, "Maximum location should be 120 for 11x11 board"
        
        # Test that coordinates are within bounds
        for y in range(constants.BOARD_SIZE):
            for x in range(constants.BOARD_SIZE):
                location = BattleField.get_location(x, y)
                assert 0 <= location <= 120, \
                    f"Location {location} (x={x}, y={y}) should be within bounds"
                
                reconstructed_x = BattleField.get_x(location)
                reconstructed_y = BattleField.get_y(location)
                assert reconstructed_x == x, \
                    f"X coordinate should match for location {location}"
                assert reconstructed_y == y, \
                    f"Y coordinate should match for location {location}"

    def test_coordinate_edge_cases(self):
        """Test coordinate conversion handles edge cases."""
        # Test corners
        top_left = BattleField.get_location(0, 0)
        assert top_left == 0, "Top-left corner should be location 0"
        
        top_right = BattleField.get_location(10, 0)
        assert top_right == 10, "Top-right corner should be location 10"
        
        bottom_left = BattleField.get_location(0, 10)
        assert bottom_left == 110, "Bottom-left corner should be location 110"
        
        bottom_right = BattleField.get_location(10, 10)
        assert bottom_right == 120, "Bottom-right corner should be location 120"
        
        # Test center
        center = BattleField.get_location(5, 5)
        assert center == 60, "Center should be location 60"

