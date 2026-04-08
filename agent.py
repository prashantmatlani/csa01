
# agent.py

import sys
from unicodedata import category
import requests
import os
import time
import json
import random

from dotenv import load_dotenv
# from openai import OpenAI
from groq import Groq

from app.env import CustomerSupportEnv

# load_dotenv()

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# BASE_URL = "http://127.0.0.1:8001"
#load_dotenv("/home/pb/projects/openenv-customer-support/.env")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)
print(f"\nCWD: {os.getcwd()}")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
#client = os.getenv("GROQ_API_KEY")

#print(f"\nENV PATH: {ENV_PATH}")
#print(f"\ngroq api key: {client}")
##print(f"\ngroq api key: {os.getenv('GROQ_API_KEY')}")
##print("KEY:", os.getenv("GROQ_API_KEY"))
#print(f"\nmodel name: {os.getenv('MODEL_NAME')}")

print("Sending request...")

#sys.exit()

# =========================
# Smarter, mapped ask_info - boosts info_progress speed, reward per episode
# =========================
def pick_field(category, known):
    if category == "billing":
        return "order_id"

    if category == "technical":
        return "account_email"

    if category == "delivery":
        return "order_id"

    return "account_email"

# =========================
# CLASSIFIER TO REDUCE LLM RELIANCE
# =========================
def smart_classify(message):
    msg = message.lower()

    if any(x in msg for x in ["refund", "cancel", "subscription", "charge"]):
        return {"category": "billing", "priority": "high"}

    if any(x in msg for x in ["crash", "bug", "error", "slow"]):
        return {"category": "technical", "priority": "high"}

    return {"category": "general", "priority": "medium"}


def override_classify(message):
    msg = message.lower()

    if any(x in msg for x in ["charged", "refund", "billing", "cancel", "subscription"]):
        return {"type": "classify", "category": "billing", "priority": "high"}

    if any(x in msg for x in ["checkout", "crash", "bug", "error", "not loading", "login"]):
        return {"type": "classify", "category": "technical", "priority": "high"}

    if any(x in msg for x in ["delivery", "order not arrived", "shipping"]):
        return {"type": "classify", "category": "delivery", "priority": "medium"}

    return {"type": "classify", "category": "general", "priority": "medium"}



def is_ready_to_resolve(category, known):
    if category == "billing":
        return "order_id" in known

    if category == "technical":
        return "account_email" in known

    if category == "delivery":
        return "order_id" in known

    return False

# =========================
# POLICY ENFORCEMENT INTEAD OF LLM DECISION
# =========================
def enforce_policy(obs, action):
    known = obs["known_info"]
    category = known.get("category")

    # Never re-classify
    if action["type"] == "classify" and category:
        return {"type": "ask_info", "field": pick_field(category, known)}

    # Force correct ask_info
    if action["type"] == "ask_info":
        action["field"] = pick_field(category, known)
    
    # if already asked → resolve instead of repeating
    if action["type"] == "ask_info":
        if action["field"] in known:
            return {"type": "resolve"}

    # Only resolve when ready
    if action["type"] == "resolve":
        if not is_ready_to_resolve(category, known):
            return {"type": "ask_info", "field": pick_field(category, known)}

    return action

# =========================
# PROMPT
# =========================

def build_prompt(obs, valid_actions):
    return f"""
You are a customer support decision agent.

Return ONLY valid JSON.

IMPORTANT DECISION RULES:

1. DO NOT ask for unnecessary information
2. If the issue is clear (e.g., password reset, login failure), resolve directly
3. Only ask for information that is REQUIRED to solve the issue
4. NEVER ask for order_id in login/password issues
5. If sufficient information is already available, choose "resolve"
6. Avoid repeating the same question

Customer message:
{obs["customer_message"]}

Known info:
{obs["known_info"]}

Progress:
{obs["info_progress"]}

VALID ACTIONS:
{valid_actions}

RULES:
- ONLY pick from VALID ACTIONS
- "charged", "refund" → billing
- "slow", "crash" → technical
- Do NOT hallucinate

CRITICAL DECISION RULE:

Only choose "resolve" IF:
1. You have correctly classified the issue
2. You have collected ALL required fields
3. You are confident you can solve the user's problem

If ANY doubt remains → ask_info

NEVER resolve early.

CLASSIFICATION RULES (STRICT):

You MUST classify into ONLY ONE of:
- billing
- technical
- delivery

NEVER output "general" or any other category.

---

BILLING:
charged, refund, payment, invoice, subscription, billing issues

TECHNICAL:
login issues, account problems, crashes, errors, bugs, slow performance, app issues

IMPORTANT:
ANY issue related to app behavior (slow, crash, not working, locked account)
→ ALWAYS technical

---

DELIVERY:
shipping, delivery delay, order not received

---

PRIORITY RULE:
If message involves money → billing (even if order mentioned)

Example:
"I was charged twice for my order"
→ billing

FORMAT:
{{
  "thought": "...",
  "action": {{ ... }}
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
# PARSER (MANDATORY)
# =========================

def parse_output(text):
    try:
        if "```" in text:
            text = text.split("```")[1]

        start = text.find("{")
        end = text.rfind("}") + 1
        text = text[start:end]

        parsed = json.loads(text)

        action = parsed.get("action")

        if not action or "type" not in action:
            raise ValueError("Invalid action format")

        return action

    except Exception as e:
        print("❌ PARSE ERROR:", e)
        print("RAW:", text)
        return None

# =========================
# VALIDATION
# =========================

def is_valid_action(action, valid_actions):
    if not action or "type" not in action:
        return False

    action_type = action["type"]

    # ✅ check type exists
    valid_types = [a["type"] for a in valid_actions]
    if action_type not in valid_types:
        return False

    # ✅ ask_info must match field
    if action_type == "ask_info":
        valid_fields = [a["field"] for a in valid_actions if a["type"] == "ask_info"]
        return action.get("field") in valid_fields

    # ✅ classify must have required keys (NOT exact match)
    if action_type == "classify":
        return "category" in action and "priority" in action
    
    # resolve always valid
    return True

# =========================
# VALID ACTION SPACE
# =========================

def get_valid_actions():
    actions = [
        {"type": "ask_info", "field": "order_id"},
        {"type": "ask_info", "field": "account_email"},
        {"type": "ask_info", "field": "device_type"},
        {"type": "ask_info", "field": "browser"},
        {"type": "resolve"},
    ]

    # ✅ allow flexible classification
    actions.append({"type": "classify"})

    return actions

# =========================
# ACTION PIPELINE
# =========================
def get_action(obs):
    msg = obs["customer_message"].lower()

    # ✅ NEW: use env-provided structure
    known = obs.get("known_info", {})
    required = obs.get("required", [])

    # =====================
    # 1. CLASSIFY (only once)
    # =====================
    if "category" not in known:

        if any(x in msg for x in [
            "charged", "refund", "billed", "payment", "invoice", "cancel"
        ]):
            return {"type": "classify", "category": "billing", "priority": "high"}

        if any(x in msg for x in [
            "delivery", "delivered", "not received", "shipment", "order"
        ]):
            return {"type": "classify", "category": "delivery", "priority": "high"}

        if any(x in msg for x in [
            "login", "password", "error", "crash", "bug", "checkout"
        ]):
            return {"type": "classify", "category": "technical", "priority": "high"}

        return {"type": "classify", "category": "technical", "priority": "medium"}

    # =====================
    # 2. COMPUTE MISSING INFO (🔥 KEY CHANGE)
    # =====================
    missing = [f for f in required if f not in known]

    # =====================
    # 3. ASK FOR NEXT FIELD
    # =====================
    if missing:
        return {"type": "ask_info", "field": missing[0]}

    # =====================
    # 4. RESOLVE
    # =====================
    return {"type": "resolve"}


# =========================
# RUN
# =========================
def run_agent():

    print("🚀 Starting agent...")
    env = CustomerSupportEnv()
    obs = env.reset()

    done = False
    trajectory = []

    while not done:
        print("\n📥 OBS:", obs)

        action = get_action(obs)
        print("🧠 ACTION:", action)

        next_obs, reward, done, info = env.step(action)

        print("🎯 REWARD:", reward)
        print("✅ DONE:", done)

        trajectory.append({
            "state": obs,
            "action": action,
            "reward": reward
        })

        obs = next_obs

        print("OBS:", obs)
        print("ACTION:", action)
        print("REWARD:", reward)
        print("DONE:", done)

    #print("\n🏁 FINAL INFO:", info)
    print("FINAL:", info if info else "No info returned")


    return {
        "final_score": info.get("final_score", 0),
        "trajectory": trajectory
    }


def run_multiple(n=3):
    scores = []

    for i in range(n):
        print(f"\n===== EPISODE {i+1} =====")
        result = run_agent()
        scores.append(result["final_score"])

    avg = sum(scores) / len(scores)
    print("\n📊 AVERAGE SCORE:", avg)


if __name__ == "__main__":
    run_multiple(3)