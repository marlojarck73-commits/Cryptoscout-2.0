"""
Utility helper functions used by main.py
- simulate payments
- small helpers
"""

import logging, os, json
from datetime import datetime

LOGFILE = "cryptoscout.log"

def simulate_payment(user: str, amount_eur: float):
    logging.info(f"[SIM PAYMENT] {user} paid {amount_eur} EUR at {datetime.utcnow().isoformat()}")
    return True

def save_json_safe(path: str, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)
