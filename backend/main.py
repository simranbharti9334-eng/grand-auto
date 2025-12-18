from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import os
import uuid

app = FastAPI()

# --------------------
# CORS
# --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# Paths
# --------------------
BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, "projects.json")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# --------------------
# Helpers
# --------------------
def read_projects():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def write_projects(projects):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2)

# --------------------
# Root
# --------------------
@app.get("/")
def root():
    return {"message": "FastAPI is running"}

# --------------------
# GET Projects
# --------------------
@app.get("/projects")
def get_projects():
    return read_projects()

# --------------------
# ADD Project (Image Upload)
# --------------------
@app.post("/projects")
def add_project(
    title: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(...)
):
    projects = read_projects()

    file_ext = image.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as f:
        f.write(image.file.read())

    new_project = {
        "id": len(projects) + 1,
        "title": title,
        "description": description,
        "image": f"/uploads/{file_name}"
    }

    projects.append(new_project)
    write_projects(projects)

    return {
        "message": "Project added successfully",
        "project": new_project
    }

# --------------------
# UPDATE Project
# --------------------
@app.put("/projects/{project_id}")
def update_project(
    project_id: int,
    title: str = Form(...),
    description: str = Form(...)
):
    projects = read_projects()

    for project in projects:
        if project["id"] == project_id:
            project["title"] = title
            project["description"] = description
            write_projects(projects)
            return {"message": "Project updated", "project": project}

    raise HTTPException(status_code=404, detail="Project not found")

# --------------------
# DELETE Project
# --------------------
@app.delete("/projects/{project_id}")
def delete_project(project_id: int):
    projects = read_projects()
    new_projects = [p for p in projects if p["id"] != project_id]

    if len(projects) == len(new_projects):
        raise HTTPException(status_code=404, detail="Project not found")

    write_projects(new_projects)
    return {"message": "Project deleted successfully"}