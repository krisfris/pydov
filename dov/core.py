import pygame
import math
import operator

from config import threshold_radius, dialing_threshold, framerate


joystick_id = 0
left_axes, right_axes = (0, 1), (3, 4)


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


class DovEvent:
    STICK_ACTION = 0
    KEY_DOWN = 1
    KEY_UP = 2

    def __init__(self, type, **data):
        self.type = type
        self.data = data

    def __getattr__(self, key):
        return self.data[key]

    def __repr__(self):
        attrs = ', '.join((f'{k}={v}' for k, v in self.data.items()))
        return f'DovEvent(type={self.type}, {attrs})'


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


def handle_stick_positions(lx, ly, rx, ry, event_callback, left=Joystick(), right=Joystick()):
    left.frame(lx, ly)
    right.frame(rx, ry)

    if not left.active and not right.active and (left.stack or right.stack):
        inp = (tuple(left.stack), tuple(right.stack))
        event_callback(DovEvent(DovEvent.STICK_ACTION, inp=inp))
        left.reset()
        right.reset()


def handle_hat_motions(x, y, event_callback, state=[0, 0]):
    prev_x, prev_y = state
    x, y = state[0], state[1] = x, y
    if prev_x == 0 and x == -1:
        event_callback(DovEvent(DovEvent.KEY_DOWN, key='left'))
    elif prev_x == 0 and x == 1:
        event_callback(DovEvent(DovEvent.KEY_DOWN, key='right'))
    elif prev_y == 0 and y == -1:
        event_callback(DovEvent(DovEvent.KEY_DOWN, key='down'))
    elif prev_y == 0 and y == 1:
        event_callback(DovEvent(DovEvent.KEY_DOWN, key='up'))
    elif prev_x == -1 and x == 0:
        event_callback(DovEvent(DovEvent.KEY_UP, key='left'))
    elif prev_x == 1 and x == 0:
        event_callback(DovEvent(DovEvent.KEY_UP, key='right'))
    elif prev_y == -1 and y == 0:
        event_callback(DovEvent(DovEvent.KEY_UP, key='down'))
    elif prev_y == 1 and y == 0:
        event_callback(DovEvent(DovEvent.KEY_UP, key='up'))


buttons = {0: 'space', 1: 'return', 3: 'backspace', 4: 'shift',
           5: 'ctrl', 6: 'alt', 7: 'winleft'}


def update(joystick, event_callback):
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            if key := buttons.get(event.button):
                event_callback(DovEvent(DovEvent.KEY_DOWN, key=key))
        elif event.type == pygame.JOYBUTTONUP:
            if key := buttons.get(event.button):
                event_callback(DovEvent(DovEvent.KEY_UP, key=key))
        elif event.type == pygame.JOYHATMOTION:
            handle_hat_motions(*event.value, event_callback)

    # Update sticks
    handle_stick_positions(*[joystick.get_axis(x) for x in [left_axes[0], left_axes[1],
                                                            right_axes[0], right_axes[1]]],
                          event_callback)



def run_dov(event_callback):
    pygame.init()
    pygame.joystick.init()
    clock = pygame.time.Clock()
    pygame.event.set_allowed([pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP, pygame.JOYHATMOTION])

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    while True:
        update(joystick, event_callback)
        clock.tick(framerate)


if __name__ == '__main__':
    def print_event(e):
        print(e)
    run_dov(print_event)
