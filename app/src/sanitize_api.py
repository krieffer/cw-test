from pathlib import Path

# Adjust path if needed
file_path = Path("fraud_model.pkl")

# Read the entire file as text
text = file_path.read_text(encoding="utf-8")

# Remove every carriage return character
fixed = text.replace('\r', '')

# Write the cleaned text back
file_path.write_text(fixed, encoding="utf-8")

print(f"Stripped all CR characters from {file_path}")
