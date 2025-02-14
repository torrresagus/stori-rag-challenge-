local_run_poetry:
	poetry run uvicorn app.main:app --reload --port 8005
install_dependencies:
	poetry install --no-interaction --no-ansi
local_run:
	uvicorn app.main:app --reload --port 8005
format:
	poetry run black . && poetry run isort .