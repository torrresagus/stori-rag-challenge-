# Application Deployed on AWS

For practical purposes, this repository is deployed on **AWS**. Its architecture is based on:

1. **PostgreSQL RDS** as the database.
2. **Private ECR** to store the built Docker image.
3. **App Runner** to deploy the image, featuring automatic scaling and more.

---

## Default AWS URL

- **URL**: [https://9y8jsuvvem.us-east-1.awsapprunner.com/](https://9y8jsuvvem.us-east-1.awsapprunner.com/)  
- **Swagger** (API Docs): [https://9y8jsuvvem.us-east-1.awsapprunner.com/docs](https://9y8jsuvvem.us-east-1.awsapprunner.com/docs)  
  - **User**: `STORI_ADMIN`  
  - **Password**: `StoriAdmin_`

Additionally, the application has been deployed with the custom domain:  
[api-2.agustinchallengeai.com.ar](http://api-2.agustinchallengeai.com.ar)  
However, DNS propagation was not yet complete as of **February 19, 2024 at 12 PM**.

---

## Additional Endpoint

- **/chat**: Provides a very simple interface to directly chat with the “Stori Annex” and run an automated analysis to generate metrics.


---
# Installation and Execution Guide

Below are the step-by-step instructions to install and run this project.

---

## 1. Clone the Repository

If you haven’t already, clone the repository:

```bash
git clone https://github.com/torrresagus/stori-rag-challenge-.git
cd https://github.com/torrresagus/stori-rag-challenge-.git
```
Checkout to branch feature/dialogue-state-management-Second-Challengeto access the second challenge
```bash
git fetch --all
git checkout -b feature/dialogue-state-management-Second-Challenge origin/feature/dialogue-state-management-Second-Challenge
```

---

## 2. Create and Activate a Virtual Environment (venv)

1. **Create** the virtual environment:
   ```bash
   python -m venv venv
   ```
   *(On Windows, you might need to use `python3 -m venv venv` or adjust your PATH as needed.)*

2. **Activate** the virtual environment:
   - **Linux/Mac**:
     ```bash
     source venv/bin/activate
     ```
   - **Windows** (PowerShell):
     ```powershell
     venv\Scripts\Activate.ps1
     ```

---

## 3. Install Initial Dependencies with `pip`

In the repository, there is a `requirements.txt` file. Install the base dependencies (including **Poetry**) by running:

```bash
pip install -r requirements.txt
```

> **Note:** This will install [Poetry](https://python-poetry.org/) as an additional dependency manager.

---

## 4. Install Project Dependencies with Poetry

Once **Poetry** is installed, there are two ways to install the dependencies defined in `pyproject.toml`:

1. **Using Make**:
   ```bash
   make install_dependencies
   ```
2. **Using Poetry directly**:
   ```bash
   poetry install --no-interaction --no-ansi
   ```

Both commands will install all the dependencies specified by the project.

---

## 5. Configure the PostgreSQL Connection

This project requires a **PostgreSQL** connection. There are several ways to set up the database:

1. **Use a deployed (remote) instance**.
2. **Install PostgreSQL locally on your computer**.
3. **Use the Docker container** provided in the repository:
   ```bash
   docker-compose up -d
   ```
   > This will spin up a local PostgreSQL instance via Docker.

Make sure to properly configure the environment variable or connection string so the application can connect to your database.

---

## 6. Run the API

### Option A: Using **Make** with Poetry

```bash
make local_run_poetry
```

This command internally runs:
```bash
poetry run uvicorn app.main:app --reload --port 8005
```
which will start the API on port 8005.

### Option B: Using Poetry Directly

```bash
poetry run uvicorn app.main:app --reload --port 8005
```

---

## 7. (Optional) Adjust the Poetry Environment Path

If you need to change the path of the virtual environment that **Poetry** uses, you can check its location with:

```bash
poetry env info --path
```

Then, **export** (in your terminal) or **configure** this path in your IDE to use that interpreter.  
There is also a **Make** command for this:

```bash
make poetry_path
```

---
