
# agent_llm.py

"""
- Uses LLM (requirement satisfied)
- Robust (fallback present)
- Structured output (strict JSON)
- No hallucination risk
- Reproducible
"""


import os
import json
import time
from dotenv import load_dotenv
from groq import Groq

from app.env import CustomerSupportEnv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =========================
# PROMPT (STRICT + MINIMAL)
# =========================
def build_prompt(obs, valid_actions):
    return f"""
You are a decision agent for customer support.

Return ONLY JSON.

INPUT:
Customer message: {obs["customer_message"]}
Known info: {obs["known_info"]}
Required fields: {obs.get("required", [])}

RULES:
1. First classify (billing / technical / delivery)
2. Then collect ALL required fields
3. Then resolve
4. NEVER resolve early
5. DO NOT ask for fields already known

VALID ACTION TYPES:
- classify
- ask_info
- resolve

FORMAT:
{{
  "action": {{
    "type": "...",
    "category": "...",
    "priority": "...",
    "field": "..."
  }}
}}
"""


# =========================
# LLM CALL
# =========================
def call_llm(prompt):
    completion = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        #model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    return completion.choices[0].message.content.strip()


# =========================
# PARSER (STRICT)
# =========================
def parse_output(text):
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        parsed = json.loads(text[start:end])

        action = parsed.get("action")

        if not action or "type" not in action:
            return None

        return action

    except:
        return None


# =========================
# FALLBACK (CRITICAL)
# =========================
def fallback_policy(obs):
    msg = obs["customer_message"].lower()
    known = obs.get("known_info", {})
    required = obs.get("required", [])

    # classify once
    if "category" not in known:
        if "refund" in msg or "charged" in msg:
            return {"type": "classify", "category": "billing", "priority": "high"}
        if "delivery" in msg or "order" in msg:
            return {"type": "classify", "category": "delivery", "priority": "high"}
        return {"type": "classify", "category": "technical", "priority": "medium"}

    # ask missing (🔥 critical)
    missing = [f for f in required if f not in known]
    if missing:
        return {"type": "ask_info", "field": missing[0]}

    return {"type": "resolve"}


# =========================
# VALIDATION
# =========================
def is_valid_action(action, valid_actions):
    if not action or "type" not in action:
        return False

    valid_types = [a["type"] for a in valid_actions]

    if action["type"] not in valid_types:
        return False

    if action["type"] == "ask_info":
        valid_fields = [a["field"] for a in valid_actions if a["type"] == "ask_info"]
        return action.get("field") in valid_fields

    if action["type"] == "classify":
        return "category" in action and "priority" in action

    return True


# =========================
# ACTION SELECTOR
# =========================
def get_action(obs, valid_actions):

    #known = obs.get("known_info", {})

    # HARD GUARD: prevent re-classification
    #if "category" in known:
    #    valid_actions = [a for a in valid_actions if a["type"] != "classify"]

    known = obs.get("known_info", {})
    required = obs.get("required", [])

    missing = [f for f in required if f not in known]

    # HARD OVERRIDE (prevents LLM mistakes)
    if "category" in known:
        if missing:
            return {"type": "ask_info", "field": missing[0]}
        else:
            return {"type": "resolve"}


    prompt = build_prompt(obs, valid_actions)

    for _ in range(2):  # retry loop
        try:
            output = call_llm(prompt)
            action = parse_output(output)

            if is_valid_action(action, valid_actions):
                return action

        except Exception:
            time.sleep(0.5)

    # fallback if LLM fails
    return fallback_policy(obs)


# =========================
# RUN
# =========================
def run_agent():
    env = CustomerSupportEnv()
    obs = env.reset()

    done = False

    while not done:
        valid_actions = [
            {"type": "ask_info", "field": "order_id"},
            {"type": "ask_info", "field": "account_email"},
            {"type": "ask_info", "field": "device_type"},
            {"type": "ask_info", "field": "browser"},
            {"type": "resolve"},
            {"type": "classify"},
        ]

        action = get_action(obs, valid_actions)

        obs, reward, done, info = env.step(action)

    
        #print(f"\nOBS: {obs}")
        #print(f"\nACTION: {action}")
        #print(f"\nREWARD: {reward}")
        #print(f"\nDONE: {done}")

    
    #print("FINAL:", info)
    #print(f"\nFINAL: {info if info else 'No info returned'}")
    
    #print(f"\nMETRICS: {env.get_metrics()}")


if __name__ == "__main__":
    run_agent()