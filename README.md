# 1016-final-project-Aline-game
Group member: Xiaoyu Zhang; HaoHang Yan; Ziqing Peng

Abstract
This proposal aims to evaluate the performance of reinforcement learning (RL) models against human players in the Atari game "Alien", using the OpenAI Gym environment. The project will focus on developing an RL model that emulates human-like behavior by integrating parameters such as bounded rationality and reaction capabilities. The study will assess whether these humanized RL models can achieve or exceed human performance levels in gameplay.

Introduction
Background: Atari games have historically served as benchmarks for evaluating RL algorithms. The game "Alien" provides a complex environment to test the adaptability of AI against human strategies.

Problem Statement: There is ongoing research interest in developing RL models that can mimic human behavior while maintaining or surpassing human performance in gaming.

Objective: To compare the game-playing performance of human players with RL models that incorporate human-like behavioral traits, with a focus on assessing strategic and tactical gameplay.

Literature Review: This section will cover seminal and recent studies in RL, human behavioral models in gaming, and the use of Atari games as AI benchmarks. Key texts include Mnih et al.'s foundational paper on Deep Q-Networks and various studies on human behavioral modeling in games.

Methodology
Data Collection Methods: RL Models: Implementing and modifying models from the PyTorch-based repository of deep RL algorithms.
Human Data: Collecting gameplay data from human participants.

Data Analysis Techniques:
Comparative Analysis: Statistical analysis of performance metrics and behavioral pattern recognition to compare human and AI gameplay.

Bounded Rationality: To mimic the initial decision-making limitations of humans
Fatigue and Concentration: Adjusting model parameters to reflect degradation in human performance over time due to fatigue.
Reaction Ability: Modelling delayed or randomized responses to simulate human reaction times.

Simulation Tactics:
Policy Adjustment: Using ε-greedy strategies to simulate fluctuating human concentration levels.
State-Dependent Actions: Incorporating time as a state variable to modify actions based on perceived fatigue levels.
Expected Results: The project expects to find nuanced differences in how humanized RL models and actual human players handle game dynamics, potentially revealing that RL can adapt human-like decision-making under varied gameplay conditions.

 
References
https://www.endtoend.ai/envs/gym/atari/alien/
https://arxiv.org/pdf/1312.5602.pdf
https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html
https://github.com/p-christ/Deep-Reinforcement-Learning-Algorithms-with-PyTorch/tree/master
https://github.com/ACampero/RC_RL
