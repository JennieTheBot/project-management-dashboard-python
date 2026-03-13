import html
import json
import re
import shutil
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).parent
TASKS_DIR = BASE_DIR / "tasks"
TASKS_DIR.mkdir(exist_ok=True)


def strip_html(value: Any) -> str:
    """Remove HTML tags from a string value.
    
    Args:
        value: Any value that may contain HTML (str, dict, list, None)
    
    Returns:
        Plain text with HTML tags removed and entities decoded
    """
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        try:
            return json.dumps(value, ensure_ascii=False)
        except Exception:
            return str(value)
    text = str(value)
    # Check if input contains HTML entities (e.g., &lt; &gt;)
    has_entities = '&' in text and ('lt;' in text or 'gt;' in text or 'amp;' in text)
    if has_entities:
        # Only unescape HTML entities, preserve the resulting tags
        return html.unescape(text).strip()
    # Process actual HTML by converting tags to spaces then stripping
    text = re.sub(r"(?i)<br\s*/?>", " ", text)
    text = re.sub(r"(?i)</p\s*>", " ", text)
    text = re.sub(r"(?i)</div\s*>", " ", text)
    text = re.sub(r"(?i)<li\s*>", "- ", text)
    text = re.sub(r"(?i)</li\s*>", " ", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\r\n", " ").replace("\r", " ")
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def load_json(path: Path) -> Dict[str, Any] | None:
    """Load JSON from a file.
    
    Args:
        path: Path to JSON file
    
    Returns:
        Parsed JSON data or None if invalid
    """
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_json(path: Path, payload: Dict[str, Any]) -> None:
    """Save data to a JSON file.
    
    Args:
        path: Path to output file
        payload: Data to serialize
    """
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def sanitize_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize and normalize a task dictionary.
    
    Args:
        task: Raw task data dictionary
    
    Returns:
        Sanitized task dictionary with validated fields
    """
    task = dict(task or {})
    task["title"] = strip_html(task.get("title")) or "Untitled task"
    task["description"] = strip_html(task.get("description")) or "No description provided."
    task["completion_summary"] = strip_html(task.get("completion_summary"))
    task["priority"] = task.get("priority") if task.get("priority") in {"urgent", "high", "medium", "low"} else "medium"
    task["stage"] = task.get("stage") if task.get("stage") in {"planning", "structuring", "unit-testing", "completion"} else "planning"
    task["workMode"] = task.get("workMode") if task.get("workMode") in {"iterative", "immediate"} else "iterative"
    task["workflowStage"] = strip_html(task.get("workflowStage")) or "initial"
    task["assignee"] = strip_html(task.get("assignee")) or "Jennie"
    notes = task.get("notes") if isinstance(task.get("notes"), dict) else {}

    requirements = notes.get("requirements", [])
    if isinstance(requirements, str):
        requirements = [requirements] if strip_html(requirements) else []
    elif not isinstance(requirements, list):
        requirements = []

    time_est = notes.get("timeEstimate") if isinstance(notes.get("timeEstimate"), dict) else {}
    actual = time_est.get("actual")
    if isinstance(actual, str):
        stripped = actual.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                actual = json.loads(stripped)
            except Exception:
                pass

    task["notes"] = {
        "goal": strip_html(notes.get("goal")),
        "requirements": [strip_html(x) for x in requirements if strip_html(x)],
        "feedback": strip_html(notes.get("feedback")),
        "blocked": bool(notes.get("blocked", False)),
        "blockReason": strip_html(notes.get("blockReason")) or None,
        "unblockNeeded": strip_html(notes.get("unblockNeeded")) or None,
        "timeEstimate": {
            "planned": strip_html(time_est.get("planned")) or None,
            "actual": strip_html(actual) or None,
        },
    }
    return task


def process_file(path: Path) -> None:
    """Process and sanitize a single task file.
    
    Args:
        path: Path to the task JSON file
    """
    data = load_json(path)
    if not data:
        print(f"SKIP invalid json: {path}")
        return
    clean = sanitize_task(data)
    backup = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, backup)
    save_json(path, clean)
    print(f"CLEANED {path.name}")


def main() -> None:
    """Main entry point for the task sanitization utility."""
    candidates = sorted(TASKS_DIR.glob("task-*.json")) + sorted(BASE_DIR.glob("task-*.json"))
    if not candidates:
        print("No task files found.")
        return
    seen = set()
    for path in candidates:
        if path.resolve() in seen:
            continue
        seen.add(path.resolve())
        process_file(path)


if __name__ == "__main__":
    main()
