#!/usr/bin/env python3.7

# Standard Library
from dataclasses import dataclass, field
from typing import Union, Any
from time import time, sleep
from copy import copy
from os.path import dirname, abspath, join

# PyPi
from pymouse import PyMouse
from PIL import Image
import mss

# print(PIL.__file__)


@dataclass(order=True, frozen=True)
class Vector:
    x: Union[int, float] = 0
    y: Union[int, float] = 0

    def _add(self, value):
        if self._value_is_numerical(value):
            (added_x, added_y) = (value, value)
        elif type(value) == Vector:
            (added_x, added_y) = (value.x, value.y)
        else:
            raise NotImplementedError(
                f"Unsuported addition of {type(self)} and {type(value)}."
            )
        return Vector(self.x + added_x, self.y + added_y)

    def _subtract(self, value, reverse_subtract=False):
        if self._value_is_numerical(value):
            (subed_x, subed_y) = (value, value)
        elif type(value) == Vector:
            (subed_x, subed_y) = (value.x, value.y)
        else:
            if reverse_subtract:
                (start_value, subtracted_value) = (value, self)
            else:
                (start_value, subtracted_value) = (self, value)
            raise NotImplementedError(
                f"Unsuported subtraction of "
                f"{type(subtracted_value)} from {type(start_value)}"
            )

        if reverse_subtract:
            sub_func = lambda x, y: y - x
        else:
            sub_func = lambda x, y: x - y
        return Vector(sub_func(self.x, subed_x), sub_func(self.y, subed_y))

    def _divide(self, value):
        if self._value_is_numerical(value):
            (divider_x, divider_y) = (value, value)
        elif type(value) == Vector:
            (divider_x, divider_y) = (value.x, value.y)
        else:
            raise NotImplementedError(
                f"Unsuported divison of {type(self)} by {type(value)}."
            )
        return Vector(self.x / divider_x, self.y / divider_y)

    def _multiply(self, value):
        if self._value_is_numerical(value):
            (multiplier_x, multiplier_y) = (value, value)
        elif type(value) == Vector:
            (multiplier_x, multiplier_y) = (value.x, value.y)
        else:
            raise NotImplementedError(
                f"Unsuported multiplication of {type(self)} by {type(value)}."
            )
        return Vector(self.x * multiplier_x, self.y * multiplier_y)

    def _value_is_numerical(self, value):
        return (type(value) == int) or (type(value) == float)

    def __add__(self, value):
        return self._add(value)

    def __radd__(self, value):
        return self._add(value)

    def __sub__(self, value):
        return self._subtract(value)

    def __rsub__(self, value):
        return self._subtract(value, reverse_subtract=True)

    def __truediv__(self, value):
        return self._divide(value)

    def __mul__(self, value):
        return self._multiply(value)

    def __rmul__(self, value):
        return self._multiply(value)

    # overridden to reduce decimal characters when printing vectors with floats
    def __repr__(self):
        if (type(self.x), type(self.y)) == (int, int):
            (x_repr, y_repr) = (str(self.x), str(self.y))
        else:
            (x_repr, y_repr) = (f"{self.x:.2f}", f"{self.y:.2f}")
        return f"{type(self).__name__}(x={x_repr}, y={y_repr})"


class TimeRecordedValue:
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


class ChangeRecordedValue:
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
        if self._value:
            return self._value.value
        else:
            return None

    @value.setter
    def value(self, value):
        self._last_value = copy(self._value)
        self._value = TimeRecordedValue(value)

    @property
    def value_time(self):
        if self._value:
            return self._value.time
        else:
            return None

    @property
    def last_value(self):
        if self._last_value:
            return self._last_value.value
        else:
            return None

    @property
    def last_value_time(self):
        if self._last_value:
            return self._last_value.time
        else:
            return None

    def differentiated(self):
        if (not self._last_value) or (not self._last_value.value):
            # we want to return the class's identity element for
            # differentiation, which is the same as the class's
            # identity element for addition (+)
            # https://en.wikipedia.org/wiki/Identity_element
            value_class = type(self._value.value)
            if value_class == int:
                identity_element = 0
            elif value_class == float:
                identity_element = 0.0
            elif type(self._value.value) == Vector:
                identity_element = Vector(0, 0)
            else:
                raise NotImplementedError(
                    f"Identity element of {value_class} "
                    "for differentiation unknown"
                )
            return identity_element

        value_change = self._value.value - self._last_value.value
        time_change = self._value.time - self._last_value.time
        differentiated_value = value_change / time_change
        return differentiated_value


class MotionVector:
    def __init__(self, x: Union[int, float], y: Union[int, float]):
        self._vector = ChangeRecordedValue(Vector(x, y))

    @property
    def vector(self):
        return self._vector.value

    @vector.setter
    def vector(self, vector):
        self._vector.value = vector

    @property
    def x(self):
        return self._vector.value.x

    @x.setter
    def x(self, x):
        self._vector.value = Vector(x, self.y)

    @property
    def y(self):
        return self._vector.value.y

    @y.setter
    def y(self, y):
        self._vector.value = Vector(self.x, y)

    def differentiated(self):
        return self._vector.differentiated()

    def __add__(self, value):
        self._vector.value += value
        return self

    def __sub__(self, value):
        self._vector.value -= value
        return self


class MovableObject:
    def __init__(self, position: Vector = Vector()):
        """
        Args:
            position (Vector):
                position of object in arbitrary unit
        """
        self._position = MotionVector(position.x, position.y)
        self._velocity = MotionVector(0, 0)  # units/sec
        self._acceleration = MotionVector(0, 0)  # units/(sec**2)

        self.position = position

    @property
    def position(self):
        return self._position.vector

    @position.setter
    def position(self, position_value):
        self._position.vector = position_value
        self._velocity.vector = self._position.differentiated()
        self._acceleration.vector = self._velocity.differentiated()
        print(
            f"position: {self.position} | "
            f"velocity: {self.velocity} | "
            f"acceleration: {self.acceleration}"
        )

    @property
    def velocity(self):
        return self._velocity.vector

    @property
    def acceleration(self):
        return self._acceleration.vector


@dataclass
class ScreenSection:
    top_left: Vector  # (70, 52)
    top_right: Vector  # (842, 52)
    bottom_left: Vector  # (70, 1080)
    bottom_right: Vector  # (842, 1080)

    @property
    def width(self):
        return (self.top_right - self.top_left).x

    @property
    def height(self):
        return (self.bottom_left - self.top_left).y

    @property
    def mss_compatible_format(self):
        """
        converts this screen section to a dict() format
        that the mss module can understand
        """
        return {
            "left": self.top_left.x,
            "top": self.top_left.y,
            "width": self.width,
            "height": self.height,
        }


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
        # After motion vector refactor:
        # MovableObject can be moved at 60000 hz


def test():
    m = PyMouse()
    while True:
        print(m.position())
        sleep(8)


def grab_image(screen_section: ScreenSection, screen_control):
    screenshot = screen_control.grab(screen_section.mss_compatible_format)
    image = Image.frombytes(
        "RGB", screenshot.size, screenshot.bgra, "raw", "BGRX"
    )
    return image


def record():
    android_screen = ScreenSection(
        Vector(70, 52), Vector(842, 52), Vector(70, 1080), Vector(842, 1080)
    )
    num_frames = 8000
    fps = 20
    frame_calculation_time = 0.04
    wait_time = (1.0 / fps) - frame_calculation_time
    print("wait_time:", wait_time)
    project_directory = dirname(abspath(__file__))

    with mss.mss() as screen_control:
        start_time = time()
        for i in range(num_frames):
            image = grab_image(android_screen, screen_control)
            img_path = join(project_directory, f"recorded_frames/image{i}.png")
            image.save(img_path)
            sleep(wait_time)
        end_time = time()
        duration = end_time - start_time
        print(f"actual fps: {num_frames/duration}")


if __name__ == "__main__":
    record()
