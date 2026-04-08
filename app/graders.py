

# app/graders.py

def grade_task1(state):
    score = 0.0
    gt = state["ground_truth"]

    if state["category"] == gt["category"]:
        score += 0.5
    if state["priority"] == gt["priority"]:
        score += 0.5

    return score


def grade_task2(state):
    required = set(state["ground_truth"]["required_info"])
    collected = set(state["collected_info"].keys())

    if not required:
        return 1.0

    return len(collected & required) / len(required)


def grade_task3(state):
    score = 0.0
    gt = state["ground_truth"]

    # classification
    if state["category"] == gt["category"]:
        score += 0.3

    # info collection
    required = set(gt["required_info"])
    collected = set(state["collected_info"].keys())
    if required:
        score += 0.3 * (len(collected & required) / len(required))

    # resolution
    if state["status"] == "resolved":
        score += 0.4

    return score