from .data_loader import load_data


class AnomalyDetector:

    def __init__(self):
        self.df = load_data()

    # -------------------------------------------------
    # DETECT ANOMALIES IN RESOLUTION TIME
    # -------------------------------------------------

    def detect_resolution_anomalies(self):

        df = self.df.copy()

        # Keep only tickets that have a resolution time
        resolved_data = df[
            df["resolution_time_hrs"].notna()
        ].copy()

        # -------------------------------------------------
        # IQR METHOD
        # -------------------------------------------------

        q1 = resolved_data[
            "resolution_time_hrs"
        ].quantile(0.25)

        q3 = resolved_data[
            "resolution_time_hrs"
        ].quantile(0.75)

        iqr = q3 - q1

        lower_bound = q1 - (1.5 * iqr)

        upper_bound = q3 + (1.5 * iqr)

        # -------------------------------------------------
        # FIND ANOMALOUS TICKETS
        # -------------------------------------------------

        anomalies = resolved_data[
            (
                resolved_data["resolution_time_hrs"]
                < lower_bound
            )
            |
            (
                resolved_data["resolution_time_hrs"]
                > upper_bound
            )
        ].copy()

        # -------------------------------------------------
        # SELECT USEFUL COLUMNS
        # -------------------------------------------------

        anomalies = anomalies[
            [
                "ticket_id",
                "created_at",
                "category",
                "priority",
                "status",
                "resolution_time_hrs",
                "agent_id",
                "issue_summary"
            ]
        ].copy()

        # Sort highest resolution time first
        anomalies = anomalies.sort_values(
            "resolution_time_hrs",
            ascending=False
        )

        # Convert datetime to string
        anomalies["created_at"] = (
            anomalies["created_at"]
            .dt.strftime("%Y-%m-%d %H:%M:%S")
        )

        # -------------------------------------------------
        # CONVERT TO JSON-SAFE RECORDS
        # -------------------------------------------------

        records = anomalies.to_dict(
            orient="records"
        )

        return {
            "method": "IQR",
            "q1": round(float(q1), 2),
            "q3": round(float(q3), 2),
            "iqr": round(float(iqr), 2),
            "upper_bound_hrs": round(
                float(upper_bound),
                2
            ),
            "anomaly_count": len(records),
            "anomalies": records
        }

    # -------------------------------------------------
    # ANALYZE RECENT DATA PERIOD
    # -------------------------------------------------

    def detect_recent_resolution_anomalies(
        self,
        days=7
    ):

        df = self.df.copy()

        # Use the latest date available in the dataset
        # rather than the computer's current date.
        latest_date = df["created_at"].max()

        start_date = (
            latest_date
            - __import__("pandas").Timedelta(
                days=days - 1
            )
        )

        recent_data = df[
            (
                df["created_at"] >= start_date
            )
            &
            (
                df["created_at"] <= latest_date
            )
        ].copy()

        # Only records with resolution times can
        # be analyzed for resolution-time anomalies.
        resolved_data = recent_data[
            recent_data["resolution_time_hrs"].notna()
        ].copy()

        # If there are not enough records, return
        # a clear response instead of failing.
        if len(resolved_data) < 4:

            return {
                "method": "IQR",
                "period_start": start_date.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "period_end": latest_date.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "anomaly_count": 0,
                "anomalies": [],
                "message": (
                    "Not enough resolved tickets "
                    "in the latest 7-day period "
                    "to perform reliable anomaly detection."
                )
            }

        # -------------------------------------------------
        # IQR CALCULATION
        # -------------------------------------------------

        q1 = resolved_data[
            "resolution_time_hrs"
        ].quantile(0.25)

        q3 = resolved_data[
            "resolution_time_hrs"
        ].quantile(0.75)

        iqr = q3 - q1

        upper_bound = q3 + (1.5 * iqr)

        # -------------------------------------------------
        # FIND ANOMALIES
        # -------------------------------------------------

        anomalies = resolved_data[
            resolved_data["resolution_time_hrs"]
            > upper_bound
        ].copy()

        anomalies = anomalies.sort_values(
            "resolution_time_hrs",
            ascending=False
        )

        anomalies = anomalies[
            [
                "ticket_id",
                "created_at",
                "category",
                "priority",
                "status",
                "resolution_time_hrs",
                "agent_id",
                "issue_summary"
            ]
        ]

        # Convert datetime to string
        anomalies["created_at"] = (
            anomalies["created_at"]
            .dt.strftime("%Y-%m-%d %H:%M:%S")
        )

        records = anomalies.to_dict(
            orient="records"
        )

        return {
            "method": "IQR",

            "period_start":
                start_date.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "period_end":
                latest_date.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "q1":
                round(float(q1), 2),

            "q3":
                round(float(q3), 2),

            "iqr":
                round(float(iqr), 2),

            "upper_bound_hrs":
                round(float(upper_bound), 2),

            "anomaly_count":
                len(records),

            "anomalies":
                records
        }


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":

    detector = AnomalyDetector()

    print("\n==============================================")
    print("ALL RESOLUTION-TIME ANOMALIES")
    print("==============================================")

    result = detector.detect_resolution_anomalies()

    print("\nMethod:")
    print(result["method"])

    print("\nQ1:")
    print(result["q1"])

    print("\nQ3:")
    print(result["q3"])

    print("\nIQR:")
    print(result["iqr"])

    print("\nUpper Bound:")
    print(
        result["upper_bound_hrs"],
        "hours"
    )

    print("\nAnomaly Count:")
    print(result["anomaly_count"])

    print("\nFirst 5 anomalies:")

    for anomaly in result["anomalies"][:5]:
        print(anomaly)

    print("\n==============================================")
    print("LATEST 7-DAY RESOLUTION-TIME ANOMALIES")
    print("==============================================")

    recent_result = (
        detector
        .detect_recent_resolution_anomalies(
            days=7
        )
    )

    print("\nPeriod:")
    print(
        recent_result.get("period_start"),
        "to",
        recent_result.get("period_end")
    )

    print("\nAnomaly Count:")
    print(
        recent_result["anomaly_count"]
    )

    if recent_result["anomalies"]:

        print("\nAnomalies:")

        for anomaly in recent_result["anomalies"]:
            print(anomaly)

    else:

        print(
            "\nNo resolution-time anomalies "
            "were detected in the latest 7-day period."
        )