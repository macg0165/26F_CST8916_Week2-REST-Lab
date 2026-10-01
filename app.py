# AI contribution note: Codex changes are tagged [AI: Codex].
# Codex wrote the task routes, task ID counter, and user_id support.
# Task seed data is user-provided.
# Tag future AI additions and edits using the same comment marker.

# Import necessary modules from Flask
# Flask: the core framework for the web app
# jsonify: to convert Python dictionaries to JSON responses
# request: to access incoming request data (e.g., POST data)
# abort: to handle errors and send error status codes
from flask import Flask, jsonify, request, abort
from flask_cors import CORS  # Enable Cross-Origin Resource Sharing for client apps

# Initialize the Flask app
app = Flask(__name__)

# Enable CORS so the HTML client can connect from a browser
# This allows requests from different origins (e.g., file:// or another port)
CORS(app)

# In-memory "database" of users
# This list holds a set of user dictionaries. 
# In a real-world application, this would be replaced by a database such as MySQL, PostgreSQL, or MongoDB.
users = [
    {"id": 1, "name": "Alice", "age": 25},
    {"id": 2, "name": "Bob", "age": 30},
]

# Define route to handle requests to the root URL ('/')
@app.route('/')
def index():
    return "Welcome to Flask REST API Demo! Try accessing /users to see all users."

# Health check route (GET)
# This endpoint returns a 200 OK status and a JSON response to confirm that the service is running.
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200  # Return HTTP status 200 OK

# Route to retrieve all users (GET request)
# When the client sends a GET request to /users, this function will return a JSON list of all users.
# The @ symbol in Python represents a decorator. 
# In this case, @app.route is a Flask route decorator.
# It is used to map a specific URL (route) to a function in your Flask application.
@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users), 200  # 200 is the HTTP status code for 'OK'

# Route to retrieve a single user by their ID (GET request)
# When the client sends a GET request to /users/<id>, this function will return the user with the specified ID.
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # Using a list comprehension to find the user by ID
    user = next((user for user in users if user['id'] == user_id), None)
    if user is None:
        abort(404)  # If the user is not found, return a 404 error (Not Found)
    return jsonify(user), 200  # Return the user as a JSON object with a 200 status code (OK)

# Route to create a new user (POST request)
# When the client sends a POST request to /users with user data, this function will add the new user to the list.
@app.route('/users', methods=['POST'])
def create_user():
    # If the request body is not in JSON format or if the 'name' field is missing, return a 400 error (Bad Request)
    if not request.json or not 'name' in request.json:
        abort(400)
    
    # Create a new user dictionary. Assign the next available ID by incrementing the highest current ID.
    # If no users exist, the new ID will be 1.
    new_user = {
        'id': users[-1]['id'] + 1 if users else 1,
        'name': request.json['name'],  # The name is provided in the POST request body
        'age': request.json.get('age', 0)  # The age is optional; default is 0 if not provided
    }
    # Add the new user to the users list
    users.append(new_user)
    return jsonify(new_user), 201  # 201 is the HTTP status code for 'Created'

# Route to update an existing user (PUT request)
# When the client sends a PUT request to /users/<id> with updated user data, this function will update the user.
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    # Find the user by their ID
    user = next((user for user in users if user['id'] == user_id), None)
    if user is None:
        abort(404)  # If the user is not found, return a 404 error (Not Found)
    
    # If the request body is missing or not in JSON format, return a 400 error (Bad Request)
    if not request.json:
        abort(400)
    
    # Update the user's data based on the request body
    # If a field is not provided in the request, keep the existing value
    user['name'] = request.json.get('name', user['name'])
    user['age'] = request.json.get('age', user['age'])
    return jsonify(user), 200  # Return the updated user data with a 200 status code (OK)

# Route to delete a user (DELETE request)
# When the client sends a DELETE request to /users/<id>, this function will remove the user with that ID.
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    global users  # Reference the global users list
    # Rebuild the users list, excluding the user with the specified ID
    users = [user for user in users if user['id'] != user_id]
    return '', 204  # 204 is the HTTP status code for 'No Content', indicating the deletion was successful



# In-memory task storage and the next task ID.
tasks = [
    {"id": 1, "title": "Learn REST", "description": "Study REST principles", "user_id": 1, "completed": True},
    {"id": 2, "title": "Build API", "description": "Complete the assignment", "user_id": 2, "completed": False},
]
# [AI: Codex] Start after the highest seed ID to avoid duplicate task IDs.
next_task_id = max((task['id'] for task in tasks), default=0) + 1


# [AI: Codex] BEGIN task routes (GET/POST collection; GET/PUT/DELETE detail)
@app.route('/tasks', methods=['GET', 'POST'])
def task_collection():
    global next_task_id
    if request.method == 'GET':
        return jsonify(tasks), 200

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('title'), str) or not data['title'].strip():
        abort(400)
    if 'description' in data and not isinstance(data['description'], str):
        abort(400)
    # [AI: Codex] Require a positive integer user_id when creating a task.
    if type(data.get('user_id')) is not int or data['user_id'] < 1:
        abort(400)
    # [AI: Codex] Tasks must belong to an existing user.
    if not any(user['id'] == data['user_id'] for user in users):
        abort(400)
    if 'completed' in data and not isinstance(data['completed'], bool):
        abort(400)

    task = {
        'id': next_task_id,
        'title': data['title'],
        'description': data.get('description', ''),
        'user_id': data['user_id'],  # [AI: Codex] Store the supplied user ID.
        'completed': data.get('completed', False),
    }
    next_task_id += 1
    tasks.append(task)
    return jsonify(task), 201


@app.route('/tasks/<int:task_id>', methods=['GET', 'PUT', 'DELETE'])
def task_detail(task_id):
    task = next((task for task in tasks if task['id'] == task_id), None)
    if task is None:
        abort(404)

    if request.method == 'GET':
        return jsonify(task), 200
    if request.method == 'DELETE':
        tasks.remove(task)
        return '', 204

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        abort(400)
    if 'title' in data and (not isinstance(data['title'], str) or not data['title'].strip()):
        abort(400)
    if 'description' in data and not isinstance(data['description'], str):
        abort(400)
    # [AI: Codex] Validate user_id when an update includes it.
    if 'user_id' in data and (type(data['user_id']) is not int or data['user_id'] < 1):
        abort(400)
    # [AI: Codex] Validate the new owner before changing the task.
    if 'user_id' in data and not any(user['id'] == data['user_id'] for user in users):
        abort(400)
    if 'completed' in data and not isinstance(data['completed'], bool):
        abort(400)

    # [AI: Codex] Added user_id to the fields that can be updated.
    for field in ('title', 'description', 'user_id', 'completed'):
        if field in data:
            task[field] = data[field]
    return jsonify(task), 200
# [AI: Codex] Retrieve the tasks belonging to a specific user.
@app.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    if not any(user['id'] == user_id for user in users):
        abort(404)
    return jsonify([task for task in tasks if task['user_id'] == user_id]), 200
# [AI: Codex] END task routes


# Entry point for running the Flask app
# The app will run on host 0.0.0.0 (accessible on all network interfaces) and port 8000.
# Debug mode is disabled (set to False).
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
