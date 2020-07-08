import sys
import math
import time
from collections import deque
import pygame
import pygame.gfxdraw
import pygame.freetype

from dov.main import joystick_id, left_axes, right_axes, threshold_radius


pygame.init()
pygame.joystick.init()

clock = pygame.time.Clock()

joystick = pygame.joystick.Joystick(joystick_id)
joystick.init()

screen = pygame.display.set_mode([400, 200])
font = pygame.freetype.SysFont(pygame.font.get_default_font(), 14)

sectors = [
#    (-0.5 * math.pi, -0.25 * math.pi),
    (-0.25 * math.pi, 0),
#    (0 , 0.25 * math.pi),
    (0.25 * math.pi, 0.5 * math.pi),
#    (0.5 * math.pi, 0.75 * math.pi),
    (0.75 * math.pi, math.pi),
#    (-math.pi, -0.75 * math.pi),
    (-0.75 * math.pi, -0.5 * math.pi)
]


def draw_stick(center, radius, stick_path):
    # Draw sector lines
    for sector in sectors[:2]:
        pygame.gfxdraw.line(screen,
                            int(math.cos(sector[0]+math.pi) * radius+center[0]),
                            int(math.sin(sector[0]+math.pi) * radius+center[1]),
                            int(math.cos(sector[0]) * radius+center[0]),
                            int(math.sin(sector[0]) * radius+center[1]),
                            (120, 120, 120))

    # Draw sector numbers
    padding = 2; color = (0, 0, 0)
    text, rect = font.render('0', color)
    screen.blit(text, (center[0]-rect.width/2, center[1]-radius-rect.height-padding))
    text, rect = font.render('1', color)
    screen.blit(text, (center[0]+radius+padding, center[1]-rect.height/2))
    text, rect = font.render('2', color)
    screen.blit(text, (center[0]-rect.width/2, center[1]+radius+padding))
    text, rect = font.render('3', color)
    screen.blit(text, (center[0]-radius-rect.width-padding, center[1]-rect.height/2))

    # Draw enclosing rect
    pygame.gfxdraw.rectangle(screen,
                             pygame.Rect(center[0]-radius,
                                         center[1]-radius,
                                         radius*2, radius*2),
                             (255, 0, 0))
    # Draw enclosing circle
    pygame.gfxdraw.aacircle(screen, *center, radius, (255, 0, 0))

    # Draw threshold circle
    pygame.gfxdraw.aacircle(screen, *center, int(threshold_radius * radius), (0, 0, 255))

    # Draw filled circle for each axis position in path
    points = [(int(center[0]-radius+(x+1)*radius), int(center[1]-radius+(y+1)*radius))
              for x, y in stick_path]

    for i, (x, y) in enumerate(points):
        f = i / len(points)
        pygame.gfxdraw.filled_circle(screen, x, y, 6, (0, 0, 0, (f**3)*255))


def draw(paths):
    screen.fill((255, 255, 255))
    radius = int(min(screen.get_width() / 4, screen.get_height() / 2)) - 30

    draw_stick((int(screen.get_width() / 4), int(screen.get_height() / 2)),
               radius,
               [x[:2] for x in paths])

    draw_stick((int(screen.get_width() * 0.75), int(screen.get_height() / 2)),
               radius,
               [x[2:] for x in paths])


def add_motions(paths, rx, ry, lx, ly):
    new = (rx, ry, lx, ly)
    last = paths[-1] if paths else new
    chosen = tuple(new[i] if new[i] != last[i] else last[i] for i in range(4))
    paths.append((chosen[0], chosen[1], chosen[2], chosen[3]))


def main():
    paths = list()
    done = False
    paused = False
    while not done:
        for event in pygame.event.get():
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) \
               or (event.type == pygame.JOYBUTTONDOWN and event.button == 1):
                # Quit on escape or O
                done = True
            elif event.type == pygame.JOYBUTTONDOWN and event.button == 0:
                # Reset paths on X
                paths.clear()
            elif event.type == pygame.JOYBUTTONDOWN and event.button == 2:
                # Take screenshot on triangle
                pygame.image.save(screen, 'screenshots/dov-screenshot-'+str(time.time())+'.png')
            elif event.type == pygame.JOYBUTTONDOWN and event.button == 3:
                # Toggle paused on square
                paused = not paused

        if not paused:
            add_motions(paths,
                        joystick.get_axis(left_axes[0]),
                        joystick.get_axis(left_axes[1]),
                        joystick.get_axis(right_axes[0]),
                        joystick.get_axis(right_axes[1]))

        draw(paths)

        pygame.display.flip()
        #clock.tick(20)

    pygame.quit()


if __name__ == '__main__':
    main()
