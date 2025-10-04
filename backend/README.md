# ExpenseFlow Backend

Django REST API backend for ExpenseFlow expense management system.

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create a superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

5. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

### Testing the API

You can test the API endpoints using the provided test scripts:

```bash
# Test basic API functionality
python test_api.py

# Test JWT authentication flow
python test_jwt_api.py
```

The JWT test script will test:
- Company registration with JWT tokens
- User login with JWT tokens
- Protected endpoint access
- Token refresh mechanism
- Logout with token blacklisting
- Invalid token handling

## API Endpoints

### Authentication (JWT-based)
- `POST /api/auth/register/company/` - Register a new company and admin
- `POST /api/auth/login/` - User login (returns JWT tokens)
- `POST /api/auth/logout/` - User logout (blacklists refresh token)
- `POST /api/auth/refresh/` - Refresh JWT access token
- `GET /api/auth/profile/` - Get current user profile (JWT protected)
- `GET /api/auth/companies/` - List companies (admin only, JWT protected)

### JWT Token Usage
- **Access Token**: Short-lived (60 minutes) for API authentication
- **Refresh Token**: Long-lived (7 days) for obtaining new access tokens
- **Authorization Header**: `Bearer <access_token>`
- **Token Refresh**: Automatic refresh on 401 responses (frontend)
- **Token Blacklisting**: Logout blacklists refresh tokens

## Models

### Company
- `name` - Company name (unique)
- `address` - Company address
- `phone` - Company phone number
- `email` - Company email (unique)
- `website` - Company website (optional)
- `industry` - Company industry
- `size` - Company size (1-10, 11-50, 51-200, 201-500, 500+)
- `description` - Company description (optional)
- `is_active` - Company status
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

### User (extends AbstractUser)
- `email` - User email (unique)
- `role` - User role (admin, manager, employee)
- `company` - Foreign key to Company
- `phone` - User phone number (optional)
- `is_company_admin` - Whether user is company admin
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

## Registration Flow

1. Company admin fills out the registration form with both personal and company information
2. System creates a new Company record
3. System creates a new User record with `is_company_admin=True` and `role=admin`
4. User is automatically logged in and redirected to admin dashboard
5. Token-based authentication is used for subsequent API calls

## Development Notes

- CORS is configured to allow requests from frontend development servers
- Token authentication is used for API security
- All API responses are in JSON format
- Input validation is handled by Django REST Framework serializers
