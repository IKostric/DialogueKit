"""A module for tracking the state of a dialogue."""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.core.annotation import Annotation
from dialoguekit.core.intent import Intent
from dialoguekit.dialogue_manager.dialogue_state import DialogueState
from dialoguekit.participant.participant import DialogueParticipant


class DialogueStateTracker:

    def __init__(self, **kwargs) -> None:
        """Initializes the dialogue state tracker."""
        super().__init__(**kwargs)
        self._dialogue_state = DialogueState()

    def get_state(self) -> DialogueState:
        """Returns the current state of the dialogue.

        Returns:
            The current state of the dialogue.
        """
        return self._dialogue_state

    def update(self, annotated_utterance: AnnotatedUtterance) -> None:
        """Updates the dialogue state with the annotated utterance.

        Args:
            annotated_utterance: The annotated utterance.
        """
        self._dialogue_state.history.append(annotated_utterance)
        if annotated_utterance.participant is not DialogueParticipant.USER:
            return

        self._dialogue_state.last_user_intent = annotated_utterance.intent

        for annotation in annotated_utterance.annotations:
            self._dialogue_state.slots[annotation.slot].append(annotation)

        self._dialogue_state.turn_count += 1
