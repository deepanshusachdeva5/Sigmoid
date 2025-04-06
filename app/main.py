from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
import numpy as np
from typing import List, Dict, Any
import ast
import sys
from io import StringIO
from pydantic import BaseModel
import csv

app = FastAPI(
    title="ML Practice Platform",
    description="A platform for learning and practicing Machine Learning problems",
    version="1.0.0",
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeSubmission(BaseModel):
    code: str

# Load problems from CSV
def load_problems():
    try:
        # Read CSV with proper parameters for handling code blocks
        df = pd.read_csv(
            "data/problems.csv",
            encoding='utf-8',
            quoting=csv.QUOTE_ALL,  # Quote all fields
            doublequote=True,  # Allow double quotes
            escapechar='\\',  # Use backslash as escape character
            sep=',',  # Use comma as separator
            lineterminator='\n',  # Use newline as line terminator
            on_bad_lines='warn'  # Warn about problematic lines
        )
        print("Loaded problems:", len(df))  # Debug print
        return df
    except Exception as e:
        print(f"Error loading problems: {str(e)}")
        return pd.DataFrame()

@app.get("/")
async def root():
    return {
        "message": "Welcome to ML Practice Platform",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/problems")
async def get_problems():
    problems = load_problems()
    if problems.empty:
        print("No problems found in DataFrame")  # Debug print
        return []
    result = problems.to_dict(orient="records")
    print(f"Returning {len(result)} problems")  # Debug print
    return result

@app.get("/problems/{problem_id}")
async def get_problem(problem_id: int):
    problems = load_problems()
    if problems.empty:
        raise HTTPException(status_code=404, detail="No problems found")
    
    # Convert problem_id to integer to ensure proper comparison
    problem = problems[problems['id'].astype(int) == int(problem_id)]
    if problem.empty:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    result = problem.iloc[0].to_dict()
    return result

def execute_code(code: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
    # Create a new namespace for code execution
    local_dict = {}
    
    # Capture stdout
    old_stdout = sys.stdout
    redirected_output = StringIO()
    sys.stdout = redirected_output
    
    try:
        # Execute the code
        exec(code, {"np": np}, local_dict)
        
        # Get the main function (assuming it's the last function defined)
        main_function = None
        for name, obj in local_dict.items():
            if callable(obj):
                main_function = obj
        
        if main_function is None:
            raise ValueError("No function found in the code")
        
        # Execute the function with test case input
        result = main_function(**test_case["input"])
        
        # Compare with expected output
        expected = test_case["output"]
        is_correct = np.allclose(np.array(result), np.array(expected)) if isinstance(result, (list, tuple, np.ndarray)) else result == expected
        
        return {
            "success": is_correct,
            "result": str(result),
            "expected": str(expected),
            "output": redirected_output.getvalue()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "output": redirected_output.getvalue()
        }
    finally:
        sys.stdout = old_stdout

@app.post("/problems/{problem_id}/submit")
async def submit_solution(problem_id: int, submission: CodeSubmission):
    problems = load_problems()
    if problems.empty:
        raise HTTPException(status_code=404, detail="No problems found")
    
    problem = problems[problems['id'].astype(int) == int(problem_id)]
    if problem.empty:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    # Parse test cases
    test_cases = json.loads(problem.iloc[0]["test_cases"])
    
    # Run each test case
    results = []
    for test_case in test_cases:
        result = execute_code(submission.code, test_case)
        results.append(result)
    
    # Check if all test cases passed
    all_passed = all(r["success"] for r in results)
    
    return {
        "success": all_passed,
        "results": results
    } 