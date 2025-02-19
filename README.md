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

# Metrics and Monitoring

In the production application, a **framework** has been implemented to measure costs, latencies, token usage, and more, allowing for performance and cost visualization.  
Additionally, it provides detailed tracking of all chats and LLM calls.

> **Note**: These metrics are **not** the same as those requested in the challenge; they are **additional** metrics.

## Access Link

- **URL**: [Traces in Langfuse](https://us.cloud.langfuse.com/project/cm7c0an7p0053ad07slee7lsk/traces)
- **Username**: `agustintorres2001@outlook.com.ar`
- **Password**: `StoriAdmin_`

# Automated Evaluation with Ground Truth

This module uses a **fact-testing** approach to automatically generate evaluation metrics (faithfulness, relevance, and correctness) by comparing the conversation against a **ground truth** dataset.

## How It Works

1. **Conversation & Ground Truth Retrieval**  
   - The system retrieves relevant ground-truth documents (questions and answers) from a vector database for each human message in the conversation.
   - By aligning the conversation content with these retrieved documents, the system determines how closely the conversation statements match the known facts (ground truth).

2. **Automated Analysis Agent**  
   - A specialized agent (**SessionAnalysisAgent**) processes the conversation and the retrieved ground truth.
   - It outputs structured metrics indicating how well the conversation aligns with verified facts.

3. **Metrics Computation**  
   The automated evaluation method provides three main metrics:

## Faithfulness
Measures how factually consistent the conversation is with the ground truth.

$$
\text{Faithfulness} 
= \frac{\text{Number of factually accurate statements}}{\text{Total number of factual statements examined}}
$$

---

## Relevance
Gauges how pertinent the content of the conversation is relative to the questions asked or the context provided.

$$
\text{Relevance}
= \frac{\text{Number of relevant statements}}{\text{Total number of statements examined}}
$$

---

## Correctness
Indicates the overall correctness of the conversation’s responses (e.g., whether given answers match the ground truth).

$$
\text{Correctness}
= \frac{\text{Number of correct answers}}{\text{Total number of answers examined}}
$$

Each of these metrics is computed by counting how many times the agent identifies a statement or response as **positive** (correct, relevant, or faithful) relative to the **total** statements or answers in the session. The higher each score, the better the conversation quality with respect to factual alignment, topical alignment, and accuracy.

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
