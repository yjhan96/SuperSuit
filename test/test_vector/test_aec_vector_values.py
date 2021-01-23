from supersuit.aec_vector import SyncAECVectorEnv,AsyncAECVectorEnv
from pettingzoo.classic import rps_v1
from pettingzoo.classic import mahjong_v2, hanabi_v3
from pettingzoo.butterfly import knights_archers_zombies_v5
from pettingzoo.mpe import simple_world_comm_v2
from pettingzoo.classic import chess_v0
from pettingzoo.sisl import multiwalker_v6
from pettingzoo.atari import warlords_v2
import numpy as np
import random
import time
import supersuit


def mahjong_maker():
    env = mahjong_v2.env()
    env = supersuit.observation_lambda_v0(env, lambda obs: obs['observation'], lambda obs_space: obs_space['observation'])
    return env

def hanabi_maker():
    env = hanabi_v3.env()
    env = supersuit.observation_lambda_v0(env, lambda obs: obs['observation'], lambda obs_space: obs_space['observation'])
    return env


def test_all():
    NUM_ENVS = 5
    NUM_CPUS = 2
    def test_vec_env(vec_env):
        vec_env.reset()
        obs, rew, agent_done, env_done, agent_passes, infos = vec_env.last()
        print(np.asarray(obs).shape)
        assert len(obs) == NUM_ENVS
        act_space = vec_env.action_spaces[vec_env.agent_selection]
        assert np.all(np.equal(obs, vec_env.observe(vec_env.agent_selection)))
        assert len(vec_env.observe(vec_env.agent_selection)) == NUM_ENVS
        vec_env.step([act_space.sample() for _ in range(NUM_ENVS)])
        obs, rew, agent_done, env_done, agent_passes, infos = vec_env.last(observe=False)
        assert obs is None

    def test_infos(vec_env):
        vec_env.reset()
        infos = vec_env.infos[vec_env.agent_selection]
        assert infos[1]['legal_moves']

    def test_some_done(vec_env):
        vec_env.reset()
        act_space = vec_env.action_spaces[vec_env.agent_selection]
        assert not any(done for dones in vec_env.dones.values() for done in dones)
        vec_env.step([act_space.sample() for _ in range(NUM_ENVS)])
        assert any(done for dones in vec_env.dones.values() for done in dones)
        assert any(rew != 0 for rews in vec_env.rewards.values() for rew in rews)

    def select_action(vec_env,passes,i):
        my_info = vec_env.infos[vec_env.agent_selection][i]
        if False and not passes[i] and 'legal_moves' in my_info:
            return random.choice(my_info['legal_moves'])
        else:
            act_space = vec_env.action_spaces[vec_env.agent_selection]
            return act_space.sample()

    test_vec_env(SyncAECVectorEnv([rps_v1.env]*NUM_ENVS))
    test_vec_env(SyncAECVectorEnv([lambda :mahjong_maker() for i in range(NUM_ENVS)]))
    test_infos(SyncAECVectorEnv([hanabi_maker]*NUM_ENVS))
    test_some_done(SyncAECVectorEnv([mahjong_maker]*NUM_ENVS))
    test_vec_env(SyncAECVectorEnv([multiwalker_v6.env]*NUM_ENVS))
    test_vec_env(SyncAECVectorEnv([simple_world_comm_v2.env]*NUM_ENVS))

    test_vec_env(AsyncAECVectorEnv([rps_v1.env]*NUM_ENVS, NUM_CPUS))
    test_vec_env(AsyncAECVectorEnv([lambda : mahjong_maker() for i in range(NUM_ENVS)], NUM_CPUS))
    test_infos(AsyncAECVectorEnv([hanabi_maker]*NUM_ENVS, NUM_CPUS))
    test_some_done(AsyncAECVectorEnv([mahjong_maker]*NUM_ENVS, NUM_CPUS))
    test_vec_env(AsyncAECVectorEnv([multiwalker_v6.env]*NUM_ENVS, NUM_CPUS))
    test_vec_env(AsyncAECVectorEnv([simple_world_comm_v2.env]*NUM_ENVS, NUM_CPUS))
