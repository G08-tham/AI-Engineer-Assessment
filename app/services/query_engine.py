from .data_loader import load_data
from .anomaly_detector import AnomalyDetector
from app.models.schemas import QueryPlan


class QueryEngine:

    def __init__(self):
        self.df = load_data()

    # =================================================
    # FILTER DATA
    # =================================================

    def apply_filters(self, filters):

        df = self.df.copy()

        if filters.status:

            df = df[
                df["status"].str.lower()
                == filters.status.lower()
            ]

        if filters.priority:

            df = df[
                df["priority"].str.lower()
                == filters.priority.lower()
            ]

        if filters.category:

            df = df[
                df["category"].str.lower()
                == filters.category.lower()
            ]

        if filters.agent_id:

            df = df[
                df["agent_id"].str.lower()
                == filters.agent_id.lower()
            ]

        return df

    # =================================================
    # COUNT TICKETS
    # =================================================

    def count_tickets(self, filters):

        df = self.apply_filters(filters)

        return len(df)

    # =================================================
    # AVERAGE RESPONSE TIME
    # =================================================

    def average_response_time(self, filters):

        df = self.apply_filters(filters)

        return round(
            df["response_time_hrs"].mean(),
            2
        )

    # =================================================
    # AVERAGE RESOLUTION TIME
    # =================================================

    def average_resolution_time(self, filters):

        df = self.apply_filters(filters)

        return round(
            df["resolution_time_hrs"].mean(),
            2
        )

    # =================================================
    # AVERAGE CUSTOMER RATING
    # =================================================

    def average_customer_rating(self, filters):

        df = self.apply_filters(filters)

        return round(
            df["customer_rating"].mean(),
            2
        )

    # =================================================
    # RESOLVED TICKETS BY AGENT
    # =================================================

    def resolved_tickets_by_agent(
        self,
        filters,
        current_month=False
    ):

        df = self.apply_filters(filters)

        # -------------------------------------------------
        # THIS MONTH
        #
        # The dataset is historical. Therefore, when the
        # question asks for "this month", we use the latest
        # calendar month available in the dataset.
        # -------------------------------------------------

        if current_month:

            latest_date = df["created_at"].max()

            latest_year = latest_date.year

            latest_month = latest_date.month

            df = df[
                (df["created_at"].dt.year == latest_year)
                & (df["created_at"].dt.month == latest_month)
            ]

        # -------------------------------------------------
        # ONLY RESOLVED TICKETS
        # -------------------------------------------------

        resolved = df[
            df["status"].str.lower()
            == "resolved"
        ]

        result = (
            resolved
            .groupby("agent_id")
            .size()
            .sort_values(
                ascending=False
            )
        )

        return result.to_dict()

    # =================================================
    # AVERAGE RATING BY CATEGORY
    # =================================================

    def average_rating_by_category(
        self,
        filters
    ):

        df = self.apply_filters(filters)

        result = (
            df.groupby("category")[
                "customer_rating"
            ]
            .mean()
            .round(2)
            .sort_values(
                ascending=False
            )
        )

        return result.to_dict()

    # =================================================
    # CRITICAL TICKETS NOT RESOLVED WITHIN 12 HOURS
    # =================================================

    def critical_unresolved(
        self,
        filters
    ):

        df = self.apply_filters(filters)

        critical = df[
            df["priority"].str.lower()
            == "critical"
        ].copy()

        not_resolved_within_12 = critical[
            (critical["resolution_time_hrs"].isna())
            | (
                critical["resolution_time_hrs"]
                > 12
            )
        ].copy()

        result = not_resolved_within_12[
            [
                "ticket_id",
                "created_at",
                "priority",
                "status",
                "resolution_time_hrs",
                "agent_id",
                "issue_summary"
            ]
        ].copy()

        result["created_at"] = (
            result["created_at"]
            .dt.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        records = result.to_dict(
            orient="records"
        )

        # Convert NaN values to None
        # so FastAPI can serialize the result.

        for record in records:

            for key, value in record.items():

                if (
                    isinstance(value, float)
                    and value != value
                ):

                    record[key] = None

        return records

    # =================================================
    # RESOLUTION-TIME ANOMALIES
    # =================================================

    def resolution_time_anomalies(self):

        detector = AnomalyDetector()

        return detector.detect_recent_resolution_anomalies(
            days=7
        )

    # =================================================
    # DATASET SUMMARY
    # =================================================

    def summary(self):

        df = self.df

        return {

            "total_tickets":
                len(df),

            "resolved":
                int(
                    (
                        df["status"].str.lower()
                        == "resolved"
                    ).sum()
                ),

            "open":
                int(
                    (
                        df["status"].str.lower()
                        == "open"
                    ).sum()
                ),

            "escalated":
                int(
                    (
                        df["status"].str.lower()
                        == "escalated"
                    ).sum()
                ),

            "average_response_time_hrs":
                round(
                    df["response_time_hrs"].mean(),
                    2
                ),

            "average_resolution_time_hrs":
                round(
                    df["resolution_time_hrs"].mean(),
                    2
                ),

            "average_customer_rating":
                round(
                    df["customer_rating"].mean(),
                    2
                )
        }

    # =================================================
    # EXECUTE QUERY PLAN
    # =================================================

    def execute_plan(self, plan):

        if plan.operation == "count":

            return self.count_tickets(
                plan.filters
            )

        if plan.operation == "average_response_time":

            return self.average_response_time(
                plan.filters
            )

        if plan.operation == "average_resolution_time":

            return self.average_resolution_time(
                plan.filters
            )

        if plan.operation == "average_customer_rating":

            return self.average_customer_rating(
                plan.filters
            )

        if plan.operation == "resolved_by_agent":

            # Determine whether the original request
            # contains "this month".
            #
            # The query engine receives only the plan,
            # so this is handled by a separate attribute
            # when used directly. By default this remains
            # False.

            return self.resolved_tickets_by_agent(
                plan.filters
            )

        if plan.operation == "rating_by_category":

            return self.average_rating_by_category(
                plan.filters
            )

        if plan.operation == "critical_unresolved":

            return self.critical_unresolved(
                plan.filters
            )

        if plan.operation == "anomaly_resolution_time":

            return self.resolution_time_anomalies()

        if plan.operation == "summary":

            return self.summary()

        raise ValueError(
            f"Unsupported operation: {plan.operation}"
        )


# =====================================================
# DIRECT TESTING
# =====================================================

if __name__ == "__main__":

    engine = QueryEngine()

    print(
        "\n===== TOTAL TICKETS ====="
    )

    print(
        engine.count_tickets(
            QueryPlan(
                operation="count"
            ).filters
        )
    )

    print(
        "\n===== OPEN TICKETS ====="
    )

    open_plan = QueryPlan(
        operation="count",
        filters={
            "status": "Open"
        }
    )

    print(
        engine.execute_plan(
            open_plan
        )
    )

    print(
        "\n===== TECHNICAL TICKETS ====="
    )

    technical_plan = QueryPlan(
        operation="count",
        filters={
            "category": "Technical"
        }
    )

    print(
        engine.execute_plan(
            technical_plan
        )
    )

    print(
        "\n===== TECHNICAL CUSTOMER RATING ====="
    )

    rating_plan = QueryPlan(
        operation="average_customer_rating",
        filters={
            "category": "Technical"
        }
    )

    print(
        engine.execute_plan(
            rating_plan
        )
    )

    print(
        "\n===== ALL RESOLVED TICKETS BY AGENT ====="
    )

    resolved_plan = QueryPlan(
        operation="resolved_by_agent"
    )

    print(
        engine.execute_plan(
            resolved_plan
        )
    )

    print(
        "\n===== THIS MONTH RESOLVED TICKETS BY AGENT ====="
    )

    this_month_result = (
        engine.resolved_tickets_by_agent(
            resolved_plan.filters,
            current_month=True
        )
    )

    print(
        this_month_result
    )

    print(
        "\n===== CRITICAL NOT RESOLVED WITHIN 12 HOURS ====="
    )

    critical_plan = QueryPlan(
        operation="critical_unresolved"
    )

    critical = engine.execute_plan(
        critical_plan
    )

    print(
        "Count:",
        len(critical)
    )

    for ticket in critical[:5]:

        print(ticket)

    print(
        "\n===== RESOLUTION-TIME ANOMALIES ====="
    )

    anomaly_plan = QueryPlan(
        operation="anomaly_resolution_time"
    )

    anomaly_result = engine.execute_plan(
        anomaly_plan
    )

    print(
        "Period:",
        anomaly_result.get(
            "period_start"
        ),
        "to",
        anomaly_result.get(
            "period_end"
        )
    )

    print(
        "Anomaly Count:",
        anomaly_result.get(
            "anomaly_count"
        )
    )

    print(
        "Upper Bound:",
        anomaly_result.get(
            "upper_bound_hrs"
        ),
        "hours"
    )

    print(
        "\nAnomalies:"
    )

    for anomaly in anomaly_result.get(
        "anomalies",
        []
    ):

        print(anomaly)