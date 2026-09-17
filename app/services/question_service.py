import re

from app.services.llm_service import LLMService
from app.services.query_engine import QueryEngine


class QuestionService:

    def __init__(self):

        self.llm = LLMService()

        self.engine = QueryEngine()

    # =================================================
    # CLEAN AND VALIDATE QUERY PLAN
    # =================================================

    def clean_query_plan(
        self,
        question,
        plan
    ):

        question_lower = question.lower()

        # -------------------------------------------------
        # CRITICAL TICKETS NOT RESOLVED WITHIN 12 HOURS
        # -------------------------------------------------

        if (
            "critical" in question_lower
            and "not resolved" in question_lower
            and "12 hours" in question_lower
        ):

            plan.operation = "critical_unresolved"

            plan.filters.status = None
            plan.filters.priority = None
            plan.filters.category = None
            plan.filters.agent_id = None

            plan.time_period = "all_time"

            return plan

        # -------------------------------------------------
        # RESOLUTION-TIME ANOMALIES
        # -------------------------------------------------

        anomaly_keywords = [
            "anomal",
            "outlier",
            "unusual resolution",
            "abnormal resolution",
            "unusually high resolution",
            "unusually long resolution"
        ]

        if any(
            keyword in question_lower
            for keyword in anomaly_keywords
        ):

            plan.operation = "anomaly_resolution_time"

            plan.filters.status = None
            plan.filters.priority = None
            plan.filters.category = None
            plan.filters.agent_id = None

            if "this week" in question_lower:
                plan.time_period = "this_week"
            else:
                plan.time_period = "all_time"

            return plan

        # -------------------------------------------------
        # STATUS FILTER
        # -------------------------------------------------

        status_match = re.search(
            r"\b(open|resolved|escalated)\b",
            question_lower
        )

        if status_match:

            plan.filters.status = (
                status_match.group(1).capitalize()
            )

        else:

            plan.filters.status = None

        # -------------------------------------------------
        # PRIORITY FILTER
        # -------------------------------------------------

        priority_match = re.search(
            r"\b(low|medium|high|critical)\b",
            question_lower
        )

        if priority_match:

            plan.filters.priority = (
                priority_match.group(1).capitalize()
            )

        else:

            plan.filters.priority = None

        # -------------------------------------------------
        # CATEGORY FILTER
        # -------------------------------------------------

        category_match = re.search(
            r"\b(general|billing|technical)\b",
            question_lower
        )

        if category_match:

            plan.filters.category = (
                category_match.group(1).capitalize()
            )

        else:

            plan.filters.category = None

        # -------------------------------------------------
        # AGENT FILTER
        # -------------------------------------------------

        agent_match = re.search(
            r"\bagt-\d{2}\b",
            question_lower
        )

        if agent_match:

            plan.filters.agent_id = (
                agent_match.group(0).upper()
            )

        else:

            plan.filters.agent_id = None

        # -------------------------------------------------
        # TIME PERIOD
        # -------------------------------------------------

        if "this month" in question_lower:

            plan.time_period = "this_month"

        elif "this week" in question_lower:

            plan.time_period = "this_week"

        else:

            plan.time_period = "all_time"

        return plan

    # =================================================
    # ASK QUESTION
    # =================================================

    def ask(self, question):

        # -------------------------------------------------
        # STEP 1:
        # LLM creates structured query plan
        # -------------------------------------------------

        plan = self.llm.create_query_plan(
            question
        )

        # -------------------------------------------------
        # STEP 2:
        # Clean and validate the plan
        # -------------------------------------------------

        plan = self.clean_query_plan(
            question,
            plan
        )

        # -------------------------------------------------
        # STEP 3:
        # Handle time-aware resolved-by-agent queries
        # -------------------------------------------------

        if (
            plan.operation == "resolved_by_agent"
            and plan.time_period == "this_month"
        ):

            result = (
                self.engine.resolved_tickets_by_agent(
                    plan.filters,
                    current_month=True
                )
            )

        else:

            # -------------------------------------------------
            # STEP 4:
            # Execute normal query
            # -------------------------------------------------

            result = self.engine.execute_plan(
                plan
            )

        # -------------------------------------------------
        # STEP 5:
        # Return API response
        # -------------------------------------------------

        return {
            "question": question,
            "query_plan": plan.model_dump(),
            "result": result
        }


# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":

    service = QuestionService()

    test_questions = [

        "How many tickets are currently open?",

        "Which agents resolved the most tickets?",

        "Which agent resolved the most tickets this month?",

        "What is the average customer rating for Technical tickets?",

        "Show me all Critical tickets not resolved within 12 hours.",

        "Are there any anomalies in resolution times this week?"
    ]

    for question in test_questions:

        print("\n" + "=" * 70)

        print("QUESTION:")

        print(question)

        try:

            response = service.ask(
                question
            )

            print("\nQUERY PLAN:")

            print(
                response["query_plan"]
            )

            result = response["result"]

            # -------------------------------------------------
            # LIST RESULT
            # -------------------------------------------------

            if isinstance(
                result,
                list
            ):

                print("\nRESULT COUNT:")

                print(
                    len(result)
                )

                print(
                    "\nFIRST 3 RESULTS:"
                )

                for item in result[:3]:

                    print(item)

            # -------------------------------------------------
            # ANOMALY RESULT
            # -------------------------------------------------

            elif (
                isinstance(result, dict)
                and "anomaly_count" in result
            ):

                print(
                    "\nANOMALY COUNT:"
                )

                print(
                    result["anomaly_count"]
                )

                print(
                    "\nPERIOD:"
                )

                print(
                    result.get(
                        "period_start"
                    ),
                    "to",
                    result.get(
                        "period_end"
                    )
                )

                print(
                    "\nUPPER BOUND:"
                )

                print(
                    result.get(
                        "upper_bound_hrs"
                    ),
                    "hours"
                )

                print(
                    "\nANOMALIES:"
                )

                for anomaly in result.get(
                    "anomalies",
                    []
                ):

                    print(anomaly)

            # -------------------------------------------------
            # DICTIONARY RESULT
            # -------------------------------------------------

            elif isinstance(
                result,
                dict
            ):

                print(
                    "\nRESULT:"
                )

                for key, value in result.items():

                    print(
                        f"{key}: {value}"
                    )

            # -------------------------------------------------
            # OTHER RESULT
            # -------------------------------------------------

            else:

                print(
                    "\nRESULT:"
                )

                print(result)

        except Exception as error:

            print(
                "\nERROR:"
            )

            print(error)