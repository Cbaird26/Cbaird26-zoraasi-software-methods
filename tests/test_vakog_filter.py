"""Paper B v0 software acceptance tests; no human data or qualia inference."""
import json
import hashlib
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType
from unittest import TestCase, main, mock

from zora_lab.vakog_filter import FilterConfig, Modality, Source, filter_observations


BASE = {"session_id": "synthetic-01", "t": 0, "consent": True}


def record(**optional):
    return {**BASE, **optional}


class PaperBv0Acceptance(TestCase):
    def test_01_missingness_not_measured_zero(self):
        result = filter_observations(record())
        self.assertIsNone(result["R_total"])
        self.assertEqual(result["B"], 0.0)
        self.assertEqual(set(result["channels"]), {"V", "A", "K", "OG", "Ad"})
        for channel in result["channels"].values():
            self.assertEqual(channel["a_m"], 0)
            self.assertIsNone(channel["R_m"])
            self.assertIsNone(channel["q_m"])
            self.assertIsNone(channel["provenance"])

    def test_02_metadata_alone_never_activates_senses(self):
        result = filter_observations(record(
            image_meta={"present": True, "provenance": "metadata_only"},
            audio_meta={"present": True, "provenance": "metadata_only"},
        ))
        self.assertIsNone(result["R_total"])
        self.assertEqual(result["B"], 0.0)
        self.assertEqual(result["channels"]["V"]["a_m"], 0)
        self.assertEqual(result["channels"]["A"]["a_m"], 0)
        self.assertEqual(result["attachment_meta"]["image_meta"]["present"], True)
        self.assertNotIn("temperature", json.dumps(result))

    def test_03_warmth_is_language_and_optional_lexical_k(self):
        result = filter_observations(record(text="I feel warm"))
        self.assertEqual(result["channels"]["Ad"]["a_m"], 1)
        self.assertEqual(result["channels"]["K"]["a_m"], 1)
        self.assertEqual(result["channels"]["K"]["provenance"], "text_lexical_proxy")
        self.assertEqual(result["channels"]["V"]["a_m"], 0)
        self.assertEqual(result["channels"]["A"]["a_m"], 0)
        self.assertEqual(result["channels"]["OG"]["a_m"], 0)
        self.assertNotIn("temperature", json.dumps(result))
        self.assertNotIn("instrument_measurement", json.dumps(result))
        self.assertNotIn("I feel warm", json.dumps(result))

    def test_04_unknown_and_field_measurement_inputs_rejected(self):
        for forbidden in ("Phi_c", "phi_c", "E_field", "weird", "model_emotion"):
            with self.subTest(key=forbidden), self.assertRaises(ValueError):
                filter_observations(record(**{forbidden: 1}))
        for forbidden in ("Phi_c", "E_field"):
            with self.subTest(nested=forbidden), self.assertRaises(ValueError):
                filter_observations(record(image_meta={"present": True, "provenance": "metadata_only", forbidden: 1}))
            with self.subTest(packet=forbidden), self.assertRaises(ValueError):
                filter_observations(record(packet={"packet_arrived": False, forbidden: 1}))

    def test_05_isolation_bare_import_no_phase2_no_write(self):
        root = Path(__file__).resolve().parents[1]
        script = """import sys, json
import zora_lab.vakog_filter
print(json.dumps({'phase2':[x for x in sys.modules if x.startswith('phase2') or '.phase2' in x], 'connection_loaded':'zora_lab.connection_study' in sys.modules}))
"""
        with tempfile.TemporaryDirectory() as d:
            environment = os.environ.copy()
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            environment["PYTHONPATH"] = str(root)
            module_path = root / "zora_lab" / "vakog_filter.py"
            before = hashlib.sha256(module_path.read_bytes()).hexdigest()
            result = subprocess.run([sys.executable, "-B", "-c", script], cwd=d, env=environment,
                                    text=True, capture_output=True, check=True, timeout=10)
            self.assertEqual(json.loads(result.stdout), {"phase2": [], "connection_loaded": False})
            self.assertEqual(list(Path(d).iterdir()), [])
            after = hashlib.sha256(module_path.read_bytes()).hexdigest()
            self.assertEqual(before, after)

    def test_06_exact_weighted_aggregate_and_bandwidth(self):
        config = FilterConfig(interference=1.0, lambda_interference=2.0)
        result = filter_observations(record(text="I feel warm"), config=config)
        self.assertAlmostEqual(result["R_total"], (0.2 * 1.0 + 0.2 * 0.5) / (0.2 + 0.2))
        self.assertAlmostEqual(result["B"], (0.2 * 1.0 + 0.2 * 0.5) / (1.0 + 2.0 * 1.0))
        self.assertEqual(result["I_method"], "operator_declared_constant_v0")
        self.assertEqual(result["I"], 1.0)
        self.assertTrue(0 <= result["B"] <= 1)

    def test_07_custom_weights_and_zero_weight_available_channel(self):
        weights = {m: 0.0 for m in Modality}
        weights[Modality.V] = 1.0
        config = FilterConfig(weights=weights)
        result = filter_observations(record(text="I feel warm"), config=config)
        self.assertEqual(result["channels"]["Ad"]["a_m"], 1)
        self.assertIsNone(result["R_total"])
        self.assertEqual(result["B"], 0.0)

    def test_08_og_remains_combined(self):
        result = filter_observations(record(text="I smell roses and I taste tea"))
        self.assertEqual(result["channels"]["OG"]["a_m"], 1)
        self.assertNotIn("O", result["channels"])
        self.assertNotIn("G", result["channels"])
        self.assertEqual(result["channels"]["OG"]["feature_map"], "explicit_lexical_indicators_v0")

    def test_09_network_state_read_only_never_affect(self):
        fake = ModuleType("zora_lab.connection_study")
        class ConnectionObservation:
            def __init__(self, packet_arrived, advance_notice=False, condition="unannounced"):
                if type(packet_arrived) is not bool or type(advance_notice) is not bool:
                    raise ValueError("bools required")
                self.packet_arrived = packet_arrived
                self.advance_notice = advance_notice
                self.condition = condition
        fake.ConnectionObservation = ConnectionObservation
        calls = []
        def telemetry(observation):
            calls.append(observation)
            return {"telemetry_state": "unexplained_gap", "model_emotion": None}
        fake.telemetry = telemetry
        with mock.patch.dict(sys.modules, {"zora_lab.connection_study": fake}):
            result = filter_observations(record(packet={"packet_arrived": False}))
        self.assertEqual(result["telemetry_state"], "unexplained_gap")
        self.assertEqual(len(calls), 1)
        self.assertTrue(all(channel["a_m"] == 0 for channel in result["channels"].values()))
        self.assertNotIn("model_emotion", result)
        self.assertEqual(result["claims"], [])

    def test_10_no_consent_no_personal_input(self):
        for optional in ({"text": "I feel warm"}, {"image_meta": {"present": False, "provenance": "metadata_only"}},
                         {"packet": {"packet_arrived": False}}):
            with self.subTest(optional=optional), self.assertRaises(ValueError):
                filter_observations({"session_id": "id", "t": 0, "consent": False, **optional})
        no_input = filter_observations({"session_id": "id", "t": 0, "consent": False})
        self.assertIsNone(no_input["R_total"])
        with self.assertRaises(ValueError):
            filter_observations({"session_id": "id", "t": 0})

    def test_11_invalid_input_types_and_metadata(self):
        bad = (dict(t=True), dict(t=-1), dict(t=0.1), dict(consent=1),
               dict(session_id=""), dict(text=123), dict(audio_meta=True),
               dict(image_meta={"present": 1, "provenance": "metadata_only"}),
               dict(image_meta={"present": True, "provenance": "instrument_measurement"}))
        for broken in bad:
            with self.subTest(broken=broken), self.assertRaises(ValueError):
                filter_observations(record(**broken))
        with self.assertRaises(TypeError):
            filter_observations("not a record")

    def test_12_weights_reliability_and_parameters_strict(self):
        for weights in ({Modality.V: 1.0}, {m: 0.0 for m in Modality},
                        {m: 1.0 for m in Modality},
                        {**{m: 0.2 for m in Modality}, Modality.V: -0.1}):
            with self.subTest(weights=weights), self.assertRaises(ValueError):
                FilterConfig(weights=weights)
        for value in (True, -1, float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                FilterConfig(interference=value)
            with self.subTest(lambda_=value), self.assertRaises(ValueError):
                FilterConfig(lambda_interference=value)
        with self.assertRaises(ValueError):
            FilterConfig(lexical_reliability={m: (1.2 if m is Modality.K else 0.5) for m in Modality})

    def test_13_config_is_frozen_and_copies_weights(self):
        weights = {m: 0.2 for m in Modality}
        config = FilterConfig(weights=weights)
        weights[Modality.V] = 0.9
        self.assertEqual(config.weights[Modality.V], 0.2)
        with self.assertRaises(TypeError):
            config.weights[Modality.V] = 0.7

    def test_14_deterministic_json_no_raw_text(self):
        x = record(text="I smell roses; I feel warm")
        a = filter_observations(x)
        self.assertEqual(a, filter_observations(x))
        self.assertNotIn(x["text"], json.dumps(a))
        self.assertEqual(a["status"], "representational_filter_v0_no_qualia")
        self.assertEqual(a["claims"], [])
        self.assertNotIn("Phi_c", a)
        self.assertNotIn("E_field", a)
        self.assertNotIn("model_emotion", a)
        self.assertTrue(math.isfinite(a["B"]))

    def test_15_missing_packet_omitted_not_false(self):
        a = filter_observations(record(text=""))
        self.assertNotIn("telemetry_state", a)
        self.assertEqual(a["channels"]["Ad"]["a_m"], 0)


if __name__ == "__main__":
    main()
