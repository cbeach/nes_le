import game_state_interfaces
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
    from game_locations import roms
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
    from game_locations import roms
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
    })


class NESLEInterface:
    def __init__(self, game):
        self.state = getattr(games, game)
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

    def loadROM(self, rom_file):
        self.sock.send(json.dumps({
            'rom_file': rom_file
        }))
        return json.loads(self.sock.recv(MB))

    def act(self, action):
        if type(action) is str:
            self.sock.send(action)
        elif type(action) is dict:
            self.sock.send(encode_input(**action))
        else:
            raise TypeError('Action but be either a string or dict')

        self.sock.recv_into(self.frame, self.frame_size, socket.MSG_WAITALL)
        return self.frame

    def _num_lives(self):
        pass

    def _game_over(self):
        pass

    def game_over(self):
        pass

    def reset_game(self):
        pass

    def getLegalActionSet(self):
        pass

    def getMinimalActionSet(self):
        pass

    def getFrameNumber(self):
        pass

    def lives(self):
        pass

    def getScreen(self, screen_data=None):
        return self.frame

    def getScreenRGB(self, screen_data=None):
        return self.frame

    def getScreenGrayscale(self, screen_data=None):
        return cv2.cvtColor(self.frame , cv2.COLOR_BGR2GRAY)

    def saveScreenPNG(self, filename):
        pass

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
        show_image(frame)
        frame_count += 1
        print('frames/sec: {}'.format(frame_count / (time.time() - start_time)))

if __name__ == '__main__':
    main()

