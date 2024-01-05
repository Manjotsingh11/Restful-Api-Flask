# Secure Scalable API

Secure Scalable API is a RESTful API built using Flask for managing and retrieving user notes securely. It provides endpoints for user authentication, note creation, retrieval, sharing, and search functionality.


# Details

## Framework

This API is built using Flask, a lightweight and versatile web framework for Python. Flask is chosen for its simplicity, flexibility, and ease of use. It allows for quick development of RESTful APIs and provides the necessary tools for building secure and scalable applications.

## Database

MongoDB is chosen as the database for this project. MongoDB is a NoSQL database that stores data in a flexible, JSON-like format known as BSON. It is suitable for handling large amounts of unstructured data and is easy to scale horizontally. The decision to use MongoDB aligns with the goal of creating a scalable and efficient API.

## Third-Party Tools

### Flask-JWT-Extended

Flask-JWT-Extended is utilized for JSON Web Token (JWT) based authentication. It extends the basic Flask-JWT package by adding features such as token refreshing and additional configuration options. JWT-based authentication provides a secure and stateless method for user authentication in web applications.

### Flask-Limiter

Flask-Limiter is integrated into the API to handle rate limiting and request throttling. This helps in preventing abuse, protecting against brute force attacks, and ensuring that the API remains responsive even during high traffic situations. Flask-Limiter allows for fine-grained control over the rate limits applied to different endpoints.

### Flask-PyMongo

Flask-PyMongo is used to simplify the interaction between Flask applications and MongoDB. It provides an easy-to-use interface for connecting to MongoDB databases, making database operations more straightforward within the Flask application.

These frameworks and tools are chosen to ensure a balance between simplicity, security, and scalability, providing a solid foundation for building a robust API.


## Getting Started

### Prerequisites

Make sure you have Python and MongoDB installed on your system.

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Manjotsingh11/Restful-Api-Flask.git

1. Change into the project directory:
   ```bash
   cd Restful-Api-Flask

2. Install dependencies:
   ```bash
   pip install -r requirements.txt

## Configuration
Update the config.py file with your MongoDB connection details and secret keys.

## Running the Application

- Run the application:

  ```bash
  python app.py
The API will be accessible at http://localhost:5000.

## API Endpoints
- POST /api/auth/signup: Sign up a new user.
- POST /api/auth/login: Log in an existing user.
- POST /api/notes: Create a new note for the authenticated user.
- GET /api/notes: Get all notes for the authenticated user.
- GET /api/notes/:id: Get a note by ID for the authenticated user.
- PUT /api/notes/:id: Update a note by ID for the authenticated user.
- DELETE /api/notes/:id: Delete a note by ID for the authenticated user.
- GET /api/notes/search?q=:query: Search for notes based on keywords for the authenticated user.
- POST /api/notes/:id/share: Share a note with another user for the authenticated user.

## Running Tests

To run the unit tests for this project, follow these steps:

1. Ensure you have Python installed on your machine. If not, you can download it from [python.org](https://www.python.org/downloads/).

2. Create a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    ```

3. Activate the virtual environment:

    - On Windows:

        ```bash
        .\venv\Scripts\activate
        ```

    - On macOS/Linux:

        ```bash
        source venv/bin/activate
        ```

4. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Run the tests:

    ```bash
    python -m unittest discover
    ```

This will execute the unit tests, and you should see the test results in the terminal.


## Rate Limiting and Request Throttling
The API implements rate limiting and request throttling to handle high traffic. The details are specified in the application code.

