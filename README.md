---
title: Customer Support Agent
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
tags:
  - openenv
---

# Customer Support RL + LLM Agent — Overview

## Overview
This project implements a hybrid agent for customer support automation.

The agent:
1. Classifies customer queries
2. Collects required information
3. Resolves efficiently

---

## Environment

The environment simulates customer support tickets with:
- Customer message
- Required information fields
- Ground truth classification

The agent uses a hybrid approach:
- LLM for classification
- deterministic policy for information gathering
- reward-shaped environment for optimization

🎯 Objective

Build an intelligent agent that:

- Classifies customer issues
- Collects required information
- Resolves efficiently

🏗 Architecture

1. Environment (env.py)

Simulates customer support workflow.

State:

customer_message
known_info
required fields
progress

Actions:

classify
ask_info
resolve

2. Reward Design

Action	            Reward
Correct classify	 +0.5
Ask required info	 +0.3
Repeat ask	         -0.3
Step penalty	     -0.05
Successful resolve	 +1.0

3. Observation Design

{
  "customer_message": str,
  "known_info": dict,
  "required": list   # full schema
}

4. Agent Types

Rule Agent (agent.py)
. Deterministic
. Uses required fields
. Computes missing info

LLM Agent (agent_llm.py)
. Uses prompt reasoning
. Strict JSON output
. Retry + fallback

5. Core Logic

if not classified:
    classify
elif missing fields:
    ask_info
else:
    resolve

6. Key Improvements Made

- Removed ground-truth leakage
- Added reward shaping
- Added efficiency scoring
- Added schema-based reasoning
- Added fallback policy
- Added metrics tracking

7. Metrics

{
  success_rate,
  avg_steps,
  avg_reward,
  info_efficiency
}

8. Inference

python inference.py

9. Deployment

docker build -t support-agent .
docker run support-agent