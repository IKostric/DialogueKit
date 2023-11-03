"""The Platform facilitates displaying of the conversation."""
from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, List, Type, cast

from flask import Flask, Request, request
from flask_socketio import Namespace, SocketIO, emit

from dialoguekit.core import AnnotatedUtterance
from dialoguekit.platforms.platform import Platform

if TYPE_CHECKING:
    from dialoguekit.core import Utterance
    from dialoguekit.participant.agent import Agent


logger = logging.getLogger(__name__)


class SocketIORequest(Request):
    """A request that contains a sid attribute."""

    sid: str


@dataclass
class Message:
    text: str
    intent: str = None

    @classmethod
    def from_utterance(self, utterance: Utterance) -> Message:
        """Converts an utterance to a message.

        Args:
            utterance: An instance of Utterance.

        Returns:
            An instance of Message.
        """
        message = Message(utterance.text)
        if isinstance(utterance, AnnotatedUtterance):
            message.intent = str(utterance.intent)
        return message


@dataclass
class Response:
    recipient: str
    message: Message


class FlaskSocketPlatform(Platform):
    def __init__(self, agent_class: Type[Agent]) -> None:
        """Represents a platform that uses Flask-SocketIO.

        Args:
            agent_class: The class of the agent.
        """
        super().__init__(agent_class)
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

    def start(self, host: str = "127.0.0.1", port: str = "5000") -> None:
        """Starts the platform.

        Args:
            host: Hostname.
            port: Port.
        """
        self.socketio.on_namespace(ChatNamespace("/", self))
        self.socketio.run(self.app, host=host, port=port)

    def display_agent_utterance(
        self, user_id: str, utterance: Utterance
    ) -> None:
        """Emits agent utterance to the client.

        Args:
            user_id: User ID.
            utterance: An instance of Utterance.
        """
        message = Message.from_utterance(utterance)
        self.socketio.send(
            asdict(Response(user_id, message)),
            room=user_id,
        )

    def display_user_utterance(
        self, user_id: str, utterance: Utterance
    ) -> None:
        """Overrides the method in Platform to avoid raising an error.

        This method is not used in FlaskSocketPlatform.

        Args:
            user_id: User ID.
            utterance: An instance of Utterance.
        """
        pass

    def provide_recommendations(self, user_id: str, articles: List) -> None:
        """Provides recommendations to the user.

        Args:
            user_id: User ID.
            articles: List of scored articles.
        """
        articles = [asdict(article) for article in articles]
        self.socketio.emit("recommendations", articles, room=user_id)

    def provide_bookmarks(self, user_id: str, articles: List) -> None:
        """Provides bookmarks to the user.

        Args:
            user_id: User ID.
            articles: List of scored articles.
        """
        articles = [asdict(article) for article in articles]
        self.socketio.emit("bookmarks", articles, room=user_id)


class ChatNamespace(Namespace):
    def __init__(self, namespace: str, platform: FlaskSocketPlatform) -> None:
        """Represents a namespace.

        Args:
            namespace: Namespace.
            platform: An instance of FlaskSocketPlatform.
        """
        super().__init__(namespace)
        self._platform = platform

    def on_connect(self) -> None:
        """Connects client to platform."""
        req: SocketIORequest = cast(SocketIORequest, request)
        self._platform.connect(req.sid)
        logger.info(f"Client connected; user_id: {req.sid}")

    def on_disconnect(self) -> None:
        """Disconnects client from server."""
        req: SocketIORequest = cast(SocketIORequest, request)
        self._platform.disconnect(req.sid)
        logger.info(f"Client disconnected; user_id: {req.sid}")

    def on_message(self, data: dict) -> None:
        """Receives message from client and sends response.

        Args:
            data: Data received from client.
        """
        req: SocketIORequest = cast(SocketIORequest, request)
        self._platform.message(req.sid, data["message"])
        logger.info(f"Message received: {data}")

    def on_feedback(self, data: dict) -> None:
        """Receives feedback from client.

        Args:
            data: Data received from client.
        """
        req: SocketIORequest = cast(SocketIORequest, request)
        logger.info(f"Utterance feedback received: {data}")
        self._platform.feedback(req.sid, data["utterance_id"], data["feedback"])

    def on_recommendation_feedback(self, data: dict) -> None:
        """Receives feedback from client.

        Args:
            data: Data received from client.
        """
        req: SocketIORequest = cast(SocketIORequest, request)
        logger.info(f"Item feedback received: {data}")
        agent = self.get_agent(req.sid)
        agent.handle_recommendation_feedback(data["item_id"], data["feedback"])

    def on_get_bookmarks(self, data: dict) -> None:
        """Receives bookmark request from client.

        Args:
            data: Data received from client.
        """
        req: SocketIORequest = cast(SocketIORequest, request)
        agent = self._platform.get_agent(req.sid)
        logger.info(f"Sending bookmarks: {data}")
        emit("bookmarks", agent.get_bookmarks())

    def on_bookmark_article(self, data: dict) -> None:
        """Receives bookmark request from client.

        Args:
            data: Data received from client.
        """
        req: SocketIORequest = cast(SocketIORequest, request)
        logger.info(f"Bookmark request received: {data}")
        agent = self._platform.get_agent(req.sid)
        agent.handle_bookmark_article(data["item_id"])

    def on_remove_bookmark(self, data: dict) -> None:
        """Receives bookmark request from client.

        Args:
            data: Data received from client.
        """
        req: SocketIORequest = cast(SocketIORequest, request)
        logger.info(f"Remove bookmark request received: {data}")
        agent = self._platform.get_agent(req.sid)
        agent.handle_remove_bookmark(data["item_id"])

    def on_get_preferences(self, data: dict) -> None:
        """Receives preferences request from client.

        Args:
            data: Data received from client.
        """
        req: SocketIORequest = cast(SocketIORequest, request)
        agent = self._platform.get_agent(req.sid)
        logger.info(f"Sending preferences: {data}")
        emit("preferences", agent.get_preferences())

    def on_remove_preference(self, data: dict) -> None:
        """Receives remove preference request from client.

        Args:
            data: Data received from client.
        """
        req: SocketIORequest = cast(SocketIORequest, request)
        agent = self._platform.get_agent(req.sid)
        logger.info(f"Removing preference: {data}")
        agent.handle_remove_preference(data["topic"])

    def on_set_style(self, data: dict) -> None:
        """Receives style request from client.

        Args:
            data: Data received from client.
        """
        req: SocketIORequest = cast(SocketIORequest, request)
        agent = self._platform.get_agent(req.sid)
        logger.info(f"Setting style: {data}")
        agent.set_style(data["style"])
