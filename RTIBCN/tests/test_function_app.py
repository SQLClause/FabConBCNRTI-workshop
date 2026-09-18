import os
import unittest
from unittest.mock import patch

import function_app


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


if __name__ == "__main__":
    unittest.main()