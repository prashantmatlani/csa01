
# server.py

from fastapi import FastAPI
from pydantic import BaseModel
from app.env import CustomerSupportEnv

import json

app = FastAPI()

env = CustomerSupportEnv()


class StepRequest(BaseModel):
    action: str  # OpenEnv sends STRING


def parse_action(action_str: str):
    """
    Convert string action → dict
    Supports both:
    - JSON string
    - simple commands
    """

    try:
        return json.loads(action_str)
    except:
        # fallback parsing
        if action_str == "classify":
            return {"type": "classify"}
        elif action_str.startswith("ask_"):
            return {
                "type": "ask_info",
                "field": action_str.replace("ask_", "")
            }
        elif action_str == "resolve":
            return {"type": "resolve"}
        else:
            return {"type": "invalid"}


@app.post("/reset")
def reset():
    obs = env.reset()
    return obs   # ✅ MUST return raw observation


@app.post("/step")
def step(req: StepRequest):

    action_dict = parse_action(req.action)

    obs, reward, done, info = env.step(action_dict)

    return {
        "observation": obs,
        "reward": float(reward),
        "done": bool(done),
        "info": info
    }