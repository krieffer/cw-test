# Transaction Fraud Detection API

A FastAPI-based fraud detection system that analyzes financial transactions in real-time using rule-based scoring to identify potentially suspicious activities.

## Overview

This system implements a transaction scoring API that evaluates incoming transactions against predefined fraud detection rules. It uses historical transaction data to identify patterns that may indicate fraudulent behavior.

## Features

- **Real-time Transaction Scoring**: Evaluate transactions as they occur
- **Rule-based Fraud Detection**: Multiple configurable fraud detection rules
- **RESTful API**: Simple HTTP POST endpoint for transaction evaluation
- **Automated Decision-Making**: Returns actionable recommendations (approve/hold_for_review)

## Fraud Detection Rules

The system currently implements two fraud detection rules:

### Rule 1: Velocity Check
Flags transactions when a user makes more than 3 transactions within a 10-minute window.

### Rule 2: Low-Value Device Testing
Flags transactions when more than 2 low-value transactions (< R$10) occur on the same device within a 10-minute window.

## Data Structure

The system expects transaction data with the following fields:

| Field                | Type     | Description                          |
|----------------------|----------|--------------------------------------|
| `transaction_id`     | string   | Unique transaction identifier        |
| `merchant_id`        | string   | Merchant identifier                  |
| `user_id`            | string   | User identifier                      |
| `card_number`        | string   | Masked card number                   |
| `transaction_date`   | datetime | Transaction timestamp                |
| `transaction_amount` | float    | Transaction amount in local currency |
| `device_id`          | string   | Device identifier (optional)         |
| `has_cbk`            | boolean  | Chargeback indicator                 |

## Installation

1. Clone the repository:
```bash
git clone https://github.com/krieffer/cw-test.git
cd cw-test
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure your data file is in the correct location:
```
app/data/transactional-sample.csv
```

## Usage

### Starting the API Server

```bash
uvicorn app.src.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit `http://localhost:8000/docs` for interactive API documentation.

### Scoring a Transaction

**Endpoint:** `POST /score`

**Request Body:**
```json
{
  "user_id": "81152",
  "device_id": "486",
  "transaction_date": "2019-12-01T21:25:00.000000",
  "transaction_amount": 25.50,
  "merchant_id": "56107",
  "card_number": "650516******9201"
}
```

**Response:**
```json
{
  "action": "hold_for_review",
  "rule_flags": {
    "rule_1": true,
    "rule_2": false
  }
}
```

## Example Usage with Sample Data

Based on the sample data in `app/data/transactional-sample.csv`, here are some example scenarios:

### Example 1: High Velocity User (Rule 1 Trigger)

User `75710` has multiple transactions in a short time window:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/score" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{
    "transaction_date": "2019-11-08T23:15:00",
    "user_id": 75710,
    "device_id": 99999,
    "transaction_amount": 100.00
  }'
```

**Expected Response:**
```json
{
  "action": "hold_for_review",
  "rule_flags": {
    "rule_1": true,
    "rule_2": false
  }
}
```

### Example 2: Low-Value Testing Pattern (Rule 2 Trigger)

Multiple small transactions on the same device (device 589318 already has low-value transactions in the historical data):

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/score" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{
    "transaction_date": "2019-12-01T11:05:00",
    "user_id": 77959,
    "device_id": 589318,
    "transaction_amount": 5.00
  }'
```

**Expected Response:**
```json
{
  "action": "hold_for_review",
  "rule_flags": {
    "rule_1": false,
    "rule_2": true
  }
}
```

### Example 3: Normal Transaction (No Rules Triggered)

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/score" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{
    "user_id": "new_user",
    "device_id": "new_device",
    "transaction_date": "2019-12-01T21:25:00.000000",
    "transaction_amount": 150.00
  }'
```

**Expected Response:**
```json
{
  "action": "approve",
  "rule_flags": {
    "rule_1": false,
    "rule_2": false
  }
}
```

## Response Format

The API returns a JSON object with:

- `action`: Either "approve" or "hold_for_review"
- `rule_flags`: Object showing which rules were triggered
  - `rule_1`: Velocity check result (boolean)
  - `rule_2`: Low-value testing check result (boolean)

## Data Analysis

The sample dataset contains 1000 transactions with the following characteristics:

- **Date Range**: November 28-29 and December 1, 2019
- **Transaction Amounts**: Range from R$3.33 to R$4,043.09
- **Users**: Multiple unique users with varying transaction patterns
- **Devices**: Some transactions include device information
- **Chargeback Rate**: Approximately 15% of transactions have chargebacks

## Architecture

```
app/
├── src/
│   └── main.py          # FastAPI application and fraud rules
└── data/
    └── transactional-sample.csv  # Historical transaction data
```

## Adding New Rules

To add new fraud detection rules:

1. Create a new function following the pattern:
```python
def rule_new_check(txn: dict) -> bool:
    # Your rule logic here
    return boolean_result
```

2. Add the function to the `rules` list:
```python
rules = [rule_velocity, rule_low_value_tests, rule_new_check]
```

## Dependencies

- **FastAPI**: Web framework for building APIs
- **Pandas**: Data manipulation and analysis
- **Python 3.7+**: Required Python version

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your fraud detection rules
4. Test with sample data
5. Submit a pull request

## License

This project is licensed under the MIT License.
