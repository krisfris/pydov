import os
import sys
import appdirs


datadir = appdirs.user_data_dir('dov')
configdir = appdirs.user_config_dir('dov')

for x in [datadir, configdir]:
    os.makedirs(x, exist_ok=True)

excluded_process_names = []
excluded_window_names = []

threshold_radius = 0.9
dialing_threshold = 0.2
framerate = 30

keymap_file = 'data/keymap.json'

sys.path.append(configdir)
try:
    from localconfig import *
except ModuleNotFoundError:
    pass
