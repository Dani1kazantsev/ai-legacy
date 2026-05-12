"""BM25-based retrieval over owner's chat messages.

Index structure: each "document" is a single owner message + the immediate
context (the preceding message from the other party if there was one).
At query time, we tokenize the query and retrieve top-K matches.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path

from rank_bm25 import BM25Okapi


_TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)


def _tokenize(text: str) -> list[str]:
    """Lowercase tokenizer that keeps Cyrillic words intact."""
    return [t.lower() for t in _TOKEN_PATTERN.findall(text)]


@dataclass(frozen=True)
class Example:
    chat: str
    in_text: str   # what the other person said (context)
    out_text: str  # what the owner replied

    def to_dict(self) -> dict:
        return {"chat": self.chat, "in": self.in_text, "out": self.out_text}


class MessageIndex:
    """BM25 index over owner messages with context."""

    def __init__(self, examples: list[Example]):
        self._examples = examples
        # Index on `in_text + out_text` so we match both incoming context and owner reply
        corpus = [_tokenize(f"{e.in_text} {e.out_text}") for e in examples]
        self._bm25 = BM25Okapi(corpus) if corpus else None

    def retrieve(self, query: str, top_k: int = 5) -> list[Example]:
        """Return top_k most relevant examples for the query."""
        if self._bm25 is None or not query.strip():
            return []
        tokens = _tokenize(query)
        if not tokens:
            return []
        scores = self._bm25.get_scores(tokens)
        # Argpartition for top-k
        ranked_indices = sorted(range(len(scores)), key=lambda i: -scores[i])[:top_k]
        return [self._examples[i] for i in ranked_indices if scores[i] > 0]

    def __len__(self) -> int:
        return len(self._examples)


def build_index_from_messages(messages_dir: Path) -> MessageIndex:
    """Build a MessageIndex from all parsed chat JSONs in messages_dir.

    Skips chats with no usable owner-with-context pairs.
    """
    examples: list[Example] = []

    for chat_file in messages_dir.glob("*.json"):
        with chat_file.open(encoding="utf-8") as f:
            data = json.load(f)

        chat_name = data.get("chat_name", chat_file.stem)
        messages = data.get("messages", [])

        for i in range(1, len(messages)):
            prev = messages[i - 1]
            curr = messages[i]
            if not prev.get("is_owner") and curr.get("is_owner"):
                in_text = (prev.get("text") or "").strip()
                out_text = (curr.get("text") or "").strip()
                if in_text and out_text:
                    examples.append(Example(
                        chat=chat_name,
                        in_text=in_text,
                        out_text=out_text,
                    ))

    return MessageIndex(examples)
