# Ooumph SHAKTI - Anganwadi Supply Chain Optimization
## Deployment Instructions

### Server Details
- **Server IP:** 135.222.42.174
- **Frontend:** http://135.222.42.174:3080
- **Backend API:** http://135.222.42.174:8080
- **API Docs:** http://135.222.42.174:8080/docs

### Steps to1. SSH into server
```bash
ssh root@135.222.42.174
```

### 2. Clone repository
```bash
git clone https://github.com/cantdoitbye/asco.git /opt/asco
cd /opt/asco
```

### 2. Setup environment
```bash
cp .env.example .env
nano .env
# Edit .env and set your production values:
nano .env << 'EOF'
OPENai_api_key=YOUR_openai_api_key_here
jwt_secret=your_production_secret_here
database_url=postgresql://admin:password@db:5432/asco_db
redis_url=redis://redis:6379/0
# ... (keep other settings)
EOF
```

### 3. Deploy with Docker Compose
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### 4. Run migrations
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec backend alembic upgrade head
```

### 5. Run seeders
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec backend python -m app.seeders.seed_all
```

### 6. Check status
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

## Important Notes
1. Make sure to update `.env` file with your actual Openai API key before running
2. All containers use the `shakti-network` network
3. Data is persisted in Docker volumes
4. The frontend is backend containers have health checks configured
5. The default credentials:
   - **admin@asco.gov** / **password123**
   - **dpo@asco.gov** / **password123**
   - **manager@asco.gov** / **password123**
   - **viewer@asco.gov** / **password123**
