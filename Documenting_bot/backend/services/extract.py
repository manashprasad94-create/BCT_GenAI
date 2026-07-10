import os
import shutil
import uuid
import zipfile
from git import Repo


BASE_TMP_DIR = "tmp_jobs"


def create_job_dir() -> tuple[str, str]:
    """Creates a fresh temp directory for one documentation job."""
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(BASE_TMP_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    return job_id, job_dir


def extract_zip(zip_path: str, job_dir: str) -> str:
    """Extracts an uploaded zip into job_dir, returns the project root path."""
    extract_path = os.path.join(job_dir, "project")
    os.makedirs(extract_path, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    return _resolve_project_root(extract_path)


def clone_repo(github_url: str, job_dir: str) -> str:
    """Clones a GitHub repo (shallow) into job_dir, returns the project root path."""
    clone_path = os.path.join(job_dir, "project")
    Repo.clone_from(github_url, clone_path, depth=1)
    return _resolve_project_root(clone_path)


def _resolve_project_root(path: str) -> str:
    """
    Zips often extract into a single nested folder (e.g. project/my-repo-main/).
    If that's the case, step into it so we're pointing at the real root.
    """
    contents = os.listdir(path)
    if len(contents) == 1:
        nested = os.path.join(path, contents[0])
        if os.path.isdir(nested):
            return nested
    return path


def cleanup_job(job_dir: str):
    """Deletes a job's temp directory after we're done with it."""
    shutil.rmtree(job_dir, ignore_errors=True)