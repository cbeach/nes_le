import math
import os
import sys

import cv2
import numpy as np

def print_grid_text(frame):
    data = s._get_text(frame)
    for i, r in enumerate([data[x:x+32] for x in xrange(0, len(data), 32)]):
        print(i, r)


def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    return err / float(imageA.shape[0] * imageA.shape[1])


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


def pretty_print_char(image):
    print(np.reshape(image[:, :, :1], image.shape[:2]))


def mutate_font(func):
    font = {
        '0': '/home/mcsmash/dev/data/game_playing/sprites/game_1/Zero.png',
        '1': '/home/mcsmash/dev/data/game_playing/sprites/game_1/1.png',
        '2': '/home/mcsmash/dev/data/game_playing/sprites/game_1/2.png',
        '3': '/home/mcsmash/dev/data/game_playing/sprites/game_1/3.png',
        '4': '/home/mcsmash/dev/data/game_playing/sprites/game_1/4.png',
        '5': '/home/mcsmash/dev/data/game_playing/sprites/game_1/5.png',
        '6': '/home/mcsmash/dev/data/game_playing/sprites/game_1/6.png',
        '7': '/home/mcsmash/dev/data/game_playing/sprites/game_1/7.png',
        '8': '/home/mcsmash/dev/data/game_playing/sprites/game_1/8.png',
        '9': '/home/mcsmash/dev/data/game_playing/sprites/game_1/9.png',
        'A': '/home/mcsmash/dev/data/game_playing/sprites/game_1/A.png',
        'D': '/home/mcsmash/dev/data/game_playing/sprites/game_1/D.png',
        'E': '/home/mcsmash/dev/data/game_playing/sprites/game_1/E.png',
        'G': '/home/mcsmash/dev/data/game_playing/sprites/game_1/G.png',
        'I': '/home/mcsmash/dev/data/game_playing/sprites/game_1/I.png',
        'L': '/home/mcsmash/dev/data/game_playing/sprites/game_1/L.png',
        'M': '/home/mcsmash/dev/data/game_playing/sprites/game_1/M.png',
        'O': '/home/mcsmash/dev/data/game_playing/sprites/game_1/O.png',
        'R': '/home/mcsmash/dev/data/game_playing/sprites/game_1/R.png',
        'T': '/home/mcsmash/dev/data/game_playing/sprites/game_1/T.png',
        'V': '/home/mcsmash/dev/data/game_playing/sprites/game_1/V.png',
        'W': '/home/mcsmash/dev/data/game_playing/sprites/game_1/W.png',
        'x': '/home/mcsmash/dev/data/game_playing/sprites/game_1/x.png',
        '-': '/home/mcsmash/dev/data/game_playing/sprites/game_1/-.png',
    }
    for key, value in font.items():
        func(key, value)


class State:
    def __init__(self):
        self.state = {
            'player': 'MARIO',
            'lives': 3,
            'money': 0,
            'world': 1,
            'stage': 1,
            'time': 0,
            'game_over': False,
        }
        self.font = {
            '0': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/Zero.png'),
            '1': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/1.png'),
            '2': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/2.png'),
            '3': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/3.png'),
            '4': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/4.png'),
            '5': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/5.png'),
            '6': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/6.png'),
            '7': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/7.png'),
            '8': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/8.png'),
            '9': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/9.png'),
            'A': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/A.png'),
            'D': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/D.png'),
            'E': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/E.png'),
            'G': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/G.png'),
            'I': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/I.png'),
            'L': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/L.png'),
            'M': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/M.png'),
            'O': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/O.png'),
            'R': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/R.png'),
            'T': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/T.png'),
            'V': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/V.png'),
            'W': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/W.png'),
            'x': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/x.png'),
            '-': cv2.imread('/home/mcsmash/dev/data/game_playing/sprites/game_1/-.png'),
            ' ': np.zeros((8, 8, 3), dtype='uint8'),
        }
        self.thresh_font = {}
        for k, v in self.font.items():
            gray = cv2.cvtColor(v, cv2.COLOR_BGR2GRAY)
            self.thresh_font[k] = cv2.threshold(gray, 254, 255, cv2.THRESH_BINARY)[1]

        self.nega_thresh_font = {}
        for k, v in self.font.items():
            gray = cv2.cvtColor(v, cv2.COLOR_BGR2GRAY)
            self.nega_thresh_font[k] = cv2.threshold(gray, 254, 255, cv2.THRESH_BINARY_INV)[1]

        self.bool_font = self._generate_bool_font(self.font)
        self._frame_number = 0

    def new_frame(self, frame):
        if self.state['game_over'] is True:
            return self.state
        self._frame_number += 1

        #text = self._get_text(frame)
        #toks = self._lex(text)
        pars = self._parse(frame)

        self.state['game_over'] = self._game_over_screen(frame)
        self.state.update(pars)
        return self.state

    def _generate_bool_font(self, font):
        bool_font = {}
        for key, value in self.font.items():
            bool_font[key] = np.ones(value.shape[:-1], dtype=bool)

            for x, row in enumerate(bool_font[key]):
                for y, pixel in enumerate(row):
                    bool_font[key][x][y] = np.array_equal(value[x][y], np.array([255, 255, 255], dtype=value.dtype))
        return bool_font

    def _raw_text(self, frame):
        gsr = []
        for x in range(30):
            for y in range(32):
                gsr.append(self._get_letter(frame, (x, y)))
        return np.array(gsr, dtype=frame.dtype)

    def _get_text(self, frame):
        gsr = self._raw_text(frame)

        gray_gsr = [cv2.cvtColor(c, cv2.COLOR_BGR2GRAY) for c in gsr]
        thresh_gsr = [cv2.threshold(i, 254, 255, cv2.THRESH_BINARY)[1] for i in gray_gsr]
        letters = []
        for i in thresh_gsr:
            for k, v in self.thresh_font.items():
                if np.array_equal(i, v):
                    letters.append(k)

        #bool_chars = []
        #for x, sprite in enumerate(gsr):
        #    bool_chars.append(self._bool_char(sprite))
        #np_bool_chars = np.array(bool_chars, dtype='uint8')

        return letters

    def _bool_char(self, sprite):
        bool_char = np.ones(sprite.shape[:-1], dtype=bool)
        white_pixel = np.array([255, 255, 255], dtype=sprite.dtype)
        for x, row in enumerate(sprite):
            for y, pixel in enumerate(row):
                bool_char[x][y] = np.array_equal(sprite[x][y], white_pixel)
        return np.array(bool_char, dtype=bool)

    def _get_letter(self, frame, coord):
        return frame[coord[0] * 8:coord[0] * 8 + 8, coord[1] * 8:coord[1] * 8 + 8, :]

    def _get_bool_letter(self, frame, coord):
        return self._bool_char(self._get_letter(frame, coord))

    def _get_number(self, frame, row, begin, end):
        raw_number = [self._recognize_letter(self._get_letter(frame, (row, x)))
                        for x in range(begin, end)]
        try:
            return int(''.join(raw_number))
        except ValueError:
            return None

    def _recognize_letter(self, sprite):
        gray_sprite = cv2.cvtColor(sprite, cv2.COLOR_BGR2GRAY)
        thresh_sprite = cv2.threshold(gray_sprite, 254, 255, cv2.THRESH_BINARY)[1]
        for k, v in self.thresh_font.items():
            if np.array_equal(thresh_sprite, v):
                return k
        return ' '

    def _game_over_screen(self, frame):
        return self._recognize_letter(self._get_letter(frame, (16, 11))) == 'G'

    def _transition_screen(self, frame):
        return self._recognize_letter(self._get_letter(frame, (14, 15))) == 'x'

    def _score(self, frame):
        return self._get_number(frame, 3, 3, 9)

    def _player(self, frame):
        return 'MARIO' if self._recognize_letter(self._get_letter(frame, (2, 3))) == 'M' else 'LUIGI'

    def _time_left(self, frame):
        return self._get_number(frame, 3, 26, 29)

    def _level(self, frame):
        return {
            'world': self._get_number(frame, 3, 19, 20),
            'stage': self._get_number(frame, 3, 21, 22),
        }

    def _coins(self, frame):
        return self._get_number(frame, 3, 13, 14)

    def _lives(self, frame):
        return self._get_number(frame, 14, 18, 20)

    def _lex(self, letters):
        tokens = []
        token = []
        in_token = False
        last_char = ' '
        for i, c in enumerate(letters):
            if in_token is False and c != ' ':
                in_token = True
                token.append(c)
            elif in_token is True and c == ' ' and last_char != ' ':
                token.append(c)
            elif in_token is True and c != ' ':
                token.append(c)
            elif in_token is True and c == ' ' and last_char == ' ':
                in_token = False
                tokens.append(''.join(token).strip())
                token = []
            last_char = c
        return tokens

    def _parse(self, frame):
        parsed = {
            'player': self._player(frame),
            'score': self._score(frame),
            'coins': self._coins(frame),
        }
        parsed.update(self._level(frame))
        if self._transition_screen(frame) is True:
            #  ts: ['MARIO', 'WORLD', 'TIME', '000000', 'x00', '1-1', 'WORLD 1-1', 'x', '3']
            parsed['lives'] = self._lives(frame)
        elif self._game_over_screen(frame) is False:
            #  es: ['MARIO', 'WORLD', 'TIME', '000100', 'x00', '1-1', '354']
            parsed['time'] = self._time_left(frame)
        return parsed

    def game_over(self):
        return self.state['game_over']

    def lives(self):
        return self.state['lives']

    def frame_number(self):
        return self.frame_number


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


if __name__ == "__main__":
    transition_screen = cv2.imread('/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_14/250.png', cv2.IMREAD_COLOR)
    game_over_screen = cv2.imread('/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_42/1891.png', cv2.IMREAD_COLOR)
    example_screen = cv2.imread('/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_14/4000.png', cv2.IMREAD_COLOR)
    white_pixel = np.array([255, 255, 255], dtype='uint8')

    es = example_screen
    ts = transition_screen
    gs = game_over_screen

    s = State()
    print_grid_text(ts)
    print(s._score(ts))
    print(s._coins(ts))
    print(s._level(ts))
    print(s._lives(ts))

    def decision(font):
        letters = font.keys()
        font_imgs = [font[l] for l in letters]
        catted = np.array(font_imgs) / 255
        summed = np.sum(catted, axis=0)
        pixel_dist = np.absolute(summed.astype('int16') - int(len(letters) / 2.0))
        minimum = np.argmin(pixel_dist)
        x = minimum / pixel_dist.shape[0]
        y = minimum % pixel_dist.shape[0]

        pos = {}
        neg = {}
        for k, v in font.items():
            if v[x][y] > 0:
                pos[k] = font[k]
            else:
                neg[k] = font[k]
        return {
            True: pos,
            False: neg,
            'pixel': (x, y),
        }

    def create_tree(font):
        d = decision(font)
        if len(d[True]) > 1:
            d[True] = create_tree(d[True])
        if len(d[False]) > 1:
            d[False] = create_tree(d[False])
        return d

    def recognize_letter(tree, sprite, color):
        recognize_letter(tree[np.array_equal(sprite[tree['pixel'][0]][tree['pixel'][1]], color)],
                         sprite,
                         color)

    #tree = create_tree(s.thresh_font)

