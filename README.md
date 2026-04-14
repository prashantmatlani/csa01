---
title: Customer Support OpenEnv Environment
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
tags:
  - openenv
  - reinforcement-learning
  - llm
  - customer-support
---

# 🤖 Customer Support Agent — OpenEnv Environment

## 🧠 Overview

This project implements a **real-world customer support simulation environment** built using the OpenEnv specification.

It is designed to evaluate and train intelligent agents capable of:

* Understanding noisy and ambiguous user queries
* Classifying issues correctly
* Gathering missing information efficiently
* Resolving tickets under uncertainty

Unlike toy environments, this system models **real operational complexity** found in production customer support workflows.

---

## 🎯 Objective

Build and evaluate an agent that can:

1. **Classify** customer issues (billing / technical / delivery)
2. **Collect required information** dynamically
3. **Resolve efficiently** under constraints
4. **Adapt behavior mid-episode** (self-correction)

---

## 🏗️ System Architecture

### 1. Environment (`env.py`)

A **stateful, stochastic simulation** of customer support operations.

#### Key Features

* Multi-step interaction loop (`step`, `reset`, `state`)
* Partial observability (missing information)
* Stochastic noise injection
* Difficulty-aware configuration
* Multi-intent ticket handling
* Reward shaping with penalties for poor decisions

---

### 2. Observation Space

```json
{
  "ticket_id": "string",
  "customer_message": "string",
  "known_info": {},
  "required": ["fields"],
  "missing_required": ["fields"],
  "info_progress": 0.0,
  "status": "open | resolved",
  "step_count": 0,
  "remaining_steps": 10,
  "difficulty": "easy | medium | hard"
}
```

---

### 3. Action Space

| Action   | Description                |
| -------- | -------------------------- |
| classify | Assign category + priority |
| ask_info | Request missing field      |
| resolve  | Attempt to close ticket    |

Example:

```json
{
  "type": "ask_info",
  "field": "order_id"
}
```

---

## 🎲 Difficulty & Stochastic Control

The environment dynamically adjusts complexity:

| Difficulty | Max Steps | Noise    | Missing Info |
| ---------- | --------- | -------- | ------------ |
| Easy       | Low       | None     | Minimal      |
| Medium     | Medium    | Moderate | Partial      |
| Hard       | High      | High     | Significant  |

### Stochastic Elements

* **Noise Injection**
  Adds irrelevant or emotional phrases

* **Information Masking**
  Required fields may be hidden

* **Ambiguity**
  Messages may not clearly indicate category

---

## 🧾 Dataset (Production-Style Tickets)

Each ticket includes:

```python
{
  "ticket_id": "...",
  "variants": [...],        # multiple phrasings
  "noise": [...],           # real-world clutter
  "ground_truth": {
      "category": "...",
      "priority": "...",
      "required_info": [...],
      "intents": [...]      # multi-intent support
  }
}
```

### Key Properties

* Multiple linguistic variations
* Realistic phrasing (not templated)
* Multi-intent issues (e.g., billing + technical)
* No explicit hints (agent must infer)

---

## 🔁 Self-Correction Mechanism

The agent is designed to **adapt within an episode**.

### What this means:

* Can **re-classify after new information**
* Can **delay resolution under uncertainty**
* Can **recover from suboptimal actions**

### Example behavior:

```
classify → ask_info → re-classify → resolve
```

This mimics real-world agent reasoning rather than fixed pipelines.

---

## 🧠 Agent Design (`agent_llm.py`)

### Hybrid Intelligence

| Component | Role                   |
| --------- | ---------------------- |
| LLM       | High-level reasoning   |
| Rules     | Safety + constraints   |
| Fallback  | Deterministic recovery |

---

### Key Capabilities

* Structured JSON output
* Retry + validation loop
* Fallback policy (guarantees progress)
* Partial autonomy (not over-constrained)

---

## 🧮 Reward Design

Reward is **dense and shaped**, not binary.

| Behavior                 | Reward       |
| ------------------------ | ------------ |
| Step penalty             | -0.05        |
| Correct classification   | +0.2         |
| Useful info collection   | +0.3         |
| Redundant action         | -0.3         |
| Premature resolve (hard) | -1.0         |
| Successful resolve       | +0.2 to +1.0 |

---

## 📊 Metrics

Tracked per episode:

```json
{
  "success_rate": 0.0,
  "avg_steps": 0.0,
  "avg_reward": 0.0,
  "info_efficiency": 0.0
}
```

### Additional Behavioral Signals

* Self-correction frequency (re-classification)
* Resolution efficiency
* Failure modes under uncertainty

---

## 🧪 Tasks & Graders

Three evaluation tasks:

| Task                      | Difficulty | Objective                              |
| ------------------------- | ---------- | -------------------------------------- |
| easy-info-collection      | Easy       | Basic info gathering                   |
| medium-complete-info      | Medium     | Complete + accurate handling           |
| hard-efficient-resolution | Hard       | Efficient resolution under uncertainty |

### Grader Properties

* Deterministic
* Score range: **0.0 – 1.0**
* Multi-factor scoring:

  * success
  * efficiency
  * completeness

---

## ▶️ Inference

Run baseline agent:

```bash
python inference.py
```

Outputs:

```
[START] task=easy-info-collection ...
[STEP] ...
[END] ...
{"task_id": "...", "score": 0.7}
```

---

## 🐳 Deployment (Hugging Face Spaces)

### Build Docker

```bash
docker build -t openenv-customer-support-agent .
```

### Run

```bash
docker run -p 7860:7860 openenv-customer-support-agent
```

---

## 🌐 API Endpoints

| Endpoint | Description            |
| -------- | ---------------------- |
| `/reset` | Initialize environment |
| `/step`  | Execute action         |

---

## ⚙️ Environment Variables

Required:

```
API_BASE_URL
MODEL_NAME
HF_TOKEN
```

---

## ✅ OpenEnv Compliance

* Typed observation/action models
* step/reset/state implemented
* 3+ tasks with graders
* Deterministic scoring
* Dockerized deployment
* HF Space compatible

---

## 🚀 Key Innovations

* Real-world task simulation (not toy)
* Stochastic difficulty scaling
* Multi-intent ticket modeling
* Self-correcting agent behavior
* Hybrid LLM + rule-based architecture
* Dense reward shaping

---

## 🔮 Future Improvements

* Multi-stage resolution pipelines
* Conversation memory (history utilization)
* Active uncertainty estimation
* Adaptive task generation
* Multi-agent coordination

---

## 🧠 Big Picture

This environment models:

> **Decision-making under uncertainty with partial information**

It is suitable for:

* RL agent training
* LLM agent evaluation
* benchmarking reasoning systems

---

## 👤 Author

Built as part of an advanced OpenEnv submission focused on real-world agent intelligence and evaluation.

---
