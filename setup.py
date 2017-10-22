#!/usr/bin/env python

from distutils.core import setup

setup(name='nes_le',
      version='0.0.1',
      description='Nintendo Entertainment System Learning Environment',
      author='Casey Beach',
      author_email='beachc@gmail.com',
      install_requires=[
          "numpy==1.13.3",
          "opencv-python==3.3.010",
      ],
      url='https://github.com/cbeach/nes_le',
      packages=['nes_le', 'nes_le.game_state_interfaces'],
      download_url='https://codeload.github.com/cbeach/nes_le/tar.gz/0.0.1',
      )
