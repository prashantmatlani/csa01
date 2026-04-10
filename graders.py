
# graders.py

def get_info_efficiency(env):
    if hasattr(env, "episode_stats") and env.episode_stats:
        return env.episode_stats[-1].get("info_efficiency", 0)
    return 0


def grade_easy(env, trajectory=None, final_state=None):
    rewards = [step.get("reward", 0) for step in (trajectory or [])]
    score = 0.3 + 0.1 * len(rewards)
    return max(0.0, min(1.0, score))


def grade_medium(env, trajectory=None, final_state=None):
    info_eff = get_info_efficiency(env)
    score = 0.5 * info_eff
    return max(0.0, min(1.0, score))


def grade_hard(env, trajectory=None, final_state=None):
    info_eff = get_info_efficiency(env)

    success = False
    steps = len(trajectory or [])

    if hasattr(env, "episode_stats") and env.episode_stats:
        success = env.episode_stats[-1].get("success", False)

    score = (
        0.5 * (1 if success else 0) +
        0.3 * info_eff +
        0.2 * (1 / (1 + steps))
    )

    return max(0.0, min(1.0, score))