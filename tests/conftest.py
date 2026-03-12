"""Pytest configuration and shared fixtures."""
import json
import tempfile
from pathlib import Path
from typing import Generator, Dict, Any

import pytest


@pytest.fixture
def temp_tasks_dir() -> Generator[tuple[Path, str], None, None]:
    """Create a temporary tasks directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tasks_dir = Path(tmpdir) / "tasks"
        tasks_dir.mkdir()
        yield tasks_dir, tmpdir


@pytest.fixture
def sample_task() -> Dict[str, Any]:
    """Sample task data for testing."""
    return {
        "id": "task-001",
        "title": "Test Task",
        "description": "This is a test task description",
        "priority": "high",
        "stage": "planning",
        "workMode": "iterative",
        "workflowStage": "initial",
        "createdAt": "2026-03-12T10:00:00.000000",
        "updatedAt": "2026-03-12T10:00:00.000000",
        "assignee": "Jennie",
        "completion_summary": "",
        "notes": {
            "goal": "Test goal",
            "requirements": ["requirement 1", "requirement 2"],
            "feedback": "",
            "blocked": False,
            "blockReason": None,
            "unblockNeeded": None,
            "timeEstimate": {
                "planned": "1 hour",
                "actual": None
            }
        }
    }


@pytest.fixture
def sample_task_file(temp_tasks_dir, sample_task) -> Path:
    """Create a sample task JSON file."""
    tasks_dir, _ = temp_tasks_dir
    task_file = tasks_dir / "task-001.json"
    task_file.write_text(json.dumps(sample_task, indent=2))
    return task_file


@pytest.fixture
def app_py_path() -> Path:
    """Get path to app.py for import testing."""
    return Path(__file__).parent.parent / "app.py"
