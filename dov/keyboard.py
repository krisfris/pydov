import os
import json
import pyautogui

import config
import dov.core
from dov.xlib2pyautogui import get_xlib_to_pyautogui_keymapping



xlib2pyautogui = get_xlib_to_pyautogui_keymapping()
action_map = {(tuple(x[0][0]), tuple(x[0][1])): xlib2pyautogui[x[1]]
              for x in json.load(open(config.keymap_file))
              if x[1] in xlib2pyautogui}


def event(e):
    if e.type == e.STICK_ACTION:
        if key := action_map.get(e.inp):
            pyautogui.press(key)
    elif e.type == e.KEY_DOWN:
        pyautogui.keyDown(e.key)
    elif e.type == e.KEY_UP:
        pyautogui.keyUp(e.key)


if __name__ == '__main__':
    dov.core.run_dov(event)
