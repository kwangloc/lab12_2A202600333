# Deployment Information

## Public URL
https://2a202600333-truong-quang-loc-production.up.railway.app

## Platform
Railway

## Test Commands

### Health Check
```bash
curl https://2a202600333-truong-quang-loc-production.up.railway.app/health
# Expected: {"status": "ok", "version": "1.0.0", ...}
```

### API Test (with authentication)
```bash
$response = Invoke-RestMethod `
  -Uri "https://2a202600333-truong-quang-loc-production.up.railway.app/ask" `
  -Method Post `
  -Headers @{
    "X-API-Key"   = "my-secret-key"
    "Content-Type" = "application/json"
  } `
  -Body (@{ question = "What is Docker?" } | ConvertTo-Json)

$response
```

### JWT Authentication
```bash
# 1. Login to get token
$response = Invoke-RestMethod `
  -Uri "https://2a202600333-truong-quang-loc-production.up.railway.app/auth/token" `
  -Method Post `
  -Headers @{
    "Content-Type" = "application/json"
  } `
  -Body (@{
    username = "student"
    password = "demo123"
  } | ConvertTo-Json)

$response

# Expected: {"access_token": "eyJ...", "token_type": "bearer", "role": "user"}
```

### Readiness Probe
```bash
curl https://2a202600333-truong-quang-loc-production.up.railway.app/ready
# Expected: {"ready": true}
```

## Local Docker Test Commands (06-lab-complete)
```bash
# Build and start full stack
cd 06-lab-complete
docker compose up -d

# Scale to 3 replicas
docker compose up -d --scale agent=3

# Health check (through nginx LB on port 8080)
curl http://localhost:8080/health

# Ask with API key
curl -X POST http://localhost:8080/ask \
  -H "X-API-Key: my-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'

# Production readiness check
python check_production_ready.py
# Result: 20/20 checks passed (100%) — PRODUCTION READY!
```

## Environment Variables Set
- `PORT` — Application port (default: 8000)
- `REDIS_URL` — Redis connection string (default: redis://redis:6379)
- `AGENT_API_KEY` — API key for authentication
- `JWT_SECRET` — Secret key for JWT token signing
- `ENVIRONMENT` — staging / production
- `LOG_LEVEL` — INFO / DEBUG
- `DAILY_BUDGET_USD` — Daily cost guard budget (default: 10.0)
- `MONTHLY_BUDGET_USD` — Monthly cost guard budget (default: 100.0)
- `APP_NAME` — Application name
- `APP_VERSION` — Application version

## Screenshots
- [Deployment dashboard](./screenshots/dashboard.png)
- [Service running](./screenshots/running.png)
- [Test results](./screenshots/test.png)