
# tasks.py

from graders import grade_easy, grade_medium, grade_hard

TASKS = [
    {
        "name": "easy-info-collection",
        "type": "easy",
        "grader": grade_easy,
    },
    {
        "name": "medium-complete-info",
        "type": "medium",
        "grader": grade_medium,
    },
    {
        "name": "hard-efficient-resolution",
        "type": "hard",
        "grader": grade_hard,
    },
]