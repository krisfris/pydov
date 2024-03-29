# pydov
Touch typing on a gamepad. The goal of this project is to provide an efficient and as ergonomic as possible typing system for gamepads based on simple gestures.
For a full explanation on how this works please see my blog post [Touch typing on a gamepad](https://darkshadow.io/2020/07/07/touch-typing-on-a-gamepad.html).

*To provide feedback, discuss features or collaboration, join this project's Matrix chat room <https://matrix.to/#/#dov:matrix.org>*

## Development setup

This project uses [poetry](https://python-poetry.org/docs/) for dependency management. Once you have poetry all you need to do is run the following command in the project directory.

```
poetry install
```

## Usage

### Keyboard input

Before you can use dov for generating keyboard events, you need to create your own *action mapping*.
This is a json file that defines which actions should be triggered upon an event produced by dov. The file must be formatted
as follows.

```
[[[[0], []], "a"], [[[2], []], "e"], [[[4], []], "o"], [[[6], []], "i"]]
```

This mapping would map `a` to the left stick being moved up and back to the center, `e` to the left stick being moved right and to the center, `o` to the bottom and to the center and `i` to the
left and to the center.

The file is expected to be located at `os.path.join(appdirs.user_data_dir('dov'), 'keymap.json')`. This shall be made configurable in the future.

With the action mapping in place, you can start dov and use it for example to generate keyboard events.

```
poetry run python -m dov.keyboard
```

### Library usage

If you wish to use dov as a library and write your own code for handling events generated by dov, simply run `dov.core.run_dov` with a function that shall be called
upon any dov event as the only parameter. The following example is the actual code used for generating keyboard events.

```
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
```
