import os
import sys

import cv2
import numpy as np

def show_image(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def get_sprites(sprite_dir):
    sprites = []
    for root, dirs, files in os.walk(sprite_dir):
        for fn in files:
            sprite_name = fn.split('.')[0]
            image = cv2.imread(os.path.join(root, fn), cv2.IMREAD_GRAYSCALE)[::2, ::2]
            w, h = image.shape
            temp = {
                'name': sprite_name,
                'path': fn,
                'image': image,
                'orientation': {
                    'v_flip': False,
                    'h_flip': False,
                },
                'width': w,
                'height': h,
            }
            sprites.append(temp)
    return sprites


class State:
    def __init__(self):
        self.lives = 3
        self.money = 0
        self.world = 1
        self.stage = 1
        self.font = {
            '0': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/Zero.png')[::2, ::2],
            '1': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/1.png')[::2, ::2],
            '2': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/2.png')[::2, ::2],
            '3': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/3.png')[::2, ::2],
            '4': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/4.png')[::2, ::2],
            '5': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/5.png')[::2, ::2],
            '6': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/6.png')[::2, ::2],
            '7': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/7.png')[::2, ::2],
            '8': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/8.png')[::2, ::2],
            '9': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/9.png')[::2, ::2],
            'A': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/A.png')[::2, ::2],
            'D': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/D.png')[::2, ::2],
            'E': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/E.png')[::2, ::2],
            'G': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/G.png')[::2, ::2],
            'I': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/I.png')[::2, ::2],
            'L': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/L.png')[::2, ::2],
            'M': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/M.png')[::2, ::2],
            'O': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/O.png')[::2, ::2],
            'R': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/R.png')[::2, ::2],
            'T': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/T.png')[::2, ::2],
            'V': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/V.png')[::2, ::2],
            'W': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/W.png')[::2, ::2],
        }

    def _get_text(self, frame):
        font = {}
        for key, value in self.font.items():
            font[key] = np.ones(value.shape[:-1], dtype=bool)

            for x, row in enumerate(font[key]):
                for y, pixel in enumerate(row):
                    font[key][x][y] = np.array_equal(value[x][y], np.array([255, 255, 255], dtype=value.dtype))

        for i, row in enumerate(frame):
            for j, pixel in enumerate(row):
                np.logical_and

    def _get_letter(self, frame, coord):
        return frame[coord[0] * 8:coord[0] * 8 + 7, coord[1] * 8:coord[1] * 8 + 7, :]

    def _game_over_screen(self, frame):
        return np.array_equal(get_letter(frame, (16, 11)), self.font['G'])

    def _score(self, frame):
        pass


    def _parse_number(self, frame):
        pass

def letter_grid(image):
    v = np.zeros((240, 1, 3), np.dtype('uint8'))
    h = np.zeros((1, 256, 3), np.dtype('uint8'))

    for i in v:
        i[0][0] = 255

    for i in h[0]:
        i[0] = 255

    t = np.array(image, copy=True)
    for i in range(31):
        t[:, i * 8 + 7:i * 8 + 8, :] = v

    for i in range(29):
        t[i * 8 + 7:i * 8 + 8, :, :] = h
    return t

def get_letter(image, coord):
    return image[coord[0] * 8:coord[0] * 8 + 7, coord[1] * 8:coord[1] * 8 + 7, :]

if __name__ == "__main__":
    transition_screen = cv2.imread('/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_14/250.png', cv2.IMREAD_COLOR)
    game_over_screen = cv2.imread( '/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_42/1891.png', cv2.IMREAD_COLOR)
    example = cv2.imread('/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_14/4000.png', cv2.IMREAD_COLOR)

    ts = transition_screen
    gs = game_over_screen
    v = cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/V.png')
    w = cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/W.png')

    s = State()
    s._game_over_screen(gs)
