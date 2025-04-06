from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import sys
import io
from contextlib import redirect_stdout
import traceback
import numpy as np

app = FastAPI(title="Sigmoid ML Learning Platform")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load problems from JSON file
def load_problems():
    try:
        with open('problems.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

problems = load_problems()

class Solution(BaseModel):
    code: str

@app.get("/problems")
async def get_problems():
    return problems

@app.get("/problems/{problem_id}")
async def get_problem(problem_id: int):
    problem = next((p for p in problems if p["id"] == problem_id), None)
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem

@app.post("/problems/{problem_id}/submit")
async def submit_solution(problem_id: int, solution: Solution):
    problem = next((p for p in problems if p["id"] == problem_id), None)
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    results = []
    all_passed = True
    
    # Create a string buffer to capture print output
    output_buffer = io.StringIO()
    
    # Prepare the global namespace for execution
    global_namespace = {}
    
    try:
        # First, execute the submitted code to define functions
        with redirect_stdout(output_buffer):
            exec(solution.code, global_namespace)
        
        # Then run test cases
        for test_case in problem["test_cases"]:
            try:
                # Prepare the test case
                input_values = test_case["input"]
                expected_output = test_case["output"]
                
                # Execute the function with test input
                if isinstance(input_values, list):
                    actual_output = global_namespace[problem["function_name"]](*input_values)
                else:
                    actual_output = global_namespace[problem["function_name"]](input_values)
                
                # Compare results
                success = actual_output == expected_output
                if not success:
                    all_passed = False
                
                results.append({
                    "success": success,
                    "result": str(actual_output),
                    "expected": str(expected_output),
                    "output": output_buffer.getvalue()
                })
                
            except Exception as e:
                all_passed = False
                results.append({
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "output": output_buffer.getvalue()
                })
                
    except Exception as e:
        return {
            "success": False,
            "results": [{
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "output": output_buffer.getvalue()
            }]
        }
    
    return {
        "success": all_passed,
        "results": results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 