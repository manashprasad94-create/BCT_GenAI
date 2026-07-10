from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import shutil

from services.extract import create_job_dir, extract_zip, clone_repo, cleanup_job
from services.file_filter import walk_project
from services.doc_pipeline import generate_documentation

load_dotenv()

app = FastAPI(title="AutoDocs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "AutoDocs backend is running"}


@app.post("/generate-docs")
async def generate_docs(
    zip_file: UploadFile = File(None),
    github_url: str = Form(None),
):
    if not zip_file and not github_url:
        raise HTTPException(status_code=400, detail="Provide either a zip_file or a github_url.")

    job_id, job_dir = create_job_dir()

    try:
        if zip_file:
            zip_path = os.path.join(job_dir, "upload.zip")
            with open(zip_path, "wb") as f:
                shutil.copyfileobj(zip_file.file, f)
            root = extract_zip(zip_path, job_dir)
        else:
            root = clone_repo(github_url, job_dir)

        files = walk_project(root)

        if not files:
            raise HTTPException(status_code=422, detail="No readable source files found in this project.")

        documentation = generate_documentation(root, files)

        return {
            "job_id": job_id,
            "file_count": len(files),
            "documentation": documentation,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Documentation generation failed: {str(e)}")

    finally:
        cleanup_job(job_dir)