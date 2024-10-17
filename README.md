# Rule Engine
# Rule Engine with AST

## Overview
This is a Rule Engine application that uses an Abstract Syntax Tree (AST) to represent conditional rules. It allows dynamic creation, combination, and evaluation of rules based on user attributes like age, department, income, and spend.

## Features
- Define rules using a string representation.
- Combine multiple rules into a single rule.
- Evaluate rules against user data.
- Supports AND/OR operators and operand comparisons.

## Technologies Used
- Python
- MongoDB (for rule storage)
- Flask (for API)

## Getting Started

### Prerequisites
- Python 3.x installed
- MongoDB installed and running locally
- Install required Python packages:
  ```bash
  pip install -r requirements.txt

#Repository Setup
1. Clone the GitHub repository:
git clone https://github.com/jaipal-reddy-p/rule-engine-app.git
cd rule-engine-app
2. Initialize the Git repository:
git init
git remote add origin https://github.com/jaipal-reddy-p/rule-engine-app.git

#How to Run the Application
1. Start the Flask API:
python rule_engine_api.py

2. You can now interact with the API through POST requests to:
Create Rule: /create_rule
Combine Rules: /combine_rules
Evaluate Rule: /evaluate_rule

3. Use tools like Postman to test the API.

#Example API Requests
1. Create Rule
POST /create_rule
{
  "rule_string": "age > 30 AND department = 'Sales'"
}

2. Combine Rules
POST /combine_rules
{
  "rule_ids": ["rule_id_1", "rule_id_2"]
}

3. Evaluate Rule
POST /evaluate_rule
{
  "rule_id": "rule_id_1",
  "user_data": {
    "age": 35,
    "department": "Sales"
  }
}


#Testing
1.Unit tests are located in the tests/ directory.
2.Run the tests:
python -m unittest discover -s tests
3.Non-Functional Aspects
Security: Use API authentication (e.g., JWT) to secure the endpoints.
Performance: Ensure MongoDB indexing on rule data to improve query performance.
Error Handling: Handles invalid rule strings, missing attributes, and malformed requests.
