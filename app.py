"""Openbot Management Dashboard - A Streamlit application for task tracking."""
import html
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

# Configure logging
logger = logging.getLogger(__name__)

TASKS_FOLDER = Path(__file__).parent / "tasks"
TASKS_FOLDER.mkdir(exist_ok=True)

PRIORITIES = {
    "urgent": {"label": "Urgent", "color": "#fb7185", "icon": "Critical"},
    "high": {"label": "High", "color": "#f59e0b", "icon": "High"},
    "medium": {"label": "Medium", "color": "#38bdf8", "icon": "Normal"},
    "low": {"label": "Low", "color": "#34d399", "icon": "Low"},
}

STAGES = {
    "planning": {"label": "Planning", "color": "#60a5fa", "icon": "Plan"},
    "structuring": {"label": "Structuring", "color": "#c084fc", "icon": "Build"},
    "unit-testing": {"label": "Unit Testing", "color": "#818cf8", "icon": "Test"},
    "completion": {"label": "Completed", "color": "#34d399", "icon": "Done"},
}

WORKFLOW_MODES = {
    "iterative": {
        "label": "Iterative",
        "icon": "Loop",
        "color": "#f472b6",
        "description": "Execute, get feedback, refine",
    },
    "immediate": {
        "label": "Immediate",
        "icon": "Fast",
        "color": "#22c55e",
        "description": "Execute without a feedback cycle",
    },
}

PRIORITY_ORDER = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
STAGE_ORDER = {"planning": 0, "structuring": 1, "unit-testing": 2, "completion": 3}
VALID_WORKFLOW_STAGES = {"initial", "executing", "waiting_feedback", "refining", "completed"}

st.set_page_config(
    page_title="Openbot Management Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
:root {
    --bg-1: #07101e;
    --bg-2: #0d1930;
    --panel: rgba(12, 22, 40, 0.86);
    --panel-2: rgba(14, 27, 49, 0.92);
    --border: rgba(148, 163, 184, 0.16);
    --border-strong: rgba(96, 165, 250, 0.22);
    --text: #f7fbff;
    --muted: #d7e6fb;
    --subtle: #b7cae6;
    --shadow: 0 20px 50px rgba(0,0,0,0.28);
}

header[data-testid="stHeader"],
[data-testid="stToolbar"],
button[kind="header"] {
    display: none !important;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(56,189,248,0.16), transparent 28%),
        radial-gradient(circle at top right, rgba(96,165,250,0.12), transparent 24%),
        linear-gradient(180deg, var(--bg-1) 0%, var(--bg-2) 100%);
    color: var(--text);
}

[data-testid="stSidebar"] {
    width: 320px !important;
    min-width: 320px !important;
    background: linear-gradient(180deg, rgba(8,16,30,0.98) 0%, rgba(12,23,40,0.98) 100%);
    border-right: 1px solid var(--border);
}

.block-container {
    max-width: none !important;
    padding: 0.9rem 1.2rem 1.2rem 1.2rem !important;
}

h1, h2, h3, h4, p, span, div, label {
    color: inherit;
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 1.45rem 1.55rem;
    border-radius: 26px;
    border: 1px solid var(--border-strong);
    background: linear-gradient(135deg, rgba(9,21,42,0.98) 0%, rgba(10,29,58,0.94) 50%, rgba(8,22,45,0.98) 100%);
    box-shadow: var(--shadow);
    margin-bottom: 0.8rem;
}
.hero:before {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 72% 0%, rgba(34,211,238,0.10), transparent 32%);
    pointer-events: none;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.24rem 0.66rem;
    border-radius: 999px;
    background: rgba(96,165,250,0.14);
    border: 1px solid rgba(96,165,250,0.24);
    color: #dbeafe;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 800;
    margin-bottom: 0.72rem;
}
.hero-title {
    margin: 0;
    font-size: 2.7rem;
    line-height: 1.02;
    letter-spacing: -0.03em;
    color: #ffffff;
    font-weight: 860;
}
.hero-subtitle {
    margin-top: 0.72rem;
    max-width: 980px;
    color: #e5efff;
    font-size: 1.14rem;
    line-height: 1.58;
}

.section-label {
    font-size: 0.88rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #eef5ff;
    font-weight: 820;
    margin-bottom: 0.45rem;
}
.section-label.centered {
    text-align: center;
    font-size: 1.08rem;
}

.kpi {
    min-height: 112px;
    border-radius: 20px;
    background: linear-gradient(180deg, rgba(8,19,37,0.96) 0%, rgba(10,24,44,0.92) 100%);
    border: 1px solid var(--border);
    padding: 0.95rem 1rem;
    box-shadow: 0 12px 30px rgba(0,0,0,0.18);
}
.kpi-label { color: #c5d9f7; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 760; }
.kpi-value { color: #ffffff; font-size: 2rem; line-height: 1; font-weight: 860; margin-top: 0.46rem; }
.kpi-meta { color: #dfebff; font-size: 0.84rem; margin-top: 0.55rem; }

.panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 0.96rem;
    box-shadow: 0 12px 30px rgba(0,0,0,0.16);
}
.board-title {
    font-size: 1.15rem;
    font-weight: 820;
    color: #ffffff;
    margin-bottom: 0.8rem;
}

.snapshot-card {
    border-radius: 16px;
    padding: 0.82rem 0.88rem;
    background: linear-gradient(180deg, rgba(13,31,58,0.96) 0%, rgba(9,23,42,0.95) 100%);
    border: 1px solid rgba(123,181,255,0.14);
    margin-bottom: 0.75rem;
}
.snapshot-label {
    color: #eef5ff;
    font-size: 0.74rem;
    letter-spacing: 0.11em;
    text-transform: uppercase;
    font-weight: 820;
    margin-bottom: 0.42rem;
}
.snapshot-value {
    color: #ffffff;
    font-size: 2rem;
    font-weight: 860;
    line-height: 1;
}
.snapshot-text {
    color: #edf5ff;
    font-size: 1rem;
    line-height: 1.55;
    overflow-wrap: anywhere;
}

.task-shell {
    background: linear-gradient(180deg, rgba(9,22,41,0.98) 0%, rgba(10,22,40,0.95) 100%);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent-color);
    border-radius: 22px;
    padding: 1.02rem;
    box-shadow: 0 16px 36px rgba(0,0,0,0.22);
}
.task-topline {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
    margin-bottom: 0.72rem;
}
.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.28rem 0.72rem;
    border-radius: 999px;
    font-size: 0.73rem;
    font-weight: 760;
    border: 1px solid rgba(255,255,255,0.07);
}
.task-title {
    margin: 0;
    color: #ffffff;
    font-size: 1.16rem;
    font-weight: 820;
    letter-spacing: -0.02em;
    overflow-wrap: anywhere;
}
.task-desc {
    margin: 0.42rem 0 0.88rem 0;
    color: #f8fbff;
    line-height: 1.64;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    font-size: 1rem;
}
.task-meta {
    color: #e1edff;
    font-size: 0.88rem;
}

.task-readable-title {
    color: #f8fafc;
    font-size: 1.18rem;
    font-weight: 780;
    letter-spacing: -0.02em;
    margin: 0.2rem 0 0.35rem 0;
    overflow-wrap: anywhere;
}

.task-readable-desc {
    color: #e8f1ff;
    line-height: 1.6;
    font-size: 0.98rem;
    margin: 0 0 0.6rem 0;
    overflow-wrap: anywhere;
}

.task-readable-meta {
    color: #bfd1ea;
    font-size: 0.84rem;
    margin-bottom: 0.75rem;
    overflow-wrap: anywhere;
}
.summary-box, .blocked-box, .info-box {
    margin-top: 0.9rem;
    padding: 0.88rem 0.92rem;
    border-radius: 16px;
}
.summary-box { background: rgba(16,185,129,0.11); border: 1px solid rgba(16,185,129,0.22); }
.blocked-box { background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.22); }
.info-box { background: rgba(37,99,235,0.12); border: 1px solid rgba(37,99,235,0.20); }
.task-divider {
    height: 2px;
    margin: 0.84rem 0 1rem 0;
    border-radius: 999px;
    background: linear-gradient(90deg, rgba(56,189,248,0) 0%, rgba(96,165,250,.55) 20%, rgba(168,85,247,.55) 50%, rgba(34,211,238,.55) 80%, rgba(56,189,248,0) 100%);
}

.action-card {
    background: linear-gradient(180deg, rgba(10,25,49,0.92) 0%, rgba(10,23,43,0.92) 100%);
    border: 1px solid rgba(96,165,250,0.16);
    border-radius: 18px;
    padding: 0.9rem;
}
.action-note {
    color: #e2edff;
    font-size: 0.84rem;
    line-height: 1.5;
    margin: 0.15rem 0 0.68rem 0;
}
.action-status {
    display: inline-block;
    padding: 0.28rem 0.62rem;
    border-radius: 999px;
    background: rgba(59,130,246,0.14);
    border: 1px solid rgba(96,165,250,0.22);
    color: #dbeafe;
    font-size: 0.74rem;
    font-weight: 760;
    margin-bottom: 0.68rem;
}

.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
    width: 100%;
    border-radius: 12px;
    border: 1px solid rgba(123,181,255,0.18);
    background: linear-gradient(180deg, rgba(37,99,235,0.96) 0%, rgba(29,78,216,0.96) 100%);
    color: #ffffff;
    font-weight: 720;
    box-shadow: 0 10px 24px rgba(37,99,235,0.22);
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {
    border-radius: 12px !important;
    background: rgba(18,33,58,0.9) !important;
    border: 1px solid rgba(123,181,255,0.18) !important;
    color: #f7fbff !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #c7d9f3 !important;
    opacity: 1 !important;
}

.stSidebar .stMarkdown h2,
.stSidebar .stMarkdown h3,
.stSidebar label,
.stSidebar .stCaption,
.stSidebar p,
.stSidebar span,
.stSidebar div {
    color: #eef5ff !important;
}

.stSidebar [data-baseweb="tag"] {
    background: rgba(37,99,235,0.22) !important;
    border: 1px solid rgba(96,165,250,0.22) !important;
    color: #eef5ff !important;
}

[data-testid="stExpander"] {
    border: 1px solid rgba(96,165,250,0.18);
    border-radius: 16px;
    background: rgba(14,24,42,0.88);
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] label,
[data-testid="stExpander"] label p,
[data-testid="stExpander"] .stMarkdown,
[data-testid="stExpander"] .stMarkdown p,
[data-testid="stExpander"] .stCheckbox label,
[data-testid="stExpander"] .stTextInput label p,
[data-testid="stExpander"] .stTextArea label p {
    color: #eef5ff !important;
}

hr { border-color: rgba(111,168,255,0.12); }
</style>
    """,
    unsafe_allow_html=True,
)


def strip_html(value: Any) -> str:
    """Strip HTML tags from a string value.

    Args:
        value: Any value that may contain HTML

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
    # First unescape HTML entities
    text = html.unescape(text)
    # Remove HTML tags while preserving content
    # Use spaces instead of newlines for inline elements to avoid double spacing
    text = re.sub(r"(?i)<br\s*/?>", " ", text)
    text = re.sub(r"(?i)</p\s*>", " ", text)
    text = re.sub(r"(?i)</div\s*>", " ", text)
    text = re.sub(r"(?i)<li\s*>", " ", text)
    text = re.sub(r"(?i)</li\s*>", " ", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def safe_text(value: Any, default: str = "") -> str:
    """Convert a value to a cleaned text string.

    Args:
        value: Any value to convert to text
        default: Default value if cleaned result is empty

    Returns:
        Cleaned text string
    """
    cleaned = strip_html(value)
    return cleaned if cleaned else default


def esc(value: Any) -> str:
    """Escape a value for safe HTML output.

    Args:
        value: Any value to escape

    Returns:
        HTML-escaped string
    """
    return html.escape(str(value or ""))


def read_json(path: Path) -> Optional[Dict[str, Any]]:
    """Read and parse a JSON file.

    Args:
        path: Path to the JSON file

    Returns:
        Parsed JSON data as dict, or None if file doesn't exist or is invalid
    """
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else None
    except Exception as e:
        logger.error(f"Error reading JSON file {path}: {e}")
        return None


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    """Write a dictionary to a JSON file.

    Args:
        path: Path to the output file
        payload: Dictionary to serialize to JSON
    """
    try:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.debug(f"Successfully wrote JSON to {path}")
    except Exception as e:
        logger.error(f"Error writing JSON file {path}: {e}")
        raise


def task_file(task_id: str) -> Path:
    """Get the path to a task JSON file.

    Args:
        task_id: The task identifier

    Returns:
        Path object for the task file
    """
    return TASKS_FOLDER / f"{task_id}.json"


def get_next_task_id() -> str:
    """Generate the next available task ID.

    Returns:
        String ID in format "task-XXX" where XXX is the next sequential number
    """
    max_num = 0
    for path in TASKS_FOLDER.glob("task-*.json"):
        try:
            max_num = max(max_num, int(path.stem.replace("task-", "")))
        except ValueError:
            continue
    return f"task-{max_num + 1:03d}"


def normalize_notes(raw_notes: Any) -> Dict[str, Any]:
    """Normalize task notes dictionary to standard format.

    Args:
        raw_notes: Raw notes data (dict, list, or string)

    Returns:
        Normalized notes dictionary with standardized fields
    """
    notes = raw_notes if isinstance(raw_notes, dict) else {}
    requirements = notes.get("requirements", [])
    if isinstance(requirements, str):
        requirements = [safe_text(requirements)] if safe_text(requirements) else []
    elif not isinstance(requirements, list):
        requirements = []

    time_est = notes.get("timeEstimate")
    if not isinstance(time_est, dict):
        time_est = {}

    actual = time_est.get("actual")
    if isinstance(actual, str):
        stripped = actual.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                actual = json.loads(stripped)
            except Exception:
                pass

    return {
        "goal": safe_text(notes.get("goal")),
        "requirements": [safe_text(x) for x in requirements if safe_text(x)],
        "feedback": safe_text(notes.get("feedback")),
        "blocked": bool(notes.get("blocked", False)),
        "blockReason": safe_text(notes.get("blockReason")) or None,
        "unblockNeeded": safe_text(notes.get("unblockNeeded")) or None,
        "timeEstimate": {
            "planned": safe_text(time_est.get("planned")) or None,
            "actual": safe_text(actual) or None,
        },
    }


def normalize_task(raw_task: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a task dictionary to standard format.

    Args:
        raw_task: Raw task data dictionary

    Returns:
        Normalized task dictionary with all required fields
    """
    task = dict(raw_task or {})
    task_id = safe_text(task.get("id")) or get_next_task_id()
    stage = task.get("stage") if task.get("stage") in STAGES else "planning"
    priority = task.get("priority") if task.get("priority") in PRIORITIES else "medium"
    work_mode = task.get("workMode") if task.get("workMode") in WORKFLOW_MODES else "iterative"
    workflow_stage = safe_text(task.get("workflowStage"), "initial")
    if workflow_stage not in VALID_WORKFLOW_STAGES:
        workflow_stage = "completed" if stage == "completion" else "initial"

    return {
        "id": task_id,
        "title": safe_text(task.get("title"), "Untitled task"),
        "description": safe_text(task.get("description"), "No description provided."),
        "priority": priority,
        "stage": stage,
        "workMode": work_mode,
        "workflowStage": workflow_stage,
        "createdAt": safe_text(task.get("createdAt"), datetime.now().isoformat()),
        "updatedAt": safe_text(task.get("updatedAt"), datetime.now().isoformat()),
        "assignee": safe_text(task.get("assignee"), "Jennie"),
        "completion_summary": safe_text(task.get("completion_summary")),
        "notes": normalize_notes(task.get("notes")),
    }


def load_task(task_id: str) -> Optional[Dict[str, Any]]:
    """Load a task from its JSON file.

    Args:
        task_id: The task identifier

    Returns:
        Task dictionary, or None if not found
    """
    path = task_file(task_id)
    if not path.exists():
        return None
    payload = read_json(path)
    if not payload:
        return None
    task = normalize_task(payload)
    if task != payload:
        write_json(path, task)
    return task


def save_task(task: Dict[str, Any]) -> None:
    """Save a task to its JSON file.

    Args:
        task: Task dictionary to save
    """
    normalized = normalize_task(task)
    normalized["updatedAt"] = datetime.now().isoformat()
    write_json(task_file(normalized["id"]), normalized)


def delete_task(task_id: str) -> None:
    """Delete a task file.

    Args:
        task_id: The task identifier
    """
    path = task_file(task_id)
    if path.exists():
        path.unlink()


def create_task(
    title: str,
    description: str,
    priority: str,
    work_mode: Optional[str] = None,
    workMode: Optional[str] = None,
    assignee: str = "Jennie"
) -> Dict[str, Any]:
    """Create a new task.

    Args:
        title: Task title
        description: Task description
        priority: Priority level (urgent, high, medium, low)
        work_mode: Workflow mode (iterative, immediate) [deprecated: use workMode]
        workMode: Workflow mode (iterative, immediate)
        assignee: Task assignee (default: Jennie)

    Returns:
        Created task dictionary
    """
    # Support both snake_case and camelCase parameter names for backwards compatibility
    mode = workMode if workMode else work_mode
    now = datetime.now().isoformat()
    task = {
        "id": get_next_task_id(),
        "title": safe_text(title, "Untitled task"),
        "description": safe_text(description, "No description provided."),
        "priority": priority if priority in PRIORITIES else "medium",
        "stage": "planning",
        "workMode": mode if mode in WORKFLOW_MODES else "iterative",
        "workflowStage": "initial",
        "createdAt": now,
        "updatedAt": now,
        "assignee": safe_text(assignee, "Jennie"),
        "completion_summary": "",
        "notes": normalize_notes({}),
    }
    save_task(task)
    return task


def get_all_tasks() -> List[Dict[str, Any]]:
    """Get all tasks sorted by priority, stage, and creation date.

    Returns:
        List of all task dictionaries, sorted
    """
    tasks: List[Dict[str, Any]] = []
    for path in TASKS_FOLDER.glob("task-*.json"):
        task = load_task(path.stem)
        if task:
            tasks.append(task)
    tasks.sort(
        key=lambda t: (
            PRIORITY_ORDER.get(t.get("priority", "medium"), 99),
            STAGE_ORDER.get(t.get("stage", "planning"), 99),
            t.get("createdAt", ""),
        )
    )
    return tasks


def fmt_date(iso_str: str) -> str:
    """Format an ISO date string to human-readable format.

    Args:
        iso_str: ISO format date string

    Returns:
        Formatted date string (e.g., "Mar 12, 2026")
    """
    try:
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00")).strftime("%b %d, %Y")
    except ValueError:
        return iso_str[:10]


def apply_iterative_action(
    task: Dict[str, Any],
    action: str,
    feedback: str = ""
) -> None:
    """Apply an action to an iterative workflow task.

    Args:
        task: Task dictionary to update
        action: Action to apply (start, done, continue, refine, apply_refinement, complete)
        feedback: Feedback text used for 'refine' action

    Returns:
        None
    """
    if action == "start":
        task["workflowStage"] = "executing"
        task["stage"] = "structuring"
    elif action == "done":
        task["workflowStage"] = "waiting_feedback"
    elif action == "continue":
        task["workflowStage"] = "executing"
        task["stage"] = "unit-testing"
    elif action == "refine":
        task["notes"]["feedback"] = safe_text(feedback)
        task["workflowStage"] = "refining"
    elif action == "apply_refinement":
        task["workflowStage"] = "executing"
        task["stage"] = "structuring"
    elif action == "complete":
        task["workflowStage"] = "completed"
        task["stage"] = "completion"
    save_task(task)


def apply_immediate_action(
    task: Dict[str, Any],
    action: str
) -> None:
    """Apply an action to an immediate workflow task.

    Args:
        task: Task dictionary to update
        action: Action to apply (start, complete)

    Returns:
        None
    """
    if action == "start":
        task["workflowStage"] = "executing"
        task["stage"] = "structuring"
    elif action == "complete":
        task["workflowStage"] = "completed"
        task["stage"] = "completion"
    save_task(task)


def render_kpi(
    title: str,
    value: str,
    meta: str
) -> None:
    """Render a KPI card in the dashboard.

    Args:
        title: KPI title/label
        value: KPI value
        meta: Additional metadata

    Returns:
        None
    """
    st.markdown(
        f"""
        <div class="kpi">
            <div class="kpi-label">{esc(title)}</div>
            <div class="kpi-value">{esc(value)}</div>
            <div class="kpi-meta">{esc(meta)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_task_card(task: Dict[str, Any]) -> None:
    """Render a task card in the dashboard.

    Args:
        task: Task dictionary to render

    Returns:
        None
    """
    task = normalize_task(task)
    priority = PRIORITIES[task["priority"]]
    stage = STAGES[task["stage"]]
    mode = WORKFLOW_MODES[task["workMode"]]
    blocked = bool(task["notes"].get("blocked", False))

    display_title = safe_text(task.get("title"), "Untitled task")
    display_description = safe_text(task.get("description"), "No description provided.")
    display_assignee = safe_text(task.get("assignee"), "Jennie")
    display_summary = safe_text(task.get("completion_summary"))
    display_block_reason = safe_text(task["notes"].get("blockReason"), "Not specified")
    display_unblock_needed = safe_text(task["notes"].get("unblockNeeded"), "Not specified")

    blocked_html = ""
    if blocked:
        blocked_html = f"""
            <div class="blocked-box">
                <div style="font-weight:800; color:#fecaca; margin-bottom:0.35rem;">Blocked</div>
                <div style="color:#fee2e2;">Reason: {esc(display_block_reason)}</div>
                <div style="color:#fee2e2; margin-top:0.24rem;">Needs: {esc(display_unblock_needed)}</div>
            </div>
        """

    summary_html = ""
    if task["stage"] == "completion" and display_summary:
        summary_html = f"""
            <div style="background:#0d3820;border:1px solid #10b981;border-radius:6px;padding:0.6rem;margin-top:0.5rem;">
                <div style="font-size:0.85rem;font-weight:600;color:#34d399;margin-bottom:0.25rem;">COMPLETED</div>
                <div style="color:#e5e7eb;line-height:1.5;font-size:0.9rem;">{esc(display_summary)}</div>
            </div>
        """

    badges = [
        f'<span class="badge" style="background:{stage["color"]}22; color:{stage["color"]};">{stage["icon"]} · {stage["label"]}</span>',
        f'<span class="badge" style="background:{mode["color"]}22; color:{mode["color"]};">{mode["icon"]} · {mode["label"]}</span>',
        f'<span class="badge" style="background:{priority["color"]}22; color:{priority["color"]};">{priority["label"]}</span>',
    ]
    if blocked:
        badges.append("<span class='badge' style='background:#ef444422;color:#fecaca;'>Blocked</span>")

    st.markdown(
        f"""
        <div class="task-shell" style="--accent-color:{priority['color']}; margin-bottom:0.4rem;">
            <div class="task-topline">{' '.join(badges)}</div>
            <div class="task-readable-title">{esc(display_title)}</div>
            <div class="task-readable-desc">{esc(display_description).replace(chr(10), '<br>')}</div>
            <div class="task-readable-meta">Assigned to {esc(display_assignee)} · Created {fmt_date(task['createdAt'])} · Updated {fmt_date(task['updatedAt'])}</div>
            {blocked_html}
            {summary_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def task_file(task_id: str) -> Path:
    """Get the path to a task JSON file.

    Args:
        task_id: The task identifier

    Returns:
        Path object for the task file
    """
    return TASKS_FOLDER / f"{task_id}.json"


def get_next_task_id() -> str:
    """Generate the next available task ID.

    Returns:
        String ID in format "task-XXX" where XXX is the next sequential number
    """
    max_num = 0
    for path in TASKS_FOLDER.glob("task-*.json"):
        try:
            max_num = max(max_num, int(path.stem.replace("task-", "")))
        except ValueError:
            continue
    return f"task-{max_num + 1:03d}"


def normalize_notes(raw_notes: Any) -> Dict[str, Any]:
    """Normalize task notes dictionary to standard format.

    Args:
        raw_notes: Raw notes data (dict, list, or string)

    Returns:
        Normalized notes dictionary with standardized fields
    """
    notes = raw_notes if isinstance(raw_notes, dict) else {}
    requirements = notes.get("requirements", [])
    if isinstance(requirements, str):
        requirements = [safe_text(requirements)] if safe_text(requirements) else []
    elif not isinstance(requirements, list):
        requirements = []

    time_est = notes.get("timeEstimate")
    if not isinstance(time_est, dict):
        time_est = {}

    actual = time_est.get("actual")
    if isinstance(actual, str):
        stripped = actual.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                actual = json.loads(stripped)
            except Exception:
                pass

    return {
        "goal": safe_text(notes.get("goal")),
        "requirements": [safe_text(x) for x in requirements if safe_text(x)],
        "feedback": safe_text(notes.get("feedback")),
        "blocked": bool(notes.get("blocked", False)),
        "blockReason": safe_text(notes.get("blockReason")) or None,
        "unblockNeeded": safe_text(notes.get("unblockNeeded")) or None,
        "timeEstimate": {
            "planned": safe_text(time_est.get("planned")) or None,
            "actual": safe_text(actual) or None,
        },
    }


def normalize_task(raw_task: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a task dictionary to standard format.

    Args:
        raw_task: Raw task data dictionary

    Returns:
        Normalized task dictionary with all required fields
    """
    task = dict(raw_task or {})
    task_id = safe_text(task.get("id")) or get_next_task_id()
    stage = task.get("stage") if task.get("stage") in STAGES else "planning"
    priority = task.get("priority") if task.get("priority") in PRIORITIES else "medium"
    work_mode = task.get("workMode") if task.get("workMode") in WORKFLOW_MODES else "iterative"
    workflow_stage = safe_text(task.get("workflowStage"), "initial")
    if workflow_stage not in VALID_WORKFLOW_STAGES:
        workflow_stage = "completed" if stage == "completion" else "initial"

    return {
        "id": task_id,
        "title": safe_text(task.get("title"), "Untitled task"),
        "description": safe_text(task.get("description"), "No description provided."),
        "priority": priority,
        "stage": stage,
        "workMode": work_mode,
        "workflowStage": workflow_stage,
        "createdAt": safe_text(task.get("createdAt"), datetime.now().isoformat()),
        "updatedAt": safe_text(task.get("updatedAt"), datetime.now().isoformat()),
        "assignee": safe_text(task.get("assignee"), "Jennie"),
        "completion_summary": safe_text(task.get("completion_summary")),
        "notes": normalize_notes(task.get("notes")),
    }


def load_task(task_id: str) -> Optional[Dict[str, Any]]:
    """Load a task from its JSON file.

    Args:
        task_id: The task identifier

    Returns:
        Task dictionary, or None if not found
    """
    path = task_file(task_id)
    if not path.exists():
        return None
    payload = read_json(path)
    if not payload:
        return None
    task = normalize_task(payload)
    if task != payload:
        write_json(path, task)
    return task


def save_task(task: Dict[str, Any]) -> None:
    """Save a task to its JSON file.

    Args:
        task: Task dictionary to save
    """
    normalized = normalize_task(task)
    normalized["updatedAt"] = datetime.now().isoformat()
    write_json(task_file(normalized["id"]), normalized)


def delete_task(task_id: str) -> None:
    """Delete a task file.

    Args:
        task_id: The task identifier
    """
    path = task_file(task_id)
    if path.exists():
        path.unlink()


def create_task(
    title: str,
    description: str,
    priority: str,
    work_mode: Optional[str] = None,
    workMode: Optional[str] = None,
    assignee: str = "Jennie"
) -> Dict[str, Any]:
    """Create a new task.

    Args:
        title: Task title
        description: Task description
        priority: Priority level (urgent, high, medium, low)
        work_mode: Workflow mode (iterative, immediate) [deprecated: use workMode]
        workMode: Workflow mode (iterative, immediate)
        assignee: Task assignee (default: Jennie)

    Returns:
        Created task dictionary
    """
    # Support both snake_case and camelCase parameter names for backwards compatibility
    mode = workMode if workMode else work_mode
    now = datetime.now().isoformat()
    task = {
        "id": get_next_task_id(),
        "title": safe_text(title, "Untitled task"),
        "description": safe_text(description, "No description provided."),
        "priority": priority if priority in PRIORITIES else "medium",
        "stage": "planning",
        "workMode": mode if mode in WORKFLOW_MODES else "iterative",
        "workflowStage": "initial",
        "createdAt": now,
        "updatedAt": now,
        "assignee": safe_text(assignee, "Jennie"),
        "completion_summary": "",
        "notes": normalize_notes({}),
    }
    save_task(task)
    return task


def get_all_tasks() -> List[Dict[str, Any]]:
    """Get all tasks sorted by priority, stage, and creation date.

    Returns:
        List of all task dictionaries, sorted
    """
    tasks: List[Dict[str, Any]] = []
    for path in TASKS_FOLDER.glob("task-*.json"):
        task = load_task(path.stem)
        if task:
            tasks.append(task)
    tasks.sort(
        key=lambda t: (
            PRIORITY_ORDER.get(t.get("priority", "medium"), 99),
            STAGE_ORDER.get(t.get("stage", "planning"), 99),
            t.get("createdAt", ""),
        )
    )
    return tasks


def fmt_date(iso_str: str) -> str:
    """Format an ISO date string to human-readable format.

    Args:
        iso_str: ISO format date string

    Returns:
        Formatted date string (e.g., "Mar 12, 2026")
    """
    try:
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00")).strftime("%b %d, %Y")
    except ValueError:
        return iso_str[:10]


def apply_iterative_action(
    task: Dict[str, Any],
    action: str,
    feedback: str = ""
) -> None:
    """Apply an action to an iterative workflow task.

    Args:
        task: Task dictionary to update
        action: Action to apply (start, done, continue, refine, apply_refinement, complete)
        feedback: Feedback text used for 'refine' action

    Returns:
        None
    """
    if action == "start":
        task["workflowStage"] = "executing"
        task["stage"] = "structuring"
    elif action == "done":
        task["workflowStage"] = "waiting_feedback"
    elif action == "continue":
        task["workflowStage"] = "executing"
        task["stage"] = "unit-testing"
    elif action == "refine":
        task["notes"]["feedback"] = safe_text(feedback)
        task["workflowStage"] = "refining"
    elif action == "apply_refinement":
        task["workflowStage"] = "executing"
        task["stage"] = "structuring"
    elif action == "complete":
        task["workflowStage"] = "completed"
        task["stage"] = "completion"
    save_task(task)


def apply_immediate_action(
    task: Dict[str, Any],
    action: str
) -> None:
    """Apply an action to an immediate workflow task.

    Args:
        task: Task dictionary to update
        action: Action to apply (start, complete)

    Returns:
        None
    """
    if action == "start":
        task["workflowStage"] = "executing"
        task["stage"] = "structuring"
    elif action == "complete":
        task["workflowStage"] = "completed"
        task["stage"] = "completion"
    save_task(task)


def render_kpi(
    title: str,
    value: str,
    meta: str
) -> None:
    """Render a KPI card in the dashboard.

    Args:
        title: KPI title/label
        value: KPI value
        meta: Additional metadata

    Returns:
        None
    """
    st.markdown(
        f"""
        <div class="kpi">
            <div class="kpi-label">{esc(title)}</div>
            <div class="kpi-value">{esc(value)}</div>
            <div class="kpi-meta">{esc(meta)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_task_card(task: Dict[str, Any]) -> None:
    """Render a task card in the dashboard.

    Args:
        task: Task dictionary to render

    Returns:
        None
    """
    task = normalize_task(task)
    priority = PRIORITIES[task["priority"]]
    stage = STAGES[task["stage"]]
    mode = WORKFLOW_MODES[task["workMode"]]
    blocked = bool(task["notes"].get("blocked", False))

    display_title = safe_text(task.get("title"), "Untitled task")
    display_description = safe_text(task.get("description"), "No description provided.")
    display_assignee = safe_text(task.get("assignee"), "Jennie")
    display_summary = safe_text(task.get("completion_summary"))
    display_block_reason = safe_text(task["notes"].get("blockReason"), "Not specified")
    display_unblock_needed = safe_text(task["notes"].get("unblockNeeded"), "Not specified")

    blocked_html = ""
    if blocked:
        blocked_html = f"""
            <div class="blocked-box">
                <div style="font-weight:800; color:#fecaca; margin-bottom:0.35rem;">Blocked</div>
                <div style="color:#fee2e2;">Reason: {esc(display_block_reason)}</div>
                <div style="color:#fee2e2; margin-top:0.24rem;">Needs: {esc(display_unblock_needed)}</div>
            </div>
        """

    summary_html = ""
    if task["stage"] == "completion" and display_summary:
        summary_html = f"""
            <div style="background:#0d3820;border:1px solid #10b981;border-radius:6px;padding:0.6rem;margin-top:0.5rem;">
                <div style="font-size:0.85rem;font-weight:600;color:#34d399;margin-bottom:0.25rem;">COMPLETED</div>
                <div style="color:#e5e7eb;line-height:1.5;font-size:0.9rem;">{esc(display_summary)}</div>
            </div>
        """

    badges = [
        f'<span class="badge" style="background:{stage["color"]}22; color:{stage["color"]};">{stage["icon"]} · {stage["label"]}</span>',
        f'<span class="badge" style="background:{mode["color"]}22; color:{mode["color"]};">{mode["icon"]} · {mode["label"]}</span>',
        f'<span class="badge" style="background:{priority["color"]}22; color:{priority["color"]};">{priority["label"]}</span>',
    ]
    if blocked:
        badges.append("<span class='badge' style='background:#ef444422;color:#fecaca;'>Blocked</span>")

    st.markdown(
        f"""
        <div class="task-shell" style="--accent-color:{priority['color']}; margin-bottom:0.4rem;">
            <div class="task-topline">{' '.join(badges)}</div>
            <div class="task-readable-title">{esc(display_title)}</div>
            <div class="task-readable-desc">{esc(display_description).replace(chr(10), '<br>')}</div>
            <div class="task-readable-meta">Assigned to {esc(display_assignee)} · Created {fmt_date(task['createdAt'])} · Updated {fmt_date(task['updatedAt'])}</div>
            {blocked_html}
            {summary_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown("## Control Center")
    st.caption("Assign work to OpenClaw and track execution without babysitting the board.")

    search_query = st.text_input("Search", placeholder="Search title or description")
    show_priority = st.multiselect(
        "Priority",
        options=list(PRIORITIES.keys()),
        default=list(PRIORITIES.keys()),
        format_func=lambda x: PRIORITIES[x]["label"],
    )
    show_stage = st.multiselect(
        "Stage",
        options=list(STAGES.keys()),
        default=list(STAGES.keys()),
        format_func=lambda x: STAGES[x]["label"],
    )
    show_mode = st.multiselect(
        "Workflow",
        options=list(WORKFLOW_MODES.keys()),
        default=list(WORKFLOW_MODES.keys()),
        format_func=lambda x: WORKFLOW_MODES[x]["label"],
    )

    st.markdown("---")
    st.markdown("### Create task")
    with st.form("create_task_form", clear_on_submit=True):
        new_title = st.text_input("Title", placeholder="Task title")
        new_description = st.text_area("Description", placeholder="What needs to get done?")
        c1, c2 = st.columns(2)
        with c1:
            new_priority = st.selectbox(
                "Priority",
                options=list(PRIORITIES.keys()),
                format_func=lambda x: PRIORITIES[x]["label"],
            )
        with c2:
            new_mode = st.selectbox(
                "Workflow mode",
                options=list(WORKFLOW_MODES.keys()),
                format_func=lambda x: WORKFLOW_MODES[x]["label"],
            )
        new_assignee = st.text_input("Assignee", value="Jennie")
        submitted = st.form_submit_button("Create Task")

    if submitted:
        title_clean = safe_text(new_title)
        desc_clean = safe_text(new_description)
        if title_clean and desc_clean:
            create_task(title_clean, desc_clean, new_priority, new_mode, new_assignee)
            st.success("Task created.")
            st.rerun()
        else:
            st.error("Title and description are required.")

all_tasks = get_all_tasks()
filtered_tasks = all_tasks[:]
if search_query:
    q = search_query.lower().strip()
    filtered_tasks = [t for t in filtered_tasks if q in t["title"].lower() or q in t["description"].lower()]
if show_priority:
    filtered_tasks = [t for t in filtered_tasks if t["priority"] in show_priority]
if show_stage:
    filtered_tasks = [t for t in filtered_tasks if t["stage"] in show_stage]
if show_mode:
    filtered_tasks = [t for t in filtered_tasks if t["workMode"] in show_mode]

completed_count = len([t for t in filtered_tasks if t["stage"] == "completion"])
in_progress_count = len([t for t in filtered_tasks if t["stage"] in ["planning", "structuring", "unit-testing"]])
blocked_count = len([t for t in filtered_tasks if t["notes"].get("blocked")])
iterative_count = len([t for t in filtered_tasks if t["workMode"] == "iterative"])
latest_task = max(filtered_tasks, key=lambda t: t.get("updatedAt", ""), default=None)

st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">OpenClaw Task Tracker</div>
        <h1 class="hero-title">Openbot Management Dashboard</h1>
        <div class="hero-subtitle">This is a task tracker that you can assign task to your OpenClaw to work and track progress 24/7.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

cols = st.columns(4)
with cols[0]:
    render_kpi("Visible tasks", str(len(filtered_tasks)), "Current board scope")
with cols[1]:
    render_kpi("In progress", str(in_progress_count), "Planning, build, or testing")
with cols[2]:
    render_kpi("Completed", str(completed_count), "Tasks already closed")
with cols[3]:
    render_kpi("Blocked / Iterative", f"{blocked_count} / {iterative_count}", "Risk and workflow mix")

st.markdown("<div style='height:0.65rem'></div>", unsafe_allow_html=True)
left, right = st.columns([4.35, 1.15], gap="medium")

with left:
    st.markdown("<div class='section-label'>Task board</div>", unsafe_allow_html=True)
    if not filtered_tasks:
        st.markdown(
            "<div class='panel'><div class='board-title' style='font-size:1rem;margin-bottom:0.25rem;'>No tasks match the current filters.</div><div style='color:#d7e6fb;'>Change filters or create a new task.</div></div>",
            unsafe_allow_html=True,
        )

    for task in filtered_tasks:
        render_task_card(task)
        action_col, details_col = st.columns([1.05, 2.95], gap="large")

        with action_col:
            st.markdown("<div class='section-label' style='margin-bottom:0.35rem;'>Status controls</div>", unsafe_allow_html=True)
            st.markdown("<div class='action-note'>These controls only update the dashboard status. They do not automatically trigger your OpenClaw agent.</div>", unsafe_allow_html=True)
            workflow_stage = task.get("workflowStage", "initial")
            st.markdown(f"<div class='action-status'>Current: {esc(workflow_stage.replace('_', ' ').title())}</div>", unsafe_allow_html=True)

            if task["workMode"] == "iterative":
                if workflow_stage == "initial":
                    if st.button("Mark in progress", key=f"iter_start_{task['id']}"):
                        apply_iterative_action(task, "start")
                        st.rerun()
                elif workflow_stage == "executing":
                    if st.button("Mark work finished", key=f"iter_done_{task['id']}"):
                        apply_iterative_action(task, "done")
                        st.rerun()
                    with st.expander("Add feedback for next revision"):
                        feedback_value = st.text_area(
                            "Feedback",
                            key=f"feedback_text_{task['id']}",
                            placeholder="What should change?",
                            label_visibility="collapsed",
                        )
                        if st.button("Save feedback", key=f"feedback_submit_{task['id']}"):
                            apply_iterative_action(task, "refine", feedback_value)
                            st.rerun()
                elif workflow_stage == "waiting_feedback":
                    if st.button("Resume work", key=f"iter_continue_{task['id']}"):
                        apply_iterative_action(task, "continue")
                        st.rerun()
                    if st.button("Mark completed", key=f"iter_complete_wait_{task['id']}"):
                        apply_iterative_action(task, "complete")
                        st.rerun()
                elif workflow_stage == "refining":
                    if st.button("Mark refinement in progress", key=f"iter_apply_{task['id']}"):
                        apply_iterative_action(task, "apply_refinement")
                        st.rerun()
                    if st.button("Mark completed", key=f"iter_complete_refine_{task['id']}"):
                        apply_iterative_action(task, "complete")
                        st.rerun()
                else:
                    st.success("Task completed")
            else:
                if workflow_stage == "initial":
                    if st.button("Mark in progress", key=f"imm_start_{task['id']}"):
                        apply_immediate_action(task, "start")
                        st.rerun()
                elif workflow_stage == "executing":
                    if st.button("Mark completed", key=f"imm_complete_{task['id']}"):
                        apply_immediate_action(task, "complete")
                        st.rerun()
                else:
                    st.success("Task completed")

            if st.button("Delete", key=f"delete_{task['id']}"):
                delete_task(task["id"])
                st.rerun()

        with details_col:
            with st.expander("Details", expanded=False):
                a, b = st.columns(2)
                with a:
                    new_summary = st.text_area(
                        "Completion summary",
                        value=task.get("completion_summary", ""),
                        key=f"summary_{task['id']}",
                        height=120,
                    )
                    goal_text = st.text_input(
                        "Goal",
                        value=task["notes"].get("goal", ""),
                        key=f"goal_{task['id']}",
                    )
                with b:
                    blocked_flag = st.checkbox(
                        "Blocked",
                        value=task["notes"].get("blocked", False),
                        key=f"blocked_flag_{task['id']}",
                    )
                    block_reason = st.text_input(
                        "Block reason",
                        value=task["notes"].get("blockReason") or "",
                        key=f"block_reason_{task['id']}",
                    )
                    unblock_needed = st.text_input(
                        "Unblock needed",
                        value=task["notes"].get("unblockNeeded") or "",
                        key=f"unblock_needed_{task['id']}",
                    )

                if task["notes"].get("feedback"):
                    st.markdown(
                        f"<div class='info-box'><div style='font-weight:800;margin-bottom:.35rem;color:#eef5ff;'>Latest feedback</div><div style='color:#f8fbff;white-space:pre-wrap;overflow-wrap:anywhere;'>{esc(task['notes']['feedback'])}</div></div>",
                        unsafe_allow_html=True,
                    )

                if st.button("Save details", key=f"save_details_{task['id']}"):
                    task["completion_summary"] = safe_text(new_summary)
                    task["notes"]["goal"] = safe_text(goal_text)
                    task["notes"]["blocked"] = blocked_flag
                    task["notes"]["blockReason"] = safe_text(block_reason) or None
                    task["notes"]["unblockNeeded"] = safe_text(unblock_needed) or None
                    save_task(task)
                    st.success("Details saved")
                    st.rerun()

        st.markdown("<div class='task-divider'></div>", unsafe_allow_html=True)

with right:
    high_pressure = len([t for t in filtered_tasks if t["priority"] in ["urgent", "high"]])
    immediate_mode = len([t for t in filtered_tasks if t["workMode"] == "immediate"])
    latest_title = latest_task["title"] if latest_task else "No visible tasks"

    st.markdown("<div class='section-label centered'>Insights</div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="panel">
            <div class="board-title">Board snapshot</div>
            <div class="snapshot-card">
                <div class="snapshot-label">High pressure</div>
                <div class="snapshot-value">{high_pressure}</div>
            </div>
            <div class="snapshot-card">
                <div class="snapshot-label">Immediate mode</div>
                <div class="snapshot-value">{immediate_mode}</div>
            </div>
            <div class="snapshot-card" style="margin-bottom:0;">
                <div class="snapshot-label">Latest update</div>
                <div class="snapshot-text">{esc(latest_title)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:0.7rem'></div>", unsafe_allow_html=True)
    stage_counts = {k: len([t for t in filtered_tasks if t["stage"] == k]) for k in STAGES}
    stage_rows = []
    total_visible = max(len(filtered_tasks), 1)
    for stage_key, info in STAGES.items():
        count = stage_counts[stage_key]
        width = min((count / total_visible) * 100, 100)
        stage_rows.append(
            f"<div style='margin-top:.72rem;'><div style='display:flex;justify-content:space-between;align-items:center;color:#e7f0ff;font-size:.92rem;margin-bottom:.28rem;'><span>{esc(info['label'])}</span><span>{count}</span></div><div style='height:7px;border-radius:999px;background:rgba(148,163,184,.14);overflow:hidden;'><div style='height:100%;border-radius:999px;background:{info['color']};width:{width}%;'></div></div></div>"
        )
    st.markdown(
        f"""
        <div class="panel">
            <div class="board-title">Stage distribution</div>
            {''.join(stage_rows)}
        </div>
        """,
        unsafe_allow_html=True,
    )
