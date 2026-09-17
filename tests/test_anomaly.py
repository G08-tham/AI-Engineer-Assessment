import unittest

from app.services.anomaly_detector import AnomalyDetector


class TestAnomalyDetector(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.detector = AnomalyDetector()

    def test_resolution_anomaly_detection(self):

        result = self.detector.detect_resolution_anomalies()

        self.assertEqual(
            result["method"],
            "IQR"
        )

        self.assertEqual(
            result["anomaly_count"],
            21
        )

        self.assertGreater(
            result["upper_bound_hrs"],
            0
        )

        self.assertIsInstance(
            result["anomalies"],
            list
        )

    def test_recent_resolution_anomaly_detection(self):

        result = (
            self.detector
            .detect_recent_resolution_anomalies(
                days=7
            )
        )

        self.assertEqual(
            result["method"],
            "IQR"
        )

        self.assertEqual(
            result["anomaly_count"],
            3
        )

        self.assertEqual(
            result["upper_bound_hrs"],
            76.84
        )

        self.assertEqual(
            len(result["anomalies"]),
            3
        )

        ticket_ids = [
            anomaly["ticket_id"]
            for anomaly in result["anomalies"]
        ]

        self.assertIn(
            "TKT-108",
            ticket_ids
        )

        self.assertIn(
            "TKT-130",
            ticket_ids
        )

        self.assertIn(
            "TKT-158",
            ticket_ids
        )


if __name__ == "__main__":
    unittest.main()