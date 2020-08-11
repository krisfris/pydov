import os
import json
import pygame
import pyautogui
import math
import operator

import config
from dov.xlib2pyautogui import get_xlib_to_pyautogui_keymapping


threshold_radius = 0.8
dialing_threshold = 0.2

joystick_id = 0
left_axes, right_axes = (0, 1), (3, 4)

buttons = {0: 'space', 1: 'return', 3: 'backspace', 4: 'shift',
           5: 'ctrl', 6: 'alt', 7: 'winleft'}

xlib2pyautogui = get_xlib_to_pyautogui_keymapping()
action_map = {(tuple(x[0][0]), tuple(x[0][1])): xlib2pyautogui[x[1]]
              for x in json.load(open(os.path.join(config.datadir, 'keymap.json')))
              if x[1] in xlib2pyautogui}


def get_sector_4(x, y):
    y = -y
    if y >= abs(x):
        return 0
    elif -y >= abs(x):
        return 2
    elif x >= abs(y):
        return 1
    elif -x >= abs(y):
        return 3
    assert False, (x, y)


def angle_between(angle, a, b):
    if a < b:
        return a <= angle and angle <= b
    return a <= angle or angle <= b


def norm_angle(angle):
    return (20.0 * math.pi + angle) % (2.0 * math.pi)


def sector_angles_8(narrowing_shift=0.1):
    angles = [4.52, 5.3, 6.09, 0.59, 1.37, 2.16, 2.95, 3.73]
    angles[0] += narrowing_shift
    angles[1] -= narrowing_shift
    angles[2] += narrowing_shift
    angles[3] -= narrowing_shift
    angles[4] += narrowing_shift
    angles[5] -= narrowing_shift
    angles[6] += narrowing_shift
    angles[7] -= narrowing_shift
    return angles


def angle_from_coordinates(x, y):
    return norm_angle(math.atan2(y, x))


def get_sector_8(x, y, sector_angles=sector_angles_8()):
    angle = angle_from_coordinates(x, y)
    l = list(range(9))
    for i, (a, b) in enumerate(zip(l, l[1:])):
        b %= 8
        if angle_between(angle, sector_angles[a], sector_angles[b]):
            return i


def test_threshold(x, y):
    return (x or y) and x**2 + y**2 > threshold_radius ** 2


def angle_diff(a, b):
    """Signed difference between 2 angles."""
    f = (a - b) % math.tau
    g = (b - a) % math.tau
    return -f if f < g else g


class Joystick:
    def __init__(self):
        self.reset()

    def reset(self):
        self.stack = []
        self.active = False
        self.dialing = False
        self.reset_sector_counts()

    def reset_sector_counts(self):
        self.sector_counts = [0 for _ in range(8)]

    def frame(self, x, y):
        if test_threshold(x, y):
            angle = angle_from_coordinates(x, y)
            if not self.active:
                self.start_pos = (x, y)
                self.start_angle = angle_from_coordinates(x, y)
            self.active = True
            if not self.dialing:
                if abs(angle_diff(angle, self.start_angle)) > dialing_threshold:
                    self.stack.append(get_sector_4(*self.start_pos))
                    self.dialing = True
            if self.dialing:
                sector = get_sector_4(x, y)
                # Prevent repeated sectors & back and forth between 2 neighboring sectors
                # otherwise slightly inaccurate inputs will lead to multiple crossings of the
                # sector boundary
                if (self.stack and sector != self.stack[-1] and
                    (len(self.stack) < 2 or sector != self.stack[-2])) or not self.stack:
                    self.stack.append(sector)
            else:
                sector = get_sector_8(x, y)
                self.sector_counts[sector] += 1
        else:
            self.active = False
            if not self.dialing:
                max_sector, count = max(enumerate(self.sector_counts), key=operator.itemgetter(1))
                if count:
                    self.stack.append(max_sector)
                    self.reset_sector_counts()
            else:
                self.dialing = False


def trigger_action(inp):
    inp = tuple(tuple(x) for x in inp)
    if action := action_map.get(inp):
        pyautogui.press(action)


def handle_stick_positions(lx, ly, rx, ry, left=Joystick(), right=Joystick()):
    left.frame(lx, ly)
    right.frame(rx, ry)

    if not left.active and not right.active and (left.stack or right.stack):
        trigger_action((left.stack, right.stack))
        left.reset()
        right.reset()


def handle_hat_motions(x, y, state=[0, 0]):
    prev_x, prev_y = state
    x, y = state[0], state[1] = event.values
    if prev_x == 0 and x == -1:
        pyautogui.keyDown('left')
    elif prev_x == 0 and x == 1:
        pyautogui.keyDown('right')
    elif prev_y == 0 and y == -1:
        pyautogui.keyDown('down')
    elif prev_y == 0 and y == 1:
        pyautogui.keyDown('up')
    elif prev_x == -1 and x == 0:
        pyautogui.keyUp('left')
    elif prev_x == 1 and x == 0:
        pyautogui.keyUp('right')
    elif prev_y == -1 and y == 0:
        pyautogui.keyUp('down')
    elif prev_y == 1 and y == 0:
        pyautogui.keyUp('up')


def update(joystick):
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            if key := buttons.get(event.button):
                pyautogui.keyDown(key)
        elif event.type == pygame.JOYBUTTONUP:
            if key := buttons.get(event.button):
                pyautogui.keyUp(key)
        elif event.type == pygame.JOYHATMOTION:
            handle_hat_motions(*event.values)

    # Update sticks
    handle_stick_positions(*[joystick.get_axis(x) for x in [left_axes[0], left_axes[1],
                                                            right_axes[0], right_axes[1]]])



def main():
    pygame.init()
    pygame.joystick.init()
    clock = pygame.time.Clock()
    pygame.event.set_allowed([pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP, pygame.JOYHATMOTION])

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    while True:
        update(joystick)
        clock.tick(20)


if __name__ == '__main__':
    main()
