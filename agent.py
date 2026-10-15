# Copyright © 2026 Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella
# Aura — Elite Upgrade (Perception)
# Source of truth: chichi-lyman/saphira-ai monorepo

from __future__ import annotations
from typing import Any, Dict, List
import asyncio
import logging
import uuid

logger = logging.getLogger("Aura")

SYSTEM_VOICE = "You are Aura — perception layer. Extract entities, scene context, and sensory signals cleanly."
CAPABILITIES = ["perception.entity", "perception.scene", "vision.context"]
NAME = "aura"


class Aura:
    name = NAME
    capabilities = CAPABILITIES
    default_policy = "ALLOW"
    SYSTEM_VOICE = SYSTEM_VOICE
    max_timeout_s = 45.0
    max_retries = 2

    def __init__(self, memory_store=None):
        self.memory = memory_store

    async def safe_run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        isolation_token = payload.get("isolation_token") or str(uuid.uuid4())
        last_error = None
        for attempt in range(1, self.max_retries + 2):
            try:
                result = await asyncio.wait_for(
                    self.process({**payload, "isolation_token": isolation_token}),
                    timeout=self.max_timeout_s,
                )
                result.setdefault("agent", self.name)
                result.setdefault("status", "success")
                result.setdefault("isolation_token", isolation_token)
                return result
            except asyncio.TimeoutError:
                last_error = "timeout"
            except Exception as e:
                last_error = str(e)
        return {
            "agent": self.name,
            "status": "recovered_from_failure",
            "error": last_error,
            "isolation_token": isolation_token,
        }

    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        entities = self._extract_entities(payload)
        return {
            "status": "success",
            "suggested_entities": entities,
            "perception": {
                "entities": entities,
                "scene_hints": payload.get("memory_context", [])[:3],
                "biometrics": payload.get("biometrics"),
            },
            "message": "Perception complete.",
            "voice_lock": True,
        }

    def _extract_entities(self, payload: Dict[str, Any]) -> List[str]:
        text = (payload.get("text") or "").lower()
        candidates = []
        for word in ("light", "lamp", "thermostat", "door", "lock", "camera", "speaker"):
            if word in text:
                candidates.append(word)
        return candidates[:5]
