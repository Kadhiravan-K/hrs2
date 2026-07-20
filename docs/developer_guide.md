# Developer Guide

## Project structure

- `backend/`: business logic, validation, reporting, and sensor management
- `frontend/`: Tkinter screens and UI flow
- `database/`: SQLite schema, connection handling, and queries
- `docs/`: project documentation
- `reports/`: generated report files

## Development setup

1. Create a Python 3.13 virtual environment.
2. Activate it.
3. Install dependencies from `requirements.txt`.
4. Run the application with `python main.py`.

## Coding conventions

- Keep UI code in the `frontend` package.
- Keep domain logic in the `backend` package.
- Keep database access in the `database` package.
- Avoid mixing UI and business logic in the same module.

## Typical workflow

1. Modify backend logic or UI screens.
2. Run the app locally.
3. Validate the flow from patient registration to report preview.
4. Update documentation if behavior changes.
