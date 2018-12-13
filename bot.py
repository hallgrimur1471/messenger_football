#!/usr/bin/env python3.7

from dataclasses import dataclass, field
from typing import Union, Any
from time import time, sleep
from copy import copy


@dataclass
class Vector:
    x: Union[int, float] = 0
    y: Union[int, float] = 0

    def __add__(self, vector):
        return Vector(self.x + vector.x, self.y + vector.y)

    def __sub__(self, vector):
        return Vector(self.x - vector.x, self.y - vector.y)

    def __truediv__(self, value):
        if (type(value) == int) or (type(value) == float):
            return Vector(self.x / value, self.y / value)
        elif type(value) == Vector:
            return Vector(self.x / value.x, self.y / value.y)
        else:
            raise NotImplementedError(
                f"Unsuported divison of {type(self)} by {type(value)}."
            )

    # overridden to reduce decimal characters when printing vectors with floats
    def __repr__(self):
        if (type(self.x) == int) and (type(self.y) == int):
            (x_repr, y_repr) = (str(self.x), str(self.y))
        else:
            (x_repr, y_repr) = ("f{self.x:.2f}", f"{self.y:.2f}")
        return f"{type(self).__name__}(x={x_repr}, y={y_repr})"


class TimedValue:
    """
    records time when value is set
    """

    def __init__(self, value: Any):
        """
        Args:
            value (Any):
                arbitrary value of any class
        """
        self._value = None
        self._value_time = None  # decimal Unix epoch time

        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        current_time = time()
        self._value = value
        self._value_time = current_time

    @property
    def time(self):
        return self._value_time


class MovingValue:
    def __init__(self, value: Any):
        """
        Args:
            value (Any):
                arbitrary value of any class
        """
        self._value = None
        self._last_value = None

        self.value = value

    @property
    def value(self):
        return self._value.value

    @value.setter
    def value(self, value):
        self._last_value = copy(self._value)
        self._value = TimedValue(value)

    @property
    def value_time(self):
        return self._value.time

    @property
    def last_value(self):
        return self._last_value.value

    @property
    def last_value_time(self):
        return self._last_value.time

    def differentiated(self):
        if (not self._last_value) or (not self._last_value.value):
            # we want to return the class's identity element for
            # differentiation, which is the same as the class's
            # identity element for addition (+)
            # https://en.wikipedia.org/wiki/Identity_element
            value_class = type(self._value.value)
            if value_class == int:
                identity_value = 0
            elif value_class == float:
                identity_value = 0.0
            elif type(self._value.value) == Vector:
                identity_value = Vector(0, 0)
            else:
                raise NotImplementedError(
                    f"Identity value of {value_class} "
                    "for differentiation unknown"
                )
            return identity_value

        value_change = self._value.value - self._last_value.value
        time_change = self._value.time - self._last_value.time
        differentiated_value = value_change / time_change
        return differentiated_value


class MovableObject:
    def __init__(self, position: Vector = Vector()):
        """
        Args:
            position (Vector):
                position of object in arbitrary unit
        """
        self._position = MovingValue(position)
        self._velocity = MovingValue(None)  # units/sec
        self._acceleration = MovingValue(None)  # units/(sec**2)

        self.position = position

    @property
    def position(self):
        return self._position.value

    @position.setter
    def position(self, position_value):
        self._position.value = position_value
        self._velocity.value = self._position.differentiated()
        self._acceleration.value = self._velocity.differentiated()
        print(
            f"position: {self._position.value} | "
            f"velocity: {self._velocity.value} | "
            f"acceleration: {self._acceleration.value}"
        )

    @property
    def velocity(self):
        return self._velocity.value

    @property
    def acceleration(self):
        return self._acceleration.value


def main():
    p = Vector(15, 15)
    atom = MovableObject(p)
    test_iterations = 10
    wait_time = 0.1

    if True:
        print("CONSTANT POSITION")
        for _ in range(test_iterations):
            sleep(wait_time)
            atom.position = p

        print("CONSTANT VELOCITY")
        (x_step, y_step) = (4, 2)
        for _ in range(test_iterations):
            sleep(wait_time)
            p += Vector(x_step, y_step)
            atom.position = p

        print("CONSTANT ACCELERATION")
        (x_step, y_step) = (4, 2)
        (x_initial, y_initial) = (x_step, y_step)
        for _ in range(test_iterations):
            sleep(wait_time)
            p += Vector(x_step, y_step)
            atom.position = p
            x_step += x_initial
            y_step += y_initial

    if False:
        print("TESTING SPEED ...")
        iterations = 1000000
        positions = map(lambda p: Vector(p, p), range(iterations))
        atom = MovableObject()
        start_time = time()
        for _ in range(iterations):
            atom.position = positions.__next__()
        end_time = time()
        duration = end_time - start_time
        print(
            f"duration: {duration:.2f} iterations/s: {iterations/duration:.2f}"
        )

        # Test results:
        # MovableObject can be moved at 80000 hz


if __name__ == "__main__":
    main()
