# Visitor Tracking API documentation

## Project Overview
A lightweight, self-hosted visitor tracking solution using Python socket programming and MySQL, designed for small to medium-sized websites.

## System Architecture
- **Backend**: Python socket server
- **Database**: MySQL
- **Frontend Integration**: JavaScript client

## Key Components

### 1. Backend (Python Socket Server)
#### Features
- Raw socket programming without web frameworks
- Visitor count tracking
- Database connection pooling
- Secure request handling
- Multithreaded request processing

#### Key Classes
- `VisitorTrackingServer`: Main server implementation
- Methods:
  - `create_database_table()`: Initialize database schema
  - `update_visitor_count()`: Track page visits
  - `get_visitor_count()`: Retrieve visitor statistics
  - `handle_request()`: Process incoming HTTP requests

### 2. Database Schema
#### Tables
- `visitors`: Tracks page visit information
- `users`: Optional user management

#### Key Fields
- `page_url`: Tracked webpage URL
- `visit_count`: Number of visits
- `last_visited`: Timestamp of last visit
- `created_at`: Initial tracking timestamp

### 3. Frontend Integration
- JavaScript client for easy integration
- Methods:
  - `updateVisitorCount()`: Send visit data to backend
  - `getVisitorCount()`: Retrieve visitor statistics

## Security Features
- URL validation
- Connection pooling
- Optional SSL support
- CORS headers
- Secure token generation
- Error handling

## Installation Requirements
### Backend
- Python 3.8+
- `mysql-connector-python`
- MySQL 8.0+

### Frontend
- Modern web browser
- JavaScript ES6+

## Configuration
1. Database Credentials
2. Server Host/Port
3. Optional SSL Configuration

## Sample Usage

### Backend Initialization
```python
server = VisitorTrackingServer(
    host='localhost', 
    port=8000, 
    db_config={
        'host': 'localhost',
        'user': 'username',
        'password': 'password',
        'database': 'visitor_tracking_db'
    }
)
server.start_server()
```

### Frontend Integration
```javascript
const tracker = new VisitorTracker();
tracker.updateVisitorCount(window.location.href);
```

## Deployment Considerations
- Use SSL for production
- Implement rate limiting
- Secure database credentials
- Regular database maintenance

## Performance Optimizations
- Connection pooling
- Atomic database operations
- Indexing
- Multithreaded request handling

## Scalability
- Supports multiple concurrent requests
- Easily extensible architecture
- Minimal resource consumption

## Troubleshooting
- Check database connection
- Verify network permissions
- Monitor server logs
- Validate URL formats

## Future Enhancements
- Advanced analytics
- More detailed geolocation tracking
- Authentication mechanisms
- Real-time dashboard

## License
- This project is licensed under the Apache 2.0 License. See the `license` file for more details.
