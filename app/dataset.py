

# app/dataset.py

"""
PURPOSE: Production-grade multi-intent dataset
- Introduces ambiguity (multiple valid interpretations)
- Separates perceived vs true intent
- Supports stochastic + difficulty-aware environments
"""

TICKETS = [

    # =========================
    # 1. BILLING vs DELIVERY
    # =========================
    {
        "ticket_id": "T001",

        "variants": [
            "I was charged but didn’t receive my order",
            "Payment went through but nothing arrived",
            "Got billed but package is missing"
        ],

        "noise": [
            "pls check asap",
            "this is urgent",
            ""
        ],

        # AGENT CONFUSION SPACE
        "possible_categories": ["billing", "delivery"],

        "ground_truth": {
            "category": "delivery",
            "priority": "high",
            "required_info": ["order_id", "account_email"]
        }
    },

    # =========================
    # 2. TECH vs ACCOUNT
    # =========================
    {
        "ticket_id": "T002",

        "variants": [
            "I can’t log into my account",
            "Login keeps failing with error",
            "Account not accessible"
        ],

        "noise": [
            "tried multiple times",
            "not sure what's wrong",
            ""
        ],

        "possible_categories": ["technical", "account"],

        "ground_truth": {
            "category": "account",
            "priority": "medium",
            "required_info": ["account_email", "device_type"]
        }
    },

    # =========================
    # 3. BILLING vs TECH
    # =========================
    {
        "ticket_id": "T003",

        "variants": [
            "I got charged twice for the same order",
            "Duplicate charge happened",
            "Payment processed twice"
        ],

        "noise": [
            "this is frustrating",
            "",
        ],

        "possible_categories": ["billing", "technical"],

        "ground_truth": {
            "category": "billing",
            "priority": "high",
            "required_info": ["order_id", "account_email"]
        }
    },

    # =========================
    # 4. DELIVERY (CLEAR)
    # =========================
    {
        "ticket_id": "T004",

        "variants": [
            "My order hasn’t arrived yet",
            "Delivery is delayed",
            "Still waiting for package"
        ],

        "noise": [
            "been 5 days",
            "",
        ],

        "possible_categories": ["delivery"],

        "ground_truth": {
            "category": "delivery",
            "priority": "medium",
            "required_info": ["order_id"]
        }
    },

    # =========================
    # 5. TECH (AMBIGUOUS UI ISSUE)
    # =========================
    {
        "ticket_id": "T005",

        "variants": [
            "App crashes when I open it",
            "Screen goes blank after launch",
            "Something is wrong with the app"
        ],

        "noise": [
            "happens randomly",
            "",
        ],

        "possible_categories": ["technical"],

        "ground_truth": {
            "category": "technical",
            "priority": "high",
            "required_info": ["device_type", "browser"]
        }
    },

    # =========================
    # 6. ACCOUNT vs BILLING
    # =========================
    {
        "ticket_id": "T006",

        "variants": [
            "My subscription is active but I can’t use features",
            "Paid but features locked",
            "Account says active but not working"
        ],

        "noise": [
            "pls fix",
            "",
        ],

        "possible_categories": ["account", "billing"],

        "ground_truth": {
            "category": "account",
            "priority": "high",
            "required_info": ["account_email"]
        }
    },

    # =========================
    # 7. HARD: MULTI-LAYER ISSUE
    # =========================
    {
        "ticket_id": "T007",

        "variants": [
            "Order delayed and I was charged twice",
            "Late delivery and duplicate payment issue",
            "Package not here and billing looks wrong"
        ],

        "noise": [
            "very frustrating",
            "please resolve quickly",
            ""
        ],

        "possible_categories": ["billing", "delivery"],

        "ground_truth": {
            "category": "billing",  # root cause focus
            "priority": "high",
            "required_info": ["order_id", "account_email"]
        }
    },

    # =========================
    # 8. HARD: VAGUE + NOISY
    # =========================
    {
        "ticket_id": "T008",

        "variants": [
            "Something is wrong with my account",
            "Not working properly",
            "Issue with my profile"
        ],

        "noise": [
            "not sure what exactly",
            "pls help",
            ""
        ],

        "possible_categories": ["technical", "account"],

        "ground_truth": {
            "category": "technical",
            "priority": "medium",
            "required_info": ["device_type"]
        }
    }

]