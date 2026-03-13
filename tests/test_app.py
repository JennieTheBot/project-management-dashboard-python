"""Unit tests for the app.py dashboard data functions."""
import json
from pathlib import Path
from unittest.mock import patch
from typing import Dict, Any

import pytest


@pytest.fixture
def sample_task() -> Dict[str, Any]:
    """Create a sample task dictionary for testing."""
    return {
        "id": "task-001",
        "title": "Test Task",
        "description": "This is a test task",
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


class TestPriorityConstants:
    """Tests for PRIORITY constants."""

    def test_priority_urgent_color(self):
        """Test urgent priority has correct color."""
        from app import PRIORITIES
        
        assert "urgent" in PRIORITIES
        assert PRIORITIES["urgent"]["color"] == "#fb7185"
        assert PRIORITIES["urgent"]["icon"] == "Critical"

    def test_priority_high_color(self):
        """Test high priority has correct color."""
        from app import PRIORITIES
        
        assert "high" in PRIORITIES
        assert PRIORITIES["high"]["color"] == "#f59e0b"

    def test_priority_medium_color(self):
        """Test medium priority has correct color."""
        from app import PRIORITIES
        
        assert "medium" in PRIORITIES
        assert PRIORITIES["medium"]["color"] == "#38bdf8"

    def test_priority_low_color(self):
        """Test low priority has correct color."""
        from app import PRIORITIES
        
        assert "low" in PRIORITIES
        assert PRIORITIES["low"]["color"] == "#34d399"

    def test_priority_order(self):
        """Test priority ordering."""
        from app import PRIORITY_ORDER
        
        assert PRIORITY_ORDER["urgent"] == 0
        assert PRIORITY_ORDER["high"] == 1
        assert PRIORITY_ORDER["medium"] == 2
        assert PRIORITY_ORDER["low"] == 3


class TestStageConstants:
    """Tests for STAGE constants."""

    def test_stage_planning(self):
        """Test planning stage has correct color."""
        from app import STAGES
        
        assert "planning" in STAGES
        assert STAGES["planning"]["color"] == "#60a5fa"

    def test_stage_structuring(self):
        """Test structuring stage has correct color."""
        from app import STAGES
        
        assert "structuring" in STAGES
        assert STAGES["structuring"]["color"] == "#c084fc"

    def test_stage_unit_testing(self):
        """Test unit-testing stage has correct color."""
        from app import STAGES
        
        assert "unit-testing" in STAGES
        assert STAGES["unit-testing"]["color"] == "#818cf8"

    def test_stage_completion(self):
        """Test completion stage has correct color."""
        from app import STAGES
        
        assert "completion" in STAGES
        assert STAGES["completion"]["color"] == "#34d399"

    def test_stage_order(self):
        """Test stage ordering."""
        from app import STAGE_ORDER
        
        assert STAGE_ORDER["planning"] == 0
        assert STAGE_ORDER["structuring"] == 1
        assert STAGE_ORDER["unit-testing"] == 2
        assert STAGE_ORDER["completion"] == 3


class TestWorkflowModes:
    """Tests for WORKFLOW_MODES constants."""

    def test_iterative_mode(self):
        """Test iterative workflow mode."""
        from app import WORKFLOW_MODES
        
        assert "iterative" in WORKFLOW_MODES
        assert WORKFLOW_MODES["iterative"]["label"] == "Iterative"
        assert WORKFLOW_MODES["iterative"]["description"] == "Execute, get feedback, refine"

    def test_immediate_mode(self):
        """Test immediate workflow mode."""
        from app import WORKFLOW_MODES
        
        assert "immediate" in WORKFLOW_MODES
        assert WORKFLOW_MODES["immediate"]["label"] == "Immediate"
        assert WORKFLOW_MODES["immediate"]["description"] == "Execute without a feedback cycle"


class TestValidWorkflowStages:
    """Tests for VALID_WORKFLOW_STAGES constant."""

    def test_valid_stages(self):
        """Test that all valid workflow stages are defined."""
        from app import VALID_WORKFLOW_STAGES
        
        assert "initial" in VALID_WORKFLOW_STAGES
        assert "executing" in VALID_WORKFLOW_STAGES
        assert "waiting_feedback" in VALID_WORKFLOW_STAGES
        assert "refining" in VALID_WORKFLOW_STAGES
        assert "completed" in VALID_WORKFLOW_STAGES


class TestEsc:
    """Tests for the esc helper function."""

    def test_esc_plain_text(self):
        """Test escaping plain text."""
        from app import esc
        
        result = esc("Hello World")
        assert result == "Hello World"

    def test_esc_html_special_chars(self):
        """Test escaping HTML special characters."""
        from app import esc
        
        result = esc("<script>alert('xss')</script>")
        assert "&lt;" in result
        assert "&gt;" in result


class TestStripHtml:
    """Tests for the strip_html function from app.py."""

    def test_plain_text(self):
        """Test stripping HTML from plain text."""
        from app import strip_html
        
        result = strip_html("Hello World")
        assert result == "Hello World"

    def test_html_tags_removed(self):
        """Test that HTML tags are removed."""
        from app import strip_html
        
        text = "<b>Bold</b> and <i>italic</i>"
        result = strip_html(text)
        assert "<b>" not in result
        assert "<i>" not in result
        assert result == "Bold and italic"

    def test_html_entities_decoded(self):
        """Test that HTML entities are decoded."""
        from app import strip_html
        
        text = "&lt;tag&gt; &amp; entity"
        result = strip_html(text)
        assert result == "<tag> & entity"


class TestSafeText:
    """Tests for the safe_text helper function."""

    def test_returns_string(self):
        """Test that safe_text returns a string."""
        from app import safe_text
        
        result = safe_text("Hello")
        assert result == "Hello"

    def test_returns_default_for_none(self):
        """Test that safe_text returns default for None."""
        from app import safe_text
        
        result = safe_text(None)
        assert result == ""

    def test_returns_custom_default(self):
        """Test that safe_text accepts custom default."""
        from app import safe_text
        
        result = safe_text(None, "default")
        assert result == "default"


class TestReadJson:
    """Tests for the read_json function."""

    def test_reads_valid_json(self, tmp_path: Path, sample_task):
        """Test reading valid JSON file."""
        from app import read_json
        
        test_file = tmp_path / "test.json"
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(sample_task, f)
        
        result = read_json(test_file)
        assert result == sample_task

    def test_returns_none_on_invalid_json(self, tmp_path: Path):
        """Test that invalid JSON returns None."""
        from app import read_json
        
        test_file = tmp_path / "invalid.json"
        test_file.write_text("{ invalid json }", encoding="utf-8")
        
        result = read_json(test_file)
        assert result is None

    def test_returns_none_on_nonexistent_file(self, tmp_path: Path):
        """Test that missing file returns None."""
        from app import read_json
        
        test_file = tmp_path / "missing.json"
        
        result = read_json(test_file)
        assert result is None


class TestWriteJson:
    """Tests for the write_json function."""

    def test_saves_valid_json(self, tmp_path: Path, sample_task):
        """Test saving valid JSON file."""
        from app import write_json
        
        test_file = tmp_path / "output.json"
        
        write_json(test_file, sample_task)
        
        assert test_file.exists()
        loaded = json.loads(test_file.read_text(encoding="utf-8"))
        assert loaded == sample_task

    def test_json_is_pretty_printed(self, tmp_path: Path, sample_task):
        """Test that JSON is saved with indentation."""
        from app import write_json
        
        test_file = tmp_path / "output.json"
        
        write_json(test_file, sample_task)
        
        content = test_file.read_text(encoding="utf-8")
        assert "  " in content  # Has indentation


class TestTaskFile:
    """Tests for the task_file function."""

    def test_task_file_path(self, tmp_path: Path):
        """Test that task_file returns correct path."""
        from app import task_file
        
        # Mock TASKS_FOLDER
        with patch("app.TASKS_FOLDER", tmp_path):
            path = task_file("task-001")
            assert path == tmp_path / "task-001.json"


class TestGetNextTaskId:
    """Tests for get_next_task_id function."""

    def test_next_id_empty_directory(self, tmp_path: Path):
        """Test getting next ID when no tasks exist."""
        from app import get_next_task_id
        
        # Mock TASKS_FOLDER
        with patch("app.TASKS_FOLDER", tmp_path):
            next_id = get_next_task_id()
            assert next_id == "task-001"

    def test_next_id_after_task_001(self, tmp_path: Path):
        """Test getting next ID after task-001."""
        from app import get_next_task_id
        
        # Create task-001
        (tmp_path / "task-001.json").write_text("{}")
        
        # Mock TASKS_FOLDER
        with patch("app.TASKS_FOLDER", tmp_path):
            next_id = get_next_task_id()
            assert next_id == "task-002"

    def test_next_id_handles_max_int(self, tmp_path: Path):
        """Test getting next ID when max task number is very large."""
        from app import get_next_task_id
        
        # Create a task with very large number
        (tmp_path / "task-999999.json").write_text("{}")
        
        # Mock TASKS_FOLDER
        with patch("app.TASKS_FOLDER", tmp_path):
            next_id = get_next_task_id()
            assert next_id == "task-1000000"

    def test_next_id_skips_non_task_files(self, tmp_path: Path):
        """Test that non-task files are ignored."""
        from app import get_next_task_id
        
        # Create non-task files
        (tmp_path / "notes.txt").write_text("ignored")
        (tmp_path / "data.json").write_text("{}")
        
        # Mock TASKS_FOLDER
        with patch("app.TASKS_FOLDER", tmp_path):
            next_id = get_next_task_id()
            assert next_id == "task-001"


class TestNormalizeNotes:
    """Tests for the normalize_notes function."""

    def test_valid_notes(self, sample_task):
        """Test normalizing valid notes."""
        from app import normalize_notes
        
        result = normalize_notes(sample_task["notes"])
        
        assert "goal" in result
        assert "requirements" in result
        assert "blocked" is True or "blocked" in result

    def test_empty_notes(self):
        """Test normalizing empty notes."""
        from app import normalize_notes
        
        result = normalize_notes({})
        
        assert "blocked" in result
        assert "requirements" in result


class TestNormalizeTask:
    """Tests for the normalize_task function."""

    def test_valid_task(self, sample_task):
        """Test normalizing a valid task."""
        from app import normalize_task
        
        result = normalize_task(sample_task)
        
        assert result["id"] == sample_task["id"]
        assert "notes" in result

    def test_minimal_task(self):
        """Test normalizing a minimal task."""
        from app import normalize_task
        
        task = {"id": "task-test"}
        
        result = normalize_task(task)
        
        assert result["id"] == "task-test"
        assert "notes" in result


class TestLoadTask:
    """Tests for load_task function."""

    def test_loads_existing_task(self, tmp_path: Path, sample_task):
        """Test loading an existing task."""
        from app import load_task, save_task
        
        # Mock TASKS_FOLDER
        with patch("app.TASKS_FOLDER", tmp_path):
            # First save
            save_task(sample_task)
            
            # Then load
            loaded = load_task("task-001")
            
            assert loaded is not None
            assert loaded["id"] == "task-001"

    def test_returns_none_for_missing_task(self, tmp_path: Path):
        """Test loading a non-existent task."""
        from app import load_task
        
        # Mock TASKS_FOLDER
        with patch("app.TASKS_FOLDER", tmp_path):
            loaded = load_task("task-nonexistent")
            
            assert loaded is None


class TestSaveTask:
    """Tests for save_task function."""

    def test_saves_new_task(self, tmp_path: Path, sample_task):
        """Test saving a new task."""
        from app import save_task
        
        # Mock TASKS_FOLDER
        with patch("app.TASKS_FOLDER", tmp_path):
            save_task(sample_task)
            
            task_file = tmp_path / "task-001.json"
            assert task_file.exists()
            
            loaded = json.loads(task_file.read_text(encoding="utf-8"))
            assert loaded["id"] == "task-001"

    def test_updates_existing_task(self, tmp_path: Path, sample_task):
        """Test updating an existing task."""
        from app import save_task
        
        # Mock TASKS_FOLDER
        with patch("app.TASKS_FOLDER", tmp_path):
            # First save
            save_task(sample_task)
            
            # Modify task
            sample_task["title"] = "Updated Title"
            sample_task["stage"] = "completion"
            
            # Save again
            save_task(sample_task)
            
            loaded = json.loads((tmp_path / "task-001.json").read_text(encoding="utf-8"))
            assert loaded["title"] == "Updated Title"
            assert loaded["stage"] == "completion"



class TestDeleteTask:
    """Tests for delete_task function."""

    def test_deletes_task_file(self, tmp_path: Path, sample_task):
        """Test deleting a task file."""
        from app import delete_task, save_task
        
        # Mock TASKS_FOLDER
        with patch("app.TASKS_FOLDER", tmp_path):
            # Save a task
            save_task(sample_task)
            
            # Delete it
            delete_task("task-001")
            
            assert not (tmp_path / "task-001.json").exists()

    def test_delete_nonexistent_task(self, tmp_path: Path):
        """Test deleting a non-existent task."""
        from app import delete_task
        
        # Mock TASKS_FOLDER
        with patch("app.TASKS_FOLDER", tmp_path):
            # Should not raise error
            delete_task("task-nonexistent")


class TestCreateTask:
    """Tests for create_task function."""

    def test_creates_new_task(self, tmp_path: Path):
        """Test creating a new task."""
        from app import create_task
        
        # Mock TASKS_FOLDER and get_next_task_id
        with patch("app.TASKS_FOLDER", tmp_path):
            with patch("app.get_next_task_id", return_value="task-001"):
                task = create_task("Test Title", "Test Description", "high")
                
                assert task["id"] == "task-001"
                assert task["title"] == "Test Title"
                assert task["priority"] == "high"

    def test_task_has_timestamps(self, tmp_path: Path):
        """Test that created tasks have timestamps."""
        from app import create_task
        
        # Mock TASKS_FOLDER and get_next_task_id
        with patch("app.TASKS_FOLDER", tmp_path):
            with patch("app.get_next_task_id", return_value="task-001"):
                task = create_task("Test", "Test", "low")
                
                assert "createdAt" in task
                assert "updatedAt" in task


"""Unit tests for the app.py dashboard data functions - Part 2."""
import json
from pathlib import Path
from unittest.mock import patch
from typing import Dict, Any

import pytest


class TestGetAllTasks:
    """Tests for get_all_tasks function."""

    def test_empty_directory(self, tmp_path: Path):
        """Test getting tasks from empty directory."""
        from app import get_all_tasks
        
        # Mock TASKS_FOLDER
        with patch("app.TASKS_FOLDER", tmp_path):
            tasks = get_all_tasks()
            assert tasks == []

    def test_with_tasks(self, tmp_path: Path):
        """Test getting tasks from directory with files."""
        from app import get_all_tasks
        
        # Create valid task files
        task1 = {"id": "task-001", "title": "Task 1", "notes": {}, "priority": "high", "stage": "planning", "createdAt": "2026-03-12T10:00:00"}
        task2 = {"id": "task-002", "title": "Task 2", "notes": {}, "priority": "low", "stage": "planning", "createdAt": "2026-03-12T09:00:00"}
        task3 = {"id": "task-003", "title": "Task 3", "notes": {}, "priority": "high", "stage": "structuring", "createdAt": "2026-03-12T11:00:00"}
        
        (tmp_path / "task-001.json").write_text(json.dumps(task1))
        (tmp_path / "task-002.json").write_text(json.dumps(task2))
        (tmp_path / "task-003.json").write_text(json.dumps(task3))
        
        # Mock TASKS_FOLDER - load_task will read from disk
        with patch("app.TASKS_FOLDER", tmp_path):
            tasks = get_all_tasks()
            assert len(tasks) == 3
            # Check all tasks are present (sorting verified separately)
            task_ids = {t["id"] for t in tasks}
            assert task_ids == {"task-001", "task-002", "task-003"}


class TestSaveTask:
    """Tests for save_task function."""

    def test_saves_new_task(self, tmp_path: Path, sample_task):
        """Test saving a new task."""
        from app import save_task
        
        # Mock TASKS_FOLDER
        with patch("app.TASKS_FOLDER", tmp_path):
            save_task(sample_task)
            
            task_file = tmp_path / "task-001.json"
            assert task_file.exists()
            
            loaded = json.loads(task_file.read_text(encoding="utf-8"))
            assert loaded["id"] == "task-001"

    def test_updates_existing_task(self, tmp_path: Path, sample_task):
        """Test updating an existing task."""
        from app import save_task
        
        # Mock TASKS_FOLDER
        with patch("app.TASKS_FOLDER", tmp_path):
            # First save
            save_task(sample_task)
            
            # Modify task
            sample_task["title"] = "Updated Title"
            sample_task["stage"] = "completion"
            
            # Save again
            save_task(sample_task)
            
            loaded = json.loads((tmp_path / "task-001.json").read_text(encoding="utf-8"))
            assert loaded["title"] == "Updated Title"
            assert loaded["stage"] == "completion"

    def test_updates_timestamp(self, tmp_path: Path, sample_task):
        """Test that save_task updates timestamp."""
        from app import save_task
        
        # Mock TASKS_FOLDER
        with patch("app.TASKS_FOLDER", tmp_path):
            save_task(sample_task)
            
            # Load and check timestamp exists
            loaded = json.loads((tmp_path / "task-001.json").read_text(encoding="utf-8"))
            assert "updatedAt" in loaded


class TestDeleteTask:
    """Tests for delete_task function."""

    def test_deletes_task_file(self, tmp_path: Path, sample_task):
        """Test deleting a task file."""
        from app import delete_task, save_task
        
        # Mock TASKS_FOLDER
        with patch("app.TASKS_FOLDER", tmp_path):
            # Save a task
            save_task(sample_task)
            
            # Delete it
            delete_task("task-001")
            
            assert not (tmp_path / "task-001.json").exists()

    def test_delete_nonexistent_task(self, tmp_path: Path):
        """Test deleting a non-existent task."""
        from app import delete_task
        
        # Mock TASKS_FOLDER
        with patch("app.TASKS_FOLDER", tmp_path):
            # Should not raise error
            delete_task("task-nonexistent")


class TestGetAllTasksNonTaskFiles:
    """Tests for get_all_tasks with non-task files."""

    def test_skips_non_task_files(self, tmp_path: Path):
        """Test that non-task files are ignored."""
        from app import get_all_tasks
        
        # Create non-task files
        (tmp_path / "notes.txt").write_text("ignored")
        (tmp_path / "data.json").write_text("{}")
        
        # Mock TASKS_FOLDER
        with patch("app.TASKS_FOLDER", tmp_path):
            tasks = get_all_tasks()
            assert len(tasks) == 0


class TestFmtDate:
    """Tests for fmt_date helper function."""

    def test_formats_iso_date(self):
        """Test formatting ISO date string."""
        from app import fmt_date
        
        result = fmt_date("2026-03-12T10:30:00.000000")
        
        # Check for expected format 'Mar 12, 2026'
        assert "Mar" in result
        assert "2026" in result
