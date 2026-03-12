# Installation Guide

## Quick Setup (Recommended)

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   ```

2. **Activate it:**
   ```bash
   source venv/bin/activate
   ```

3. **Install packages:**
   ```bash
   pip install streamlit watchdog
   ```

4. **Run the dashboard:**
   ```bash
   streamlit run app.py
   ```

5. **Open in browser:** http://localhost:8501

## Exit Virtual Environment

When done:
```bash
deactivate
```

---

That's it! The virtual environment keeps your packages isolated and won't break your system Python.
