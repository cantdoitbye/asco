# Ooumph SHAKTI - Anganwadi Supply Chain Optimization

AI-powered supply chain management system for Anganwadi centers using OpenAI GPT-4

## Features

- **Route Intelligence Agent** - Optimal delivery routes using AI-powered optimization
- **Supply Sentinel Agent** - Real-time supply monitoring and tracking
- **Demand Forecasting Agent** - Predict demand patterns with machine learning
- **Grievance Intelligence Agent** - NLP-based complaint analysis and resolution
- **Trust Score System** - Credibility metrics for stakeholders
- **Offline Support** - Work without internet connectivity
- **Compliance & Audit** - Automated reporting and compliance tracking
- **Community Coordination** - Stakeholder management and communication
- **Recommendations** - AI-powered suggestions for optimization

## Tech Stack

### Backend
- FastAPI
- Python
- PostgreSQL
- Redis

### Frontend
- React
- Vite
- TypeScript
- Tailwind CSS

### AI
- OpenAI GPT-4

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- OpenAI API Key

## Quick Start

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd ooumph-asco
   ```

2. Copy environment file
   ```bash
   cp .env.example .env
   ```

3. Add your OpenAI API key to `.env`
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

4. Start the application
   ```bash
   docker-compose up -d
   ```

5. Access the application
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

**Backend:**
```bash
cd backend
pytest
```

**Frontend:**
```bash
cd frontend
npm test
```

## Project Structure

```
ooumph-asco/
├── backend/
│   ├── app/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── docker-compose.yml
└── README.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/routes` | GET | Get optimized delivery routes |
| `/api/supplies` | GET | Get supply status |
| `/api/demand` | GET | Get demand forecasts |
| `/api/grievances` | GET | Get grievance analysis |
| `/api/trust-scores` | GET | Get trust score metrics |
| `/api/recommendations` | GET | Get AI recommendations |

## License

MIT License
