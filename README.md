# Agworld Reporter

A FastAPI-based service for integrating with Agworld, processing data, generating reports, and sending notifications.

## 🚀 Features

- **Agworld API Integration**: Fetch field, crop, and activity data
- **Data Processing**: Clean and transform raw data for reporting
- **Automated Reports**: Generate PDF and HTML reports with visualizations
- **Email Notifications**: Send reports via email with customizable templates
- **Background Tasks**: Celery-powered async processing
- **Scheduled Polling**: Automated data collection using APScheduler
- **Caching**: Redis-based caching for improved performance
- **Visualizations**: Interactive charts with Plotly and static charts with Matplotlib
- **RESTful API**: Complete API for managing reports and data

## 🏗️ Architecture

```
app/
├── api/           # FastAPI routes and endpoints
├── models/        # SQLAlchemy models and Pydantic schemas
├── services/      # Business logic services
│   ├── agworld_client.py    # Agworld API integration
│   ├── processor.py         # Data processing
│   ├── reporter.py          # Report generation
│   ├── notifier.py          # Email notifications
│   └── visualizer.py        # Data visualizations
├── scheduler/     # APScheduler polling logic
├── tasks/         # Celery background tasks
├── templates/     # Jinja2 email/report templates
└── utils/         # Utility functions
```

## 🛠️ Setup

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd syndicagent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/agworld

# Redis
REDIS_URL=redis://localhost:6379/0

# Agworld API
AGWORLD_API_KEY=your_agworld_api_key_here

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
```

### Database Setup

1. **Start PostgreSQL and Redis** (if using Docker):
   ```bash
   cd docker
   docker-compose up -d db redis
   ```

2. **Create database tables**:
   ```bash
   python -c "from app.database import create_tables; create_tables()"
   ```

## 🏃‍♂️ Running the Application

### Development Mode

**Option 1: Run all services together**
```bash
python run.py all
```

**Option 2: Run services separately**

Terminal 1 - Web Server:
```bash
python run.py server
```

Terminal 2 - Celery Worker:
```bash
python run.py worker
```

Terminal 3 - Celery Beat (Scheduler):
```bash
python run.py beat
```

### Production Mode

**Using Docker:**
```bash
cd docker
docker-compose up -d
```

**Manual deployment:**
```bash
# Web server
python run.py server --host 0.0.0.0 --port 8000 --no-reload

# Background worker
python run.py worker

# Scheduler
python run.py beat
```

## 📊 API Endpoints

### Health Check
- `GET /` - Basic info and available endpoints
- `GET /api/v1/health` - Health check with service status

### Reports
- `GET /api/v1/reports` - List all reports
- `POST /api/v1/reports` - Create new report
- `GET /api/v1/reports/{id}` - Get specific report
- `POST /api/v1/reports/generate` - Generate report immediately

### Data Processing
- `POST /api/v1/data/process` - Process raw data

### Scheduler Management
- `GET /api/v1/scheduler/status` - Get scheduler status
- `POST /api/v1/scheduler/start` - Start scheduler
- `POST /api/v1/scheduler/stop` - Stop scheduler

### Polling Status
- `GET /api/v1/polling/status` - Get polling job status
- `POST /api/v1/polling/trigger/{job_type}` - Manually trigger polling

### API Documentation
- `/docs` - Swagger UI documentation
- `/redoc` - ReDoc documentation

## 🔧 Configuration

### Scheduled Tasks

The application includes several pre-configured scheduled tasks:

- **Field Data Polling**: Every hour
- **Activity Data Polling**: Every 30 minutes
- **Daily Summary Report**: Daily at 8:00 AM
- **Cache Cleanup**: Daily

Modify schedules in `app/scheduler/poller.py` or `app/tasks/worker.py`.

### Email Templates

Customize email templates in `app/templates/report.html`. The template uses Jinja2 syntax and includes:

- Responsive design
- Professional styling
- Data visualization sections
- Configurable content blocks

### Data Processing

Extend data processing logic in `app/services/processor.py`:

```python
def _process_custom_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Add custom data processing logic"""
    return {
        "custom_field": raw_data.get("field"),
        "processed_value": some_transformation(raw_data)
    }
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_processor.py -v
```

## 📈 Monitoring

### Application Health

Monitor application health via:
- Health check endpoint: `GET /api/v1/health`
- Scheduler status: `GET /api/v1/scheduler/status`
- Polling status: `GET /api/v1/polling/status`

### Logs

Application logs include:
- API requests and responses
- Data processing activities
- Scheduler job execution
- Error tracking

### Redis Monitoring

Monitor Redis usage:
- Cache hit/miss rates
- Stored data keys
- Memory usage

## 🔒 Security

### API Security
- Add authentication middleware for production
- Implement rate limiting
- Use HTTPS in production

### Environment Security
- Store sensitive data in environment variables
- Use secrets management in production
- Rotate API keys regularly

## 🐛 Troubleshooting

### Common Issues

**Redis Connection Failed**
```bash
# Check Redis status
redis-cli ping

# Restart Redis
docker-compose restart redis
```

**Database Connection Issues**
```bash
# Check PostgreSQL status
docker-compose logs db

# Reset database
docker-compose down db && docker-compose up -d db
```

**Celery Worker Not Starting**
```bash
# Check Redis connection
python -c "from app.redis_client import redis_client; print(redis_client.ping())"

# Check worker logs
celery -A app.tasks.worker worker --loglevel=debug
```

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review API documentation at `/docs`

---

**Next Steps for Development:**

1. **Set up Agworld API credentials** in the `.env` file
2. **Configure email settings** for notifications
3. **Customize data processing logic** in `app/services/processor.py`
4. **Add authentication and authorization** for production use
5. **Set up monitoring and logging** for production deployment
