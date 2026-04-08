

# agent_rule_based.py

def get_action(obs):
#def act(obs):

    known = obs.get("known_info", {})
    required_full = obs.get("required_info_full", [])

    # 1. classify first
    if "category" not in known or "priority" not in known:
        return {"type": "classify"}

    # 2. collect missing info
    missing = [f for f in required_full if f not in known]

    if len(missing) > 0:
        return {"type": "ask_info", "field": missing[0]}

    # 3. resolve only when complete
    return {"type": "resolve"}