from pathlib import Path

REQUIRED_FILES = [
    "README.md",
    "README_CN.md",
    "LICENSE",
    "requirements.txt",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "docs/quickstart.md",
    "docs/project_overview.md",
    "docs/model_file_policy.md",
]

FORBIDDEN_DIRS = {
    ".idea",
    "__pycache__",
}

FORBIDDEN_FILES = {
    ".DS_Store",
}

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "ENV",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}


def iter_repository_paths(root: Path):
    for path in root.rglob("*"):
        relative_parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS for part in relative_parts):
            continue
        yield path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    missing = []

    for file_path in REQUIRED_FILES:
        if not (root / file_path).exists():
            missing.append(file_path)

    if missing:
        print("Missing required files:")
        for item in missing:
            print(f"  - {item}")
        return 1

    found_forbidden = []

    for path in iter_repository_paths(root):
        if path.is_dir() and path.name in FORBIDDEN_DIRS:
            found_forbidden.append(str(path.relative_to(root)))
        elif path.is_file() and (path.name in FORBIDDEN_FILES or path.suffix == ".pyc"):
            found_forbidden.append(str(path.relative_to(root)))

    if found_forbidden:
        print("Found files or directories that should not be committed:")
        for item in found_forbidden:
            print(f"  - {item}")
        return 1

    print("Repository health check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
