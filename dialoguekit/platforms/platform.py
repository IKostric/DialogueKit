"""The Platform facilitates displaying of the conversation."""
from abc import ABC, abstractmethod
from typing import Dict, Type

from dialoguekit.connector import DialogueConnector
from dialoguekit.core import Utterance
from dialoguekit.participant import Agent, User


class Platform(ABC):
    def __init__(self, agent_class: Type[Agent]) -> None:
        """Represents a platform.

        Args:
            agent_class: The class of the agent.
        """
        if not issubclass(agent_class, Agent):
            raise ValueError("agent_class must be a subclass of Agent")
        self._agent_class = agent_class
        self._active_connections: Dict[str, DialogueConnector] = {}

    @abstractmethod
    def start(self) -> None:
        """Starts the platform.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def display_agent_utterance(
        self, user_id: str, utterance: Utterance
    ) -> None:
        """Displays an agent utterance.

        Args:
            user_id: User ID.
            utterance: An instance of Utterance.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def display_user_utterance(
        self, user_id: str, utterance: Utterance
    ) -> None:
        """Displays a user utterance.

        Args:
            user_id: User ID.
            utterance: An instance of Utterance.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def get_new_agent(self, user_id: str) -> Agent:
        """Returns a new instance of the agent.

        Returns:
            Agent.
        """
        return self._agent_class(self._agent_class.__name__, user_id)

    def get_user(self, user_id: str) -> User:
        """Returns the user.

        Args:
            user_id: User ID.

        Returns:
            User.
        """
        return self._active_connections.get(user_id).user

    def get_agent(self, user_id: str) -> Agent:
        """Returns the agent.

        Args:
            user_id: User ID.

        Returns:
            Agent.
        """
        return self._active_connections.get(user_id).agent

    def get_dialogue_connector(self, user_id: str) -> DialogueConnector:
        """Returns the dialogue connector.

        Args:
            user_id: User ID.

        Returns:
            DialogueConnector.
        """
        return self._active_connections.get(user_id)

    def connect(self, user_id: str) -> None:
        """Connects a user to an agent.

        Args:
            user_id: User ID.
        """
        user = User(user_id)
        self._active_connections[user_id] = DialogueConnector(
            agent=self.get_new_agent(user_id),
            user=user,
            platform=self,
        )
        self._active_connections[user_id].start()

    def disconnect(self, user_id: str) -> None:
        """Disconnects a user from an agent.

        Args:
            user_id: User ID.
        """
        dialogue_connector = self._active_connections.pop(user_id)
        dialogue_connector.close()

    def message(self, user_id: str, text: str) -> None:
        """Gets called every time there is a new user input.

        Args:
            user_id: User ID.
            text: User input.
        """
        self.get_user(user_id).handle_input(text)

    def feedback(self, user_id: str, utterance_id: str, value: int) -> None:
        """Gets called every time there is a new feedback.

        Args:
            user_id: User ID.
            utterance_id: Utterance ID.
            value: Feedback value.
        """
        self.get_dialogue_connector(user_id).handle_feedback(
            utterance_id, value
        )
