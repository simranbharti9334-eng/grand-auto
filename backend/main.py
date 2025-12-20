from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import secrets

app = FastAPI(
    title="Grand Auto API",
    version="1.0.0"
)

# ---------------- CORS (IMPORTANT) ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev ke liye OK
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- BASIC AUTH ----------------
security = HTTPBasic()

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    if not (
        secrets.compare_digest(credentials.username, ADMIN_USERNAME)
        and secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# ---------------- MODEL ----------------
class Project(BaseModel):
    id: int = Field(..., gt=0)
    title: str = Field(..., min_length=3)


# ---------------- DATA ----------------
projects = [
    {"id": 1, "title": "Project One"},
    {"id": 2, "title": "Project Two"},
]


# ---------------- ROUTES ----------------
@app.get("/")
def root():
    return {"status": "API running"}


@app.get("/admin/projects")
def get_projects(admin: str = Depends(verify_admin)):
    return projects


@app.post("/admin/projects")
def add_project(project: Project, admin: str = Depends(verify_admin)):
    for p in projects:
        if p["id"] == project.id:
            raise HTTPException(
                status_code=400,
                detail="Project with this ID already exists"
            )

    projects.append(project.dict())
    return {"message": "Project added successfully"}


@app.delete("/admin/projects/{project_id}")
def delete_project(project_id: int, admin: str = Depends(verify_admin)):
    for p in projects:
        if p["id"] == project_id:
            projects.remove(p)
            return {"message": "Project deleted"}

    raise HTTPException(status_code=404, detail="Project not found")