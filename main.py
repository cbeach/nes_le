from nes_le.interface import NESLEInterface, show_image

n = NESLEInterface('super_mario_bros')
while True:
    frame = n.act(0)
    show_image(frame)
