import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

app = FastAPI(title="Backend Developer Portfolio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContactMessage(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    message: str = Field(..., min_length=10, max_length=2000)


@app.get("/")
def read_root():
    return {"message": "Portfolio API running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


# Static JSON-based data for projects and experience (can be moved to DB later)
class Project(BaseModel):
    title: str
    description: str
    stack: List[str]
    github: Optional[str] = None
    api_docs: Optional[str] = None


class ExperienceItem(BaseModel):
    title: str
    organization: str
    period: str
    description: str
    tags: List[str]


PROJECTS: List[Project] = [
    Project(
        title="Scalable Task Queue with Distributed Workers",
        description="Built a Celery + RabbitMQ based task processing system with autoscaling workers, metrics, and retries.",
        stack=["Python", "FastAPI", "Celery", "RabbitMQ", "Docker", "Prometheus"],
        github="https://github.com/example/scalable-task-queue",
        api_docs=None,
    ),
    Project(
        title="API Gateway & Auth Service",
        description="Kong gateway with JWT auth service, rate limiting, and observability integrated.",
        stack=["Kong", "PostgreSQL", "Redis", "Go", "Docker", "Grafana"],
        github="https://github.com/example/api-gateway-auth",
        api_docs="https://api.example.com/docs",
    ),
    Project(
        title="Event-Driven Microservices",
        description="Microservices communicating via Kafka with schema registry and idempotent consumers.",
        stack=["Node.js", "TypeScript", "Kafka", "PostgreSQL", "Docker", "Kubernetes"],
        github="https://github.com/example/event-driven-services",
        api_docs=None,
    ),
]

EXPERIENCE: List[ExperienceItem] = [
    ExperienceItem(
        title="Open-source Contributor",
        organization="FastAPI Ecosystem",
        period="2022 — Present",
        description="Contributed bug fixes and performance tweaks, improved docs, and triaged issues.",
        tags=["FastAPI", "Open Source", "Performance"],
    ),
    ExperienceItem(
        title="Freelance Backend Developer",
        organization="Remote",
        period="2021 — 2024",
        description="Delivered APIs, database schemas, and deployment pipelines for startups and solo founders.",
        tags=["APIs", "Databases", "CI/CD"],
    ),
    ExperienceItem(
        title="Personal Projects",
        organization="Various",
        period="Ongoing",
        description="R&D on distributed systems, caching strategies, and resilience patterns.",
        tags=["Kafka", "Caching", "Resilience"],
    ),
]


@app.get("/api/projects", response_model=List[Project])
def get_projects():
    return PROJECTS


@app.get("/api/experience", response_model=List[ExperienceItem])
def get_experience():
    return EXPERIENCE


@app.post("/api/contact")
def submit_contact(payload: ContactMessage):
    # Try to persist to MongoDB if available
    stored_id = None
    try:
        from database import create_document
        stored_id = create_document("message", payload)
    except Exception as e:
        # Database not available; continue without failing
        stored_id = None
    return {"status": "ok", "stored_id": stored_id}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
