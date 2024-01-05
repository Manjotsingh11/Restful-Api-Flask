import unittest
from flask import Flask
from flask.testing import FlaskClient
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_ping(self):
        response = self.client.get('/test-mongo')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'MongoDB connection successful', response.data)

    def test_signup(self):
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


# Add more test cases for other endpoints as needed

if __name__ == '__main__':
    unittest.main()
