class Node:
    def __init__(self, node_type, value=None, left=None, right=None):
        self.node_type = node_type  # 'operator' or 'operand'
        self.value = value          # The condition for operands, e.g., "age > 30"
        self.left = left            # Left child for operators
        self.right = right          # Right child for operators
    
    def __repr__(self):
        # This is to print a readable version of the node and its children
        return f"Node({self.node_type}, {self.value}, {self.left}, {self.right})"

# Function to manually create a simple AST based on a rule string with AND/OR
def create_rule_ast():
    # Accept the rule input from the user
    rule = input("Enter a rule (e.g., 'age > 30 AND department = Sales'): ").strip()

    # Split rule into conditions and operators (for now, assume a single AND/OR)
    tokens = rule.split()
    
    # For simplicity, assume two conditions and one operator in this basic version
    left_operand = Node(node_type='operand', value=f"{tokens[0]} {tokens[1]} {tokens[2]}")
    operator = tokens[3].upper()
    right_operand = Node(node_type='operand', value=f"{tokens[4]} {tokens[5]} {tokens[6]}")

    # Create root operator node (AND/OR)
    root = Node(node_type='operator', value=operator, left=left_operand, right=right_operand)
    
    return root

# Function to evaluate if a user's data matches the rule represented by the AST
def evaluate_ast(ast, data):
    # If it's an operand, we evaluate the condition directly
    if ast.node_type == 'operand':
        return eval_condition(ast.value, data)
    
    # If it's an operator, evaluate both left and right sides
    if ast.node_type == 'operator':
        left_result = evaluate_ast(ast.left, data)
        right_result = evaluate_ast(ast.right, data)
        
        # Perform the operation (AND or OR)
        if ast.value == 'AND':
            return left_result and right_result
        elif ast.value == 'OR':
            return left_result or right_result

# Helper function to evaluate a condition like "age > 30" or "department = 'Sales'"
def eval_condition(condition, data):
    field, operator, value = parse_condition(condition)
    
    # Handle numeric fields like age or salary
    if field in data and isinstance(data[field], (int, float)):
        if operator == '>':
            return data[field] > int(value)
        elif operator == '<':
            return data[field] < int(value)
    
    # Handle string fields like department
    elif field in data and isinstance(data[field], str):
        if operator == '=':
            return data[field] == value.strip("'")
    
    return False

# Function to parse the condition string (e.g., "age > 30" -> ["age", ">", "30"])
def parse_condition(condition):
    tokens = condition.split()
    return tokens[0], tokens[1], tokens[2]

# Main function to accept user inputs and display the evaluation result
if __name__ == "__main__":
    # Create a rule AST based on user input
    ast = create_rule_ast()
    
    # Print the AST to verify its structure
    print("\nGenerated AST Structure:")
    print(ast)
    
    # Accept user data input for evaluation
    print("\nEnter user data for evaluation (e.g., age=35 department=Sales):")
    user_data = {}
    while True:
        entry = input("Enter attribute (or type 'done' to finish): ").strip()
        if entry.lower() == 'done':
            break
        key, value = entry.split('=')
        
        # Convert numeric values to integers
        if value.isdigit():
            user_data[key] = int(value)
        else:
            user_data[key] = value.strip()
    
    # Evaluate the user data against the AST
    result = evaluate_ast(ast, user_data)
    
    # Display the evaluation result
    print("\nUser Data:", user_data)
    print("Rule Evaluation Result:", result)
