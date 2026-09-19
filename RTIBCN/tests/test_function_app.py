import os
import unittest
from unittest.mock import patch

import function_app


class OutputRecorder:
    def __init__(self) -> None:
        self.value = None

    def set(self, value) -> None:
        self.value = value


class MetroRequestTests(unittest.TestCase):
    @patch.dict(os.environ, {"TMB_METRO_STATIONS": "120, 122,321"}, clear=False)
    def test_metro_request_uses_live_arrivals_endpoint(self) -> None:
        self.assertEqual(
            function_app._metro_request(),
            (
                "120,122,321",
                "itransit/metro/estacions",
                {"estacions": "120,122,321"},
            ),
        )

    @patch.dict(os.environ, {"TMB_METRO_STATIONS": ""}, clear=False)
    def test_metro_request_requires_station_codes(self) -> None:
        self.assertIsNone(function_app._metro_request())


class BusRequestTests(unittest.TestCase):
    @patch.dict(os.environ, {"TMB_IBUS_STOPS": "108, 1265"}, clear=False)
    def test_bus_requests_use_current_realtime_endpoint(self) -> None:
        self.assertEqual(
            function_app._ibus_requests(),
            [
                ("108", "itransit/bus/parades/108", None),
                ("1265", "itransit/bus/parades/1265", None),
            ],
        )


class EventHubFanOutTests(unittest.TestCase):
    def test_sets_identical_events_on_both_outputs(self) -> None:
        first = OutputRecorder()
        second = OutputRecorder()
        messages = ["first", "second"]

        function_app._set_dual_outputs(first, second, messages)

        self.assertEqual(first.value, messages)
        self.assertEqual(second.value, messages)


if __name__ == "__main__":
    unittest.main()