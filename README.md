# Openbot Management Dashboard 🎯

A modern, user-friendly Streamlit dashboard for prioritized task management and tracking work assigned to Jennie (your autonomous coding agent).

## 🚀 Quick Start

### Installation

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Dashboard

```bash
# Option 1: Direct execution
streamlit run app.py

# Option 2: Using the start script
chmod +x start.sh
./start.sh
```

### Access

Open your browser and navigate to: **http://localhost:8501**

## 🎯 Features

- **Priority-based task assignment** - Urgent, High, Medium, Low with color coding
- **Visual progress tracking** - Planning → Structuring → Unit Testing → Completion
- **Two workflow modes:**
  - **Iterative** - Execute, get feedback, refine (feedback loop)
  - **Immediate** - Execute without feedback cycle
- **Beautiful Streamlit UI** - Modern, dark theme with smooth animations
- **Auto-refresh** - See changes immediately when task files update
- **Search & Filter** - Find tasks by title, description, priority, or stage
- **KPI Dashboard** - Track visible tasks, in-progress, completed, and blocked items
- **Task persistence** - Tasks stored as JSON files in `tasks/` directory
- **One-click status updates** - Progress through stages effortlessly

## 📊 Workflow Stages

1. **Planning** - Task is created and ready to be worked on
2. **Structuring** - Jennie is working on the task
3. **Unit Testing** - Code is being tested/verified
4. **Completion** - Task is finished with a summary

## 📁 Project Structure

```
project-management-dashboard-python/
├── app.py                    # Main Streamlit dashboard application
├── convert_tasks.py          # Task file sanitization utility
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore patterns
├── start.sh                 # Quick start shell script
├── README.md                # This file
├── INSTALL.md               # Installation guide
├── SUMMARY.md               # Project summary
├── tasks/                   # Task storage directory
│   ├── task-001.json        # Individual task files
│   └── ...
└── venv/                    # Python virtual environment
```

## 💡 Usage Guide

### Creating a Task

1. Open the dashboard in your browser
2. In the sidebar, fill in:
   - **Title** - Brief description of the task
   - **Description** - Detailed explanation of what needs to be done
   - **Priority** - Select from Urgent, High, Medium, Low
   - **Workflow Mode** - Iterative (with feedback) or Immediate
   - **Assignee** - Usually "Jennie" (your coding agent)
3. Click **"Create Task"**
4. ✨ Task appears instantly in the board!

### Tracking Progress

- Each task shows its current stage with colored badges
- Click **Status Controls** to advance the task:
  - **Mark in progress** - Start working on the task
  - **Mark work finished** - Move to feedback stage (iterative mode)
  - **Resume work** - Continue after feedback (iterative mode)
  - **Mark completed** - Close the task
- Add a **Completion Summary** in the Details panel to document what was done

### Managing Tasks

- **Search** - Type in the search box to filter by title/description
- **Filter** - Use sidebar filters for priority, stage, or workflow mode
- **Block/Unblock** - Mark tasks as blocked with a reason and unblock requirements
- **Delete** - Remove tasks permanently

## 🔧 Task File Format

Tasks are stored as JSON files in the `tasks/` directory:

```json
{
  "id": "task-001",
  "title": "Task Title",
  "description": "Task description",
  "priority": "high",
  "stage": "planning",
  "workMode": "iterative",
  "workflowStage": "initial",
  "createdAt": "2026-03-12T11:10:48.534906",
  "updatedAt": "2026-03-12T11:10:48.535100",
  "assignee": "Jennie",
  "completion_summary": "What was accomplished",
  "notes": {
    "goal": "Optional goal",
    "requirements": ["Requirement 1", "Requirement 2"],
    "feedback": "Latest feedback if any",
    "blocked": false,
    "blockReason": null,
    "unblockNeeded": null,
    "timeEstimate": {
      "planned": "1 hour",
      "actual": null
    }
  }
}
```

## 🎨 Design

- **Colors:** Modern gradient dark theme with priority color coding
  - Urgent: 🔴 `#fb7185`
  - High: 🟠 `#f59e0b`
  - Medium: 🟡 `#38bdf8`
  - Low: 🟢 `#34d399`
- **Layout:** Clean, spacious, easy to read
- **Responsive:** Works on different screen sizes

## 🔧 Development

### Adding New Features

1. Edit `app.py` for UI/logic changes
2. Move complex logic to separate modules in `tasks/` if needed
3. Use `st.rerun()` to refresh the dashboard
4. Test changes by restarting Streamlit

### Task Sanitization

Run the utility to clean up task files:

```bash
python convert_tasks.py
```

This will:
- Remove HTML tags from text fields
- Normalize task structure
- Create `.bak` backups of modified files

### Running Tests (if added)

```bash
pytest tests/
```

## 🛠️ Tools & Technologies

- **Python 3.12**
- **Streamlit** - Web framework for the dashboard
- **Watchdog** - File system monitoring for auto-refresh
- **JSON** - Task storage format

## 📋 Best Practices

- Keep task descriptions clear and actionable
- Use appropriate priority levels (don't mark everything as urgent!)
- Add completion summaries when tasks are finished
- Review blocked tasks regularly
- Clean up old task files if needed

## 🚀 Next Steps

1. Install dependencies (`pip install -r requirements.txt`)
2. Run the dashboard (`streamlit run app.py`)
3. Create your first task
4. Start assigning work to Jennie
5. Track progress visually!

## 🤝 Contributing

This is a personal tool for managing work with Jennie. Feel free to customize it for your workflow!

## 📄 License

Proprietary - For personal use with Jennie

---

**Made with 💝 for Lei** | **Powered by Jennie**
