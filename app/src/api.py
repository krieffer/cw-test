from datetime import datetime, timedelta
from fastapi import FastAPI
import joblib
import pandas as pd
from pathlib import Path

with open(__file__, "rb") as f:
    first = f.readline()
print("First line bytes:", first)


app = FastAPI()

# Determine the path to this source file:
HERE = Path(__file__).resolve().parent

# Construct the full path to fraud_model.pkl inside the same folder:
MODEL_PATH = HERE / "fraud_model.pkl"

# Load machine-learning pre‑trained model
model = joblib.load(MODEL_PATH)

# Example in‑memory store of recent transactions for velocity calculation
# In prod use a time‑series database or cache (Redis, etc.)
RECENT_TXNS = []


def compute_velocity(txn: dict, window_minutes: int = 10) -> int:
    """
    Count how many transactions from this user_id occurred in the past `window_minutes`.
    For demo, uses RECENT_TXNS list of (timestamp, user_id).
    """
    now = datetime.fromisoformat(txn["transaction_time"])
    # Purge old entries
    cutoff = now - timedelta(minutes=window_minutes)
    global RECENT_TXNS
    RECENT_TXNS = [(ts, uid) for ts, uid in RECENT_TXNS if ts >= cutoff]
    # Count recent by same user
    count = sum(1 for ts, uid in RECENT_TXNS if uid == txn["user_id"])
    # Add current txn to store
    RECENT_TXNS.append((now, txn["user_id"]))
    return count


def compute_amount_bin(amount: float, bin_size: float = 100.0) -> str:
    """
    Place `amount` into a text bin, e.g. "0-100", "100-200", etc.
    """
    lower = (amount // bin_size) * bin_size
    upper = lower + bin_size
    return f"{int(lower)}-{int(upper)}"


# Example business rule: more than 3 small txns in 10 minutes
def rule_velocity(features: pd.Series) -> bool:
    return features["velocity_10min"] > 3


rules = [rule_velocity]


@app.post("/score")
def score_transaction(txn: dict):
    # 1) Feature extraction
    features = pd.DataFrame([txn]).iloc[0]
    features["velocity_10min"] = compute_velocity(txn)
    features["amount_bin"] = compute_amount_bin(txn["transaction_amount"])

    # 2) Rules scoring
    rule_flags = [int(rule(features)) for rule in rules]
    score_rules = sum(rule_flags) / len(rules)

    # 3) ML scoring
    df_single = pd.DataFrame([txn])
    score_ml = model.predict_proba(df_single)[:, 1][0]

    # 4) Combined risk score
    risk_score = 0.5 * score_rules + 0.5 * score_ml

    # 5) Decision logic
    if risk_score >= 0.8:
        action = "decline"
    elif risk_score >= 0.5:
        action = "step_up"
    else:
        action = "approve"

    return {
        "risk_score": round(risk_score, 3),
        "action": action,
        "features": {
            "velocity_10min": features["velocity_10min"],
            "amount_bin": features["amount_bin"],
        }
    }
