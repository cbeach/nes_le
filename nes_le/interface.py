from nes_le import game_state_interfaces
#import curses
import inspect
import json
import math
import socket
import sys
import time

import cv2
import grpc
import numpy as np

import common_pb2_grpc
import common_pb2
import controller
import deep_thought_pb2_grpc
import deep_thought_pb2
import nes_pb2_grpc
import nes_pb2

from common_pb2 import DPad

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
    actions = {
        0 :  ("NOOP",        nes_pb2.NESControllerState()),
        1 :  ("UP",          nes_pb2.NESControllerState(dpad=DPad(up=True))),
        2 :  ("RIGHT",       nes_pb2.NESControllerState(dpad=DPad(right=True))),
        3 :  ("LEFT",        nes_pb2.NESControllerState(dpad=DPad(left=True))),
        4 :  ("DOWN",        nes_pb2.NESControllerState(dpad=DPad(down=True))),
        5 :  ("UPRIGHT",     nes_pb2.NESControllerState(dpad=DPad(up=True, right=True))),
        6 :  ("UPLEFT",      nes_pb2.NESControllerState(dpad=DPad(up=True, left=True))),
        7 :  ("DOWNRIGHT",   nes_pb2.NESControllerState(dpad=DPad(down=True, right=True))),
        8 :  ("DOWNLEFT",    nes_pb2.NESControllerState(dpad=DPad(down=True, left=True))),
        9 :  ("A",           nes_pb2.NESControllerState(a=True)),
        10 : ("B",           nes_pb2.NESControllerState(b=True)),
        11 : ("UPA",         nes_pb2.NESControllerState(a=True, dpad=DPad(up=True))),
        12 : ("RIGHTA",      nes_pb2.NESControllerState(a=True, dpad=DPad(right=True))),
        13 : ("LEFTA",       nes_pb2.NESControllerState(a=True, dpad=DPad(left=True))),
        14 : ("DOWNA",       nes_pb2.NESControllerState(a=True, dpad=DPad(down=True))),
        15 : ("UPRIGHTA",    nes_pb2.NESControllerState(a=True, dpad=DPad(up=True, right=True))),
        16 : ("UPLEFTA",     nes_pb2.NESControllerState(a=True, dpad=DPad(up=True, left=True))),
        17 : ("DOWNRIGHTA",  nes_pb2.NESControllerState(a=True, dpad=DPad(down=True, right=True))),
        18 : ("DOWNLEFTA",   nes_pb2.NESControllerState(a=True, dpad=DPad(down=True, left=True))),
        19 : ("UPB",         nes_pb2.NESControllerState(b=True, dpad=DPad(up=True))),
        20 : ("RIGHTB",      nes_pb2.NESControllerState(b=True, dpad=DPad(right=True))),
        21 : ("LEFTB",       nes_pb2.NESControllerState(b=True, dpad=DPad(left=True))),
        22 : ("DOWNB",       nes_pb2.NESControllerState(b=True, dpad=DPad(down=True))),
        23 : ("UPRIGHTB",    nes_pb2.NESControllerState(b=True, dpad=DPad(up=True, right=True))),
        24 : ("UPLEFTB",     nes_pb2.NESControllerState(b=True, dpad=DPad(up=True, left=True))),
        25 : ("DOWNRIGHTB",  nes_pb2.NESControllerState(b=True, dpad=DPad(down=True, right=True))),
        26 : ("DOWNLEFTB",   nes_pb2.NESControllerState(b=True, dpad=DPad(down=True, left=True))),
        27 : ("UPAB",        nes_pb2.NESControllerState(a=True, b=True, dpad=DPad(up=True))),
        28 : ("RIGHTAB",     nes_pb2.NESControllerState(a=True, b=True, dpad=DPad(right=True))),
        29 : ("LEFTAB",      nes_pb2.NESControllerState(a=True, b=True, dpad=DPad(left=True))),
        31 : ("DOWNAB",      nes_pb2.NESControllerState(a=True, b=True, dpad=DPad(down=True))),
        32 : ("UPRIGHTAB",   nes_pb2.NESControllerState(a=True, b=True, dpad=DPad(up=True, right=True))),
        33 : ("UPLEFTAB",    nes_pb2.NESControllerState(a=True, b=True, dpad=DPad(up=True, left=True))),
        34 : ("DOWNRIGHTAB", nes_pb2.NESControllerState(a=True, b=True, dpad=DPad(down=True, right=True))),
        35 : ("DOWNLEFTAB",  nes_pb2.NESControllerState(a=True, b=True, dpad=DPad(down=True, left=True))),
    }

    def __init__(self, game, event_handler=None):
        self.event_handler = controller.NESController()
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = deep_thought_pb2_grpc.EmulatorStub(self.channel)
        self.device = controller.select_device()

        self.cel = controller.ControllerEventLoop(self.device, self.event_handler)
        self.cel.start()


        self.state = getattr(game_state_interfaces, game).State()
        rom_file = get_rom('nes', game)

        self.scale = 1
        self.width = 256
        self.height = 240
        self.depth = 4
        self.frame = np.empty((self.height, self.width, self.depth), dtype=np.uint8)
        self.non_black_frame_received = False
        self.frame_size = self.height * self.width * self.depth
        self.minimal_action_set = np.array(range(34), dtype='int32')
        self.legal_action_set = self.minimal_action_set
        self.player_action = self.actions[0]
        self.controller_ready = False

        self.stream = self.stub.play_game(self._get_input_state(frame_rate=60))

    def _get_input_state(self, frame_rate=math.inf):
        while True:
            #import pdb; pdb.set_trace()
            time.sleep(1 / frame_rate)
            while not self.controller_ready:

                time.sleep(.000001)
            ms = deep_thought_pb2.MachineState(
                nes_console_state=nes_pb2.NESConsoleState(
                    player1_input=self.player_action,
                    game=common_pb2.Game(
                        name="Super Mario Brothers",
                        #path="/home/mcsmash/dev/emulators/LaiNES/smb.nes"
                        path="/home/app/smb.nes"
                    )
                )
            )
            self.controller_ready = False
            yield ms

    def act(self, action):
        """
            Args:
                action:
                    type: int
                    value: a key from the self.actions dict
        """
        if type(action) is int or issubclass(type(action), np.int_):
            self.player_action = self.actions[action][1]
        else:
            raise TypeError('Action must be a key from the self.actions dict'
                            'This includes subclasses of numpy.int_'
                            'The class\'s type was {}'.format(type(action)))

        if self.controller_ready:
            # There is already a frame processing. Wait for it to finish before
            # messing with the controller
            while self.controller_ready:
                time.sleep(.0001)

        self.controller_ready = True
        response = self.stream.next()

        return np.reshape(np.frombuffer(response.raw_frame.data, dtype='uint8'), (240, 256, 4))

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
    def getScreenDims(self):
        return (256, 240)

    def getScreenRGB(self, screen_data=None):
        return self.frame

    def getScreenGrayscale(self, screen_data=None):
        return cv2.cvtColor(self.frame , cv2.COLOR_BGR2GRAY)

    def saveScreenPNG(self, filename):
        cv2.imwrite(filename, self.frame)

def old_main():
    nes_con = controller.NESController()
    start_time = time.time()
    client = NESLEInterface('super_mario_bros', event_handler=nes_con)
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
        print('f/s: {}, s: {}, t: {}'.format(frame_count / (time.time() - start_time), client.state.state['score'], client.state.state['time'],))


if __name__ == '__main__':
    n = NESLEInterface('super_mario_bros')
    while True:
        frame = n.act(0)
        show_image(frame)

