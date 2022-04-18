"""Tests for the Utterance class."""

from dialoguekit.core.utterance import Utterance
from dialoguekit.core.intent import Intent


def test_utterance_text():
    u = Utterance("Hello world")
    assert u.text == "Hello world"


def test_comparison():
    u1 = Utterance("Test1", intent=Intent("1"))
    u2 = u1
    assert u1 == u2

    u3 = Utterance("Test1", intent=Intent("1"))
    assert u1 == u3

    # Test Text difference
    u1 = Utterance(text="Test1", intent=Intent("1"))
    u2 = Utterance(text="Test2", intent=Intent("1"))
    assert u1 != u2

    # Test Intent difference
    u1 = Utterance(text="Test1", intent=Intent("1"))
    u2 = Utterance(text="Test1", intent=Intent("2"))
    assert u1 != u2
