"""Pytest configuration and shared fixtures for EASI Bot tests."""

from unittest.mock import Mock

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from easibot.graph.state import ConsultantState, ResearchFinding


@pytest.fixture
def mock_bedrock_llm():
    """Mock ChatBedrock LLM for testing without AWS credentials."""
    mock_llm = Mock()
    mock_response = AIMessage(
        content="This is a test response from the LLM.", name="test_agent"
    )
    mock_llm.invoke = Mock(return_value=mock_response)
    return mock_llm


@pytest.fixture
def sample_state():
    """Create a sample ConsultantState for testing."""
    return ConsultantState(
        messages=[HumanMessage(content="What is application rationalization?")],
        offerings=["app-rationalization"],
        iteration_count=0,
        max_iterations=10,
    )


@pytest.fixture
def sample_state_with_research():
    """Create a ConsultantState with research findings."""
    return ConsultantState(
        messages=[
            HumanMessage(content="Create an application rationalization assessment")
        ],
        offerings=["app-rationalization"],
        research_findings=[
            ResearchFinding(
                source="App Rationalization Guide",
                content="Application rationalization involves portfolio analysis.",
                relevance_score=0.9,
                metadata={"offering": "app-rationalization"},
            )
        ],
        iteration_count=1,
        max_iterations=10,
    )


@pytest.fixture
def sample_bcdr_state():
    """Create a ConsultantState for BC/DR testing."""
    return ConsultantState(
        messages=[HumanMessage(content="Help me develop a disaster recovery plan")],
        offerings=["bcdr"],
        iteration_count=0,
        max_iterations=10,
    )
