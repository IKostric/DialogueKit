from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.core.annotation import Annotation
from dialoguekit.core.intent import Intent


@dataclass
class DialogueState:
    """A class to represent the state of a dialogue."""

    history: List[AnnotatedUtterance] = field(default_factory=list)
    last_user_intent: Optional[Intent] = None
    slots: Dict[str, List[Annotation]] = field(
        default_factory=lambda: defaultdict(list)
    )
    turn_count: int = 0
