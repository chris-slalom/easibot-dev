"""Tests for the Research specialist."""

from unittest.mock import patch

from langchain_core.messages import AIMessage, HumanMessage

from easibot.agents.research import ResearchSpecialist
from easibot.graph.state import ConsultantState


class TestResearchSpecialist:
    """Test cases for ResearchSpecialist."""

    @patch("easibot.agents.research.ChatBedrock")
    def test_research_specialist_creation(self, mock_bedrock):
        """Test that research specialist can be instantiated."""
        agent = ResearchSpecialist()
        assert agent is not None
        assert agent.llm is not None
        assert agent.system_prompt is not None
        mock_bedrock.assert_called_once()

    @patch("easibot.agents.research.ChatBedrock")
    def test_research_returns_findings(self, mock_bedrock, mock_bedrock_llm):
        """Test that research specialist returns findings."""
        mock_bedrock.return_value = mock_bedrock_llm
        agent = ResearchSpecialist()

        state = ConsultantState(
            messages=[HumanMessage(content="What is application rationalization?")],
            offerings=["app-rationalization"],
            iteration_count=0,
            max_iterations=10,
        )

        result = agent.research(state)

        assert "messages" in result
        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)
        assert result["messages"][0].name == "research_specialist"

        assert "research_findings" in result
        assert len(result["research_findings"]) > 0

        assert "next_specialist" in result
        assert "active_specialist" in result
        assert result["active_specialist"] == "research"

    @patch("easibot.agents.research.ChatBedrock")
    def test_research_with_offerings_filter(self, mock_bedrock, mock_bedrock_llm):
        """Test research with offering-specific filtering."""
        mock_bedrock.return_value = mock_bedrock_llm
        agent = ResearchSpecialist()

        state = ConsultantState(
            messages=[HumanMessage(content="Find BC/DR best practices")],
            offerings=["bcdr"],
            iteration_count=0,
            max_iterations=10,
        )

        result = agent.research(state)

        assert "research_findings" in result
        assert len(result["research_findings"]) > 0

    @patch("easibot.agents.research.ChatBedrock")
    def test_research_suggests_specialist(self, mock_bedrock, mock_bedrock_llm):
        """Test that research suggests routing to specialist for deliverables."""
        mock_bedrock.return_value = mock_bedrock_llm
        agent = ResearchSpecialist()

        state = ConsultantState(
            messages=[HumanMessage(content="Create a disaster recovery plan")],
            offerings=["bcdr"],
            iteration_count=0,
            max_iterations=10,
        )

        result = agent.research(state)

        # Should suggest supervisor for routing when deliverables are requested
        assert result["next_specialist"] == "supervisor"

    @patch("easibot.agents.research.ChatBedrock")
    def test_research_ends_for_simple_query(self, mock_bedrock, mock_bedrock_llm):
        """Test that research ends for simple informational queries."""
        mock_bedrock.return_value = mock_bedrock_llm
        agent = ResearchSpecialist()

        state = ConsultantState(
            messages=[HumanMessage(content="What is BCDR?")],
            offerings=["bcdr"],
            iteration_count=0,
            max_iterations=10,
        )

        result = agent.research(state)

        # Simple query should end after research
        assert result["next_specialist"] == "END"

    @patch("easibot.agents.research.ChatBedrock")
    def test_research_with_no_message(self, mock_bedrock, mock_bedrock_llm):
        """Test research behavior with no user message."""
        mock_bedrock.return_value = mock_bedrock_llm
        agent = ResearchSpecialist()

        state = ConsultantState(
            messages=[], offerings=[], iteration_count=0, max_iterations=10
        )

        result = agent.research(state)

        assert result == {}
