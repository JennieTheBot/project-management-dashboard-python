# OpenClaw Dashboard Usage Guide

## Overview

This project provides a local web dashboard for managing tasks assigned to autonomous coding agents (OpenClaw bots). It's designed for multi-bot workflows where humans can assign tasks and bots autonomously complete them.

## Quick Start for New OpenClaw Bots

### 1. Clone the Repository

```bash
git clone https://github.com/JennieTheBot/project-management-dashboard-python.git
cd project-management-dashboard-python
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will start at `http://localhost:8501`

## How It Works

### For Humans (Task Assigners)

1. Navigate to the dashboard
2. Add tasks via the "Add Task" form
3. Tasks are saved as JSON files in the `tasks/` directory
4. Monitor progress via the dashboard interface

### For Bots (Task Executors)

The bot should:

1. **Monitor the tasks folder** - Check `/home/lei/Desktop/project-management-dashboard-python/tasks` for new `task-*.json` files
2. **Read the task** - Parse the JSON to understand:
   - `title`: Task name
   - `description`: Detailed requirements
   - `priority`: urgent, high, medium, low
   - `workflowStage`: initial, planning, structuring, unit-testing, completion
3. **Execute the work** - Complete the task according to requirements
4. **Update the JSON file**:
   - Set `stage` to "completion"
   - Set `workflowStage` to "completed"
   - Add `completion_summary` describing what was done
5. **Continue monitoring** - Wait for new tasks

### Task Lifecycle

```
initial → planning → structuring → unit-testing → completion
```

Each stage represents a phase of work. The bot should update the workflow stage as it progresses.

## Multi-Bot Considerations

### When You Have Multiple OpenClaw Bots

- **Task Selection**: Each bot should check if a task is already being worked on (look for `assignee` field)
- **Conflict Resolution**: If multiple bots try to work on the same task, the first one to update the `assignee` field wins
- **State Updates**: Always read the latest JSON file before acting - files can be modified by humans or other bots
- **No Queuing**: Tasks are assigned individually, not in batches

### Best Practices

1. **Check before acting**: Always read the task file first to see current state
2. **Update atomically**: Make all changes to a task JSON in one operation
3. **Communicate completion**: Use `completion_summary` to document what was done
4. **Stay silent on HEARTBEAT_OK**: Don't respond to every heartbeat poll
5. **Batch similar checks**: If checking emails, calendar, and tasks, do it together

## Files Structure

```
project-management-dashboard-python/
├── app.py                      # Streamlit dashboard
├── convert_tasks.py           # Task sanitization utility
├── requirements.txt           # Dependencies
├── tasks/                     # Task storage (bot reads this)
│   └── task-001.json         # Example task file
├── tests/                     # Test suite
├── .gitignore                 # Git ignore patterns
├── LICENSE                    # MIT License
├── README.md                  # Project documentation
├── CHANGELOG.md              # Version history
└── INSTRUCTIONS.md           # This file
```

## Example Task Workflow

1. **Human creates task-005.json** with `workflowStage: "initial"`
2. **Bot detects new file** during monitoring cycle
3. **Bot reads and plans** - updates `workflowStage: "planning"`
4. **Bot executes work** - may create subtasks if needed
5. **Bot completes** - sets `stage: "completion"`, `workflowStage: "completed"`, adds `completion_summary`
6. **Dashboard updates** - human sees completion in UI

## Troubleshooting

### Bot can't read tasks
- Ensure bot has read permissions on `tasks/` directory
- Check file permissions: `chmod 644 tasks/*.json`

### Task not updating
- Bot needs write permissions
- Ensure JSON is valid after updates
- Check for file locks from other processes

### Multiple bots conflicting
- Implement task claiming in `assignee` field
- Add timestamp to track when task was last modified
- Use a simple locking mechanism if needed

## API Reference (Optional for Advanced Usage)

If you prefer programmatic access instead of file watching:

```python
import json
import os
from pathlib import Path

TASKS_DIR = Path("/home/lei/Desktop/project-management-dashboard-python/tasks")

def get_pending_tasks():
    """Get all tasks not yet completed"""
    pending = []
    for task_file in TASKS_DIR.glob("task-*.json"):
        with open(task_file) as f:
            task = json.load(f)
            if task["stage"] != "completion":
                pending.append(task)
    return pending

def update_task(task_file, updates):
    """Update a task file atomically"""
    with open(task_file) as f:
        task = json.load(f)
    
    task.update(updates)
    
    with open(task_file, 'w') as f:
        json.dump(task, f, indent=2)
```

## Credits

Created for use with OpenClaw autonomous coding agents.
