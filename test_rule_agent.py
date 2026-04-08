
# test_rule_agent.py

from app.env import CustomerSupportEnv
from agent_rule_based import get_action

env = CustomerSupportEnv()

for i in range(5):
    obs = env.reset()
    done = False

    print(f"\n===== EPISODE {i+1} =====")

    while not done:
        action = get_action(obs)
        obs, reward, done, info = env.step(action)

    print("FINAL:", info)
    print(env.get_metrics())