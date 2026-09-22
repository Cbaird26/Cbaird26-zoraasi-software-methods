"""Paper B v0: five-channel, text-first representational filter.

Implements the separate Paper_B_v0_spec_sheet.md software contract. This is
not a sensor, affect-recognition model, consciousness measurement, or physics
model. Importing this module neither imports nor writes Phase 2.3 files.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import fsum, isclose, isfinite
import re
from types import MappingProxyType
from typing import Mapping


class Modality(str, Enum):
    V = "V"
    A = "A"
    K = "K"
    OG = "OG"
    Ad = "Ad"


class Source(str, Enum):
    TEXT_LEXICAL_PROXY = "text_lexical_proxy"
    METADATA_ONLY = "metadata_only"


STATUS = "representational_filter_v0_no_qualia"
FEATURE_MAP_VERSION = "explicit_lexical_indicators_v0"
INTERFERENCE_RULE_VERSION = "operator_declared_constant_v0"
_INPUT_KEYS = frozenset({"session_id", "t", "consent", "text", "image_meta", "audio_meta", "packet"})
_METADATA_KEYS = frozenset({"present", "provenance"})
_PACKET_KEYS = frozenset({"packet_arrived", "advance_notice", "condition"})
_DEFAULT_WEIGHTS = {m: 1.0 / len(Modality) for m in Modality}
_DEFAULT_RELIABILITY = {m: (1.0 if m is Modality.Ad else 0.5) for m in Modality}

# Explicit narrow lexical proxies: these are word/phrase matches, not evidence
# of an image, waveform, bodily state, smell, or taste in the model.
_PATTERNS = {
    Modality.V: (re.compile(r"\b(?:i see|i saw|i look at|picture of|image of)\b", re.I),),
    Modality.A: (re.compile(r"\b(?:i hear|i heard|sound of|listening to)\b", re.I),),
    Modality.K: (re.compile(r"\b(?:i feel warm|i feel cold|i feel hot|i feel pressure|i feel pain)\b", re.I),),
    Modality.OG: (re.compile(r"\b(?:i smell|i smelled|i taste|i tasted)\b", re.I),),
}


def _finite_nonnegative(value: object, name: str) -> float:
    if type(value) not in (int, float):
        raise ValueError(f"{name} must be a nonnegative finite number (not bool)")
    result = float(value)
    if not isfinite(result) or result < 0:
        raise ValueError(f"{name} must be a nonnegative finite number")
    return result


def _unit(value: object, name: str) -> float:
    result = _finite_nonnegative(value, name)
    if result > 1:
        raise ValueError(f"{name} must be in [0, 1]")
    return result


def _modality_map(value: Mapping, name: str, *, unit: bool) -> Mapping:
    if not isinstance(value, Mapping) or set(value) != set(Modality):
        raise ValueError(f"{name} must have exactly V, A, K, OG, Ad keys")
    cleaned = {}
    for modality, number in value.items():
        if not isinstance(modality, Modality):
            raise ValueError(f"{name} keys must be Modality members")
        cleaned[modality] = _unit(number, name) if unit else _finite_nonnegative(number, name)
    return MappingProxyType(cleaned)


@dataclass(frozen=True)
class FilterConfig:
    """Immutable operator-declared configuration, never fitted to test data."""
    weights: Mapping[Modality, float] = field(default_factory=lambda: dict(_DEFAULT_WEIGHTS))
    lexical_reliability: Mapping[Modality, float] = field(default_factory=lambda: dict(_DEFAULT_RELIABILITY))
    lambda_interference: float = 1.0
    interference: float = 0.0
    version: str = "paper_b_v0_1"

    def __post_init__(self) -> None:
        weights = _modality_map(self.weights, "weights", unit=True)
        if not isclose(fsum(weights.values()), 1.0, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError("weights must sum to 1")
        reliability = _modality_map(self.lexical_reliability, "lexical_reliability", unit=True)
        if not isinstance(self.version, str) or not self.version.strip():
            raise ValueError("version must be a nonempty string")
        object.__setattr__(self, "weights", weights)
        object.__setattr__(self, "lexical_reliability", reliability)
        object.__setattr__(self, "lambda_interference", _finite_nonnegative(self.lambda_interference, "lambda_interference"))
        object.__setattr__(self, "interference", _finite_nonnegative(self.interference, "interference"))


def _metadata(value: object, name: str) -> dict[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping) or set(value) != _METADATA_KEYS:
        raise ValueError(f"{name} requires exactly present and provenance")
    if type(value["present"]) is not bool or value["provenance"] != Source.METADATA_ONLY.value:
        raise ValueError(f"{name} must declare a boolean presence and metadata_only provenance")
    return {"present": value["present"], "provenance": Source.METADATA_ONLY.value}


def _network_state(packet: object) -> str:
    # A lazy, read-only call to Paper A. The module is not imported at all when
    # there is no packet; no source code or report is ever opened or modified.
    if isinstance(packet, Mapping):
        if not set(packet).issubset(_PACKET_KEYS) or "packet_arrived" not in packet:
            raise ValueError("packet requires packet_arrived and only declared keys")
    from zora_lab.connection_study import ConnectionObservation, telemetry

    if isinstance(packet, Mapping):
        packet = ConnectionObservation(**packet)
    if not isinstance(packet, ConnectionObservation):
        raise TypeError("packet must be a ConnectionObservation or its declared mapping")
    result = telemetry(packet)
    return result["telemetry_state"]


def filter_observations(record: Mapping[str, object], *, config: FilterConfig | None = None) -> dict[str, object]:
    """Return a JSON-compatible provenance-aware representation, without raw text.

    Input keys are strictly gated; lexical indicators are declared design
    choices rather than calibrated sensory measurements. The output has no
    emotion, subjective-state, or speculative field-measurement keys.
    """
    if not isinstance(record, Mapping):
        raise TypeError("record must be a mapping")
    if not set(record).issubset(_INPUT_KEYS) or not {"session_id", "t", "consent"}.issubset(record):
        raise ValueError("missing required input or undeclared input key")
    if not isinstance(record["session_id"], str) or not 0 < len(record["session_id"].strip()) <= 128:
        raise ValueError("session_id must be a nonempty pseudonymous string of at most 128 characters")
    if type(record["t"]) is not int or record["t"] < 0:
        raise ValueError("t must be a nonnegative integer, not bool")
    if type(record["consent"]) is not bool:
        raise ValueError("consent must be an explicit boolean")
    if not record["consent"] and any(key in record and record[key] is not None for key in ("text", "image_meta", "audio_meta", "packet")):
        raise ValueError("optional personal inputs require consent")
    text = record.get("text")
    if text is not None and not isinstance(text, str):
        raise ValueError("text must be a string or null")
    image_meta = _metadata(record.get("image_meta"), "image_meta")
    audio_meta = _metadata(record.get("audio_meta"), "audio_meta")
    if config is None:
        config = FilterConfig()
    if not isinstance(config, FilterConfig):
        raise TypeError("config must be a FilterConfig")

    tokens = text.strip() if text is not None else ""
    channels: dict[str, dict[str, object]] = {}
    weighted_resonance = 0.0
    active_weight = 0.0
    reliability_mass = 0.0
    for modality in Modality:
        if modality is Modality.Ad:
            available = bool(tokens)
        else:
            available = bool(tokens) and any(pattern.search(tokens) for pattern in _PATTERNS[modality])
        if available:
            # v0 binary feature map: 1 if a declared lexical indicator exists.
            feature_value = 1.0
            q = config.lexical_reliability[modality]
            resonance = q * feature_value
            w = config.weights[modality]
            weighted_resonance += w * resonance
            active_weight += w
            reliability_mass += w * q
        else:
            q = None
            resonance = None
        channels[modality.value] = {
            "a_m": int(available),
            "q_m": q,
            "R_m": resonance,
            "provenance": Source.TEXT_LEXICAL_PROXY.value if available else None,
            "feature_map": FEATURE_MAP_VERSION if available else None,
        }

    denominator = 1.0 + config.lambda_interference * config.interference
    result: dict[str, object] = {
        "channels": channels,
        "R_total": weighted_resonance / active_weight if active_weight > 0 else None,
        "B": reliability_mass / denominator,
        "I": config.interference,
        "I_method": INTERFERENCE_RULE_VERSION,
        "lambda_interference": config.lambda_interference,
        "config_version": config.version,
        "status": STATUS,
        "claims": [],
    }
    if image_meta is not None or audio_meta is not None:
        result["attachment_meta"] = {k: v for k, v in (("image_meta", image_meta), ("audio_meta", audio_meta)) if v is not None}
    if "packet" in record and record["packet"] is not None:
        result["telemetry_state"] = _network_state(record["packet"])
    return result
