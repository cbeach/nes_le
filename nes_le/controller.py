import asyncio
import pprint
import sys
import threading

from sys import exit

import common_pb2
import deep_thought_pb2
import evdev
import nes_pb2

from common_pb2 import DPad
from nes_pb2 import NESControllerState


class NESController:
    key_map = {
        'BTN_THUMB': 'a',
        'BTN_THUMB2': 'b',
        'BTN_BASE3': 'select',
        'BTN_BASE4': 'start',
    }
    abs_map = [
        {
            'name': 'x',
            0: 'left',
            127: '',
            255: 'right',
        }, {
            'name': 'y',
            0: 'up',
            127: '',
            255: 'down',
        },
    ]

    def __init__(self):
        self.controller_state = NESControllerState(
            dpad=DPad(
                up=False,
                down=False,
                left=False,
                right=False,
            ),
            select=False,
            start=False,
            a=False,
            b=False,
        )

    def state(self):
        return self.controller_state

    def event(self, event):
        categorized_event = evdev.categorize(event)
        #print(categorized_event)
        if isinstance(categorized_event, evdev.events.KeyEvent):
            self._key_event(categorized_event)
        elif isinstance(categorized_event, evdev.events.AbsEvent):
            self._abs_event(categorized_event)
        elif isinstance(categorized_event, evdev.events.RelEvent):
            self._rel_event(categorized_event)
        elif isinstance(categorized_event, evdev.events.InputEvent):
            self._input_event(categorized_event)
        elif isinstance(categorized_event, evdev.events.SynEvent):
            pass
        #print(self.controller_state)

    def _key_event(self, event):
        if isinstance(event.keycode, list):
            button_name = self.key_map.get(tuple(event.keycode), '?')
        else:
            button_name = self.key_map.get(event.keycode, '?')

        if hasattr(self.controller_state, button_name):
            setattr(self.controller_state, button_name, event.event.value > 0)

    def _abs_event(self, event):
        axis = self.abs_map[event.event.code]['name']
        if axis == 'y':  # up/down
            if (event.event.value == 0):
                self.controller_state.dpad.up = True
                self.controller_state.dpad.down = False
            elif (event.event.value == 127):
                self.controller_state.dpad.up = False
                self.controller_state.dpad.down = False
            elif (event.event.value == 255):
                self.controller_state.dpad.up = False
                self.controller_state.dpad.down = True

        elif axis == 'x':  # left/right
            if (event.event.value == 0):
                self.controller_state.dpad.left = True
                self.controller_state.dpad.right = False
            elif (event.event.value == 127):
                self.controller_state.dpad.left = False
                self.controller_state.dpad.right = False
            elif (event.event.value == 255):
                self.controller_state.dpad.left = False
                self.controller_state.dpad.right = True

    def _rel_event(self, event):
        pass

    def _input_event(self, event):
        pass

    def __str__(self):
        return ('controller:\n'
                '  a:       {}\n'
                '  b:       {}\n'
                '  dpad:\n'
                '    up:    {}\n'
                '    down:  {}\n'
                '    left:  {}\n'
                '    right: {}\n').format(self.controller_state.a,
                                        self.controller_state.b,
                                        self.controller_state.dpad.up,
                                        self.controller_state.dpad.down,
                                        self.controller_state.dpad.left,
                                        self.controller_state.dpad.right)


class SNESController:
    key_map = {
        ('BTN_JOYSTICK', 'BTN_TRIGGER'): 'X',
        'BTN_THUMB': 'A',
        'BTN_THUMB2': 'B',
        'BTN_TOP':   'Y',
        'BTN_TOP2':  'L',
        'BTN_BASE':  'R',
        'BTN_BASE3': 'select',
        'BTN_BASE4': 'start',
    }
    abs_map = {
        'ABS_X': {
            0: 'left',
            255: 'right',
        }, #left/right
        'ABS_Y': {
            0: 'up',
            255: 'down',
        } #up/down
    }
    def __init__(self):
        self.controller_state = SNESControllerState(
            dpad=DPad(
                up=False,
                down=False,
                left=False,
                right=False,
            ),
            select=False,
            start=False,
            a=False,
            b=False,
            x=False,
            y=False,
            l=False,
            r=False,
        )


@asyncio.coroutine
def event_processor(device, event_handler):
    while True:
        events = yield from device.async_read()
        for event in events:
            event_handler.event(event)

def select_device():
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    if len(devices) > 1:
        while True:
            for i, device in enumerate(devices):
                print('{}: {}, {}, {}'.format(i, device.fn, device.name, device.phys))
            raw_choice = input('select controller> ')
            try:
                int_choice = int(raw_choice)
                fn = devices[int_choice].fn
                break
            except ValueError:
                print('Please enter a valid choice.')
                print('Must be an integer in the range listed above')
    elif len(devices) == 1:
        fn = devices[0].fn
    else:
        raise Exception("no joysticks are present")

    controller = evdev.InputDevice(fn)
    print('using conroller ({})'.format(controller))
    return controller


class ControllerEventLoop(threading.Thread):
    def __init__(self, device, event_handler):
        super(ControllerEventLoop, self).__init__()
        self.device = device
        self.event_handler = event_handler

    def run(self):
        for event in self.device.read_loop():
            self.event_handler.event(event)

def async_events(device, event_handler):
    asyncio.async(event_processor(device, event_handler))
    loop = asyncio.get_event_loop()
    loop.run_forever()


if __name__ == '__main__':
    print("main")
    device = select_device()
    nes_con = NESController()
    #async_events(device, nes_con)
    cel = ControllerEventLoop(device, nes_con)
    cel.start()
