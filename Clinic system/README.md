# Clinic Management System Backend

A comprehensive Python backend API for clinic operations management, featuring appointment scheduling, patient triage, and analytics.

## Features

- **Patient Management**: Registration, profiles, medical history tracking
- **Appointment Scheduling**: Booking, cancellation, rescheduling with conflict resolution
- **Triage System**: Priority assessment and urgent case management
- **Staff Management**: User authentication, role-based access control
- **Analytics**: Performance insights and care quality metrics
- **RESTful API**: Auto-documented endpoints with FastAPI
- **Security**: JWT authentication, role-based permissions, input validation

## Technology Stack

- **Runtime**: Python 3.8+
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT with python-jose
- **Validation**: Pydantic
- **Testing**: pytest + httpx
- **Documentation**: Automatic OpenAPI/Swagger docs

## Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL (v12 or higher)
- pip or poetry

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. Set up the database:
   ```bash
   # Create database
   createdb clinic_management

   # Initialize database with tables and default admin user
   python -m app.database.init_db
   ```

6. Start the development server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Default Credentials

After running the database initialization, you can login with:
- **Email**: admin@clinic.com
- **Password**: admin123

## API Endpoints

### Health Check
- `GET /health` - Server health status
- `GET /api/v1/health` - API health status

### Authentication
- `POST /api/v1/auth/login` - User login (OAuth2 form)
- `POST /api/v1/auth/login-json` - User login (JSON)
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/refresh` - Refresh JWT token

### Patients
- `GET /api/v1/patients` - List all patients (with pagination and filters)
- `POST /api/v1/patients` - Create new patient
- `GET /api/v1/patients/stats` - Get patient statistics
- `GET /api/v1/patients/search` - Search patients
- `GET /api/v1/patients/{id}` - Get patient details
- `PUT /api/v1/patients/{id}` - Update patient
- `DELETE /api/v1/patients/{id}` - Delete patient (soft delete)

### Appointments (Coming Soon)
- `GET /api/v1/appointments` - List appointments
- `POST /api/v1/appointments` - Book appointment
- `GET /api/v1/appointments/{id}` - Get appointment details
- `PUT /api/v1/appointments/{id}` - Update appointment
- `POST /api/v1/appointments/{id}/cancel` - Cancel appointment

### Triage (Coming Soon)
- `GET /api/v1/triage` - List triage assessments
- `POST /api/v1/triage` - Create triage assessment
- `GET /api/v1/triage/{id}` - Get triage details
- `PUT /api/v1/triage/{id}` - Update triage assessment

### Analytics (Coming Soon)
- `GET /api/v1/analytics/dashboard` - Dashboard metrics
- `GET /api/v1/analytics/appointments` - Appointment analytics
- `GET /api/v1/analytics/patients` - Patient flow analytics

## Development

### Running Tests
```bash
pytest                  # Run all tests
pytest --cov           # Run tests with coverage
pytest -v              # Verbose output
pytest --watch          # Watch mode (requires pytest-watch)
```

### Database Operations
```bash
# Initialize database
python -m app.database.init_db

# Using Alembic for migrations (optional)
alembic revision --autogenerate -m "Description"
alembic upgrade head
alembic downgrade -1
```

### Code Quality
```bash
# Format code
black app/
isort app/

# Lint code
flake8 app/
```

## Project Structure

```
app/
├── api/              # API routes and endpoints
│   └── v1/          # API version 1
├── core/            # Core configuration and utilities
├── database/        # Database models and migrations
├── schemas/         # Pydantic schemas for validation
├── services/        # Business logic services
└── main.py          # FastAPI application entry point
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License
