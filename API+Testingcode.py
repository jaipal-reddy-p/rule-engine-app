from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import json
import pytest

app = Flask(__name__)

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/')
db = client['rule_engine_db']
rules_collection = db['rules']

# Node class for AST representation
class Node:
    def __init__(self, node_type, value=None, left=None, right=None):
        self.node_type = node_type
        self.value = value
        self.left = left
        self.right = right

    def to_dict(self):
        return {"node_type": self.node_type, "value": self.value, 
                "left": self.left.to_dict() if self.left else None, 
                "right": self.right.to_dict() if self.right else None}

# Function to parse a rule string into an AST
def create_ast_from_rule(rule_string):
    tokens = rule_string.split()
    if len(tokens) < 7:
        raise ValueError("Invalid rule format")
    left_operand = Node(node_type='operand', value=f"{tokens[0]} {tokens[1]} {tokens[2]}")
    operator = tokens[3].upper()
    right_operand = Node(node_type='operand', value=f"{tokens[4]} {tokens[5]} {tokens[6]}")
    root = Node(node_type='operator', value=operator, left=left_operand, right=right_operand)
    return root

# Function to evaluate a rule's AST against user data
def evaluate_ast(ast, data):
    if ast['node_type'] == 'operand':
        return eval_condition(ast['value'], data)
    if ast['node_type'] == 'operator':
        left_result = evaluate_ast(ast['left'], data)
        right_result = evaluate_ast(ast['right'], data)
        if ast['value'] == 'AND':
            return left_result and right_result
        elif ast['value'] == 'OR':
            return left_result or right_result

# Helper function to evaluate a condition
def eval_condition(condition, data):
    field, operator, value = condition.split()
    if field in data and isinstance(data[field], (int, float)):
        return (data[field] > int(value)) if operator == '>' else (data[field] < int(value))
    elif field in data and isinstance(data[field], str):
        return data[field] == value.strip("'")
    return False

# API Endpoint 1: Create Rule
@app.route('/create_rule', methods=['POST'])
def create_rule():
    data = request.json
    rule_string = data.get('rule_string')
    
    try:
        # Create AST from the rule string
        ast = create_ast_from_rule(rule_string)
        ast_dict = ast.to_dict()
    
        # Store rule in MongoDB
        rule_document = {
            "rule_string": rule_string,
            "rule_ast": ast_dict,
            "created_at": datetime.utcnow()
        }
        result = rules_collection.insert_one(rule_document)
        return jsonify({"message": "Rule created", "rule_id": str(result.inserted_id)})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# API Endpoint 2: Combine Rules
@app.route('/combine_rules', methods=['POST'])
def combine_rules():
    data = request.json
    rule_ids = data.get('rule_ids')
    
    # Retrieve and combine the ASTs of the specified rules
    asts = []
    for rule_id in rule_ids:
        rule = rules_collection.find_one({"_id": rule_id})
        if rule:
            asts.append(rule['rule_ast'])
    
    if not asts:
        return jsonify({"error": "No valid rules found to combine"}), 404
    
    # Simple combine logic: We'll just AND them together
    combined_ast = asts[0]
    for ast in asts[1:]:
        combined_ast = {
            "node_type": "AND",
            "left": combined_ast,
            "right": ast
        }
    
    # Store the combined rule
    combined_rule_document = {
        "rule_string": "Combined Rule",
        "rule_ast": combined_ast,
        "created_at": datetime.utcnow()
    }
    result = rules_collection.insert_one(combined_rule_document)
    return jsonify({"message": "Combined rule created", "rule_id": str(result.inserted_id)})

# API Endpoint 3: Evaluate Rule
@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule():
    data = request.json
    rule_id = data.get('rule_id')
    user_data = data.get('user_data')
    
    # Retrieve the rule by ID
    rule = rules_collection.find_one({"_id": rule_id})
    if not rule:
        return jsonify({"error": "Rule not found"}), 404
    
    # Evaluate the rule's AST against the user data
    ast = rule['rule_ast']
    result = evaluate_ast(ast, user_data)
    return jsonify({"result": result})

# Test cases using pytest
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Test Case 1: Create Rule and Verify AST
def test_create_rule(client):
    rule_string = "age > 30 AND department = 'Sales'"
    
    # Make API request to create the rule
    response = client.post('/create_rule', json={"rule_string": rule_string})
    assert response.status_code == 200
    
    rule_id = response.json['rule_id']
    
    # Retrieve the stored rule from the database
    stored_rule = rules_collection.find_one({"_id": rule_id})
    
    # Check if the AST is correctly generated
    expected_ast = {
        "node_type": "AND",
        "left": {"node_type": "operand", "value": "age > 30"},
        "right": {"node_type": "operand", "value": "department = 'Sales'"}
    }
    assert stored_rule['rule_ast'] == expected_ast
    print("Test Case 1 Passed: Rule Created and AST Verified")

# Test Case 2: Combine Rules
def test_combine_rules(client):
    # Create two rules
    rule1 = client.post('/create_rule', json={"rule_string": "age > 30 AND department = 'Sales'"}).json['rule_id']
    rule2 = client.post('/create_rule', json={"rule_string": "experience > 5 OR salary > 50000"}).json['rule_id']
    
    # Combine the rules
    response = client.post('/combine_rules', json={"rule_ids": [rule1, rule2]})
    assert response.status_code == 200
    
    combined_rule_id = response.json['rule_id']
    
    # Retrieve and check the combined rule
    combined_rule = rules_collection.find_one({"_id": combined_rule_id})
    
    # Verify the combined AST structure
    expected_combined_ast = {
        "node_type": "AND",
        "left": {
            "node_type": "AND",
            "left": {"node_type": "operand", "value": "age > 30"},
            "right": {"node_type": "operand", "value": "department = 'Sales'"}
        },
        "right": {
            "node_type": "OR",
            "left": {"node_type": "operand", "value": "experience > 5"},
            "right": {"node_type": "operand", "value": "salary > 50000"}
        }
    }
    assert combined_rule['rule_ast'] == expected_combined_ast
    print("Test Case 2 Passed: Rules Combined and AST Verified")

# Test Case 3: Evaluate Rule
def test_evaluate_rule(client):
    # Create a rule
    rule_id = client.post('/create_rule', json={"rule_string": "age > 30 AND department = 'Sales'"}).json['rule_id']
    
    # Evaluate the rule against user data
    user_data = {"age": 35, "department": "Sales"}
    response = client.post('/evaluate_rule', json={"rule_id": rule_id, "user_data": user_data})
    
    # Check if the result is True
    assert response.status_code == 200
    assert response.json['result'] == True
    print("Test Case 3 Passed: Rule Evaluated and Returned Correct Result")

# Test Case 4: Invalid Rule Handling
def test_invalid_rule(client):
    # Attempt to create an invalid rule
    response = client.post('/create_rule', json={"rule_string": "age >"})
    
    # Check if the system handles the invalid rule
    assert response.status_code == 400
    assert "error" in response.json
    print("Test Case 4 Passed: Invalid Rule Handled Correctly")

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
