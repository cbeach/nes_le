import os

base_path = '/home/app/'

#nes_base_path = os.path.join(base_path, 'nes')
nes_base_path = base_path
atari_2600_base_path = os.path.join(base_path, 'atari_2600')
ps2_base_path = os.path.join(base_path, 'ps2')

roms = {
    'nes': {
        'super_mario_bros': os.path.join(nes_base_path, 'smb.nes'),
    },
    'atari_2600': {
        'alien':            os.path.join(nes_base_path, 'alien.bin'),
        'amidar':           os.path.join(nes_base_path, 'amidar.bin'),
        'archives':         os.path.join(nes_base_path, 'archives'),
        'assault':          os.path.join(nes_base_path, 'assault.bin'),
        'asterix':          os.path.join(nes_base_path, 'asterix.bin'),
        'asteroids':        os.path.join(nes_base_path, 'asteroids.bin'),
        'breakout':         os.path.join(nes_base_path, 'breakout.bin'),
    },
    'ps2': {
        'kingdom_hearts':   os.path.join(ps2_base_path, 'kingdom_hearts.iso'),
    }
}
