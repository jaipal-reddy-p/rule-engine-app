from pymongo import MongoClient
from datetime import datetime
import json

# MongoDB connection setup
# Replace <connection_string> with your MongoDB connection string
client = MongoClient('mongodb://localhost:27017/')  # Local MongoDB
# client = MongoClient('<connection_string>')  # Uncomment this line for MongoDB Atlas

# Define the database and collection
db = client['rule_engine_db']  # Database name
rules_collection = db['rules']  # Collection name

# Node class for AST representation
class Node:
    def __init__(self, node_type, value=None, left=None, right=None):
        self.node_type = node_type  # 'operator' or 'operand'
        self.value = value          # The condition for operands, e.g., "age > 30"
        self.left = left            # Left child for operators
        self.right = right          # Right child for operators
    
    def __repr__(self):
        return f"Node({self.node_type}, {self.value}, {self.left}, {self.right})"

# Function to store a rule in the database
def store_rule(rule_string, rule_ast):
    rule_document = {
        "rule_string": rule_string,
        "rule_ast": json.loads(json.dumps(rule_ast, default=lambda o: o.__dict__)),  # Convert AST to JSON
        "created_at": datetime.utcnow()
    }
    
    result = rules_collection.insert_one(rule_document)
    return result.inserted_id

# Function to retrieve a rule by its ID
def get_rule(rule_id):
    rule = rules_collection.find_one({"_id": rule_id})
    return rule

# Function to manually create a sample AST
def create_sample_ast():
    left_operand = Node(node_type='operand', value="age > 30")
    right_operand = Node(node_type='operand', value="department = 'Sales'")
    root = Node(node_type='operator', value='AND', left=left_operand, right=right_operand)
    return root

# Main function to demonstrate storing and retrieving rules
if __name__ == "__main__":
    # Example rule as a string
    rule_string = "age > 30 AND department = 'Sales'"
    
    # Simulating AST creation (as in Step 1)
    ast = create_sample_ast()

    # Store the rule and get the inserted ID
    rule_id = store_rule(rule_string, ast)
    print(f"Rule stored with ID: {rule_id}")

    # Retrieve and print the stored rule
    retrieved_rule = get_rule(rule_id)
    print("Retrieved Rule:", retrieved_rule)
