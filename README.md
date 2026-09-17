# AI Support Ticket Assistant

An AI-powered support ticket analytics application that allows users to ask natural-language questions about support tickets and receive data-driven answers.

The application combines a local Large Language Model (LLM) with deterministic Python/Pandas data processing to convert natural-language questions into structured query plans and execute them against a support-ticket dataset.

---
## Features

- Natural-language support ticket queries
- Local LLM-based query understanding using Ollama
- Structured query-plan generation
- Deterministic Pandas-based query execution
- Ticket count analysis
- Response-time analysis
- Resolution-time analysis
- Customer-rating analysis
- Agent performance analysis
- Critical-ticket detection
- Resolution-time anomaly detection using the IQR method
- REST API using FastAPI
- Interactive Streamlit web interface
- API health-check endpoint
- Automated unit tests
- Error handling for API and data-processing failures

---
## Example Questions

The application supports questions such as:

```text
How many tickets are currently open?

Which agent resolved the most tickets this month?

What is the average customer rating for Technical tickets?

Show me all Critical tickets not resolved within 12 hours.

Are there any anomalies in resolution times this week?

## Architecture

The application follows a simple AI-to-data pipeline:

```text
User Question
      |
      v
Streamlit UI
      |
      v
FastAPI REST API
      |
      v
LLM Service (Ollama)
      |
      v
Structured Query Plan
      |
      v
Question Service
      |
      v
Deterministic Query Engine
      |
      v
Pandas Data Processing
      |
      +----------------------+
      |                      |
      v                      v
Support Ticket Data     Anomaly Detector
      |                      |
      +----------+-----------+
                 |
                 v
            Final Result
                 |
                 v
           User Response
--

## Project Structure

```text
AI-Engineer-Assessment/
│
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── anomaly_detector.py
│   │   ├── data_loader.py
│   │   ├── llm_service.py
│   │   ├── query_engine.py
│   │   └── question_service.py
│   │
│   ├── __init__.py
│   ├── config.py
│   └── main.py
│
├── data/
│   └── support_tickets.csv
│
├── tests/
│   ├── test_anomaly.py
│   └── test_query.py
│
├── ui/
│   └── app.py
│
├── .gitignore
├── README.md
├── requirements.txt
└── venv/                  # Local only, excluded from Git
--
## Dataset

The application uses a support-ticket dataset containing **500 records**.

### Dataset Columns

| Column | Description |
|---|---|
| `ticket_id` | Unique support ticket identifier |
| `created_at` | Ticket creation date and time |
| `category` | Ticket category such as General, Billing, or Technical |
| `priority` | Ticket priority such as Low, Medium, High, or Critical |
| `status` | Ticket status such as Open, Resolved, or Escalated |
| `response_time_hrs` | Time taken to respond to the ticket |
| `resolution_time_hrs` | Time taken to resolve the ticket |
| `agent_id` | Support agent identifier |
| `customer_rating` | Customer rating for the ticket |
| `issue_summary` | Short description of the customer issue |

---
## Technology Stack

### Programming

- Python

### Data Processing

- Pandas
- NumPy

### AI / LLM

- Ollama
- Llama 3.2

### API

- FastAPI
- Uvicorn
- Pydantic

### User Interface

- Streamlit

### Data Science

- Scikit-learn

### Testing

- Python `unittest`

---
## LLM Query Planning

The application uses Ollama with the Llama 3.2 model to convert natural-language questions into structured JSON query plans.

For example:

```text
User Question:

How many tickets are currently open?
{
    "operation": "count",
    "filters": {
        "status": "Open"
    },
    "time_period": "all_time"
}
instead

Natural Language
       ↓
LLM
       ↓
Structured Query Plan
       ↓
Pydantic Validation
       ↓
Pandas Query Engine
       ↓
Actual Dataset Result

--
## Supported Operations

### Ticket Count

Counts tickets matching the requested filters.

Example:

```text
How many tickets are currently open?

Average Response Time

Calculates the average response time.

Example:

What is the average response time?
Average Resolution Time

Calculates the average resolution time.

Example:

What is the average resolution time for Technical tickets?
Average Customer Rating

Calculates average customer ratings.

Example:

What is the average customer rating for Technical tickets?
Resolved Tickets by Agent

Counts resolved tickets grouped by support agent.

Example:

Which agent resolved the most tickets?

The application can also interpret:

Which agent resolved the most tickets this month?
Rating by Category

Calculates average customer ratings grouped by ticket category.

Example:

Show average rating by category.
Critical Unresolved Tickets

Identifies Critical tickets that were not resolved within the 12-hour threshold.

Example:

Show me all Critical tickets not resolved within 12 hours.

Tickets with missing resolution time are treated as not resolved within the threshold.

Resolution-Time Anomaly Detection

Detects unusually high resolution times using the Interquartile Range (IQR) method.

Example:

Are there any anomalies in resolution times this week?

--
## Anomaly Detection

Resolution-time anomalies are detected using the **IQR method**.

The calculation is:

```text
IQR = Q3 - Q1

Upper Bound = Q3 + (1.5 × IQR)
--
## API

The application provides a REST API using FastAPI.

### Root Endpoint

```text
GET /
--
GET /health
{
    "status": "healthy"
}
--
POST /ask
{
    "question": "How many tickets are currently open?"
}
--
{
    "question": "How many tickets are currently open?",
    "query_plan": {
        "operation": "count",
        "filters": {
            "status": "Open"
        },
        "time_period": "all_time"
    },
    "result": 111
}
--
## Running the Application

### 1. Clone the Repository

```bash
git clone https://github.com/G08-tham/AI-Engineer-Assessment.git
cd AI-Engineer-Assessment
--
python -m venv venv
.\venv\Scripts\Activate.ps1
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
--
## Configure Ollama

Install Ollama and download the Llama 3.2 model.

Pull the model:

```powershell
ollama pull llama3.2
ollama list
http://localhost:11434
--
## Start the FastAPI Server

Open **Terminal 1** and activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1

uvicorn app.main:app --reload

http://127.0.0.1:8000
http://127.0.0.1:8000/docs
--
## Start the Streamlit Interface

Open **Terminal 2** and activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1

streamlit run ui/app.py

http://localhost:8501
--
## Running Tests

Open **Terminal 3** and activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1

python -m unittest discover -s tests -v

The project contains 10 automated tests covering:

Ticket counting
Status filtering
Category filtering
Customer-rating calculations
Agent resolution analysis
Monthly agent analysis
Critical-ticket detection
Dataset summary
Overall anomaly detection
Recent anomaly detection

Current validation result:

Ran 10 tests

OK
--
## Implementation Notes

### Current Month

For the `this_month` query, the application uses the latest month available in the dataset rather than the computer's calendar month.

This allows the assessment dataset to be analyzed consistently even though its records are historical.

### Current Week

For anomaly queries referring to `this week`, the application analyzes the latest 7-day period available in the dataset.

### Critical Ticket Rule

A Critical ticket is considered not resolved within 12 hours when:

```text
resolution_time_hrs is missing
OR
resolution_time_hrs > 12
--
## Error Handling

The application includes error handling for:

- Missing dataset files
- Invalid CSV values
- Invalid LLM JSON responses
- Invalid query plans
- Unsupported operations
- API execution errors

Pydantic models are used to validate the generated query plan before execution.

---
## Design Approach

A key design decision was to avoid allowing the LLM to directly execute arbitrary code or generate unrestricted database queries.

Instead, the LLM is restricted to a predefined set of operations and filters.

This provides a controlled architecture:

```text
User
  ↓
Natural Language Question
  ↓
LLM
  ↓
Validated Query Plan
  ↓
Predefined Python Operations
  ↓
Pandas
  ↓
Dataset
--
## Validation Results

The application was validated against the assessment's example questions.

| Question | Result |
|---|---:|
| How many tickets are currently open? | 111 |
| Which agent resolved the most tickets this month? | AGT-01 — 16 |
| Average customer rating for Technical tickets | 3.74 |
| Critical tickets not resolved within 12 hours | 34 |
| Resolution-time anomalies in latest 7-day period | 3 |

The automated test suite also passes all 10 tests.

---
## Future Improvements

Possible future enhancements include:

- Database-backed ticket storage
- Authentication and authorization
- More advanced date-range filtering
- Additional business KPIs
- More anomaly-detection techniques
- Conversation history
- Production LLM deployment
- Docker containerization
- Cloud deployment
- Expanded automated test coverage

---
## Author

**Gowtham R**

AI Engineer Intern Assessment Project