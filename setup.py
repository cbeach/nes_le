#!/usr/bin/env python

from distutils.core import setup

setup(name='nes_le',
      version='0.0.1',
      description='Nintendo Entertainment System Learning Environment',
      author='Casey Beach',
      author_email='beachc@gmail.com',
      url='https://github.com/cbeach/NES-LE',
      packages=['nes_le', 'nes_le.game_state_interfaces'],
      )
