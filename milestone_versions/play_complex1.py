#!/usr/bin/env python3

from time import time, sleep
from statistics import mean
from math import floor, inf
from copy import copy

from pymouse import PyMouse
import mss
import mss.tools
from PIL import Image


def main():
    pass


def grab_image(screen, portion):
    screenshot = screen.grab(portion)
    image = Image.frombytes(
        "RGB", screenshot.size, screenshot.bgra, "raw", "BGRX"
    )
    return image


def resize_image(image, new_width, new_height):
    image_resized = image.resize(
        (new_width, new_height), resample=Image.BICUBIC
    )
    return image_resized


def calculate_pixel_intensity(pixel):
    mean_value = int(mean(pixel))
    reversed_ = abs(mean_value - 255)
    intensity = float(reversed_) / 255
    return intensity


def update_accumulative_map(image, acc_map):
    (width, height) = image.size
    points = []
    for i in range(width):
        for j in range(height):
            pixel = image.getpixel((i, j))
            pixel_intensity = calculate_pixel_intensity(pixel)
            points.append(pixel_intensity)

            acc_map[(i, j)] = pixel_intensity
            if i > 0:
                acc_map[(i, j)] += acc_map[(i - 1, j)]
            if j > 0:
                acc_map[(i, j)] += acc_map[(i, j - 1)]
            if (i > 0) and (j > 0):
                acc_map[(i, j)] -= acc_map[(i - 1, j - 1)]
    # for i in range(0, 10):
    #    print("i:", i)
    #    for j in range(0, 10):
    #        print(acc_map[(i, j)])


def search_for_ball(acc_map, bar_width, bar_height):
    lens_width = floor(bar_width / 4)
    lens_height = bar_height
    left = 0
    right = bar_width - lens_width
    num_steps = 10
    step = floor((right - left) / num_steps)
    cursor = left
    lens = {
        "left": cursor,
        "top": 0,
        "width": lens_width,
        "height": lens_height,
    }
    lens_intensities = []
    while cursor < right:
        lens_intensity = calculate_lens_intensity(lens, acc_map)
        lens_intensities.append((lens_intensity, cursor))
        cursor += step
        lens["left"] = cursor
    mx = (-inf, None)
    for intensity in lens_intensities:
        if intensity[0] > mx[0]:
            mx = intensity
    position_x = mx[1] + round(lens_width / 2)
    confidence = mx[0]
    return (position_x, confidence)


def calculate_lens_intensity(lens, acc_map):
    (left_top, right_top, left_bottom, right_bottom) = (
        (lens["left"], lens["top"]),
        (lens["left"] + lens["width"] - 1, lens["top"]),
        (lens["left"], lens["top"] + lens["height"] - 1),
        (lens["left"] + lens["width"] - 1, lens["top"] + lens["height"] - 1),
    )
    lens_intensity = (
        acc_map[right_bottom]
        - acc_map[left_bottom]
        - acc_map[right_top]
        + acc_map[left_top]
    )
    return lens_intensity / (lens["width"] * lens["height"])


# approx. starting ball top:
# approx. starting ball bottom:
def convert_to_mouse_x_position(acc_x, acc_width, pixel_left, pixel_right):
    # mouse_left = 69
    # mouse_right = 843
    left_favored = interpolate(acc_x, pixel_left, pixel_right, 0, acc_width)
    right_favored = interpolate(
        acc_x + 1, pixel_left, pixel_right, 0, acc_width
    )
    return round(mean((left_favored, right_favored)))


def interpolate(t, v1, v2, t1, t2):
    return v1 + (v2 - v1) * ((t - t1) / (t2 - t1))


def test():
    m = PyMouse()
    already_clicked = False
    with mss.mss() as screen:
        original_bar = {
            "left": 60,
            "top": 880,
            "width": 205 + (635 - 60),
            "height": 200,
        }
        bar = {"left": 60, "top": 880, "width": 205 + (635 - 60), "height": 200}

        start_time = time()
        time_last_clicked = -inf
        iterations = 500
        (resample_width, resample_height) = (40, 25)
        (resample_width, resample_height) = (400, 5)
        # (resample_width, resample_height) = (300, 2)
        acc_map = dict()  # accumulative sum of top and left neighbours
        first_click_complete = False
        # for iteration in range(0, iterations):
        mouse_y = bar["top"] + bar["height"]
        while True:
            image = grab_image(screen, bar)
            resampled_image = resize_image(
                image, resample_width, resample_height
            )
            update_accumulative_map(resampled_image, acc_map)
            acc_x_position, confidence = search_for_ball(
                acc_map, resample_width, resample_height
            )
            mouse_x = convert_to_mouse_x_position(
                acc_x_position,
                resample_width,
                bar["left"],
                bar["left"] + bar["width"],
            )
            confidence_threshold = 0.05
            confidence_threshold = 0.03
            if confidence >= confidence_threshold:
                print(mouse_x, confidence)
            else:
                print("NOPE")
            if (
                (confidence >= confidence_threshold)
                and (time() - time_last_clicked > 0.1)
                and (click_wait_counter >= 0)
                and (ball_has_left)
            ):
                if not first_click_complete:
                    bar["top"] -= 140
                    mouse_y -= 0
                    first_click_complete = True
                m.click(mouse_x, mouse_y)
                ## sleep(sleeping_constant)
                # m.click(mouse_x - 50, mouse_y + 50)
                # sleep(sleeping_constant)
                # m.click(mouse_x + 50, mouse_y + 50)
                # sleep(sleeping_constant)
                # sleep(sleeping_constant)
                # m.click(mouse_x - 100, mouse_y)
                # sleep(sleeping_constant)
                # m.click(mouse_x + 100, mouse_y)
                # sleep(sleeping_constant)
                # if bar["top"] < 770:
                #    bar["top"] -= 50
                time_last_clicked = time()
                already_clicked = True
                print("clicked:", (mouse_x, mouse_y))
            else:
            # if confidence >= 0.1:
            #    print(
            #        "acc_x_pos:",
            #        acc_x_position,
            #        "mouse_x:",
            #        mouse_x,
            #        "confidence:",
            #        confidence,
            #    )
            # else:
            #    pass
            #    # print("NOPE")
        end_time = time()
        duration = end_time - start_time
        print(
            "duration:",
            duration,
            "    iterations/sec:",
            float(iterations) / duration,
        )


def continuously_print_mouse_position():
    m = PyMouse()
    while True:
        print(m.position())


def test_pymouse():
    m = PyMouse()
    print(m.position())
    x_start = 70
    x_end = 843
    for i in range(2):
        # x = x_start
        # interval = int(float(x_end - x_start) / 7)
        # x += interval
        # print("clicking")
        # while x < x_end:
        #    m.click(x, 1039)
        #    sleep(0.01)
        #    x += interval
        m.click(457, 1039)
        sleep(0.7)

    # bring focus back to terminal
    sleep(0.2)
    m.click(1392, 295)


if __name__ == "__main__":
    test()
    # sleep(1)
    # continuously_print_mouse_position()


# resampled_image.save("./resized_image.png")
#
#        football_at_start = {
#            "left": 355,
#            "top": 880,
#            "width": 205,
#            "height": 200,
#        }
#
#        # resampled_image.save("./resized_image.png")
#        # screenshot = screen.grab(bar)
#        # image = Image.frombytes(
#        #    "RGB", screenshot.size, screenshot.bgra, "raw", "BGRX"
#        # )
#        # image = Image.new("RGB", screenshot.size)
#        # pixels = zip(
#        #    screenshot.raw[2::4], screenshot.raw[1::4], screenshot.raw[0::4]
#        # )
#        # image.putdata(list(pixels))
#        # image.show()
#
#        # bring focus back to terminal
#        # m = PyMouse()
#        # sleep(0.2)
#        # m.click(1392, 295)
#
#        # image_resized.save("./resized_image.png")
#        # image = Image.new("RGB", screenshot.size)
#        # pixels = zip(
#        #    screenshot.raw[2::4], screenshot.raw[1::4], screenshot.raw[0::4]
#        # )
#        # image.putdata(list(pixels))
#
#
