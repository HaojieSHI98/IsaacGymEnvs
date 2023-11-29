import isaacgym
import isaacgymenvs
import torch

num_envs = 100

envs = isaacgymenvs.make(
    seed=0, 
    task="FrankaTool", 
    num_envs=num_envs, 
    sim_device="cuda:0",
    rl_device="cuda:0",
    graphics_device_id=0,
    # headless=True,
)
print("Observation space is", envs.observation_space)
print("Action space is", envs.action_space)
obs = envs.reset()
for _ in range(2000):
    random_actions = 2.0 * torch.rand((num_envs,) + envs.action_space.shape, device = 'cuda:0') - 1.0
    obs,re,reset,info = envs.step(random_actions)
    # print(obs["obs"][:2,:12])
    # print(random_actions)