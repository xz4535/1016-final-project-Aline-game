import player
# import gym
# import gym_gvgai
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T
import rl_models
import random
from collections import namedtuple, defaultdict
import numpy as np
from PIL import Image
import pdb
from scipy import misc
import imageio
import sys
from VGDLEnv import VGDLEnv
import csv
import cloudpickle
import matplotlib as plt

import os
from pygame.locals import K_RIGHT, K_LEFT, K_UP, K_DOWN, K_SPACE
import time

# colors from VGDL?


class Player_test(object):
    def __init__(self, config):
        self.config = config
        self.Env = VGDLEnv(self.config.game_name, 'all_games')
        self.Env.set_level(0)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print('device = {}, Training at seed = {}'.format(self.device,self.config.trial_num))

        self.game_size = np.shape(self.Env.render())
        self.input_channels = self.game_size[2]
        self.n_actions = len(self.Env.actions)

        self.policy_net = rl_models.rl_model(self)
        self.target_net = rl_models.rl_model(self)
        self.target_net.load_state_dict(self.policy_net.state_dict())

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=config.lr)
        self.memory = rl_models.ReplayMemory(self.config.max_mem)

        self.Transition = namedtuple('Transition',
                                     ('state', 'action', 'next_state', 'reward'))

        self.steps_done = 0
        self.ended = 0

        self.resize = T.Compose([T.ToPILImage(),
                                 T.Pad((np.max(self.game_size[0:2]) - self.game_size[1],
                                        np.max(self.game_size[0:2]) - self.game_size[0])),
                                 T.Resize((self.config.img_size, self.config.img_size), interpolation=Image.CUBIC),
                                 T.ToTensor()])

        self.episode_durations = []

        self.num_episodes = config.num_episodes

        self.start_time = 0
        self.screen_history = []
        self.num_runs = 0
        self.duration = 0
        self.end_time = 0

    def save_screen(self):

        misc.imsave('original.png', self.Env.render())

        misc.imsave('altered.png', np.rollaxis(self.get_screen().cpu().numpy()[0], 0, 3))

    def get_screen(self):
        # imageio.imsave('sample.png', self.Env.render())
        #pdb.set_trace()
        screen = self.Env.render().transpose((2, 0, 1))
        screen = np.ascontiguousarray(screen, dtype=np.float32) / 255
        screen = torch.from_numpy(screen)
        # Resize, and add a batch dimension (BCHW)
        return self.resize(screen).unsqueeze(0).to(self.device)

    def save_gif(self):

        imageio.mimsave('screens/{}_frame{}.gif'.format(self.config.game_name, self.steps), self.screen_history)

    def append_gif(self):

        frame = self.Env.render(gif=True)
        self.screen_history.append(frame)

    # def save_model(self):

    #     torch.save(self.target_net.state_dict(),
    #                'model_weights/{}_trial{}_{}.pt'.format(self.config.game_name, self.config.trial_num,
    #                                                        self.config.level_switch))

    def load_model(self):

        self.policy_net.load_state_dict(torch.load('model_weights/{}'.format(self.config.model_weight_path), map_location=torch.device(self.device)))
        self.target_net.load_state_dict(torch.load('model_weights/{}'.format(self.config.model_weight_path), map_location=torch.device(self.device)))

    def level_step(self):

        if self.config.level_switch == 'sequential':

            if sum(self.recent_history) == int(self.config.criteria.split('/')[0]):  # if level is 'won'

                if self.Env.lvl == len(self.Env.env_list) - 1:  # if this is the last training level
                    print("pass all level")

                    return 1

                else:  # if this isn't the last level

                    self.Env.lvl += 1

                    self.Env.set_level(self.Env.lvl)
                    print("Level {} use {:.4f} seconds to win".format(self.Env.lvl, self.end_time))

                    print("Next Level!")

                    self.recent_history = [0] * int(self.config.criteria.split('/')[1])

                    return 0

        elif self.config.level_switch == 'random':
            # else:

            self.Env.lvl = np.random.choice(range(len(self.Env.env_list) - 1))
            self.Env.set_level(self.Env.lvl)

            return 0

        else:

            raise Exception('level switch not specified.')

    # def model_update(self):

    #     if self.steps > 1000 and not self.steps % self.config.target_update:

    #         self.target_net.load_state_dict(self.policy_net.state_dict())

    #         if self.episode_reward > self.best_reward or self.steps % 50000:
    #             self.best_reward = self.episode_reward
    #             print("New Best Reward: {}".format(self.best_reward))
    #             self.save_model()

    # def select_action(self):

    #     sample = np.random.uniform()
    #     eps_threshold = self.config.eps_end + (self.config.eps_start - self.config.eps_end) * \
    #                     np.exp(-1. * self.steps_done / self.config.eps_decay)
    #     self.steps_done += 1.
    #     if sample > eps_threshold:
    #         with torch.no_grad():
    #             return self.policy_net(self.state).max(1)[1].view(1, 1)
    #     else:
    #         return torch.tensor([[np.random.choice([0, 1])]], device=self.device, dtype=torch.long)
        
    def select_action_with_best_policy(self):
        with torch.no_grad():
            return self.policy_net(self.state).max(1)[1].view(1, 1)


    def run_model(self):
        print("game Starting")
        print("-" * 25)

        if self.config.pretrain:
            print("Loading Model Training Results")

            self.load_model()
        duration_sum = 0
        self.steps = 0
        self.episode_steps = 0
        self.episode = 0
        self.best_reward = 0
        self.episode_reward = 0
        self.duration = 0
        # self.reward_history = []

        self.start_time = time.time()

        with open('reward_result_histories/{}_reward_result_history_{}_trial{}.csv'.format(self.config.game_name,
                                                                             self.config.level_switch,
                                                                             self.config.trial_num), 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["level","runs","steps", "ep_reward", "win", "game_name", "criteria","time use"])

        with open('object_interaction_result_histories/{}_object_interaction_result_history_{}_trial{}.csv'.format(
                self.config.game_name, self.config.level_switch, self.config.trial_num), 'w', newline='', encoding='utf-8') as file:
            interactionfilewriter = csv.writer(file)
            interactionfilewriter.writerow(
                ['agent_type', 'subject_ID', 'modelrun_ID', 'game_name', 'game_level','runs', 'episode_number', 'event_name',
                 'count'])

        # ## PEDRO: Rename as needed
        # picklefilepath = 'pickleFiles/{}.csv'.format(self.config.game_name)

        self.recent_history = [0] * int(self.config.criteria.split('/')[1])

        torch.backends.cudnn.deterministic = True
        torch.manual_seed = (self.config.random_seed)

        self.Env.reset()
        ## store game info once
        # pdb.set_trace()
        ## each episode gets a list of tuples, where each tuple has (avatar.x,, avatar.y, game.time, level_number)
        avatar_position_data = {'game_info': (self.Env.current_env._game.width, self.Env.current_env._game.height),
                                'episodes': [[(self.Env.current_env._game.sprite_groups['avatar'][0].rect.left,
                                               self.Env.current_env._game.sprite_groups['avatar'][0].rect.top,
                                               self.Env.current_env._game.time,
                                               self.Env.lvl)]]}

        event_dict = defaultdict(lambda: 0)
        last_screen = self.get_screen()
        current_screen = self.get_screen()
        self.state = current_screen - last_screen

        while self.steps < self.config.max_steps:
            self.steps += 1
            self.episode_steps += 1

            # if not self.steps%100:
            # print(self.steps)
            # print(self.episode_reward)

            self.append_gif()

            # Select and perform an action
            self.action = self.select_action_with_best_policy()

            self.reward, self.ended, self.win = self.Env.step(self.action.item())

            avatar_position_data['episodes'][-1].append((self.Env.current_env._game.sprite_groups['avatar'][0].rect.left,
                                                         self.Env.current_env._game.sprite_groups['avatar'][0].rect.top,
                                                         self.Env.current_env._game.time,
                                                         self.Env.lvl))

            ## PEDRO: 2. Store events that occur at each timestep
            timestep_events = set()
            for e in self.Env.current_env._game.effectListByClass:
                ## because event handling is so weird in Frogs, we need to filter out these events.
                ## Avatar-water and avatar-log collisions will still be reported from the (killSprite avatar water) interaction and (pullWithIt avatar log) interaction
                ## which is what a player perceives when they play
                if e in [('changeResource', 'avatar', 'water'), ('changeResource', 'avatar', 'log')]:
                    pass
                else:
                    timestep_events.add(tuple(sorted((e[1], e[2]))))

            for e in timestep_events:
                event_dict[e] += 1
            # if self.episode_reward < 0: pdb.set_trace()

            self.episode_reward += self.reward

            self.reward = max(-1.0, min(self.reward, 1.0))

            self.reward = torch.tensor([self.reward], device=self.device)

            # print(self.reward)

            # Observe new state
            last_screen = current_screen
            current_screen = self.get_screen()
            if not self.ended:
                self.next_state = current_screen - last_screen
            else:
                self.next_state = None

            # Store the transition in memory
            #self.memory.push(self)

            # Move to the next state
            self.state = self.next_state

            # Perform one step of the optimization (on the target network)
            # self.optimize_model()

            if self.ended or self.episode_steps > self.config.timeout:

                if self.episode_steps > self.config.timeout: print("Game Timed Out")

                ## PEDRO: 3. At the end of each episode, write events to csv
                with open('object_interaction_result_histories/{}_object_interaction_result_history_{}_trial{}.csv'.format(
                        self.config.game_name, self.config.level_switch, self.config.trial_num), "a", newline='') as file:
                    interactionfilewriter = csv.writer(file)
                    for event_name, count in event_dict.items():
                        row = ('DDQN', 'NA', 'NA', self.config.game_name, self.Env.lvl+1, self.episode, event_name, count)
                        interactionfilewriter.writerow(row)

                self.episode += 1

                # pdb.set_trace()
                sys.stdout.flush()
                self.end_time = time.time()
                self.duration = self.end_time - self.start_time
                duration_sum += self.duration
                print("Level {}, rounds {}, episode use {} step earn {} rewards in {:.3f} seconds".format(self.Env.lvl+1, self.num_runs+1, self.steps, self.episode_reward, self.duration))

                # Update the target network
                self.num_runs += 1
                # self.duration = 0
                # self.model_update()
                # self.reward_history.append([self.Env.lvl, self.steps, self.episode_reward, self.win])
                episde_results = [self.Env.lvl+1, self.num_runs,self.steps, self.episode_reward, self.win, self.config.game_name,
                                  int(self.config.criteria.split('/')[0]), self.duration]

                self.recent_history.insert(0, self.win)
                self.recent_history.pop()

                if self.level_step():
                    with open('reward_result_histories/{}_reward_result_history_{}_trial{}.csv'.format(self.config.game_name,
                                                                                         self.config.level_switch,
                                                                                         self.config.trial_num),
                              "a", newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(episde_results)

                    print("Level {} use {:.2f} seconds to win".format(self.Env.lvl, duration_sum))
                    duration_sum=0
                    break
            

                self.episode_reward = 0
                # print(self.recent_history)
                # print("Print Current Level: {}".format(self.Env.lvl))
                self.start_time = time.time()
                self.Env.reset()

                ## PEDRO: Write pickle to file every 100 episodes
                if self.episode % 2 == 0:
                    with open('avator_position/aliens_avator_position_data.csv', 'wb') as f:
                        cloudpickle.dump(avatar_position_data, f)

                ## add a new list for the new episode; populate new list with tuple of first state
                avatar_position_data['episodes'].append([(self.Env.current_env._game.sprite_groups['avatar'][0].rect.left,
                                                          self.Env.current_env._game.sprite_groups['avatar'][0].rect.top,
                                                          self.Env.current_env._game.time, self.Env.lvl)])

                event_dict = defaultdict(lambda: 0)
                self.episode_steps = 0
                last_screen = self.get_screen()
                current_screen = self.get_screen()
                self.state = current_screen - last_screen

                # if not self.episode % 10:
                # np.save("reward_histories/{}_reward_history_{}_trial{}.npy".format(self.config.game_name, self.config.level_switch, self.config.trial_num), self.reward_history)
                # np.savetxt('reward_histories/{}_reward_history_{}_trial{}.csv'.format(self.config.game_name, self.config.level_switch, self.config.trial_num), a, fmt='%.2f', delimiter=',', header=" level,  steps,  ep_reward,  win")
                with open('reward_result_histories/{}_reward_result_history_{}_trial{}.csv'.format(self.config.game_name,
                                                                                     self.config.level_switch,
                                                                                     self.config.trial_num),
                          "a", newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(episde_results)

                # self.save_gif()
                # self.screen_history = []
                # plt.plot(self.total_reward_history)
                # plt.savefig('reward_history{}.png'.format(self.config.game_name))

        # self.save_model()
