
# app/env.py

from typing import Tuple, Dict, Any
from app.models import Observation, Action, Reward
from app.dataset import TICKETS
import random

import sys

class CustomerSupportEnv:

    # INTERNAL STATE REPRESENTATION - 
    def _get_observation(self):

        total_required = len(self.ticket.get("required_info", []))
        collected_required = sum(
            1 for f in self.ticket.get("required_info", [])
            if f in self.state_data["collected_info"]
        )

        info_progress = collected_required / max(1, total_required)
        
        return {
        "ticket_id": self.ticket["ticket_id"],
        "customer_message": self.ticket["customer_message"],
        "history": [],
        "known_info": self.state_data["collected_info"],
        "required": self.ticket.get("required_info", []),  # FULL requirement space (agent uses this)
        #"remaining_required": self.state_data["required_info"],   # OPTIONAL (env/debug/analysis); agent_llm shouldn't use this directly - it should infer from known_info + customer_message
        "missing_required": [
            f for f in self.ticket.get("required_info", [])
            if f not in self.state_data["collected_info"]
        ],
        #"info_progress": len(self.state_data["collected_info"]) / 3,
        "info_progress": info_progress,
        "status": self.state_data["status"],
        "step_count": self.state_data["steps_taken"],
        "remaining_steps": self.max_steps - self.state_data["steps_taken"],
        }

    def __init__(self):
        self.state_data = None
        self.max_steps = 10
        self.last_action = None

        # ✅ METRICS TRACKING
        self.episode_stats = []

    def reset(self):

        self.last_action = None

        # ✅ episode tracking
        self.current_episode_reward = 0.0
        self.current_steps = 0
        self.success = False

        self.ticket = random.choice(TICKETS)

        self.state_data = {
            "ticket_id": self.ticket["ticket_id"],
            "customer_message": self.ticket["customer_message"],
            "history": [],
            "status": "open",
            "priority": None,
            "category": None,
            "required_info": self.ticket["required_info"].copy(),
            "collected_info": {},
            "steps_taken": 0,
            "max_steps": self.max_steps,
            "ground_truth": self.ticket
        }

        return self._get_observation()
    
    
    def step(self, action: dict):

        reward = 0.0
        done = False
        info = {}
        #info = {
        #"final_score": self._compute_final_score() if done else None
        #}

        collected = self.state_data["collected_info"]
        required = self.state_data["required_info"]
        gt = self.ticket

        # -----------------------
        # STEP PENALTY
        # -----------------------
        reward -= 0.05

        action_type = action.get("type")

        # -----------------------
        # REPEAT PENALTY
        # -----------------------
        if self.last_action == action:
            reward -= 0.2

        # -----------------------
        # CLASSIFY
        # -----------------------
        if action_type == "classify":

            collected["category"] = gt["category"]
            collected["priority"] = gt["priority"]

            reward += 0.2

        # -----------------------
        # ASK INFO
        # -----------------------
        elif action_type == "ask_info":

            field = action.get("field")

            if field not in collected:
                collected[field] = "sample_value"
                reward += 0.3

                if field in required:
                    required.remove(field)
            else:
                reward -= 0.3

        # -----------------------
        # RESOLVE
        # -----------------------
        elif action_type == "resolve":

            done = True
            final_score = 0.0

            # classification
            if collected.get("category") == gt.get("category"):
                final_score += 0.3

            if collected.get("priority") == gt.get("priority"):
                final_score += 0.2

            # required info
            required_fields = gt.get("required_info", [])
            if all(f in collected for f in required_fields):
                final_score += 0.3
                self.success = True
            else:
                reward -= 0.5

            # resolve bonus
            final_score += 0.2

            reward += final_score

            # efficiency bonus
            optimal_steps = len(required_fields) + 1
            if self.state_data["steps_taken"] <= optimal_steps:
                reward += 0.3

            # episode stats
            collected_required = sum(1 for f in required_fields if f in collected)

            episode_data = {
                "success": self.success,
                "steps": self.state_data["steps_taken"],
                "reward": reward,
                "info_efficiency": collected_required / max(1, len(required_fields))
            }

            self.episode_stats.append(episode_data)

            info = {
                "final_score": final_score,
                "task_success": self.success,
                "collected_info": collected
            }

            self.last_action = action
            return self._get_observation(), reward, done, info

        # -----------------------
        # INVALID
        # -----------------------
        else:
            reward -= 0.3

        # -----------------------
        # STEP UPDATE
        # -----------------------
        self.state_data["steps_taken"] += 1
        self.current_steps += 1

        # -----------------------
        # MAX STEP TERMINATION
        # -----------------------
        if self.state_data["steps_taken"] >= self.state_data["max_steps"]:
            done = True
            reward -= 2.0

            # record failure episode
            self.episode_stats.append({
                "success": False,
                "steps": self.state_data["steps_taken"],
                "reward": reward,
                "info_efficiency": 0
            })

            info = {
                "final_score": 0.0,
                "task_success": False
            }

        # -----------------------
        # SAVE STATE
        # -----------------------
        self.last_action = action
        self.current_episode_reward += reward

        return self._get_observation(), reward, done, info
    
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