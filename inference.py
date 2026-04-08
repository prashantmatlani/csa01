
# inference.py

import os
from agent_llm import get_action
from app.env import CustomerSupportEnv


def format_action(action: dict) -> str:
    """Convert action dict → string"""
    if not action:
        return "null"
    return str(action).replace("\n", "").replace("  ", " ")


def main():

    env = CustomerSupportEnv()
    obs = env.reset()

    #model_name = os.getenv("MODEL_NAME", "unknown-model")
    model_name="llama-3.1-8b-instant"

    task_name = "customer-support"
    benchmark = "openenv"

    step_count = 0
    rewards = []
    success = False

    # =========================
    # START
    # =========================
    print(f"[START] task={task_name} env={benchmark} model={model_name}")

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

            # =========================
            # STEP
            # =========================
            print(
                f"[STEP] step={step_count} "
                f"action={format_action(action)} "
                f"reward={reward:.2f} "
                f"done={'true' if done else 'false'} "
                f"error=null"
            )

            obs = next_obs

        # success from env
        success = info.get("task_success", False)

    except Exception as e:
        # still must print END
        print(
            f"[STEP] step={step_count+1} "
            f"action=null reward=0.00 done=true error={str(e)}"
        )

    finally:
        # =========================
        # END
        # =========================
        rewards_str = ",".join(f"{r:.2f}" for r in rewards)

        print(
            f"[END] success={'true' if success else 'false'} "
            f"steps={step_count} "
            f"rewards={rewards_str}"
        )


if __name__ == "__main__":
    main()