from typing import Optional, Literal

from pydantic import BaseModel, Field


class QueryFilters(BaseModel):

    status: Optional[str] = None

    priority: Optional[str] = None

    category: Optional[str] = None

    agent_id: Optional[str] = None


class QueryRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=3,
        description="Natural language question about support tickets"
    )


class QueryPlan(BaseModel):

    operation: Literal[
        "count",
        "average_response_time",
        "average_resolution_time",
        "average_customer_rating",
        "resolved_by_agent",
        "rating_by_category",
        "critical_unresolved",
        "anomaly_resolution_time",
        "summary"
    ]

    filters: QueryFilters = QueryFilters()

    time_period: Optional[
        Literal[
            "this_month",
            "this_week",
            "all_time"
        ]
    ] = "all_time"