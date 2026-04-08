
# server/main.py

from fastapi import FastAPI
from app.env import CustomerSupportEnv

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

app = FastAPI()
env = CustomerSupportEnv()

@app.get("/reset")
def reset():
    return env.reset()

"""
@app.post("/step")
def step(action: dict):
    return env.step(action)
"""
@app.post("/step")
def step(action: dict):
    obs, reward, done, info = env.step(action)

    return {
        "observation": obs,
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/state")
def state():
    return env.state()

@app.get("/health")
def health():
    return {"status": "ok"}