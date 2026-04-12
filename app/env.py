
# app/env.py

from typing import Tuple, Dict, Any
from app.models import Observation, Action, Reward
from app.dataset import TICKETS
import random
from graders import grade_easy, grade_medium, grade_hard
#from tasks import TASKS

import sys

# =========================
# PURPOSE: Controls difficulty-driven stochasticity
# - noise_prob → message distortion
# - missing_info_prob → partial observability
# =========================
DIFFICULTY_CONFIG = {
    "easy": {
        "max_steps": 8,
        "noise_prob": 0.0,
        "missing_info_prob": 0.1
    },
    "medium": {
        "max_steps": 10,
        "noise_prob": 0.2,
        "missing_info_prob": 0.3
    },
    "hard": {
        "max_steps": 12,
        "noise_prob": 0.4,
        "missing_info_prob": 0.5
    }
}

# =========================
# PURPOSE: Defines tasks exposed to validator
# =========================
AVAILABLE_TASKS = [
    {
        "id": "easy-info-collection",
        "difficulty": "easy",
        "grader": grade_easy
    },
    {
        "id": "medium-complete-info",
        "difficulty": "medium",
        "grader": grade_medium
    },
    {
        "id": "hard-efficient-resolution",
        "difficulty": "hard",
        "grader": grade_hard
    }
]

def get_tasks():
    return AVAILABLE_TASKS

class CustomerSupportEnv:

    # OBTAIN TASKS FROM GRADERS.PY
    def get_tasks(self):
        return [
            {
                "id": "easy-info-collection",
                "difficulty": "easy",
                "grader": grade_easy,
            },
            {
                "id": "medium-complete-info",
                "difficulty": "medium",
                "grader": grade_medium,
            },
            {
                "id": "hard-efficient-resolution",
                "difficulty": "hard",
                "grader": grade_hard,
            },
        ]

    # =========================
    # PURPOSE: Build observation exposed to agent
    # =========================
    def _get_observation(self):

        required = self.state_data["required_info"]
        collected = self.state_data["collected_info"]

        total = len(required)
        collected_count = sum(1 for f in required if f in collected)

        return {
            "ticket_id": self.ticket["ticket_id"],
            "customer_message": self.state_data["customer_message"],
            "known_info": collected,
            "required": required,
            "missing_required": [f for f in required if f not in collected],
            "info_progress": collected_count / max(1, total),
            "status": self.state_data["status"],
            "step_count": self.state_data["steps_taken"],
            "remaining_steps": self.max_steps - self.state_data["steps_taken"],
            "difficulty": self.difficulty # difficulty awareness 
        }

    # =========================
    # PURPOSE: Initialize environment with difficulty & randomness
    # =========================
    def __init__(self, difficulty="medium", seed=None):

        self.difficulty = difficulty
        self.config = DIFFICULTY_CONFIG[difficulty]

        if seed is not None:
            random.seed(seed)

        self.state_data = None
        self.max_steps = self.config["max_steps"]
        self.last_action = None

        # self-correction tracking
        self.classification_history = []
        
        # METRICS TRACKING
        self.episode_stats = []

    def list_tasks(self):
        return self.tasks

    def reset(self):

        self.last_action = None
        #self.current_episode_reward = 0.0
        self.current_steps = 0
        self.success = False

        self.ticket = random.choice(TICKETS)
        gt = self.ticket["ground_truth"]

        msg = random.choice(self.ticket["variants"])
        msg = self._inject_noise(msg)

        masked_required = self._mask_required_info(gt["required_info"])

        self.state_data = {
            "ticket_id": self.ticket["ticket_id"],
            "customer_message": msg,
            "status": "open",
            "category": None,
            "priority": None,
            "required_info": masked_required,
            "collected_info": {},
            "steps_taken": 0,
            "ground_truth": gt
        }

        return self._get_observation()

    # =========================
    # PURPOSE: Core transition function with self-correction logic
    # =========================
    def step(self, action: dict):

        if self.state_data is None:
            self.reset()

        reward = -0.05
        done = False
        info = {}

        collected = self.state_data["collected_info"]
        gt = self.ticket["ground_truth"]

        action_type = action.get("type") if isinstance(action, dict) else None

        # -----------------------
        # CLASSIFY (SELF-CORRECTION ENABLED)
        # -----------------------
        if action_type == "classify":

            new_cat = action.get("category")
            prev_cat = collected.get("category")

            collected["category"] = new_cat
            collected["priority"] = action.get("priority")

            self.classification_history.append(new_cat)

            # correct classification
            if new_cat == gt["category"]:
                reward += 0.3

            # self-correction bonus
            if prev_cat and prev_cat != gt["category"] and new_cat == gt["category"]:
                reward += 0.5  # major reward

            # flip-flop penalty
            if len(self.classification_history) >= 3:
                if len(set(self.classification_history[-3:])) > 2:
                    reward -= 0.3

        # -----------------------
        # ASK INFO
        # -----------------------
        elif action_type == "ask_info":

            field = action.get("field")

            if field not in collected:
                collected[field] = "value"
                reward += 0.25
            else:
                reward -= 0.2

        # -----------------------
        # RESOLVE
        # -----------------------
        elif action_type == "resolve":

            done = True

            required = gt["required_info"]
            all_info = all(f in collected for f in required)

            correct_cat = collected.get("category") == gt["category"]

            # 🔥 premature penalty
            if not all_info:
                reward -= 0.7

            # scoring
            if correct_cat:
                reward += 0.3

            if all_info:
                reward += 0.3
                self.success = True

            reward += 0.2  # completion bonus

        else:
            reward -= 0.3

        # -----------------------
        # STEP UPDATE
        # -----------------------
        self.state_data["steps_taken"] += 1

        if self.state_data["steps_taken"] >= self.max_steps:
            done = True
            reward -= 1.5

        return self._get_observation(), reward, done, {
            "task_success": self.success
        }
    
    def state(self) -> Dict:
        return self.state_data

    def get_metrics(self):

        if not self.episode_stats:
            return {}

        total = len(self.episode_stats)

        success_rate = sum(e["success"] for e in self.episode_stats) / total
        avg_steps = sum(e["steps"] for e in self.episode_stats) / total
        avg_reward = sum(e["reward"] for e in self.episode_stats) / total
        info_eff = sum(e["info_efficiency"] for e in self.episode_stats) / total

        return {
            "success_rate": round(success_rate, 3),
            "avg_steps": round(avg_steps, 3),
            "avg_reward": round(avg_reward, 3),
            "info_efficiency": round(info_eff, 3)
        }
    
    # =========================
    # PURPOSE: Apply noise to simulate real-world messy input
    # =========================
    def _inject_noise(self, message):
        if random.random() < self.config["noise_prob"]:
            noise = random.choice([
                "pls help asap",
                "not sure what's wrong",
                "this is urgent",
                "been days"
            ])
            return message + " " + noise
        return message


     # =========================
    # PURPOSE: Mask required fields → partial observability
    # =========================
    def _mask_required_info(self, required_fields):
        masked = [
            f for f in required_fields
            if random.random() > self.config["missing_info_prob"]
        ]
        return masked if masked else required_fields

    """
    def _mask_required_info(self, required_fields):

        masked = []

        for field in required_fields:
            if random.random() > self.config["missing_info_prob"]:
                masked.append(field)

        # ensure at least 1 required field remains
        return masked if masked else required_fields
    """