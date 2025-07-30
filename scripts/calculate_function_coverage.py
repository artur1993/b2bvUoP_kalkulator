# scripts/calculate_function_coverage.py

import json
import ast
import os
import sys

def get_all_functions_and_methods(file_path):
    """Parses a Python file and returns a list of (function_name, start_line, end_line) tuples."""
    functions = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=file_path)
    except Exception as e:
        # print(f"Error parsing {file_path}: {e}", file=sys.stderr)
        return functions

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Regular function or async function
            functions.append((node.name, node.lineno, node.end_lineno))
        elif isinstance(node, ast.ClassDef):
            # Methods within a class
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append((f"{node.name}.{item.name}", item.lineno, item.end_lineno))
    return functions

def calculate_function_coverage(coverage_data_path, source_dir):
    """
    Calculates the percentage of functions that were called based on coverage data.
    A function is considered called if at least one line within it was executed.
    """
    try:
        with open(coverage_data_path, 'r', encoding='utf-8') as f:
            coverage_data = json.load(f)
    except FileNotFoundError:
        # print(f"Error: Coverage data file not found at {coverage_data_path}", file=sys.stderr)
        return 0.0, 0, 0
    except json.JSONDecodeError:
        # print(f"Error: Could not decode JSON from {coverage_data_path}", file=sys.stderr)
        return 0.0, 0, 0

    files_coverage = coverage_data.get('files', {})
    
    total_functions = 0
    called_functions = 0
    
    for file_path_relative, data in files_coverage.items():
        # Ensure we only process files within the specified source directory
        if not file_path_relative.startswith(source_dir):
            continue

        full_file_path = os.path.join(os.getcwd(), file_path_relative)
        
        if not os.path.exists(full_file_path):
            # print(f"Warning: Source file not found: {full_file_path}", file=sys.stderr)
            continue

        all_funcs_in_file = get_all_functions_and_methods(full_file_path)
        total_functions += len(all_funcs_in_file)

        executed_lines = set(data.get('executed_lines', []))

        for func_name, start_line, end_line in all_funcs_in_file:
            # Check if any line within the function's body was executed
            # Adjust line numbers to be 0-indexed for internal processing if needed,
            # but coverage.py reports 1-indexed lines.
            for line_num in range(start_line, end_line + 1):
                if line_num in executed_lines:
                    called_functions += 1
                    break # This function was called, move to the next one

    if total_functions == 0:
        return 0.0, 0, 0

    percentage = (called_functions / total_functions) * 100
    return percentage, called_functions, total_functions

if __name__ == "__main__":
    # Expects two arguments: path to coverage.json and source directory
    if len(sys.argv) != 3:
        print("Usage: python calculate_function_coverage.py <coverage_json_path> <source_directory>", file=sys.stderr)
        sys.exit(1)

    coverage_json_path = sys.argv[1]
    source_directory = sys.argv[2] # e.g., 'src' or '.'

    percentage, called, total = calculate_function_coverage(coverage_json_path, source_directory)
    print(f"{percentage:.2f}") # Output only the percentage for easy parsing by bash script
