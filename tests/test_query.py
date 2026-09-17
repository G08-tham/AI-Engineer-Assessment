import unittest

from app.models.schemas import QueryPlan
from app.services.query_engine import QueryEngine


class TestQueryEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = QueryEngine()

    def test_total_ticket_count(self):
        plan = QueryPlan(
            operation="count"
        )

        result = self.engine.execute_plan(plan)

        self.assertEqual(result, 500)

    def test_open_ticket_count(self):
        plan = QueryPlan(
            operation="count",
            filters={
                "status": "Open"
            }
        )

        result = self.engine.execute_plan(plan)

        self.assertEqual(result, 111)

    def test_technical_ticket_count(self):
        plan = QueryPlan(
            operation="count",
            filters={
                "category": "Technical"
            }
        )

        result = self.engine.execute_plan(plan)

        self.assertEqual(result, 152)

    def test_technical_average_customer_rating(self):
        plan = QueryPlan(
            operation="average_customer_rating",
            filters={
                "category": "Technical"
            }
        )

        result = self.engine.execute_plan(plan)

        self.assertEqual(result, 3.74)

    def test_resolved_tickets_by_agent(self):
        plan = QueryPlan(
            operation="resolved_by_agent"
        )

        result = self.engine.execute_plan(plan)

        self.assertIsInstance(result, dict)

        self.assertIn(
            "AGT-01",
            result
        )

        self.assertEqual(
            result["AGT-09"],
            37
        )

        self.assertEqual(
            result["AGT-12"],
            37
        )

    def test_resolved_tickets_by_agent_this_month(self):
        plan = QueryPlan(
            operation="resolved_by_agent"
        )

        result = self.engine.resolved_tickets_by_agent(
            plan.filters,
            current_month=True
        )

        self.assertIsInstance(
            result,
            dict
        )

        self.assertEqual(
            result["AGT-01"],
            16
        )

    def test_critical_unresolved_tickets(self):
        plan = QueryPlan(
            operation="critical_unresolved"
        )

        result = self.engine.execute_plan(plan)

        self.assertIsInstance(
            result,
            list
        )

        self.assertEqual(
            len(result),
            34
        )

        for ticket in result:

            self.assertEqual(
                ticket["priority"],
                "Critical"
            )

    def test_summary(self):
        plan = QueryPlan(
            operation="summary"
        )

        result = self.engine.execute_plan(plan)

        self.assertEqual(
            result["total_tickets"],
            500
        )

        self.assertEqual(
            result["resolved"],
            327
        )

        self.assertEqual(
            result["open"],
            111
        )

        self.assertEqual(
            result["escalated"],
            62
        )


if __name__ == "__main__":
    unittest.main()