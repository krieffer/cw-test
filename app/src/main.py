from pathlib import Path

import pandas as pd
from fastapi import FastAPI

app = FastAPI()

# Paths
HERE = Path(__file__).resolve().parent  # app/src
PROJECT_ROOT = HERE.parent  # app
DATA_CSV = PROJECT_ROOT / "data" / "transactional-sample.csv"

# Load and preprocess
df_all = pd.read_csv(DATA_CSV)
df_all["transaction_date"] = pd.to_datetime(df_all["transaction_date"])


# Rule: more than 3 transactions by the same user in 10 minutes
def rule_velocity(txn: dict) -> bool:
    now = pd.to_datetime(txn["transaction_date"])
    cutoff = now - pd.Timedelta(minutes=10)
    mask = (
            (df_all["user_id"] == txn["user_id"]) &
            (df_all["transaction_date"] >= cutoff) &
            (df_all["transaction_date"] < now)
    )
    return bool(mask.sum() > 3)


# Rule: more than 2 low-value transactions (<R$10) on same device in 10 minutes
def rule_low_value_tests(txn: dict) -> bool:
    now = pd.to_datetime(txn["transaction_date"])
    cutoff = now - pd.Timedelta(minutes=10)
    mask = (
            (df_all["device_id"] == txn["device_id"]) &
            (df_all["transaction_date"] >= cutoff) &
            (df_all["transaction_date"] < now) &
            (df_all["transaction_amount"] < 10)
    )
    return bool(mask.sum() > 2)


rules = [rule_velocity, rule_low_value_tests]


@app.post("/score")
def score_transaction(txn: dict):
    # Normalize timestamp key
    txn_time = txn.get("transaction_date") or txn.get("transaction_time")
    txn = {**txn, "transaction_date": txn_time}

    # Evaluate rules
    flags = {f"rule_{i + 1}": rule(txn) for i, rule in enumerate(rules)}
    is_suspicious = any(flags.values())

    action = "hold_for_review" if is_suspicious else "approve"

    return {
        "action": action,
        "rule_flags": flags
    }
