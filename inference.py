
# inference.py

import os
import json
from agent_llm import get_action
from app.env import CustomerSupportEnv
from graders import grade_easy, grade_medium, grade_hard
#from tasks import TASKS
from app.env import get_tasks

import sys

TASKS = get_tasks()

def compute_score(task_type, env, success, steps, rewards):

    if task_type == "easy":
        return grade_easy(env, success, steps, rewards)

    elif task_type == "medium":
        return grade_medium(env, success, steps, rewards)

    elif task_type == "hard":
        return grade_hard(env, success, steps, rewards)

    return 0.5  # fallback (should never hit)


# =========================
# ACTION FORMATTER
# =========================
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


# =========================
# RUN SINGLE TASK
# =========================
def run_single_task(task):

    task_name = task["name"]
    task_type = task["type"]

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
                f"[STEP] task={task_name} step={step_count} "
                f"action={format_action(action)} "
                f"reward={reward:.2f} "
                f"done={'true' if done else 'false'} "
                f"error=null"
            )

            obs = next_obs

        success = info.get("task_success", False)

    except Exception as e:
        print(
            f"[STEP] task={task_name} step={step_count+1} "
            f"action=null reward=0.00 done=true error={str(e)}"
        )

    # =========================
    # SCORE USING TASK-SPECIFIC GRADER
    # =========================
    #score = compute_score(task_type, env, success, step_count, rewards)

    grader = task.get("grader")

    if grader:
        score = grader(env, success, step_count, rewards)
    else:
        score = 0.5

    """
    if task_type == "easy":
        score = grade_easy(env)
    elif task_type == "medium":
        score = grade_medium(env)
    elif task_type == "hard":
        score = grade_hard(env)
    else:
        score = 0.5
    """

    rewards_str = ",".join(f"{r:.2f}" for r in rewards)

    print(
        f"[END] task={task_name} "
        f"success={'true' if success else 'false'} "
        f"steps={step_count} "
        f"score={score:.2f} "
        f"rewards={rewards_str}"
    )

    # =========================
    # CRITICAL: JSON OUTPUT (GRADER SIGNAL)
    # =========================
    #print(f"\n")
    print(json.dumps({
    "task_id": task_name,
    "score": float(round(score, 4))
    }), flush=True)
    #print(f"\n")

# =========================
# MAIN
# =========================
"""
def main():

    model_name = os.getenv("MODEL_NAME", "unknown-model")
    api_base_url = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")

    print(f"[CONFIG] api_base_url={api_base_url}")

    print(f"[START] task=customer-support env=openenv model={model_name}")

    #print(f"[DEBUG] Running {len(TASKS)} tasks")

    # RUN DISTINCT TASKS (NOT LOOP COPIES)
    for task in TASKS:
        run_single_task(task)
"""

def main():

    model_name = os.getenv("MODEL_NAME", "unknown-model")
    api_base_url = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")

    print(f"[CONFIG] api_base_url={api_base_url}")

    benchmark = "openenv"

    # 🚨 CRITICAL: One START per task (validator reads this)
    for task in TASKS:

        task_name = task["name"]

        print(f"[START] task={task_name} env={benchmark} model={model_name}")

        run_single_task(task)

if __name__ == "__main__":
    main()

