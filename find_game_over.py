from collections import Counter
from glob import glob
import json
import os
from os.path import join, basename
import random
import sys
import time

from matplotlib import pyplot as plt
from termcolor import cprint
import cv2
import numpy as np

def show_image(image):
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def get_sprites(sprite_dir):
    sprites = []
    for root, dirs, files in os.walk(sprite_dir):
        for fn in files:
            sprite_name = fn.split('.')[0]
            image = cv2.imread(os.path.join(root, fn), cv2.IMREAD_GRAYSCALE)[::2, ::2]
            w, h = image.shape
            if sprite_name == 'A':
                image1 = cv2.imread(os.path.join(root, fn), cv2.IMREAD_GRAYSCALE)#[::2, ::2]
                print(sprite_name, w, h)
                print(sprite_name, image1.shape[0], image1.shape[1])
                print(image)
                print(image1)
            temp = {
                'name': sprite_name,
                'path': fn,
                'image': image,
                'orientation': {
                    'v_flip': False,
                    'h_flip': False,
                },
                'width': w,
                'height': h,
            }
            sprites.append(temp)
    return sprites

def main():
    templates = get_sprites('/home/mcsmash/dev/data/game_playing/sprites/')
    templates = filter(lambda s: s['name'] == 'G' and s['orientation']['h_flip'] == False and s['orientation']['v_flip'] == False, templates)

    data_dirs = [
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_6',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_7',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_8',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_9',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_10',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_11',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_12',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_13',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_14',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_15',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_16',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_17',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_18',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_19',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_20',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_21',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_22',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_23',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_24',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_25',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_26',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_27',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_28',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_29',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_30',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_31',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_32',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_33',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_34',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_35',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_36',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_37',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_38',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_39',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_40',
        #'/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_41',
        '/home/mcsmash/dev/data/game_playing/frames/game_1/play_number_42',
    ]
    accume = 0
    start = time.time()
    found = 0
    num = 10
    total_frames = 0
    hits = 0
    Gs = []
    for data_dir in data_dirs:
        files = glob('{}/*'.format(data_dir))
        files = [f for f in files if f.endswith('.png')]

        for i, fn in enumerate(files):
            name = os.path.basename(fn).split('.')[0]
            #cprint(name, 'yellow')
            color_frame = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
            gray_frame = cv2.cvtColor(color_frame, cv2.COLOR_BGR2GRAY)
            analyzed = []

            frame = gray_frame.copy()
            frame2 = gray_frame.copy()

            for template in templates:
                res = cv2.matchTemplate(frame, template['image'], cv2.TM_CCOEFF_NORMED)
                threshold = 0.99
                loc = np.where(res >= threshold)
                if len(loc[0]) > 0:
                    hits += 1
                    Gs.append(fn)
                    print(fn)
                #print('{}%: {}'.format(total_frames / 56000.0 * 100, hits))
                total_frames += 1
                #threshold = 0.99
                #loc = np.where(res >= threshold)
                #w, h = template['image'].shape
                #for pt in zip(*loc[::-1]):
                #        analyzed.append(encode_data({
                #            'image': fn,
                #            'width': color_frame.shape[0],
                #            'height': color_frame.shape[1],
                #        }, template, pt))
                    #cv2.rectangle(color_frame, pt, (pt[0] + h, pt[1] + w), (0, 0, 255), 1)
                #cv2.imwrite(join('/home/mcsmash/dev/data/game_playing/analysis/', basename(fn)),
                #    color_frame)
            accume += 1
            #cprint('Finished processing: {} of {}'.format(i, total_frames), 'green')
            #cprint('{}% done'.format(float(i) / float(total_frames) * 100), 'green')
    cprint('time: {}'.format(time.time() - start), 'green')
    cprint('rate: {}'.format((time.time() - start) / num), 'green')
    print(Gs)


if __name__ == '__main__':
    main()
