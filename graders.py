
# graders.py

def get_info_efficiency(env):
    if hasattr(env, "episode_stats") and env.episode_stats:
        return env.episode_stats[-1].get("info_efficiency", 0)
    return 0


def grade_easy(env, success=None, steps=None, rewards=None):
    score = 0.3 + 0.1 * (len(rewards) if rewards else 0)

    #print(f"\nrewards: {rewards}")
    #print(f"\nlen rewards: {len(rewards)}")
    #print(f"\nscore: {score}")

    return max(0.01, min(0.99, score))


def grade_medium(env, success=None, steps=None, rewards=None):
    info_eff = get_info_efficiency(env)
    score = 0.5 * info_eff

    #print(f"\ninfo_eff: {info_eff}")
    #print(f"\nscore: {score}")

    return max(0.01, min(0.99, score))


def grade_hard(env, success=None, steps=None, rewards=None):
    info_eff = get_info_efficiency(env)

    score = (
        0.5 * (1 if success else 0) +
        0.3 * info_eff +
        0.2 * (1 / (1 + (steps or 1)))
    )

    #print(f"\nsteps: {steps}")
    #print(f"\ninfo_eff: {info_eff}")
    #print(f"\nlen trajectory: {len(trajectory or [])}")
    #print(f"\nscore: {score}")

    return max(0.01, min(0.99, score))



