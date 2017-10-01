import os

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
        ' ': np.zeros((8, 8, 3)),
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
            ' ': np.zeros((7, 7, 3)),
        }

        self.bool_font = self._generate_bool_font(self.font)

    def new_frame(self, frame):
        if self.state['game_over'] is True:
            return self.state

        text = self._get_text(frame)
        toks = self._lex(text)
        pars = self._parse(toks, frame)

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
                gsr.append(s._get_letter(frame, (x, y)))
        return np.array(gsr, dtype=gs.dtype)

    def _get_text(self, frame):
        gsr = self._raw_text(frame)

        bool_chars = []
        for x, sprite in enumerate(gsr):
            bool_chars.append(self._bool_char(sprite))
        np_bool_chars = np.array(bool_chars, dtype='uint8')

        return [self._recognize_letter(i) for i in np_bool_chars]

    def _bool_char(self, sprite):
        bool_char = np.ones(sprite.shape[:-1], dtype=bool)
        for x, row in enumerate(sprite):
            for y, pixel in enumerate(row):
                bool_char[x][y] = np.array_equal(sprite[x][y], np.array([255, 255, 255], dtype=sprite.dtype))
        return np.array(bool_char, dtype=bool)

    def _get_letter(self, frame, coord):
        return frame[coord[0] * 8:coord[0] * 8 + 8, coord[1] * 8:coord[1] * 8 + 8, :]

    def _get_bool_letter(self, frame, coord):
        return self._bool_char(self._get_letter(frame, coord))

    def _recognize_letter(self, sprite):
        for character, bf in self.bool_font.items():
            if np.array_equal(sprite[:-1, :-1], bf):
                return character
        return ' '

    def _game_over_screen(self, frame):
        return self._recognize_letter(self._get_bool_letter(frame, (16, 11))) == 'G'

    def _transition_screen(self, frame):
        return self._recognize_letter(self._get_bool_letter(frame, (14, 15))) == 'x'

    def _score(self, frame):
        pass

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

    def _parse(self, tokens, frame):
        parsed = {
            'player': tokens[0],
            'score': int(tokens[3]),
            'coins': int(tokens[4][1:]),
            'world': int(tokens[5].split('-')[0]),
            'stage': int(tokens[5].split('-')[1]),
        }
        if self._transition_screen(frame) is True:
            #  ts: ['MARIO', 'WORLD', 'TIME', '000000', 'x00', '1-1', 'WORLD 1-1', 'x', '3']
            parsed['lives'] = int(tokens[8])
        elif self._game_over_screen(frame) is False:
            #  es: ['MARIO', 'WORLD', 'TIME', '000100', 'x00', '1-1', '354']
            parsed['time'] = int(tokens[6])
        return parsed


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

    es = example_screen
    ts = transition_screen
    gs = game_over_screen

    s = State()
