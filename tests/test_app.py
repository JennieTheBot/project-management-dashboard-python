"""Tests for app.py dashboard functionality."""
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import (
    read_json,
    write_json,
    task_file,
    get_next_task_id,
    normalize_notes,
    normalize_task,
    load_task,
    save_task,
    delete_task,
    create_task,
    get_all_tasks,
    strip_html,
    safe_text,
    PRIORITIES,
    STAGES,
    WORKFLOW_MODES,
)


class TestStripHtml:
    """Tests for strip_html function."""

    def test_strip_html_basic(self):
        """Test basic HTML stripping."""
        result = strip_html("<p>Hello <b>world</b></p>")
        assert result == "Hello world"

    def test_strip_html_empty(self):
        """Test with None input."""
        assert strip_html(None) == ""

    def test_strip_html_dict(self):
        """Test with dict input."""
        result = strip_html({"key": "value"})
        assert "key" in result
        assert "value" in result

    def test_strip_html_list(self):
        """Test with list input."""
        result = strip_html(["item1", "item2"])
        assert "item1" in result
        assert "item2" in result

    def test_strip_html_unicode(self):
        """Test HTML entity conversion."""
        result = strip_html("&lt;div&gt;Test&lt;/div&gt;")
        assert result == "<div>Test</div>"


class TestSafeText:
    """Tests for safe_text function."""

    def test_safe_text_valid(self):
        """Test with valid string."""
        result = safe_text("Hello World")
        assert result == "Hello World"

    def test_safe_text_empty(self):
        """Test with empty string."""
        result = safe_text("")
        assert result == ""

    def test_safe_text_default(self):
        """Test with default value."""
        result = safe_text(None, "Default")
        assert result == "Default"


class TestReadWriteJson:
    """Tests for JSON file operations."""

    def test_read_json_valid(self, sample_task_file):
        """Test reading valid JSON file."""
        result = read_json(sample_task_file)
        assert result is not None
        assert result["id"] == "task-001"

    def test_read_json_invalid(self, temp_tasks_dir):
        """Test reading invalid JSON file."""
        invalid_file = temp_tasks_dir[0] / "invalid.json"
        invalid_file.write_text("not valid json")
        result = read_json(invalid_file)
        assert result is None

    def test_read_json_nonexistent(self, temp_tasks_dir):
        """Test reading non-existent file."""
        result = read_json(temp_tasks_dir[0] / "nonexistent.json")
        assert result is None

    def test_write_json(self, temp_tasks_dir):
        """Test writing JSON file."""
        test_file = temp_tasks_dir[0] / "test.json"
        test_data = {"key": "value", "number": 42}
        write_json(test_file, test_data)
        
        result = read_json(test_file)
        assert result == test_data


class TestTaskFile:
    """Tests for task_file function."""

    def test_task_file_path(self):
        """Test task file path generation."""
        result = task_file("task-001")
        assert result.name == "task-001.json"
        assert "tasks" in str(result)


class TestGetNextTaskId:
    """Tests for get_next_task_id function."""

    def test_get_next_task_id_empty(self, temp_tasks_dir):
        """Test with empty tasks directory."""
        # Temporarily replace TASKS_FOLDER
        with patch('app.TASKS_FOLDER', temp_tasks_dir[0]):
            result = get_next_task_id()
            assert result == "task-001"

    def test_get_next_task_id_existing(self, temp_tasks_dir):
        """Test with existing task files."""
        # Create some task files
        (temp_tasks_dir[0] / "task-001.json").write_text("{}")
        (temp_tasks_dir[0] / "task-005.json").write_text("{}")
        
        with patch('app.TASKS_FOLDER', temp_tasks_dir[0]):
            result = get_next_task_id()
            assert result == "task-006"


class TestNormalizeNotes:
    """Tests for normalize_notes function."""

    def test_normalize_notes_empty(self):
        """Test with empty notes."""
        result = normalize_notes({})
        assert result["goal"] == ""
        assert result["requirements"] == []
        assert result["blocked"] is False

    def test_normalize_notes_with_data(self, sample_task):
        """Test with populated notes."""
        result = normalize_notes(sample_task["notes"])
        assert result["goal"] == "Test goal"
        assert result["requirements"] == ["requirement 1", "requirement 2"]
        assert result["blocked"] is False

    def test_normalize_notes_requirements_string(self):
        """Test requirements as string."""
        notes = {"requirements": "single requirement"}
        result = normalize_notes(notes)
        assert result["requirements"] == ["single requirement"]

    def test_normalize_notes_blocked(self):
        """Test blocked status."""
        notes = {"blocked": True, "blockReason": "Waiting for review"}
        result = normalize_notes(notes)
        assert result["blocked"] is True
        assert result["blockReason"] == "Waiting for review"


class TestNormalizeTask:
    """Tests for normalize_task function."""

    def test_normalize_task_empty(self):
        """Test with empty task."""
        result = normalize_task({})
        assert "id" in result
        assert result["stage"] == "planning"
        assert result["priority"] == "medium"

    def test_normalize_task_valid(self, sample_task):
        """Test with valid task."""
        result = normalize_task(sample_task)
        assert result["id"] == "task-001"
        assert result["title"] == "Test Task"
        assert result["stage"] == "planning"
        assert result["priority"] == "high"
        assert result["workMode"] == "iterative"

    def test_normalize_task_invalid_stage(self):
        """Test with invalid stage."""
        task = {"stage": "invalid_stage"}
        result = normalize_task(task)
        assert result["stage"] == "planning"

    def test_normalize_task_invalid_priority(self):
        """Test with invalid priority."""
        task = {"priority": "invalid"}
        result = normalize_task(task)
        assert result["priority"] == "medium"


class TestLoadTask:
    """Tests for load_task function."""

    def test_load_task_exists(self, sample_task_file):
        """Test loading existing task."""
        with patch('app.TASKS_FOLDER', sample_task_file.parent):
            result = load_task("task-001")
        assert result is not None
        assert result["id"] == "task-001"

    def test_load_task_nonexistent(self):
        """Test loading non-existent task."""
        result = load_task("task-nonexistent")
        assert result is None


class TestSaveTask:
    """Tests for save_task function."""

    def test_save_task(self, temp_tasks_dir):
        """Test saving a task."""
        task = {
            "id": "task-002",
            "title": "Saved Task",
            "description": "Test",
            "priority": "high",
            "stage": "planning",
            "workMode": "immediate",
            "workflowStage": "initial",
            "assignee": "Jennie"
        }
        
        # Temporarily replace TASKS_FOLDER
        with patch('app.TASKS_FOLDER', temp_tasks_dir[0]):
            save_task(task)
            result = load_task("task-002")
            assert result is not None
            assert result["title"] == "Saved Task"


class TestDeleteTask:
    """Tests for delete_task function."""

    def test_delete_task(self, temp_tasks_dir, sample_task_file):
        """Test deleting a task."""
        # Copy sample file to temp dir for deletion test
        test_file = temp_tasks_dir[0] / "task-001.json"
        test_file.write_text(sample_task_file.read_text())
        
        with patch('app.TASKS_FOLDER', temp_tasks_dir[0]):
            delete_task("task-001")
            assert not test_file.exists()


class TestCreateTask:
    """Tests for create_task function."""

    def test_create_task(self, temp_tasks_dir):
        """Test creating a new task."""
        task = create_task(
            title="New Task",
            description="Test description",
            priority="high",
            workMode="iterative",
            assignee="Jennie"
        )
        
        assert task["id"] is not None
        assert task["title"] == "New Task"
        assert task["priority"] == "high"
        assert task["stage"] == "planning"
        assert task["workMode"] == "iterative"
        assert task["assignee"] == "Jennie"


class TestGetAllTasks:
    """Tests for get_all_tasks function."""

    def test_get_all_tasks_empty(self, temp_tasks_dir):
        """Test with empty tasks directory."""
        with patch('app.TASKS_FOLDER', temp_tasks_dir[0]):
            result = get_all_tasks()
            assert result == []

    def test_get_all_tasks_multiple(self, temp_tasks_dir):
        """Test with multiple tasks."""
        # Create multiple tasks
        for i in range(3):
            task = {
                "id": f"task-{i:03d}",
                "title": f"Task {i}",
                "description": f"Desc {i}",
                "priority": "medium",
                "stage": "planning"
            }
            (temp_tasks_dir[0] / f"task-{i:03d}.json").write_text(json.dumps(task))
        
        with patch('app.TASKS_FOLDER', temp_tasks_dir[0]):
            result = get_all_tasks()
            assert len(result) == 3


class TestConstants:
    """Tests for constant definitions."""

    def test_priorities(self):
        """Test PRIORITIES constant."""
        assert "urgent" in PRIORITIES
        assert "high" in PRIORITIES
        assert "medium" in PRIORITIES
        assert "low" in PRIORITIES

    def test_stages(self):
        """Test STAGES constant."""
        assert "planning" in STAGES
        assert "structuring" in STAGES
        assert "unit-testing" in STAGES
        assert "completion" in STAGES

    def test_workflow_modes(self):
        """Test WORKFLOW_MODES constant."""
        assert "iterative" in WORKFLOW_MODES
        assert "immediate" in WORKFLOW_MODES
