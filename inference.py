
# inference.py

import os
from agent_llm import get_action
from app.env import CustomerSupportEnv


#"""
#def format_action(action: dict) -> str:
    #"""Convert action dict → string"""
#    if not action:
#        return "null"
#    return str(action).replace("\n", "").replace("  ", " ")
#"""

def format_action(action: dict) -> str:
    if not action:
        return "null"

    action_type = action.get("type")

    if action_type == "ask_info":
        return f"ask_info('{action.get('field')}')"
    elif action_type == "resolve":
        return "resolve()"
    elif action_type == "classify":
        return "classify()"

    return str(action)

def compute_score(success, steps, rewards):
    """
    Continuous score in (0,1)
    """
    avg_reward = sum(rewards) / max(1, len(rewards))

    score = (
        0.5 * (1.0 if success else 0.0) +
        0.3 * (1 / (1 + steps)) +
        0.2 * max(0, min(1, avg_reward))
    )

    # Clamp to (0,1) but not exact
    return max(0.01, min(0.99, score))


def run_single_task(task_id):
    env = CustomerSupportEnv()
    obs = env.reset()

    step_count = 0
    rewards = []
    success = False

    try:
        done = False

        while not done:

            valid_actions = [
                {"type": "ask_info", "field": "order_id"},
                {"type": "ask_info", "field": "account_email"},
                {"type": "ask_info", "field": "device_type"},
                {"type": "ask_info", "field": "browser"},
                {"type": "resolve"},
                {"type": "classify"},
            ]

            action = get_action(obs, valid_actions)

            next_obs, reward, done, info = env.step(action)

            step_count += 1
            rewards.append(reward)

            print(
                f"[STEP] task={task_id} step={step_count} "
                f"action={format_action(action)} "
                f"reward={reward:.2f} "
                f"done={'true' if done else 'false'} "
                f"error=null"
            )

            obs = next_obs

        success = info.get("task_success", False)

    except Exception as e:
        print(
            f"[STEP] task={task_id} step={step_count+1} "
            f"action=null reward=0.00 done=true error={str(e)}"
        )

    score = compute_score(success, step_count, rewards)

    rewards_str = ",".join(f"{r:.2f}" for r in rewards)

    print(
        f"[END] task={task_id} "
        f"success={'true' if success else 'false'} "
        f"steps={step_count} "
        f"score={score:.2f} "
        f"rewards={rewards_str}"
    )


def main():

    model_name = os.getenv("MODEL_NAME", "unknown-model")
    api_base_url = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")

    print(f"[CONFIG] api_base_url={api_base_url}")

    task_name = "customer-support"
    benchmark = "openenv"

    print(f"[START] task={task_name} env={benchmark} model={model_name}")

    # =========================
    # RUN MULTIPLE TASKS (IMPORTANT)
    # =========================
    NUM_TASKS = 3

    for i in range(NUM_TASKS):
        run_single_task(task_id=i + 1)


if __name__ == "__main__":
    main()