from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId, regex
from flask_limiter import Limiter


app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/secure-scalable-db'
app.config['JWT_SECRET_KEY'] = 'secret_key' # Add your secret key



mongo = PyMongo(app)
jwt = JWTManager(app)
limiter = Limiter(app)

@limiter.request_filter
def ip_whitelist():
    #  logic to determine if the request should be throttled
    return False  # Return True to throttle, False to allow the request

@app.route('/throttled-route')
@limiter.limit("5 per second")  # Adjusting rate limit
def throttled_route():
    return "This route is throttled"

# Test MongoDB Connection Route
@app.route('/test-mongo')
def test_mongo():
    try:
        mongo.db.command('ping')
        return jsonify({'message': 'MongoDB connection successful'}), 200
    except Exception as e:
        return jsonify({'message': f'MongoDB connection failed: {str(e)}'}), 500


# Signup endpoint
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return {'message': 'Username and password are required'}, 400

    # Check if the username is already taken in the MongoDB collection
    existing_user = mongo.db.users.find_one({'username': username})
    if existing_user:
        return {'message': 'Username is already taken'}, 400

    # Hash the password before storing it
    hashed_password = generate_password_hash(password)

    # Store the user data in the MongoDB collection
    mongo.db.users.insert_one({'username': username, 'password': hashed_password})

    return {'message': 'User registered successfully'}, 201

# Login endpoint
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return {'message': 'Username and password are required'}, 400

    # Find the user in the MongoDB collection
    stored_user = mongo.db.users.find_one({'username': username})
    if not stored_user or not check_password_hash(stored_user['password'], password):
        return {'message': 'Invalid username or password'}, 401

    # If login is successful, create an access token
    access_token = create_access_token(identity=username)
    return {'access_token': access_token}, 200

# Create a Note
@app.route('/api/notes', methods=['POST'])
@jwt_required()
def create_note():
    # Get the note content from the request payload
    data = request.get_json()
    content = data.get('content')

    if not content:
        return {'message': 'Note content is required'}, 400

    # Get the user ID from the JWT token
    user_id = get_jwt_identity()

    # Insert the note into the MongoDB collection
    result = mongo.db.notes.insert_one({
        'user': user_id,
        'content': content
    })

    # Format the response
    created_note = {
        'id': str(result.inserted_id),
        'content': content
    }

    return jsonify({'message': 'Note created successfully', 'note': created_note}), 201



# Get all notes endpoint
@app.route('/api/notes', methods=['GET'])
@jwt_required()
def get_notes():
    # Get the user ID from the JWT token
    user_id = get_jwt_identity()

    # Query the MongoDB collection to find all notes for the authenticated user
    notes = mongo.db.notes.find({'user': user_id})

    # Format the response
    formatted_notes = [{
        'id': str(note['_id']),
        'content': note['content']
    } for note in notes]

    return jsonify({'message': 'Notes retrieved successfully', 'notes': formatted_notes}), 200

# Get note by ID endpoint
@app.route('/api/notes/<string:note_id>', methods=['GET'])
@jwt_required()
def get_note(note_id):
    # Get the user ID from the JWT token
    user_id = get_jwt_identity()

    # Query the MongoDB collection to find the note by ID and user ID
    note = mongo.db.notes.find_one({
        '_id': ObjectId(note_id),
        '$or': [
            {'user': user_id},
            {'shared_with': user_id}
        ]
    })

    if not note:
        return jsonify({'message': 'Note not found or does not belong to the authenticated user'}), 404

    # Format the response
    formatted_note = {
        'id': str(note['_id']),
        'content': note['content']
    }

    return jsonify({'message': 'Note retrieved successfully', 'note': formatted_note}), 200

# Update note endpoint
@app.route('/api/notes/<string:note_id>', methods=['PUT'])
@jwt_required()
def update_note(note_id):
    # Get the user ID from the JWT token
    user_id = get_jwt_identity()

    # Get the note content from the request payload
    data = request.get_json()
    new_content = data.get('content')

    if not new_content:
        return {'message': 'New note content is required'}, 400

    # Query the MongoDB collection to find the note by ID and user ID
    note = mongo.db.notes.find_one({
        '_id': ObjectId(note_id),
        'user': user_id
    })

    if not note:
        return jsonify({'message': 'Note not found or does not belong to the authenticated user'}), 404

    # Update the note content in the MongoDB collection
    mongo.db.notes.update_one({'_id': ObjectId(note_id)}, {'$set': {'content': new_content}})

    return jsonify({'message': 'Note updated successfully'}), 200

# Delete note by ID endpoint
@app.route('/api/notes/<string:note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    try:
        # Get the user ID from the JWT token
        user_id = get_jwt_identity()

        # Delete the note from the MongoDB collection based on ID and user ID
        result = mongo.db.notes.delete_one({
            '_id': ObjectId(note_id),
            'user': user_id
        })

        if result.deleted_count == 1:
            return jsonify({'message': 'Note deleted successfully'}), 200
        else:
            return jsonify({'message': 'Note not found or does not belong to the authenticated user'}), 404

    except Exception as e:
        return jsonify({'message': f'Error deleting note: {str(e)}'}), 500


# Search for Notes endpoint
@app.route('/api/notes/search', methods=['GET'])
@jwt_required()
def search_notes():
    # Get the user ID from the JWT token
    user_id = get_jwt_identity()

    # Get the search query from the request
    search_query = request.args.get('q')

    if not search_query:
        return jsonify({'message': 'Search query is required'}), 400

    # Query the MongoDB collection to find notes that match the search query and user ID
    notes = mongo.db.notes.find({
        'user': user_id,
        'content': {'$regex': f'.*{search_query}.*', '$options': 'i'}  # Case-insensitive regex
    })

    # Format the response
    formatted_notes = [{
        'id': str(note['_id']),
        'content': note['content']
    } for note in notes]

    return jsonify({'message': 'Notes retrieved successfully', 'notes': formatted_notes}), 200

# Share note endpoint
@app.route('/api/notes/<string:note_id>/share', methods=['POST'])
@jwt_required()
def share_note(note_id):
    # Get the user ID from the JWT token
    current_user = get_jwt_identity()

    # Get the target user from the request payload
    data = request.get_json()
    target_user = data.get('target_user')

    if not target_user:
        return jsonify({'message': 'Target user is required'}), 400

    # Check if the note exists and belongs to the authenticated user
    note = mongo.db.notes.find_one({
        '_id': ObjectId(note_id),
        'user': current_user
    })

    if not note:
        return jsonify({'message': 'Note not found or does not belong to the authenticated user'}), 404

    # Share the note with the target user
    mongo.db.notes.update_one(
        {'_id': ObjectId(note_id)},
        {'$addToSet': {'shared_with': target_user}}
    )

    return jsonify({'message': 'Note shared successfully'}), 200
    

if __name__ == '__main__':
    app.run(debug=True)
