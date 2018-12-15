#!/usr/bin/env python3.7
# pylint: disable=unused-argument, singleton-comparison, no-self-use

# Standard library
from unittest.mock import MagicMock, patch, call

# PyPi
import pytest

# This project
import bot as b


class TestVector:
    def test_vector_calculations(self):
        assert b.Vector(1, 2) + b.Vector(4, 2) == b.Vector(5, 4)
        assert sum([b.Vector(0, 0), b.Vector(0, 0)]) == b.Vector(0, 0)
        assert sum([b.Vector(1, 2), b.Vector(3, 4)]) == b.Vector(4, 6)
        assert 2 + b.Vector(3, 4) == b.Vector(5, 6)
        assert b.Vector(3, 4) + 2 == b.Vector(5, 6)

        assert b.Vector(100, 200) - b.Vector(100, 100) == b.Vector(0, 100)
        assert b.Vector(0, 0) - b.Vector(0, 0) == b.Vector(0, 0)
        assert b.Vector(0, 10) - b.Vector(10, 10) == b.Vector(-10, 0)
        assert 8 - b.Vector(2, 2) == b.Vector(6, 6)
        assert b.Vector(2, 2) - 8 == b.Vector(-6, -6)

        assert b.Vector(100, 200) / b.Vector(10, 20) == b.Vector(10, 10)
        assert b.Vector(0, 0) / b.Vector(10, 20) == b.Vector(0, 0)
        assert b.Vector(10, 16) / 2 == b.Vector(5, 8)


class TestPosition:
    def test_position_calculations(self):
        assert b.Position(1, 2) + b.Position(4, 2) == b.Position(5, 4)
        assert sum([b.Position(0, 0), b.Position(0, 0)]) == b.Position(0, 0)
        assert sum([b.Position(1, 2), b.Position(3, 4)]) == b.Position(4, 6)
        assert 2 + b.Position(3, 4) == b.Position(5, 6)
        assert b.Position(3, 4) + 2 == b.Position(5, 6)

        assert b.Position(100, 200) - b.Position(100, 100) == b.Position(0, 100)
        assert b.Position(0, 0) - b.Position(0, 0) == b.Position(0, 0)
        assert b.Position(0, 10) - b.Position(10, 10) == b.Position(-10, 0)
        assert 8 - b.Position(2, 2) == b.Position(6, 6)
        assert b.Position(2, 2) - 8 == b.Position(-6, -6)

        assert b.Position(100, 200) / b.Position(10, 20) == b.Position(10, 10)
        assert b.Position(0, 0) / b.Position(10, 20) == b.Position(0, 0)
        assert b.Position(10, 16) / 2 == b.Position(5, 8)

    def test_position_differentiation(self):
        p = b.Position(0, 0)
        p += b.Vector(1, 1)
        assert type(p) == b.Position

        velocity = p.differentiated()
        assert type(velocity) == b.Velocity
