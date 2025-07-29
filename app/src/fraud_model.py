from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
import pandas as pd
import joblib

# 1. Load your labeled dataset
df = pd.read_csv("transactional-sample.csv")

# 2. Feature engineering (example)
df["velocity_10min"] = ...       # compute per user/device
df["amount_bin"]     = ...       # map amounts to numeric bins
# Convert chargeback bool to 0/1
df["is_cbk"] = df["has_cbk"].astype(int)

# 3. Select features and label
feature_cols = ["velocity_10min", "transaction_amount"]  # plus any other engineered features
X = df[feature_cols]
y = df["is_cbk"]

# 4. Split into train/test
X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                    test_size=0.2,
                                                    random_state=42,
                                                    stratify=y)

# 5. Train model
model = XGBClassifier(use_label_encoder=False, eval_metric="logloss")
model.fit(X_train, y_train)

# 6. Evaluate (optional)
print("Test accuracy:", model.score(X_test, y_test))

# 7. Serialize to disk
joblib.dump(model, "fraud_model.pkl")
print("Saved model to fraud_model.pkl")
