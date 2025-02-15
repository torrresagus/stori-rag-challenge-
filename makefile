local_run_poetry:
	poetry run uvicorn app.main:app --reload --port 8005
install_dependencies:
	poetry install --no-interaction --no-ansi
local_run:
	uvicorn app.main:app --reload --port 8005
format:
	poetry run black . && poetry run isort .

docker_build:
	docker build -t stori-rag-challenge -f Dockerfile . --platform linux/amd64

docker_run:
	docker run --env-file .env -p 8000:8000 stori-rag-challenge:latest

poetry_path:
	poetry env info --path