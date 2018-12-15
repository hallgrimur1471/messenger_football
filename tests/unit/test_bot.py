#!/usr/bin/env python3.7
# pylint: disable=unused-argument, singleton-comparison, no-self-use

# Standard library
from unittest.mock import patch

# PyPi
# import pytest

# This project
import bot as b


def almost_equal(value_1, value_2, eps):
    return (value_1 + eps >= value_2) and (value_2 - eps <= value_1)


class TestVector:
    def test_calculations(self):
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


class TestTimeRecordedValue:
    @patch("bot.time")
    def test(self, time):
        time.return_value = 1544891730
        tv = b.TimeRecordedValue("foo")
        assert tv.value == "foo"
        assert tv.time == 1544891730

        time.return_value = 1544891345
        tv.value = "bar"
        assert tv.value == "bar"
        assert tv.time == 1544891345


class TestChangeRecordedValue:
    @patch("bot.time")
    def test(self, time):
        time.side_effect = [1544891730, 1544891732]

        cv = b.ChangeRecordedValue(1)
        assert cv.value == 1
        assert cv.value_time == 1544891730
        assert cv.last_value is None
        assert cv.last_value_time is None

        cv.value = 2
        assert cv.value == 2
        assert cv.value_time == 1544891732
        assert cv.last_value == 1
        assert cv.last_value_time == 1544891730


class TestMotionVector:
    def test_calculations(self):
        mv = b.MotionVector(0, 0)
        mv += b.Vector(5, 5)
        assert mv.vector == b.Vector(5, 5)
        mv -= b.Vector(1, 1)
        assert mv.vector == b.Vector(4, 4)

    @patch("bot.time")
    def test_differentiation(self, time):
        time.side_effect = [1544891730, 1544891732]
        mv = b.MotionVector(4, 4)
        mv += b.Vector(16, 16)
        assert almost_equal(mv.differentiated(), b.Vector(8.0, 8.0), 0.0001)


@patch("bot.time")
class TestMovableObject:
    def test_constant_position(self, time):
        iterations = 10
        start_time = 1544891730
        time.side_effect = map(lambda x: 2 * x, range(iterations + 26))
        time.side_effect = map(lambda x: start_time + x, time.side_effect)
        position = b.Vector(10, 10)
        atom = b.MovableObject(position)

        for _ in range(iterations):
            atom.position = position
            assert atom.position == b.Vector(10, 10)
            assert atom.velocity == b.Vector(0, 0)
            assert atom.acceleration == b.Vector(0, 0)

    def test_constant_velocity(self, time):
        iterations = 10
        start_time = 1544891730
        time.side_effect = map(
            lambda i: start_time + (0.3333 * i), range(iterations + 26)
        )
        position = b.Vector(10, 10)
        atom = b.MovableObject(position)

        step_vector = b.Vector(4, 4)
        expected_positions = list(
            map(
                lambda i: position + ((i + 1) * step_vector),
                range(iterations + 10),
            )
        )
        print(expected_positions)

        for i in range(iterations):
            position += step_vector
            atom.position = position
            assert atom.position == expected_positions[i]
            assert almost_equal(atom.velocity, b.Vector(4.0, 4.0), 0.001)
            if i == 0:
                assert almost_equal(atom.acceleration, b.Vector(4, 4), 0.001)
            else:
                assert almost_equal(atom.acceleration, b.Vector(0, 0), 0.001)

    def test_constant_acceleration(self, time):
        iterations = 10
        start_time = 1544891730
        time.side_effect = map(
            lambda i: start_time + (0.3333 * i), range(iterations + 26)
        )
        position = b.Vector(10, 10)
        atom = b.MovableObject(position)

        acceleration = b.Vector(8, 8)
        step_vector = b.Vector(8, 8)
        for _ in range(iterations):
            position += step_vector
            atom.position = position
            assert almost_equal(atom.acceleration, b.Vector(8, 8), 0.001)

            step_vector += acceleration
