from sys import exit
import math
import multiprocessing
import sys
import time

import grpc
import cv2
import numpy as np

import common_pb2_grpc
import common_pb2
import controller
import deep_thought_pb2_grpc
import deep_thought_pb2
import nes_pb2_grpc
import nes_pb2


def generate_constant_machine_states():
    ms = deep_thought_pb2.MachineState(
        nes_console_state=nes_pb2.NESConsoleState(
            game=common_pb2.Game(
                name="Super Mario Brothers",
                path="/home/mcsmash/dev/emulators/LaiNES/smb.nes"
            )
        )
    )
    while True:
        yield ms

def get_input_state(controller, frame_rate=math.inf):
    while True:
        #import pdb; pdb.set_trace()
        time.sleep(1 / frame_rate)
        ms = deep_thought_pb2.MachineState(
            nes_console_state=nes_pb2.NESConsoleState(
                player1_input=controller.state(),
                game=common_pb2.Game(
                    name="Super Mario Brothers",
                    path="/home/mcsmash/dev/emulators/LaiNES/smb.nes"
                    #path="/home/app/smb.nes"
                )
            )
        )
        yield ms

def play_game_stream(stub, event_handler=None):
    device = controller.select_device()
    #async_events(device, nes_con)
    cel = controller.ControllerEventLoop(device, nes_con)
    cel.start()

    if event_handler is not None:
        m_state = get_input_state(event_handler, frame_rate=60)
    else:
        m_state = generate_constant_machine_states()

    responses = stub.play_game(m_state)

    counter = 0
    while True:
        response = responses.next()
        counter += 1
        img = np.reshape(np.frombuffer(response.raw_frame.data, dtype='uint8'), (240, 256, 4))
        cv2.imshow('game session', img)
        if cv2.waitKey(1) == 27:
            break


if __name__ == '__main__':
    nes_con = controller.NESController()
    channel = grpc.insecure_channel('localhost:50051')
    stub = deep_thought_pb2_grpc.EmulatorStub(channel)
    play_game_stream(stub, event_handler=nes_con)
