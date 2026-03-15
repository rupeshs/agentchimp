import json
import os
from re import DOTALL, sub

from loguru import logger

from agent.message import Message
from llm.abstract_llm_adapter import AbstractLLMAdapter
from memory.prompts import COMPRESSION_SYSTEM_PROMPT, EXTRACTION_SYSTEM_PROMPT
from paths import get_workspace_path

PREFERENCES_FILE = get_workspace_path() / "preferences.json"
PREFERENCES_META_FILE = get_workspace_path() / "preferences_meta.json"

COMPRESS_EVERY_N_CONVERSATIONS = 3


class PreferencesMemory:
    def __init__(self, llm_adapter: AbstractLLMAdapter):
        self.llm_adapter = llm_adapter
        self.count = self._load_count()

    def _load_count(self) -> int:
        if PREFERENCES_META_FILE.exists():
            return json.loads(PREFERENCES_META_FILE.read_text()).get(
                "conversations_since_compression", 0
            )
        return 0

    def _save_count(self) -> None:
        PREFERENCES_META_FILE.write_text(
            json.dumps({"conversations_since_compression": self.count}, indent=2)
        )

    def _load_preferences(self) -> dict:
        """Load existing preferences from disk, or return empty structure."""
        if os.path.exists(PREFERENCES_FILE):
            with open(PREFERENCES_FILE) as f:
                return json.load(f)
        return {
            "communication_style": {
                "prefers_brief": None,
                "prefers_technical": None,
                "preferred_format": None,
            },
            "interests": [],
            "tools_and_stack": [],
            "context": [],
            "dislikes": [],
        }

    def _merge_preferences(self, existing: dict, new: dict) -> dict:
        merged = existing.copy()

        # Merge communication_style scalars
        new_style = new.get("communication_style", {})
        for key, value in new_style.items():
            if value is not None:
                merged.setdefault("communication_style", {})[key] = value

        # Merge lists (case-insensitive dedup: normalize to lowercase for comparison,
        # but preserve the first-seen casing in the output)
        for field in ("interests", "tools_and_stack", "context", "dislikes"):
            existing_items = existing.get(field, [])
            new_items = new.get(field, [])
            seen_lower = {}
            for item in existing_items + new_items:
                key = item.strip().lower()
                if key not in seen_lower:
                    seen_lower[key] = item.strip()
            merged[field] = list(seen_lower.values())[:20]

        return merged

    def _save_preferences(self, prefs: dict) -> None:
        with open(PREFERENCES_FILE, "w") as f:
            json.dump(prefs, f, indent=2)

    def compress_preferences(self) -> dict:
        """
        Run a compression pass on preferences.json — deduplicate, resolve
        contradictions, and drop stale entries.

        Safe to call manually anytime. Also called automatically every
        COMPRESS_EVERY_N_CONVERSATIONS conversations via extract_and_update_preferences.
        """
        prefs = self._load_preferences()

        response = self.llm_adapter.generate(
            [
                Message(role="system", content=COMPRESSION_SYSTEM_PROMPT),
                Message(
                    role="user",
                    content=f"Compress these preferences:\n\n{json.dumps(prefs, indent=2)}",
                ),
            ]
        )

        raw = response.content.strip()
        raw = self._extract_json(raw)
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        try:
            compressed = json.loads(raw)
        except json.JSONDecodeError:
            logger.error(f"Compression parse failed, keeping existing: {raw}")
            return prefs

        self._save_preferences(compressed)
        self.count = 0
        self._save_count()
        logger.info("Compression pass complete.")
        return compressed

    def extract_and_update_preferences(
        self,
        messages: list[Message],
    ) -> dict:
        if not messages:
            return {}
        relevant_messages = []
        for msg in messages:
            if msg.role == "user":
                relevant_messages.append(f"{msg.role}: {msg.content}")

        transcript = "\n".join(relevant_messages)

        response = self.llm_adapter.generate(
            [
                Message(role="system", content=EXTRACTION_SYSTEM_PROMPT),
                Message(role="user", content=transcript),
            ]
        )

        raw = response.content.strip()
        raw = self._extract_json(raw)

        # Strip accidental markdown fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        try:
            extracted = json.loads(raw)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response: {raw}")
            return self._load_preferences()

        existing = self._load_preferences()
        merged = self._merge_preferences(existing, extracted)
        self._save_preferences(merged)

        self.count += 1
        self._save_count()
        if self.count >= COMPRESS_EVERY_N_CONVERSATIONS:
            logger.info("Compression threshold reached, compressing...")
            merged = self.compress_preferences()  # also resets self.count to 0

        logger.info(f"Preferences updated: {PREFERENCES_FILE}")
        return merged

    def build_preference_prompt(self) -> str:
        prefs = self._load_preferences()

        style = prefs.get("communication_style", {})
        has_content = any(v is not None for v in style.values()) or any(
            prefs.get(f)
            for f in ("interests", "tools_and_stack", "context", "dislikes")
        )

        if not has_content:
            return ""

        lines = ["\n--- User Preferences ---"]

        if style.get("prefers_brief") is True:
            lines.append("- Keep responses concise and to the point.")
        elif style.get("prefers_brief") is False:
            lines.append("- The user appreciates thorough, detailed responses.")

        if style.get("prefers_technical") is True:
            lines.append(
                "- Use technical language freely; the user is comfortable with it."
            )
        elif style.get("prefers_technical") is False:
            lines.append("- Prefer plain language over technical jargon.")

        if style.get("preferred_format"):
            lines.append(f"- Preferred response format: {style['preferred_format']}.")

        if prefs.get("interests"):
            lines.append(f"- Interests: {', '.join(prefs['interests'])}.")

        if prefs.get("tools_and_stack"):
            lines.append(f"- Tools/stack: {', '.join(prefs['tools_and_stack'])}.")

        if prefs.get("context"):
            for item in prefs["context"]:
                lines.append(f"- {item}")

        if prefs.get("dislikes"):
            lines.append(f"- Avoid: {', '.join(prefs['dislikes'])}.")

        return "\n".join(lines)

    def _extract_json(self, raw: str) -> str:
        # Strip <think>...</think> reasoning blocks
        raw = sub(r"<think>.*?</think>", "", raw, flags=DOTALL)
        raw = raw.strip()
        raw = sub(r"^```(?:json)?\s*", "", raw)
        raw = sub(r"\s*```$", "", raw)
        return raw
