# FaceDInterview Django Backend API

This is the Django REST Framework backend for the FaceDInterview application.

## Setup Instructions

### 1. Create a Virtual Environment (Recommended)

```bash
# Navigate to the backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create a Superuser (Optional - for Django admin)

```bash
python manage.py createsuperuser
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

The API will be available at: `http://127.0.0.1:8000`

## API Endpoints

### Register User
- **URL:** `POST /api/register/`
- **Request Body:**
  ```json
  {
    "name": "John Doe",
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Success Response (201):**
  ```json
  {
    "message": "Account created successfully!",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe"
    }
  }
  ```

### Login User
- **URL:** `POST /api/login/`
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Success Response (200):**
  ```json
  {
    "message": "Login successful!",
    "token": "dummy-token-for-now",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe"
    }
  }
  ```

## CORS Configuration

The backend is configured to allow requests from:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

This is configured in `VerifiHireAI_backend/settings.py`.

## Testing the API

You can test the API using:
- Postman
- curl
- Your React frontend (which is already configured)

### Example curl commands:

**Register:**
```bash
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","password":"password123"}'
```

**Login:**
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"password123"}'
```

## Next Steps

1. Implement JWT authentication for better security
2. Add more API endpoints as needed
3. Add email verification
4. Add password reset functionality

