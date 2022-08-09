"""Tests the dialogue evaluation."""

import pytest
from dialoguekit.nlu.models.satisfaction_classifier import (
    SatisfactionClassifierSVM,
)
from dialoguekit.participant.participant import DialogueParticipant
from dialoguekit.utils.dialogue_evaluation import Evaluator
from dialoguekit.utils.dialogue_reader import json_to_dialogues


@pytest.fixture
def dialogues():
    export_dialogues = json_to_dialogues(
        filepath="tests/data/annotated_dialogues.json",
        agent_id=DialogueParticipant.AGENT,
        user_id=DialogueParticipant.USER,
    )
    return export_dialogues


@pytest.fixture
def reward_config():
    _REWARD_CONFIG = {
        "full_set_points": 20,
        "intents": {
            "DISCLOSE": 4,
            "REVEAL.REFINE": 4,
            "INQUIRE": 4,
            "NAVIGATE": 4,
        },
        "repeat_penalty": 1,
        "cost": 1,
    }
    return _REWARD_CONFIG


@pytest.fixture
def satisfaction_classifier():
    return SatisfactionClassifierSVM()


def test_init(dialogues, reward_config):
    Evaluator(dialogues=dialogues, reward_config=reward_config)


def test_avg_turns(dialogues, reward_config):
    ev = Evaluator(dialogues=dialogues, reward_config=reward_config)
    avg_turns = ev.avg_turns()
    assert avg_turns == pytest.approx(16.33, 0.1)
    avg_turns2 = ev.avg_turns()
    assert avg_turns2 == pytest.approx(16.33, 0.1)


def test_user_act_ratio(dialogues, reward_config):
    ev = Evaluator(dialogues=dialogues, reward_config=reward_config)
    stats = ev.user_act_ratio()

    assert stats
    assert "AGENT/USER" in list(stats.keys())
    assert stats.get("USER") == 50
    assert stats.get("USER/AGENT") == pytest.approx(0.84, 0.1)


def test_reward(dialogues, reward_config):
    ev = Evaluator(dialogues=dialogues, reward_config=reward_config)
    rewards = ev.reward()
    assert len(rewards["dialogues"]) == len(dialogues)
    for reward in rewards["dialogues"]:
        assert reward["reward"] >= 0


def test_satisfaction_classification(
    dialogues, reward_config, satisfaction_classifier
):
    ev = Evaluator(dialogues=dialogues, reward_config=reward_config)
    satisfactions = ev.satisfaction(satisfaction_classifier)
    print(satisfactions)
    assert satisfactions
    for sc in satisfactions:
        assert 1 <= sc <= 5