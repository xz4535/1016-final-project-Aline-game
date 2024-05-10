import argparse
import sys
import time
from Testforun import Player_test
import pdb
import numpy as np
import inspect
model_para_name= 'model.pth'

parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
parser.add_argument('-trial_num', default = 1, required = False)
parser.add_argument('-batch_size', default = 32, required = False)
parser.add_argument('-lr', default = .00025, type = float, required = False)
parser.add_argument('-gamma', default = .999, required = False)
parser.add_argument('-eps_start', default = 1, required = False)
parser.add_argument('-eps_end', default = .1, required = False)
parser.add_argument('-eps_decay', default = 200., required = False)
parser.add_argument('-target_update', default = 100, required = False)
parser.add_argument('-img_size', default = 64, required = False)
parser.add_argument('-num_episodes', default = 20000, type = int, required = False)
parser.add_argument('-max_steps', default = 2000, type = int, required = False)
parser.add_argument('-max_mem', default = 50000, required = False)
parser.add_argument('-model_name', default = 'DQN', required = False)
parser.add_argument('-model_weight_path',default=model_para_name, required = False)
parser.add_argument('-test_mode', default = 0, type = int, required = False)
parser.add_argument('-pretrain', default = 1, type = int, required = False)
parser.add_argument('-cuda', default = 1, required = False)
parser.add_argument('-doubleq', default = 1, type = int, required = False)
parser.add_argument('-level_switch', default = 'sequential', type = str, required = False)
parser.add_argument('-timeout', default = 2000, type = int, required = False)
parser.add_argument('-criteria', default = '1/1', type = str, required = False)
parser.add_argument('-game_name', default = 'aliens', required = False)
parser.add_argument('-num_trials', default = 1, type = int, required = False)
parser.add_argument('-random_seed', default = 7, type = int, required = False)

config = parser.parse_args();

print(config)

config.file_names = 'all_games/'

print("Game: {}".format(config.game_name))
game_player = Player_test(config)
game_player.run_model()