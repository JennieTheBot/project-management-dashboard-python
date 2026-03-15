"""Tests for convert_tasks.py utility functions."""
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from convert_tasks import strip_html, load_json, save_json, sanitize_task, process_file


class TestStripHtml:
    """Tests for strip_html function (shared with app.py)."""

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
        assert result == "Test" # After unescaping and stripping tags


class TestLoadJson:
    """Tests for load_json function."""

    def test_load_json_valid(self, tmp_path):
        """Test loading valid JSON file."""
        test_file = tmp_path / "test.json"
        test_data = {"key": "value", "number": 42}
        test_file.write_text(json.dumps(test_data))
        
        result = load_json(test_file)
        assert result == test_data

    def test_load_json_invalid(self, tmp_path):
        """Test loading invalid JSON file."""
        test_file = tmp_path / "invalid.json"
        test_file.write_text("not valid json")
        result = load_json(test_file)
        assert result is None

    def test_load_json_nonexistent(self, tmp_path):
        """Test loading non-existent file."""
        result = load_json(tmp_path / "nonexistent.json")
        assert result is None


class TestSaveJson:
    """Tests for save_json function."""

    def test_save_json(self, tmp_path):
        """Test writing JSON file."""
        test_file = tmp_path / "test.json"
        test_data = {"key": "value", "number": 42}
        save_json(test_file, test_data)
        
        result = test_file.read_text()
        assert "key" in result
        assert "value" in result
        assert "42" in result


class TestSanitizeTask:
    """Tests for sanitize_task function."""

    def test_sanitize_task_empty(self):
        """Test with empty task."""
        result = sanitize_task({})
        assert result["title"] == "Untitled task"
        assert result["description"] == "No description provided."
        assert result["priority"] == "medium"
        assert result["stage"] == "planning"
        assert result["workMode"] == "iterative"

    def test_sanitize_task_valid(self):
        """Test with valid task data."""
        task = {
            "id": "task-001",
            "title": "Test Task",
            "description": "Test description",
            "priority": "high",
            "stage": "structuring",
            "workMode": "immediate",
            "notes": {
                "goal": "Test goal",
                "requirements": ["req1", "req2"],
                "blocked": False
            }
        }
        result = sanitize_task(task)
        assert result["title"] == "Test Task"
        assert result["description"] == "Test description"
        assert result["priority"] == "high"
        assert result["stage"] == "structuring"
        assert result["workMode"] == "immediate"
        assert result["notes"]["goal"] == "Test goal"
        assert result["notes"]["requirements"] == ["req1", "req2"]

    def test_sanitize_task_with_html(self):
        """Test task with HTML in fields."""
        task = {
            "title": "<b>Bold</b> Title",
            "description": "<p>Paragraph</p> text",
            "priority": "urgent"
        }
        result = sanitize_task(task)
        assert result["title"] == "Bold Title"
        assert result["description"] == "Paragraph text"
        assert result["priority"] == "urgent"

    def test_sanitize_task_invalid_priority(self):
        """Test with invalid priority."""
        task = {"priority": "invalid_priority"}
        result = sanitize_task(task)
        assert result["priority"] == "medium"

    def test_sanitize_task_invalid_stage(self):
        """Test with invalid stage."""
        task = {"stage": "invalid_stage"}
        result = sanitize_task(task)
        assert result["stage"] == "planning"

    def test_sanitize_task_invalid_workmode(self):
        """Test with invalid work mode."""
        task = {"workMode": "invalid_mode"}
        result = sanitize_task(task)
        assert result["workMode"] == "iterative"

    def test_sanitize_task_time_estimate(self):
        """Test time estimate handling."""
        task = {
            "notes": {
                "timeEstimate": {
                    "planned": "1 hour",
                    "actual": "2 hours"
                }
            }
        }
        result = sanitize_task(task)
        assert result["notes"]["timeEstimate"]["planned"] == "1 hour"
        assert result["notes"]["timeEstimate"]["actual"] == "2 hours"

    def test_sanitize_task_blocked(self):
        """Test blocked status handling."""
        task = {
            "notes": {
                "blocked": True,
                "blockReason": "Waiting for approval",
                "unblockNeeded": "Manager sign-off"
            }
        }
        result = sanitize_task(task)
        assert result["notes"]["blocked"] is True
        assert result["notes"]["blockReason"] == "Waiting for approval"
        assert result["notes"]["unblockNeeded"] == "Manager sign-off"

    def test_sanitize_task_requirements_string(self):
        """Test requirements as string."""
        task = {
            "notes": {
                "requirements": "single requirement string"
            }
        }
        result = sanitize_task(task)
        assert result["notes"]["requirements"] == ["single requirement string"]

    def test_sanitize_task_requirements_empty(self):
        """Test empty requirements."""
        task = {
            "notes": {
                "requirements": ""
            }
        }
        result = sanitize_task(task)
        assert result["notes"]["requirements"] == []


class TestProcessFile:
    """Tests for process_file function (integration)."""

    def test_process_file_valid(self, tmp_path):
        """Test processing valid task file."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        
        task_file = tasks_dir / "task-001.json"
        task_data = {
            "id": "task-001",
            "title": "<b>Test</b> Task",
            "description": "Test description",
            "priority": "high",
            "stage": "planning"
        }
        task_file.write_text(json.dumps(task_data))
        
        # Mock TASKS_DIR
        with patch('convert_tasks.TASKS_DIR', tasks_dir):
            process_file(task_file)
            
            # Check file was updated
            result = json.loads(task_file.read_text())
            assert result["title"] == "Test Task"

    def test_process_file_invalid(self, tmp_path):
        """Test processing invalid JSON file."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        
        task_file = tasks_dir / "invalid.json"
        task_file.write_text("not valid json")
        
        with patch('convert_tasks.TASKS_DIR', tasks_dir):
            # Should handle gracefully
            try:
                process_file(task_file)
            except Exception:
                pytest.fail("process_file should handle invalid JSON gracefully")

    def test_process_file_creates_backup(self, tmp_path):
        """Test that backup file is created."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        
        task_file = tasks_dir / "task-001.json"
        task_file.write_text('{"title": "Original"}')
        
        with patch('convert_tasks.TASKS_DIR', tasks_dir):
            process_file(task_file)
            
            backup_file = tasks_dir / "task-001.json.bak"
            assert backup_file.exists()
