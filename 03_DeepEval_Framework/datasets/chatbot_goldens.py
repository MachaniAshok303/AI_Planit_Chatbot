"""Golden cases for the chatbot (Subsystem A).

Each golden carries:
- input         : user prompt
- expected_output : reference / canonical answer (for G-Eval & faithfulness)
- context       : ground-truth context (for hallucination metric)
- categories    : tags so we can filter
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ChatbotGolden:
    input: str
    expected_output: str
    context: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)


JSON_FILE_PATH = Path(__file__).parent / "chatbot_goldens.json"


def load_goldens_from_json(path: Path | str = JSON_FILE_PATH) -> tuple[list[ChatbotGolden], list[str]]:
    """Load golden test cases and safety prompts from a JSON dataset file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    goldens = [
        ChatbotGolden(
            input=item["input"],
            expected_output=item["expected_output"],
            context=item.get("context", []),
            categories=item.get("categories", []),
        )
        for item in data.get("chatbot_goldens", [])
    ]
    safety_prompts = data.get("safety_prompts", [])
    return goldens, safety_prompts


CHATBOT_GOLDENS, SAFETY_PROMPTS = load_goldens_from_json()