from nes_le import game_state_interfaces
#import curses
import inspect
import json
import socket
import sys
import time

#from matplotlib import pyplot as plt
#from termcolor import cprint
import cv2
import numpy as np

MB = 2 ** 20
port = 9090


def list_roms(console='all'):
    from nes_le.rom_locations import roms
    formatted_roms = []
    def format_rom_names(console):
        return [{
            'console': c,
            'rom': rom,
        } for rom in roms[console].keys()]

    if console == 'all':
        for c in roms.keys():
            formatted_roms.extend(format_rom_names(c))
    else:
        formatted_roms.extend(format_rom_names(console))
    return formatted_roms


def get_rom(console, game):
    from nes_le.rom_locations import roms
    return roms[console][game]


def show_image(image):
    cv2.imshow('image', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        sys.exit(0)
    #cv2.destroyAllWindows()


def encode_input(player=0, up=False, down=False, left=False, right=False, select=False,
                 start=False, a=False, b=False, turbo_a=False, turbo_b=False, altspeed=False,
                 insertcoin1=False, insertcoin2=False, fdsflip=False, fdsswitch=False,
                 qsave1=False, qsave2=False, qload1=False, qload2=False, screenshot=False,
                 reset=False, rwstart=False, rwstop=False, fullscreen=False, video_filter=False,
                 scalefactor=False, quit=False):
    buttons = ['up', 'down', 'left', 'right', 'select', 'start', 'a', 'b', 'turbo_a', 'turbo_b',
               'altspeed', 'insertcoin1', 'insertcoin2', 'fdsflip', 'fdsswitch', 'qsave1',
               'qsave2', 'qload1', 'qload2', 'screenshot', 'reset', 'rwstart', 'rwstop',
               'fullscreen', 'video_filter', 'scalefactor', 'quit']

    frame = inspect.currentframe()
    args, _, _, values = inspect.getargvalues(frame)

    pressed_buttons = []
    for arg in args:
        if values[arg] is True and arg in buttons:
            pressed_buttons.append(arg)
    return json.dumps({
        'controls': pressed_buttons,
        'player': player,
    }).encode()


def action_to_encoded_input(action):
    mapping = {
        0: {},
        1: {"a": True},
        2: {"b": True},
        3: {"up": True},
        4: {"right": True},
        5: {"left": True},
        6: {"down": True},
        7:  {"up": True, "right": True},
        8:  {"up": True, "left": True},
        9:  {"down": True, "right": True},
        10: {"down": True, "left": True},
        11: {"up": True, "a": True},
        12: {"right": True, "a": True},
        13: {"left": True, "a": True},
        14: {"down": True, "a": True},
        15: {"up": True, "right": True, "a": True},
        16: {"up": True, "left": True, "a": True},
        17: {"down": True, "right": True, "a": True},
        18: {"down": True, "left": True, "a": True},
        19: {"up": True, "b": True},
        20: {"right": True, "b": True},
        21: {"left": True, "b": True},
        22: {"down": True, "b": True},
        23: {"up": True, "right": True, "b": True},
        24: {"up": True, "left": True, "b": True},
        25: {"down": True, "right": True, "b": True},
        26: {"down": True, "left": True, "b": True},
        27: {"right": True, "a": True, "b": True},
        28: {"left": True, "a": True, "b": True},
        29: {"down": True, "a": True, "b": True},
        30: {"up": True, "right": True, "a": True, "b": True},
        31: {"up": True, "left": True, "a": True, "b": True},
        32: {"down": True, "right": True, "a": True, "b": True},
        33: {"down": True, "left": True, "a": True, "b": True},
    }
    return encode_input(**mapping[action])


class NESLEInterface:
    def __init__(self, game):
        self.state = getattr(game_state_interfaces, game).State()
        rom_file = get_rom('nes', game)
        self.sock = socket.socket()         # Create a socket object
        self.host = socket.gethostname()  # Get local machine name
        self.sock.connect((self.host, port))
        response = self.loadROM(rom_file)
        width = int(response['width'])
        height = int(response['height'])
        scale = int(response['scale'])
        self.scale = scale
        self.width = width * scale
        self.height = height * scale
        self.depth = 4
        self.frame = np.empty((self.height, self.width, self.depth), dtype=np.uint8)
        self.non_black_frame_received = False
        self.frame_size = self.height * self.width * self.depth
        self.minimal_action_set = np.array(range(34), dtype='int32')
        self.legal_action_set = self.minimal_action_set

    def loadROM(self, rom_file):
        self.sock.send(json.dumps({
            'rom_file': rom_file
        }).encode())
        return json.loads(self.sock.recv(MB).decode())

    def act(self, action):
        if type(action) is str or type(action) is bytes:
            self.sock.send(action)
        elif type(action) is dict:
            self.sock.send(encode_input(**action))
        elif type(action) is int or issubclass(type(action), np.int_):
            self.sock.send(action_to_encoded_input(action))
        else:
            raise TypeError('Action must be a string, a dict, a python int, or a numpy.int_. '
                            'This includes subclasses of numpy.int_'
                            'The class\'s type was {}'.format(type(action)))

        self.sock.recv_into(self.frame, self.frame_size, socket.MSG_WAITALL)
        self.state.new_frame(self.frame)
        return self.frame

    def game_over(self):
        return self.state.game_over()

    def reset_game(self):
        pass

    def getLegalActionSet(self):
        return self.legal_action_set

    def getMinimalActionSet(self):
        return self.minimal_action_set

    def getFrameNumber(self):
        self.state.frame_number()

    def lives(self):
        return self.state.lives()

    def getScreen(self, screen_data=None):
        return self.frame

    def getScreenRGB(self, screen_data=None):
        return self.frame

    def getScreenGrayscale(self, screen_data=None):
        return cv2.cvtColor(self.frame , cv2.COLOR_BGR2GRAY)

    def saveScreenPNG(self, filename):
        cv2.imwrite(filename, self.frame)

def main():
    start_time = time.time()
    client = NESLEInterface('super_mario_bros')
    frame_count = 0
    control_sequence = []
    control_sequence.append(
        (175, 1, {
            'start': True,
        })
    )
    control_sequence.append(
        (225, 1, {
            'start': True,
        })
    )
    control_sequence.append(
        (400, 1, {
            'a': True,
        })
    )
    countdown = 0
    current_control_sequence = None
    while True:
        if current_control_sequence is None:
            current_control_sequence = control_sequence.pop(0)
        if current_control_sequence[0] == frame_count:
            countdown = current_control_sequence[1]
        if countdown > 0:
            countdown -= 1
            frame = client.act(encode_input(**current_control_sequence[2]))
        else:
            if frame_count > current_control_sequence[0]:
                try:
                    current_control_sequence = control_sequence.pop(0)
                except(IndexError):
                    pass
            frame = client.act(encode_input())
        #show_image(frame)
        frame_count += 1
        print('f/s: {}, s: {}, t: {}'.format(frame_count / (time.time() - start_time), client.state.state['score'], client.state.state['time'],))

if __name__ == '__main__':
    main()

