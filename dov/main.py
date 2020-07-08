import os
import json
import pygame
import pyautogui
import math

import config
from dov.xlib2pyautogui import get_xlib_to_pyautogui_keymapping


threshold_radius = 0.8

joystick_id = 0
left_axes, right_axes = (0, 1), (3, 4)

buttons = {0: 'space', 1: 'return', 3: 'backspace', 4: 'shift',
           5: 'ctrl', 6: 'alt', 7: 'winleft'}

xlib2pyautogui = get_xlib_to_pyautogui_keymapping()
action_map = {(tuple(x[0][0]), tuple(x[0][1])): xlib2pyautogui[x[1]]
              for x in json.load(open(os.path.join(config.datadir, 'keymap.json')))
              if x[1] in xlib2pyautogui}


def get_sector_by_pos(x, y):
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


class Joystick:
    def __init__(self):
        self.stack = []
        self.waiting = None

    def frame(self, x, y):
        if (x or y) and x**2 + y**2 > threshold_radius ** 2:
            sector = get_sector_by_pos(x, y)
            # Prevent repeated sectors & back and forth between 2 neighboring sectors
            # otherwise slightly inaccurate inputs will lead to multiple crossings of the
            # sector boundary
            if (self.stack and sector != self.stack[-1] and
                (len(self.stack) < 2 or sector != self.stack[-2])) or not self.stack:
                self.stack.append(sector)
        elif self.stack:
            out = self.stack
            self.stack = []
            return out


def trigger_action(inp):
    inp = tuple(tuple() if x is None else tuple(x) for x in inp)
    if action := action_map.get(inp):
        pyautogui.press(action)


def handle_stick_positions(lx, ly, rx, ry, left=Joystick(), right=Joystick()):
    out1 = left.frame(lx, ly)
    out2 = right.frame(rx, ry)

    if out1:
        if right.waiting is not None:
            trigger_action((out1, right.waiting))
            right.waiting = None
        elif out2:
            if left.waiting is not None:
                trigger_action((left.waiting, out2))
                left.waiting = None
            else:
                trigger_action((out1, out2))
        elif right.stack:
            if left.waiting is None:
                left.waiting = out1
        else:
            trigger_action((out1, None))
    elif out2:
        if left.waiting is not None:
            trigger_action((left.waiting, out2))
            left.waiting = None
        elif left.stack:
            if right.waiting is None:
                right.waiting = out2
        else:
            trigger_action((None, out2))


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
