# Testing CI/CD

Sample project with FastAPI backend, React frontend, and GitHub Actions CI/CD pipeline.

## Structure

```
├── backend/        FastAPI app + pytest tests
├── frontend/       React (Vite) app + Vitest tests
├── docker-compose.yml
└── .github/workflows/ci-cd.yml
```

## Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Docker Compose (both services)
```bash
docker compose up --build
```

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci-cd.yml`) runs on every push/PR:

1. **Backend Tests** — pytest
2. **Frontend Tests** — Vitest + Vite build
3. **Docker Build & Push** — builds images and pushes to GHCR (on push to main/develop)
4. **Deploy** — placeholder step (customize for your platform)
