# AI Career Platform

An AI-driven career recommendation and internship matching platform for BPUT students, employers, and placement officers.

## Features

- **Student Profiles**: Automated digital profiles with skills, academic records, and activities
- **AI Recommendations**: Career recommendations using predictive models
- **Job Matching**: AI-powered job/internship matching and candidate shortlisting
- **Analytics Dashboard**: Placement trends, skill gaps, and industry forecasts
- **Multi-language Support**: English and Odia language support
- **Gamification**: Points, badges, and micro-credentials system

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd ai-career-platform
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Access the Platform**
   - API: http://localhost:5000
   - Health Check: http://localhost:5000/api/health

## Project Structure

```
ai-career-platform/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── database.py           # Database connection and utilities
├── requirements.txt      # Python dependencies
├── blueprints/          # Flask blueprints
│   ├── auth.py          # Authentication endpoints
│   ├── student.py       # Student profile management
│   ├── employer.py      # Employer portal
│   ├── analytics.py     # Analytics dashboard
│   └── api.py           # General API endpoints
└── utils/               # Utility functions
    ├── auth_helpers.py  # Authentication utilities
    └── validators.py    # Input validation
```

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/profile` - Get user profile

### Student Portal
- `GET/POST/PUT /student/profile` - Profile management
- `GET /student/recommendations` - Career recommendations
- `GET /student/jobs` - Job matches
- `GET /student/dashboard` - Dashboard data

### Employer Portal
- `GET/POST /employer/jobs` - Job posting management
- `GET/PUT/DELETE /employer/jobs/<id>` - Individual job management
- `GET /employer/candidates` - Candidate matches
- `GET/PUT /employer/profile` - Company profile

### Analytics
- `GET /analytics/dashboard` - Analytics dashboard
- `GET /analytics/skill-gaps` - Skill gap analysis
- `GET /analytics/placement-trends` - Placement trends
- `GET/POST /analytics/reports` - Report generation

## Environment Variables

See `.env.example` for all available configuration options.

## Development

This is a demo version using:
- SQLite database (file-based, no server required)
- Free AI APIs (Hugging Face, OpenAI free tier)
- Minimal dependencies for lightweight deployment

## License

MIT License