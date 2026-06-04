from pathlib import Path


def test_required_files_exist():
    root = Path(__file__).resolve().parents[1]

    required_files = [
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

    for file_path in required_files:
        assert (root / file_path).exists(), f"Missing required file: {file_path}"


def test_readme_mentions_project_scope():
    root = Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text(encoding="utf-8").lower()

    assert "computer vision" in readme
    assert "educational" in readme
    assert "security" in readme
