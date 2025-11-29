"""End-to-end tests for the complete LangGraph workflow."""

from unittest.mock import Mock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from easibot.agent import create_consultant_graph


@pytest.fixture
def mock_all_bedrock():
    """Mock all Bedrock LLM instances used in agents."""
    with (
        patch("easibot.agents.supervisor.ChatBedrock") as mock_supervisor,
        patch("easibot.agents.research.ChatBedrock") as mock_research,
        patch("easibot.agents.app_rationalization.ChatBedrock") as mock_app_rat,
        patch("easibot.agents.bcdr.ChatBedrock") as mock_bcdr,
    ):
        # Create mock LLM responses
        mock_llm = Mock()
        mock_response = AIMessage(content="Test response from agent")
        mock_llm.invoke = Mock(return_value=mock_response)

        # Apply to all mocks
        mock_supervisor.return_value = mock_llm
        mock_research.return_value = mock_llm
        mock_app_rat.return_value = mock_llm
        mock_bcdr.return_value = mock_llm

        yield {
            "supervisor": mock_supervisor,
            "research": mock_research,
            "app_rat": mock_app_rat,
            "bcdr": mock_bcdr,
        }


class TestGraphEndToEnd:
    """End-to-end tests for the complete graph."""

    def test_graph_creation(self, mock_all_bedrock):
        """Test that the graph can be created."""
        graph = create_consultant_graph()
        assert graph is not None
        assert "supervisor" in graph.nodes
        assert "research" in graph.nodes
        assert "app_rationalization" in graph.nodes
        assert "bcdr" in graph.nodes

    def test_graph_invoke_research_query(self, mock_all_bedrock):
        """Test graph invocation with informational query."""
        graph = create_consultant_graph()

        input_state = {
            "messages": [HumanMessage(content="What is application rationalization?")],
            "offerings": ["app-rationalization"],
        }

        config = {"configurable": {"thread_id": "test-thread-1"}}
        result = graph.invoke(input_state, config)

        # Verify we got a result
        assert result is not None
        assert "messages" in result
        assert len(result["messages"]) > 1  # Original + responses

        # Check that messages include responses
        ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
        assert len(ai_messages) > 0

    def test_graph_invoke_app_rationalization(self, mock_all_bedrock):
        """Test graph invocation for app rationalization work."""
        graph = create_consultant_graph()

        input_state = {
            "messages": [
                HumanMessage(content="Create an application portfolio assessment")
            ],
            "offerings": ["app-rationalization"],
        }

        config = {"configurable": {"thread_id": "test-thread-2"}}
        result = graph.invoke(input_state, config)

        assert result is not None
        assert "messages" in result
        assert "deliverables" in result

        # Should have created at least one deliverable
        assert len(result["deliverables"]) >= 1

        # Verify deliverable is for the right offering
        app_rat_deliverables = [
            d for d in result["deliverables"] if d.offering == "app-rationalization"
        ]
        assert len(app_rat_deliverables) > 0

    def test_graph_invoke_bcdr(self, mock_all_bedrock):
        """Test graph invocation for BC/DR work."""
        graph = create_consultant_graph()

        input_state = {
            "messages": [HumanMessage(content="I need a disaster recovery plan")],
            "offerings": ["bcdr"],
        }

        config = {"configurable": {"thread_id": "test-thread-3"}}
        result = graph.invoke(input_state, config)

        assert result is not None
        assert "deliverables" in result

        # Should have BC/DR deliverable
        bcdr_deliverables = [d for d in result["deliverables"] if d.offering == "bcdr"]
        assert len(bcdr_deliverables) > 0

    def test_graph_state_preservation(self, mock_all_bedrock):
        """Test that state is properly preserved through the graph."""
        graph = create_consultant_graph()

        input_state = {
            "messages": [HumanMessage(content="What is BCDR?")],
            "offerings": ["bcdr"],
            "client_industry": "Healthcare",
        }

        config = {"configurable": {"thread_id": "test-thread-4"}}
        result = graph.invoke(input_state, config)

        # Client industry should be preserved
        assert result.get("client_industry") == "Healthcare"

        # Original message should still be in messages
        assert any(
            msg.content == "What is BCDR?"
            for msg in result["messages"]
            if isinstance(msg, HumanMessage)
        )

    def test_graph_iteration_control(self, mock_all_bedrock):
        """Test that graph respects iteration limits."""
        graph = create_consultant_graph()

        input_state = {
            "messages": [HumanMessage(content="Complex multi-step query")],
            "offerings": [],
            "max_iterations": 3,
        }

        config = {"configurable": {"thread_id": "test-thread-5"}}
        result = graph.invoke(input_state, config)

        # Should not exceed max iterations
        assert result.get("iteration_count", 0) <= 3

    def test_graph_with_multiple_offerings(self, mock_all_bedrock):
        """Test graph handling multiple offerings."""
        graph = create_consultant_graph()

        input_state = {
            "messages": [
                HumanMessage(
                    content="I need both application rationalization and disaster recovery"
                )
            ],
            "offerings": ["app-rationalization", "bcdr"],
        }

        config = {"configurable": {"thread_id": "test-thread-6"}}
        result = graph.invoke(input_state, config)

        assert result is not None
        assert "messages" in result

        # Should have processed the request
        ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
        assert len(ai_messages) > 0

    def test_graph_empty_message_handling(self, mock_all_bedrock):
        """Test graph handles edge cases gracefully."""
        graph = create_consultant_graph()

        input_state = {"messages": [], "offerings": []}

        config = {"configurable": {"thread_id": "test-thread-7"}}
        result = graph.invoke(input_state, config)

        # Should complete without error
        assert result is not None

    def test_graph_produces_consultant_state(self, mock_all_bedrock):
        """Test that graph output conforms to ConsultantState schema."""
        graph = create_consultant_graph()

        input_state = {
            "messages": [HumanMessage(content="Test query")],
            "offerings": ["app-rationalization"],
        }

        config = {"configurable": {"thread_id": "test-thread-8"}}
        result = graph.invoke(input_state, config)

        # Verify result has ConsultantState fields
        assert "messages" in result
        assert "offerings" in result
        assert "iteration_count" in result
        assert "research_findings" in result
        assert "deliverables" in result

        # Verify types
        assert isinstance(result["messages"], list)
        assert isinstance(result["offerings"], list)
        assert isinstance(result["iteration_count"], int)
        assert isinstance(result["research_findings"], list)
        assert isinstance(result["deliverables"], list)

        # Verify state has expected content
        assert len(result["messages"]) > 0
        assert result["iteration_count"] > 0
