# Dockerfile
FROM public.ecr.aws/docker/library/python:3.12-slim

# Set the time zone
ENV TZ=America/Argentina/Buenos_Aires
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install unix dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
        libmagic-dev \
        file \
        python3-dev \
        libpq-dev \
        postgresql-contrib && \
    rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip install --upgrade pip
COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY poetry.lock /poetry.lock
COPY pyproject.toml /pyproject.toml
RUN  poetry install --no-interaction --no-ansi --no-root

COPY app /app
COPY .env /.env

# Run start script
CMD ["poetry","run","uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]