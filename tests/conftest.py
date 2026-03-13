"""Shared pytest fixtures for dashboard tests."""
import json
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest


@pytest.fixture
def sample_task() -> Dict[str, Any]:
    """Create a sample task dictionary for testing."""
    return {
        "id": "task-001",
        "title": "Test Task",
        "description": "This is a test task <b>with HTML</b>",
        "priority": "high",
        "stage": "planning",
        "workMode": "iterative",
        "workflowStage": "initial",
        "createdAt": "2026-03-12T10:00:00.000000",
        "updatedAt": "2026-03-12T10:00:00.000000",
        "assignee": "Jennie",
        "completion_summary": None,
        "notes": {
            "goal": "Test goal",
            "requirements": ["Requirement 1", "Requirement 2"],
            "feedback": None,
            "blocked": False,
            "blockReason": None,
            "unblockNeeded": None,
            "timeEstimate": {
                "planned": "1 hour",
                "actual": None,
            },
        },
    }


@pytest.fixture
def task_with_html() -> Dict[str, Any]:
    """Create a task with HTML content that needs sanitization."""
    return {
        "id": "task-002",
        "title": "<h1>Task with HTML</h1>",
        "description": "Description with <b>bold</b>, <i>italic</i>, and <br/> line breaks",
        "priority": "medium",
        "stage": "structuring",
        "workMode": "immediate",
        "workflowStage": "executing",
        "createdAt": "2026-03-12T11:00:00.000000",
        "updatedAt": "2026-03-12T11:00:00.000000",
        "assignee": "Jennie",
        "completion_summary": None,
        "notes": {
            "goal": "<p>Goal with paragraph</p>",
            "requirements": ["<li>Item 1</li>", "<li>Item 2</li>"],
            "feedback": "<div>Feedback content</div>",
            "blocked": True,
            "blockReason": "Waiting on dependency",
            "unblockNeeded": "Task-003 to be completed",
            "timeEstimate": {
                "planned": "2 hours",
                "actual": "2.5 hours",
            },
        },
    }


@pytest.fixture
def task_with_invalid_data() -> Dict[str, Any]:
    """Create a task with invalid or missing data to test validation."""
    return {
        "id": "task-003",
        "title": "",  # Empty title
        "description": None,  # None description
        "priority": "invalid_priority",  # Invalid priority
        "stage": "invalid_stage",  # Invalid stage
        "workMode": "unknown_mode",  # Invalid work mode
        "workflowStage": "unknown_stage",
        "createdAt": "2026-03-12T12:00:00.000000",
        "updatedAt": "2026-03-12T12:00:00.000000",
        "assignee": "",  # Empty assignee
        "completion_summary": "",
        "notes": {
            "goal": None,
            "requirements": "single_string_not_list",  # String instead of list
            "feedback": None,
            "blocked": "true",  # String boolean
            "blockReason": "",
            "unblockNeeded": "",
            "timeEstimate": "string_not_dict",  # String instead of dict
        },
    }


@pytest.fixture
def empty_tasks_dir(tmp_path: Path) -> Path:
    """Create an empty temporary tasks directory."""
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()
    return tasks_dir


@pytest.fixture
def tasks_dir_with_files(tmp_path: Path, sample_task: Dict[str, Any]) -> Path:
    """Create a temporary tasks directory with sample task files."""
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()
    
    task_file = tasks_dir / "task-001.json"
    with open(task_file, "w", encoding="utf-8") as f:
        json.dump(sample_task, f, indent=2)
    
    return tasks_dir


@pytest.fixture
def temp_base_dir(tmp_path: Path) -> Path:
    """Create a temporary base directory structure."""
    (tmp_path / "tasks").mkdir()
    return tmp_path
