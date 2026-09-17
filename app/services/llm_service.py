import json
import requests

from app.models.schemas import QueryPlan


class LLMService:

    def __init__(
        self,
        model="llama3.2",
        base_url="http://localhost:11434"
    ):
        self.model = model
        self.base_url = base_url

    def create_query_plan(self, question):

        prompt = f"""
You convert support-ticket questions into JSON.

You MUST return ONLY one valid JSON object.

Do NOT write explanations.
Do NOT use markdown.
Do NOT use code fences.

=================================================
ALLOWED OPERATIONS
=================================================

count
average_response_time
average_resolution_time
average_customer_rating
resolved_by_agent
rating_by_category
critical_unresolved
anomaly_resolution_time
summary

=================================================
ALLOWED FILTERS
=================================================

status:
Open, Resolved, Escalated

priority:
Low, Medium, High, Critical

category:
General, Billing, Technical

agent_id:
Agent IDs are strings in the format AGT-01, AGT-02, ..., AGT-12.

agent_id must ALWAYS be a string.

=================================================
ALLOWED TIME PERIODS
=================================================

time_period must be exactly one of:

this_month
this_week
all_time

Use:

"this_month"

when the user explicitly says:
- this month
- during this month
- in the current month

Use:

"this_week"

when the user explicitly says:
- this week
- during this week
- in the current week

Otherwise use:

"all_time"

IMPORTANT:
Do NOT create timestamp filters.

Do NOT create date ranges.

Do NOT create fields such as:
timestamp
created_at
date
start_date
end_date

The application handles time periods.

=================================================
FILTER RULE
=================================================

Only use a status, priority, category, or agent_id
filter when the user explicitly mentions it.

Do NOT invent filters.

=================================================
OPERATION RULES
=================================================

1. COUNT

Use "count" when the user asks how many tickets
match a condition.

Example:

Question:
How many tickets are currently open?

Return:

{{
    "operation": "count",
    "filters": {{
        "status": "Open"
    }},
    "time_period": "all_time"
}}


2. AVERAGE RESPONSE TIME

Use "average_response_time" when the user asks
for average response time.

Example:

Question:
What is the average response time?

Return:

{{
    "operation": "average_response_time",
    "filters": {{}},
    "time_period": "all_time"
}}


3. AVERAGE RESOLUTION TIME

Use "average_resolution_time" when the user asks
for average resolution time.

Example:

Question:
What is the average resolution time for Technical tickets?

Return:

{{
    "operation": "average_resolution_time",
    "filters": {{
        "category": "Technical"
    }},
    "time_period": "all_time"
}}


4. AVERAGE CUSTOMER RATING

Use "average_customer_rating" when the user asks
for average customer rating.

Example:

Question:
What is the average customer rating for Technical tickets?

Return:

{{
    "operation": "average_customer_rating",
    "filters": {{
        "category": "Technical"
    }},
    "time_period": "all_time"
}}


5. RESOLVED TICKETS BY AGENT

Use "resolved_by_agent" when the user asks:

- Which agents resolved the most tickets?
- Which agent resolved the most tickets?
- Show resolved tickets by agent.
- Who resolved the most tickets?

Example:

Question:
Which agents resolved the most tickets?

Return:

{{
    "operation": "resolved_by_agent",
    "filters": {{}},
    "time_period": "all_time"
}}

For:

Question:
Which agent resolved the most tickets this month?

Return:

{{
    "operation": "resolved_by_agent",
    "filters": {{}},
    "time_period": "this_month"
}}

IMPORTANT:
Do NOT add "status": "Resolved" as a user filter
unless the user explicitly says "resolved".

The resolved_by_agent operation itself counts
resolved tickets.


6. RATING BY CATEGORY

Use "rating_by_category" when the user asks
for customer ratings grouped by category.

Example:

Question:
Show average rating by category.

Return:

{{
    "operation": "rating_by_category",
    "filters": {{}},
    "time_period": "all_time"
}}


7. CRITICAL UNRESOLVED TICKETS

Use "critical_unresolved" when the user asks:

- Critical tickets not resolved within 12 hours.
- Critical unresolved tickets.
- Critical tickets that exceeded the 12-hour resolution limit.

Example:

Question:
Show me all Critical tickets not resolved within 12 hours.

Return:

{{
    "operation": "critical_unresolved",
    "filters": {{}},
    "time_period": "all_time"
}}

IMPORTANT:
For critical_unresolved, do NOT add:

status
priority
category
agent_id
timestamp
created_at
resolution_time
date filters

The application handles the Critical priority
and 12-hour resolution rule automatically.


8. RESOLUTION-TIME ANOMALIES

Use "anomaly_resolution_time" when the user asks
about anomalies, unusual resolution times,
outliers, or abnormal resolution times.

Example:

Question:
Are there any anomalies in resolution times this week?

Return:

{{
    "operation": "anomaly_resolution_time",
    "filters": {{}},
    "time_period": "this_week"
}}

Question:
Show me resolution time outliers.

Return:

{{
    "operation": "anomaly_resolution_time",
    "filters": {{}},
    "time_period": "all_time"
}}

IMPORTANT:
Do NOT create timestamp or date filters.

The application handles the time period.


9. SUMMARY

Use "summary" when the user asks for an overall
summary or overview of the support-ticket dataset.

Example:

Question:
Give me an overview of the support tickets.

Return:

{{
    "operation": "summary",
    "filters": {{}},
    "time_period": "all_time"
}}


=================================================
USER QUESTION
=================================================

{question}

=================================================
OUTPUT REQUIREMENT
=================================================

Return ONLY one valid JSON object.

The JSON object MUST contain:

operation
filters
time_period

Example:

{{
    "operation": "count",
    "filters": {{
        "status": "Open"
    }},
    "time_period": "all_time"
}}
"""

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        raw_response = data.get(
            "response",
            ""
        ).strip()

        print("\n===== RAW LLM RESPONSE =====")
        print(raw_response)

        if raw_response.startswith("```"):

            raw_response = raw_response.replace(
                "```json",
                ""
            )

            raw_response = raw_response.replace(
                "```",
                ""
            )

            raw_response = raw_response.strip()

        try:

            parsed_response = json.loads(
                raw_response
            )

        except json.JSONDecodeError as error:

            raise ValueError(
                "LLM did not return valid JSON.\n"
                f"Raw response: {raw_response}\n"
                f"Error: {error}"
            )

        query_plan = QueryPlan(
            **parsed_response
        )

        return query_plan


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":

    llm = LLMService()

    test_questions = [

        "How many tickets are currently open?",

        "Which agents resolved the most tickets?",

        "Which agent resolved the most tickets this month?",

        "What is the average customer rating for Technical tickets?",

        "Show me all Critical tickets not resolved within 12 hours.",

        "Are there any anomalies in resolution times this week?"
    ]

    for question in test_questions:

        print(
            "\n" + "=" * 70
        )

        print(
            "QUESTION:"
        )

        print(question)

        try:

            plan = llm.create_query_plan(
                question
            )

            print(
                "\nQUERY PLAN:"
            )

            print(
                plan.model_dump()
            )

        except Exception as error:

            print(
                "\nERROR:"
            )

            print(error)