import json
import unittest
from pathlib import Path

from flatten import flatten_ibus, flatten_metro

IBUS_PAYLOAD = {
    "status": "success",
    "data": {
        "ibus": [
            {"line": "H16", "routeId": "1601", "destination": "Forum Campus Besos", "t-in-min": 4, "t-in-s": 230, "text-ca": "4 min"},
            {"line": "7", "routeId": "701", "destination": "Zona Universitaria", "t-in-min": 11, "t-in-s": 655, "text-ca": "11 min"},
            {"line": "H16", "routeId": "1601", "destination": "Forum Campus Besos", "t-in-min": 13, "t-in-s": 790, "text-ca": "13 min"},
            {"line": "7", "routeId": "701", "destination": "Zona Universitaria", "t-in-min": 0, "t-in-s": 20, "text-ca": "imminent"},
        ]
    },
}

# Real iTransit response captured 2026-09-18 (RTI/artifacts/EventSamples/itransit-metro-response.json)
_SAMPLE = Path(__file__).resolve().parents[2] / "artifacts" / "EventSamples" / "itransit-metro-response.json"
METRO_PAYLOAD = json.loads(_SAMPLE.read_text(encoding="utf-8")) if _SAMPLE.exists() else {
    "timestamp": 1789680601030,
    "linies": [{"codi_linia": 3, "nom_linia": "L3", "estacions": [
        {"codi_via": 1, "id_sentit": 1, "codi_estacio": 321, "linies_trajectes": [
            {"nom_linia": "L3", "codi_trajecte": "0031", "desti_trajecte": "Trinitat Nova",
             "propers_trens": [{"codi_servei": "303", "temps_arribada": 1789680710000}, {"codi_servei": "305", "temps_arribada": 1789681176000}]}]}]}]}


class FlattenIbusTests(unittest.TestCase):
    def test_one_event_per_prediction_with_rank_per_line(self) -> None:
        events = flatten_ibus("1497", "2026-09-30T07:15:02.123456+00:00", IBUS_PAYLOAD)
        self.assertEqual(len(events), 4)
        h16 = sorted((e for e in events if e["LineCode"] == "H16"), key=lambda e: e["Rank"])
        self.assertEqual([e["MinutesToArrival"] for e in h16], [4, 13])
        self.assertEqual([e["Rank"] for e in h16], [1, 2])
        seven = sorted((e for e in events if e["LineCode"] == "7"), key=lambda e: e["Rank"])
        self.assertEqual([e["SecondsToArrival"] for e in seven], [20, 655])  # rank by t-in-s, not array order

    def test_contract_fields_and_types(self) -> None:
        e = flatten_ibus(1497, "2026-09-30T07:15:02+00:00", IBUS_PAYLOAD)[0]
        self.assertEqual(set(e), {"EventType", "PolledAtUtc", "StopCode", "LineCode", "RouteId", "Destination",
                                  "Rank", "MinutesToArrival", "SecondsToArrival", "ArrivalText", "IsStale", "Source"})
        self.assertEqual(e["EventType"], "BusArrival")
        self.assertEqual(e["PolledAtUtc"], "2026-09-30T07:15:02Z")
        self.assertIsInstance(e["StopCode"], int)
        self.assertIs(e["IsStale"], False)

    def test_empty_or_malformed_payload_yields_nothing(self) -> None:
        self.assertEqual(flatten_ibus("1497", "2026-09-30T07:15:02Z", {}), [])
        self.assertEqual(flatten_ibus("1497", "2026-09-30T07:15:02Z", {"data": {"ibus": "nope"}}), [])
        self.assertEqual(flatten_ibus("abc", "2026-09-30T07:15:02Z", IBUS_PAYLOAD), [])


class FlattenMetroTests(unittest.TestCase):
    def test_real_response_shape(self) -> None:
        events = flatten_metro("2026-09-17T21:30:01Z", METRO_PAYLOAD)
        self.assertTrue(events)
        # one event per train: sample has 2 trains per station/track
        st321_dir1 = [e for e in events if e["StationCode"] == 321 and e["Direction"] == "Trinitat Nova"]
        self.assertEqual([(e["Rank"], e["ServiceId"]) for e in st321_dir1], [(1, "303"), (2, "305")])
        # seconds relative to the payload's own timestamp: (1789680710000 - 1789680601030) // 1000 = 108
        self.assertEqual(st321_dir1[0]["SecondsToArrival"], 108)
        self.assertEqual(st321_dir1[0]["PredictedArrivalUtc"], "2026-09-17T21:31:50Z")
        self.assertEqual(st321_dir1[0]["LineCode"], "L3")
        self.assertEqual(st321_dir1[0]["RouteId"], "0031")
        self.assertEqual(st321_dir1[0]["Track"], 1)

    def test_contract_fields(self) -> None:
        e = flatten_metro("2026-09-17T09:30:01Z", METRO_PAYLOAD)[0]
        self.assertEqual(set(e), {"EventType", "PolledAtUtc", "StationCode", "LineCode", "RouteId", "Direction",
                                  "DirectionId", "Track", "ServiceId", "Rank", "PredictedArrivalUtc",
                                  "SecondsToArrival", "IsStale", "Source"})
        self.assertEqual(e["EventType"], "MetroArrival")

    def test_unknown_shape_yields_nothing(self) -> None:
        self.assertEqual(flatten_metro("2026-09-30T07:15:05Z", {"whatever": 1}), [])


if __name__ == "__main__":
    unittest.main()
