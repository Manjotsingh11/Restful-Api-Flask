import unittest
from flask import Flask
from flask.testing import FlaskClient
from bson import ObjectId
from app import app, mongo

class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_ping(self):
        response = self.client.get('/test-mongo')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'MongoDB connection successful', response.data)

    def test_signup(self):
        
        response = self.client.post('/api/auth/signup', json={'username': 'testuser3', 'password': 'testpassword3'})
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'User registered successfully', response.data)
        
        response = self.client.post('/api/auth/signup', json={'username': 'testuser4', 'password': 'testpassword4'})
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'User registered successfully', response.data)

    def test_login(self):
        response = self.client.post('/api/auth/login', json={'username': 'testuser3', 'password': 'testpassword3'})
        self.assertEqual(response.status_code, 200)

        # # Incorrect login (wrong password)
        response_wrong_password = self.client.post('/api/auth/login', json={'username': 'testuser3', 'password': 'wrongpassword'})
        self.assertEqual(response_wrong_password.status_code, 401)
        self.assertIn(b'Invalid username or password', response_wrong_password.data)
    
    def test_create_note(self):
        # Login
        login_response = self.client.post('/api/auth/login', json={'username': 'testuser3', 'password': 'testpassword3'})
        self.assertEqual(login_response.status_code, 200)

        # Create note
        create_note_response = self.client.post('/api/notes', json={'content': 'Test note content'},
                                               headers={'Authorization': 'Bearer ' + login_response.json['access_token']})
        self.assertEqual(create_note_response.status_code, 201)
        self.assertIn(b'Note created successfully', create_note_response.data)

    def test_get_notes(self):
        # Login
        login_response = self.client.post('/api/auth/login', json={'username': 'testuser3', 'password': 'testpassword3'})
        self.assertEqual(login_response.status_code, 200)

        # Get all notes
        get_notes_response = self.client.get('/api/notes',
                                            headers={'Authorization': 'Bearer ' + login_response.json['access_token']})
        self.assertEqual(get_notes_response.status_code, 200)
        self.assertIn(b'Notes retrieved successfully', get_notes_response.data)

    def test_get_note_by_id(self):
        # Login
        login_response = self.client.post('/api/auth/login', json={'username': 'testuser3', 'password': 'testpassword3'})
        self.assertEqual(login_response.status_code, 200)

        # Create note
        create_note_response = self.client.post('/api/notes', json={'content': 'Test note content'},
                                               headers={'Authorization': 'Bearer ' + login_response.json['access_token']})
        self.assertEqual(create_note_response.status_code, 201)

        # Get note by id
        note_id = create_note_response.json['note']['id']
        get_note_response = self.client.get(f'/api/notes/{note_id}',
                                           headers={'Authorization': 'Bearer ' + login_response.json['access_token']})
        self.assertEqual(get_note_response.status_code, 200)
        self.assertIn(b'Note retrieved successfully', get_note_response.data)
        
    def test_update_note(self):
        # Login
        login_response = self.client.post('/api/auth/login', json={'username': 'testuser4', 'password': 'testpassword4'})
        self.assertEqual(login_response.status_code, 200)

        # Create note
        create_note_response = self.client.post(
            '/api/notes',
            json={'content': 'Test note content new'},
            headers={'Authorization': 'Bearer ' + login_response.json['access_token']}
)
        self.assertEqual(create_note_response.status_code, 201)

        # Get note by id
        note_id = create_note_response.json['note']['id']

        # Update note
        response = self.client.put(
            f'/api/notes/{note_id}',
            json={'content': 'Updated note content'},
            headers={'Authorization': 'Bearer ' + login_response.json['access_token']}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Note updated successfully', response.data)

    def test_delete_note(self):
#         # Login
        login_response = self.client.post('/api/auth/login', json={'username': 'testuser4', 'password': 'testpassword4'})
        self.assertEqual(login_response.status_code, 200)

        # Create note
        create_note_response = self.client.post(
            '/api/notes',
            json={'content': 'Test note content for deletion'},
            headers={'Authorization': 'Bearer ' + login_response.json['access_token']}
)
        self.assertEqual(create_note_response.status_code, 201)

        # Get note by id
        note_id = create_note_response.json['note']['id']
        # Assuming note_id is a valid ObjectId
        response = self.client.delete(
                f'/api/notes/{note_id}',
                headers={'Authorization': 'Bearer ' + login_response.json['access_token']})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Note deleted successfully', response.data)

    def test_search_notes(self):
        # Login and create a note for the search query
        login_response = self.client.post('/api/auth/login', json={'username': 'testuser4', 'password': 'testpassword4'})
        self.assertEqual(login_response.status_code, 200)

        create_note_response = self.client.post(
            '/api/notes',
            json={'content': 'Note for search query test'},
            headers={'Authorization': 'Bearer ' + login_response.json['access_token']}
        )
        self.assertEqual(create_note_response.status_code, 201)

        # Search for the created note
        response = self.client.get('/api/notes/search?q=search', headers={'Authorization': 'Bearer ' + login_response.json['access_token']})
        self.assertEqual(response.status_code, 200)
        data = response.json

        # Assertions for the response structure
        self.assertIn('message', data)
        self.assertIn('notes', data)

        # Assertions for the note in the response
        self.assertEqual(len(data['notes']), 1)
        note = data['notes'][0]
        self.assertIn('id', note)
        self.assertIn('content', note)
        self.assertEqual(note['content'], 'Note for search query test')
        

    def test_share_note(self):
        # Login user who owns the note
        login_response_owner = self.client.post('/api/auth/login', json={'username': 'testuser3', 'password': 'testpassword3'})
        self.assertEqual(login_response_owner.status_code, 200)

        # Create a note
        create_note_response = self.client.post(
            '/api/notes',
            json={'content': 'Test note content for sharing'},
            headers={'Authorization': 'Bearer ' + login_response_owner.json['access_token']}
        )
        self.assertEqual(create_note_response.status_code, 201)

        # Get the note ID
        note_id = create_note_response.json['note']['id']

        # Share the note with the target user
        response = self.client.post(
            f'/api/notes/{note_id}/share',
            json={'target_user': 'testuser4'},
            headers={'Authorization': 'Bearer ' + login_response_owner.json['access_token']}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Note shared successfully', response.data)

        # Verify that the note is now shared with the target user
        shared_note = mongo.db.notes.find_one({'_id': ObjectId(note_id), 'shared_with': 'testuser4'})
        self.assertIsNotNone(shared_note)


if __name__ == '__main__':
    unittest.main()
