# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-03-12

### Added
- Comprehensive test suite with pytest (30+ unit tests)
  - `tests/test_app.py` - Dashboard functionality tests
  - `tests/test_convert_tasks.py` - Utility function tests
  - `tests/conftest.py` - Shared fixtures
- Type hints added to app.py core functions
- Module-level docstrings for main components

### Changed
- Updated requirements.txt with development dependencies (pytest, black, flake8, mypy, pre-commit, twine, build)
- Enhanced README.md with complete documentation
- Improved .gitignore with comprehensive Python patterns

### Security
- Added MIT License for open-source compliance

---

## [1.0.0] - 2026-03-05

### Added
- Initial release of Openbot Management Dashboard
- Streamlit-based task tracking interface
- Priority-based task assignment (Urgent, High, Medium, Low)
- Workflow stages (Planning → Structuring → Unit Testing → Completion)
- Two workflow modes: Iterative and Immediate
- Task persistence via JSON files
- Search and filter capabilities
- Visual KPIs and stage distribution charts
- Task sanitization utility script
