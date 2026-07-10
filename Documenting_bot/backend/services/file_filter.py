import os

# Directories we never want to walk into
IGNORE_DIRS = {
    "node_modules", ".git", "venv", "env", "__pycache__",
    "dist", "build", ".next", ".vscode", ".idea",
    "target", "bin", "obj", ".pytest_cache", "coverage",
}

# File extensions we consider "readable source" for documentation purposes
INCLUDE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".c", ".cpp", ".h",
    ".cs", ".go", ".rb", ".php", ".html", ".css", ".scss", ".json",
    ".yml", ".yaml", ".md", ".sql", ".sh", ".ps1", ".toml", ".env.example",
}

# Config/meta files worth always including regardless of extension
ALWAYS_INCLUDE_FILES = {
    "package.json", "requirements.txt", "pyproject.toml", "dockerfile",
    "docker-compose.yml", "readme.md", "readme", "pipfile", "go.mod", "cargo.toml",
}

MAX_FILE_SIZE_BYTES = 50_000  # skip anything bigger than ~50KB


def walk_project(root: str) -> list[dict]:
    """
    Walks the project directory and returns a list of dicts:
    {relative_path, absolute_path, size}
    for every file we want to consider for documentation.
    """
    collected = []

    for dirpath, dirnames, filenames in os.walk(root):
        # prune ignored directories in-place so os.walk skips them entirely
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]

        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            ext = os.path.splitext(filename)[1]

            is_always_include = filename in ALWAYS_INCLUDE_FILES
            is_valid_ext = ext in INCLUDE_EXTENSIONS

            if not (is_always_include or is_valid_ext):
                continue

            try:
                size = os.path.getsize(full_path)
            except OSError:
                continue

            if size > MAX_FILE_SIZE_BYTES and not is_always_include:
                continue

            rel_path = os.path.relpath(full_path, root)
            collected.append({
                "relative_path": rel_path.replace("\\", "/"),
                "absolute_path": full_path,
                "size": size,
            })

    return collected


def build_tree_string(root: str, files: list[dict]) -> str:
    """
    Builds a simple indented tree string from the filtered file list,
    for use in the final documentation prompt.
    """
    paths = sorted(f["relative_path"] for f in files)
    lines = []
    for path in paths:
        depth = path.count("/")
        name = path.split("/")[-1]
        lines.append("  " * depth + "- " + name)
    return "\n".join(lines)