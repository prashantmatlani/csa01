

# app/dataset.py

TICKETS = [

    # Billing Issues
    {
        "ticket_id": "T1",
        "customer_message": "I was charged twice for my order #1234. Please refund.",
        "category": "billing",
        "priority": "high",
        "required_info": ["order_id"]
    },
    {
        "ticket_id": "T2",
        "customer_message": "I want to cancel my subscription and get a refund.",
        "category": "billing",
        "priority": "medium",
        "required_info": ["account_email"]
    },
    {
        "ticket_id": "T3",
        "customer_message": "Why was I billed after cancelling my plan?",
        "category": "billing",
        "priority": "high",
        "required_info": ["account_email"]
    },
    {
        "ticket_id": "T20",
        "customer_message": "I was charged twice and want a refund.",
        "category": "billing",
        "priority": "high",
        "required_info": ["order_id", "account_email"]
    },

    # Technical Issues
    {
        "ticket_id": "T4",
        "customer_message": "I can't log into my account. It says invalid credentials.",
        "category": "technical",
        "priority": "high",
        "required_info": ["account_email"]
    },
    {
        "ticket_id": "T5",
        "customer_message": "The app crashes every time I upload a file.",
        "category": "technical",
        "priority": "medium",
        "required_info": ["device_type"]
    },
    {
        "ticket_id": "T6",
        "customer_message": "Page not loading on checkout.",
        "category": "technical",
        "priority": "high",
        "required_info": ["browser"]
    },
    {
        "ticket_id": "T21",
        "customer_message": "App crashes when I try to checkout.",
        "category": "technical",
        "priority": "high",
        "required_info": ["device_type", "browser"]
    },
    {
        "ticket_id": "T12",
        "customer_message": "App is very slow lately.",
        "category": "technical",
        "priority": "low",
        "required_info": ["device_type"]
    },

    # Account Issues
    {
        "ticket_id": "T7",
        "customer_message": "I forgot my password and can't reset it.",
        "category": "account",
        "priority": "medium",
        "required_info": ["account_email"]
    },
    {
        "ticket_id": "T8",
        "customer_message": "My account got locked for no reason.",
        "category": "account",
        "priority": "high",
        "required_info": ["account_email"]
    },
    {
        "ticket_id": "T9",
        "customer_message": "How do I change my registered email address?",
        "category": "account",
        "priority": "low",
        "required_info": ["account_email"]
    },

    # Edge Cases
    {
        "ticket_id": "T10",
        "customer_message": "Something is wrong with my account.",
        "category": "other",
        "priority": "medium",
        "required_info": ["account_email"]
    },
    {
        "ticket_id": "T11",
        "customer_message": "I didn't receive my order but it shows delivered.",
        "category": "other",
        "priority": "high",
        "required_info": ["order_id"]
    }
    

    ]