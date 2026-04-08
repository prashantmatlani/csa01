
"""
// Testing, conceptually

Test	            What it verifies
ask_info	    info collection logic
resolve (after)	    success path
resolve (before)	penalty logic
reward values	correctness of shaping
done flag	    termination logic

> Detailed test flow

- ask_info

Conceptually, checks whether agent can reduce uncerainiy by asking the correct question

-- The environment is partially observable — the agent doesn’t know everything upfront --

Real-world analogy:
Support agent asking the client of their email


- resolve (after)

Conceptually, checks:

“Can the agent complete the task after gathering required info?”

This is goal completion

- resolve (before)

Conceptually, checks:

“Does the system penalize shortcut / lazy behavior?”

Without this:
Agent would always jump to resolve

- Reward values

Conceptually, checks:

“Is the agent receiving useful learning signals?”

With the reward-mechanism implemented:

Behavior	           Reward
correct info	        +0.3
correct resolution	    +1.0
final score	        +0.0 → +1.0
wrong action	      negative

 technically, we validate:

reward accumulation works
no random jumps
consistent scaling

This is critical, because:

. Bad reward = bad agent/system
. Good reward = learnable system

- done flag

Conceptually, checks:

“Does the environment know when the episode ends?”

- no score field in /reset, since at reset:

Episode has not happened yet
→ No performance → No score


These tests collectively validate:

MDP (Markov Decision Process) -> (State, Action, Reward, Transition, Termination) -> Thorough RL Environment

Component	    Verified by
State	          reset
Action	    ask_info / resolve
Reward	        reward tests
Transition	    state updates
Termination	    done flag



// Expected behavior

Good Agent Flow:
Reset
→ ask_info (+0.3)
→ resolve (+1.0 + bonus)

Bad Agent Flow:
Reset
→ resolve (-0.3)
→ ask random info (-0.1)
→ timeout (-1.0)







"""

import requests

BASE = "http://127.0.0.1:8001"

# Reset
r = requests.get(f"{BASE}/reset")
print(f"\nRESET: \n\n{r.json()}")


# Ask info
r = requests.post(f"{BASE}/step", json={
    "type": "ask_info",
    "field": "account_email"
})
#print("ASK INFO:", r.json())
print(f"\nASK INFO: \n\n{r.json()}")

# Resolve
r = requests.post(f"{BASE}/step", json={
    "type": "resolve"
})
print(f"\nRESOLVE: \n\n{r.json()}")
#print(f"\n"RESOLVE:", {r.json()})