"""Unit tests for the convert_tasks.py utility module."""
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from convert_tasks import (
    load_json,
    save_json,
    strip_html,
    sanitize_task,
    process_file,
    main,
)


class TestStripHtml:
    """Tests for the strip_html function."""

    def test_plain_text(self):
        """Test stripping HTML from plain text."""
        result = strip_html("Hello World")
        assert result == "Hello World"

    def test_empty_string(self):
        """Test stripping HTML from empty string."""
        result = strip_html("")
        assert result == ""

    def test_none_value(self):
        """Test stripping HTML from None."""
        result = strip_html(None)
        assert result == ""

    def test_html_tags_removed(self):
        """Test that HTML tags are removed."""
        text = "<b>Bold</b> and <i>italic</i>"
        result = strip_html(text)
        assert "<b>" not in result
        assert "<i>" not in result
        assert "Bold" in result
        assert "italic" in result

    def test_html_entities_decoded(self):
        """Test that HTML entities are decoded."""
        text = "&lt;tag&gt; &amp; entity"
        result = strip_html(text)
        assert result == "<tag> & entity"

    def test_brl_tags_converted_to_spaces(self):
        """Test that <br> tags are converted to spaces."""
        text = "Line 1<br/>Line 2<br>Line 3"
        result = strip_html(text)
        # br tags become spaces, not newlines
        assert " " in result
        assert "Line 1" in result
        assert "Line 2" in result

    def test_list_items_converted_to_dashes(self):
        """Test that <li> tags are converted to list items."""
        text = "<li>Item 1</li><li>Item 2</li>"
        result = strip_html(text)
        assert result.startswith("- Item 1")

    def test_dict_value_converts_to_json(self):
        """Test stripping HTML from a dict value converts to JSON string."""
        data = {"key": "<b>value</b>"}
        result = strip_html(data)
        # Dicts are converted to JSON string, tags preserved inside
        assert "key" in result
        assert "value" in result

    def test_list_value_converts_to_json(self):
        """Test stripping HTML from a list value converts to JSON string."""
        data = ["<b>item1</b>", "<i>item2</i>"]
        result = strip_html(data)
        # Lists are converted to JSON string, tags preserved inside
        assert "item1" in result
        assert "item2" in result

    def test_consecutive_spaces_collapsed(self):
        """Test that multiple consecutive spaces are collapsed."""
        text = "Line 1     Line 2"
        result = strip_html(text)
        assert "  " not in result or result == "Line 1 Line 2"

    def test_carriage_returns_normalized(self):
        """Test that \r\n is normalized to space."""
        text = "Line 1\r\nLine 2\r\nLine 3"
        result = strip_html(text)
        assert "\r" not in result


class TestLoadJson:
    """Tests for the load_json function."""

    def test_loads_valid_json(self, tmp_path: Path, sample_task):
        """Test loading valid JSON file."""
        test_file = tmp_path / "test.json"
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(sample_task, f)
        
        result = load_json(test_file)
        assert result == sample_task

    def test_returns_none_on_invalid_json(self, tmp_path: Path):
        """Test that invalid JSON returns None."""
        test_file = tmp_path / "invalid.json"
        test_file.write_text("{ invalid json }", encoding="utf-8")
        
        result = load_json(test_file)
        assert result is None

    def test_returns_none_on_nonexistent_file(self, tmp_path: Path):
        """Test that missing file returns None."""
        test_file = tmp_path / "missing.json"
        
        result = load_json(test_file)
        assert result is None


class TestSaveJson:
    """Tests for the save_json function."""

    def test_saves_valid_json(self, tmp_path: Path, sample_task):
        """Test saving valid JSON file."""
        test_file = tmp_path / "output.json"
        
        save_json(test_file, sample_task)
        
        assert test_file.exists()
        loaded = load_json(test_file)
        assert loaded == sample_task

    def test_json_is_pretty_printed(self, tmp_path: Path, sample_task):
        """Test that JSON is saved with indentation."""
        test_file = tmp_path / "output.json"
        
        save_json(test_file, sample_task)
        
        content = test_file.read_text(encoding="utf-8")
        assert "  " in content  # Has indentation


class TestSanitizeTask:
    """Tests for the sanitize_task function."""

    def test_sanitizes_empty_title(self, task_with_invalid_data):
        """Test that empty title becomes 'Untitled task'."""
        task_with_invalid_data["title"] = ""
        result = sanitize_task(task_with_invalid_data)
        assert result["title"] == "Untitled task"

    def test_sanitizes_none_description(self, task_with_invalid_data):
        """Test that None description becomes default."""
        result = sanitize_task(task_with_invalid_data)
        assert result["description"] == "No description provided."

    def test_normalizes_invalid_priority(self, task_with_invalid_data):
        """Test that invalid priority defaults to 'medium'."""
        result = sanitize_task(task_with_invalid_data)
        assert result["priority"] == "medium"

    def test_normalizes_valid_priority(self):
        """Test that valid priorities are preserved."""
        task = {"priority": "urgent"}
        result = sanitize_task(task)
        assert result["priority"] == "urgent"

        task = {"priority": "low"}
        result = sanitize_task(task)
        assert result["priority"] == "low"

    def test_normalizes_invalid_stage(self, task_with_invalid_data):
        """Test that invalid stage defaults to 'planning'."""
        result = sanitize_task(task_with_invalid_data)
        assert result["stage"] == "planning"

    def test_normalizes_invalid_work_mode(self, task_with_invalid_data):
        """Test that invalid work mode defaults to 'iterative'."""
        result = sanitize_task(task_with_invalid_data)
        assert result["workMode"] == "iterative"

    def test_converts_string_requirements_to_list(self, task_with_invalid_data):
        """Test that string requirements are converted to list."""
        result = sanitize_task(task_with_invalid_data)
        assert isinstance(result["notes"]["requirements"], list)

    def test_empty_string_requirements_becomes_empty_list(self, task_with_invalid_data):
        """Test that empty string requirements becomes empty list."""
        task_with_invalid_data["notes"]["requirements"] = ""
        result = sanitize_task(task_with_invalid_data)
        assert result["notes"]["requirements"] == []

    def test_preserves_valid_requirements_list(self, task_with_html):
        """Test that valid requirements list is preserved."""
        result = sanitize_task(task_with_html)
        assert len(result["notes"]["requirements"]) == 2

    def test_sets_default_assignee(self, task_with_invalid_data):
        """Test that empty assignee becomes 'Jennie'."""
        result = sanitize_task(task_with_invalid_data)
        assert result["assignee"] == "Jennie"

    def test_converts_string_boolean_blocked(self, task_with_invalid_data):
        """Test that string 'true' boolean is converted to actual boolean."""
        result = sanitize_task(task_with_invalid_data)
        assert result["notes"]["blocked"] is True

    def test_handles_invalid_time_estimate(self, task_with_invalid_data):
        """Test that invalid time estimate structure is handled."""
        result = sanitize_task(task_with_invalid_data)
        assert isinstance(result["notes"]["timeEstimate"], dict)

    def test_sanitizes_html_in_title(self, task_with_html):
        """Test that HTML in title is stripped."""
        result = sanitize_task(task_with_html)
        assert "<h1>" not in result["title"]
        assert "Task with HTML" in result["title"]

    def test_sanitizes_html_in_description(self, task_with_html):
        """Test that HTML in description is stripped."""
        result = sanitize_task(task_with_html)
        assert "<b>" not in result["description"]
        assert "<i>" not in result["description"]
        assert "<br" not in result["description"]

    def test_preserves_completion_summary(self):
        """Test that completion summary is preserved when present."""
        task = {
            "title": "Test",
            "description": "Test",
            "completion_summary": "Completed successfully",
        }
        result = sanitize_task(task)
        assert result["completion_summary"] == "Completed successfully"


class TestProcessFile:
    """Tests for the process_file function."""

    def test_process_valid_task_file(self, tmp_path: Path, sample_task):
        """Test processing a valid task file."""
        test_file = tmp_path / "task-001.json"
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(sample_task, f, indent=2)
        
        process_file(test_file)
        
        assert (test_file.with_suffix(".json.bak")).exists()
        loaded = load_json(test_file)
        assert loaded is not None

    def test_process_invalid_json_file(self, tmp_path: Path, capsys):
        """Test processing an invalid JSON file."""
        test_file = tmp_path / "task-invalid.json"
        test_file.write_text("{ invalid }", encoding="utf-8")
        
        process_file(test_file)
        
        captured = capsys.readouterr()
        assert "SKIP invalid json" in captured.out


class TestMain:
    """Tests for the main function."""

    def test_main_no_tasks_found(self, tmp_path: Path, capsys):
        """Test main when no task files exist."""
        with patch("convert_tasks.BASE_DIR", tmp_path):
            with patch("convert_tasks.TASKS_DIR", tmp_path / "tasks"):
                (tmp_path / "tasks").mkdir()
                main()
        
        captured = capsys.readouterr()
        assert "No task files found" in captured.out

    def test_main_processes_files(self, tmp_path: Path, sample_task, capsys):
        """Test main processing multiple task files."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        
        task_file = tasks_dir / "task-001.json"
        with open(task_file, "w", encoding="utf-8") as f:
            json.dump(sample_task, f, indent=2)
        
        with patch("convert_tasks.BASE_DIR", tmp_path):
            with patch("convert_tasks.TASKS_DIR", tasks_dir):
                main()
        
        captured = capsys.readouterr()
        assert "CLEANED" in captured.out
        assert task_file.with_suffix(".json.bak").exists()
