from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
import os
import sys
import io
from contextlib import redirect_stdout
import traceback
import numpy as np

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.urandom(24)  # For session management

# Database initialization
def init_db():
    conn = sqlite3.connect('sigmoid.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create user_progress table to track solved problems
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            user_id INTEGER,
            problem_id INTEGER,
            status TEXT,
            solution TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            PRIMARY KEY (user_id, problem_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# User registration
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not all(key in data for key in ['username', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        conn = sqlite3.connect('sigmoid.db')
        c = conn.cursor()
        
        # Check if username or email already exists
        c.execute('SELECT id FROM users WHERE username = ? OR email = ?',
                 (data['username'], data['email']))
        if c.fetchone():
            return jsonify({'error': 'Username or email already exists'}), 409
        
        # Hash password and create user
        password_hash = generate_password_hash(data['password'])
        c.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                 (data['username'], data['email'], password_hash))
        
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# User login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not all(key in data for key in ['username', 'password']):
        return jsonify({'error': 'Missing username or password'}), 400
    
    try:
        conn = sqlite3.connect('sigmoid.db')
        c = conn.cursor()
        
        # Get user by username
        c.execute('SELECT id, username, password_hash FROM users WHERE username = ?',
                 (data['username'],))
        user = c.fetchone()
        
        if user and check_password_hash(user[2], data['password']):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return jsonify({
                'message': 'Login successful',
                'user': {'id': user[0], 'username': user[1]}
            }), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# User logout
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

# Check authentication status
@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {'id': session['user_id'], 'username': session['username']}
        }), 200
    return jsonify({'authenticated': False}), 200

# Get user progress
@app.route('/api/user/progress', methods=['GET'])
def get_user_progress():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        conn = sqlite3.connect('sigmoid.db')
        c = conn.cursor()
        
        c.execute('''
            SELECT problem_id, status, solution, submitted_at 
            FROM user_progress 
            WHERE user_id = ?
        ''', (session['user_id'],))
        
        progress = [{
            'problem_id': row[0],
            'status': row[1],
            'solution': row[2],
            'submitted_at': row[3]
        } for row in c.fetchall()]
        
        return jsonify({'progress': progress}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# Update user progress
@app.route('/api/user/progress/<int:problem_id>', methods=['POST'])
def update_progress(problem_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    if 'status' not in data or 'solution' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        conn = sqlite3.connect('sigmoid.db')
        c = conn.cursor()
        
        c.execute('''
            INSERT OR REPLACE INTO user_progress (user_id, problem_id, status, solution)
            VALUES (?, ?, ?, ?)
        ''', (session['user_id'], problem_id, data['status'], data['solution']))
        
        conn.commit()
        return jsonify({'message': 'Progress updated successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# Serve problems
@app.route('/problems', methods=['GET'])
def get_problems():
    try:
        with open('problems.json', 'r') as f:
            problems = json.load(f)
        return jsonify(problems)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get specific problem
@app.route('/problems/<int:problem_id>', methods=['GET'])
def get_problem(problem_id):
    try:
        with open('problems.json', 'r') as f:
            problems = json.load(f)
        problem = next((p for p in problems if p['id'] == problem_id), None)
        if problem:
            return jsonify(problem)
        return jsonify({'error': 'Problem not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

if __name__ == '__main__':
    app.run(port=8000, debug=True) 