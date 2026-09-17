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