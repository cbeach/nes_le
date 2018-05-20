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

from .deep_thought_pb2 import MachineState
from .deep_thought_pb2_grpc import EmulatorStub

from .controller import NESController, select_device, ControllerEventLoop
from .nes_pb2 import NESControllerState, NESConsoleState

from .common_pb2 import DPad, Game

MB = 2 ** 20


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


class NESLEInterface:
    actions = {
        0 :  ("NOP",         NESControllerState()),
        1 :  ("UP",          NESControllerState(dpad=DPad(up=True))),
        2 :  ("RIGHT",       NESControllerState(dpad=DPad(right=True))),
        3 :  ("LEFT",        NESControllerState(dpad=DPad(left=True))),
        4 :  ("DOWN",        NESControllerState(dpad=DPad(down=True))),
        5 :  ("UPRIGHT",     NESControllerState(dpad=DPad(up=True, right=True))),
        6 :  ("UPLEFT",      NESControllerState(dpad=DPad(up=True, left=True))),
        7 :  ("DOWNRIGHT",   NESControllerState(dpad=DPad(down=True, right=True))),
        8 :  ("DOWNLEFT",    NESControllerState(dpad=DPad(down=True, left=True))),
        9 :  ("A",           NESControllerState(a=True)),
        10 : ("B",           NESControllerState(b=True)),
        11 : ("UPA",         NESControllerState(a=True, dpad=DPad(up=True))),
        12 : ("RIGHTA",      NESControllerState(a=True, dpad=DPad(right=True))),
        13 : ("LEFTA",       NESControllerState(a=True, dpad=DPad(left=True))),
        14 : ("DOWNA",       NESControllerState(a=True, dpad=DPad(down=True))),
        15 : ("UPRIGHTA",    NESControllerState(a=True, dpad=DPad(up=True, right=True))),
        16 : ("UPLEFTA",     NESControllerState(a=True, dpad=DPad(up=True, left=True))),
        17 : ("DOWNRIGHTA",  NESControllerState(a=True, dpad=DPad(down=True, right=True))),
        18 : ("DOWNLEFTA",   NESControllerState(a=True, dpad=DPad(down=True, left=True))),
        19 : ("UPB",         NESControllerState(b=True, dpad=DPad(up=True))),
        20 : ("RIGHTB",      NESControllerState(b=True, dpad=DPad(right=True))),
        21 : ("LEFTB",       NESControllerState(b=True, dpad=DPad(left=True))),
        22 : ("DOWNB",       NESControllerState(b=True, dpad=DPad(down=True))),
        23 : ("UPRIGHTB",    NESControllerState(b=True, dpad=DPad(up=True, right=True))),
        24 : ("UPLEFTB",     NESControllerState(b=True, dpad=DPad(up=True, left=True))),
        25 : ("DOWNRIGHTB",  NESControllerState(b=True, dpad=DPad(down=True, right=True))),
        26 : ("DOWNLEFTB",   NESControllerState(b=True, dpad=DPad(down=True, left=True))),
        27 : ("UPAB",        NESControllerState(a=True, b=True, dpad=DPad(up=True))),
        28 : ("RIGHTAB",     NESControllerState(a=True, b=True, dpad=DPad(right=True))),
        29 : ("LEFTAB",      NESControllerState(a=True, b=True, dpad=DPad(left=True))),
        31 : ("DOWNAB",      NESControllerState(a=True, b=True, dpad=DPad(down=True))),
        32 : ("UPRIGHTAB",   NESControllerState(a=True, b=True, dpad=DPad(up=True, right=True))),
        33 : ("UPLEFTAB",    NESControllerState(a=True, b=True, dpad=DPad(up=True, left=True))),
        34 : ("DOWNRIGHTAB", NESControllerState(a=True, b=True, dpad=DPad(down=True, right=True))),
        35 : ("DOWNLEFTAB",  NESControllerState(a=True, b=True, dpad=DPad(down=True, left=True))),
    }

    def __init__(self, game, event_handler=None):
        self.event_handler = NESController()
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = EmulatorStub(self.channel)
        self.device = select_device()

        self.cel = ControllerEventLoop(self.device, self.event_handler)
        self.cel.start()


        self.state = getattr(game_state_interfaces, game).State()
        self.rom_file = get_rom('nes', game)

        self.scale = 1
        self.width = 256
        self.height = 240
        self.depth = 4
        self.frame = np.empty((self.height, self.width, self.depth), dtype=np.uint8)
        self.non_black_frame_received = False
        self.frame_size = self.height * self.width * self.depth
        self.minimal_action_set = np.array(range(len(self.actions)), dtype='int32')
        self.legal_action_set = self.minimal_action_set
        self.player_action = self.actions[0]  # initialize to NOP
        self.controller_ready = False

        self.stream = self.stub.play_game(self._get_input_state(frame_rate=60))

    def _get_input_state(self, frame_rate=math.inf):
        while True:
            #import pdb; pdb.set_trace()
            time.sleep(1 / frame_rate)
            while not self.controller_ready:

                time.sleep(.000001)
            ms = MachineState(
                nes_console_state=NESConsoleState(
                    player1_input=self.player_action,
                    game=Game(
                        name="Super Mario Brothers",
                        #path="/home/mcsmash/dev/emulators/LaiNES/smb.nes"
                        path=self.rom_file
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

        self.frame = np.reshape(np.frombuffer(response.raw_frame.data, dtype='uint8'), (240, 256, 4))
        return self.frame

    def game_over(self):
        return self.state.game_over()

    def reset_game(self):
        """
            TODO: Close the grpc stream and start a new game.
        """
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


if __name__ == '__main__':
    n = NESLEInterface('super_mario_bros')
    while True:
        frame = n.act(0)
        show_image(frame)

