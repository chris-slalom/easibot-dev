"""Tests for the Supervisor agent."""

from unittest.mock import patch

from langchain_core.messages import HumanMessage

from easibot.agents.supervisor import SupervisorAgent
from easibot.graph.state import ConsultantState


class TestSupervisorAgent:
    """Test cases for SupervisorAgent."""

    @patch("easibot.agents.supervisor.ChatBedrock")
    def test_supervisor_creation(self, mock_bedrock):
        """Test that supervisor can be instantiated."""
        agent = SupervisorAgent()
        assert agent is not None
        assert agent.llm is not None
        assert agent.system_prompt is not None
        mock_bedrock.assert_called_once()

    @patch("easibot.agents.supervisor.ChatBedrock")
    def test_route_to_research(self, mock_bedrock, mock_bedrock_llm):
        """Test routing to research specialist."""
        mock_bedrock.return_value = mock_bedrock_llm
        agent = SupervisorAgent()

        state = ConsultantState(
            messages=[HumanMessage(content="What is application rationalization?")],
            offerings=[],
            iteration_count=0,
            max_iterations=10,
        )

        result = agent.route(state)

        assert "next_specialist" in result
        assert result["next_specialist"] == "research"
        assert result["iteration_count"] == 1

    @patch("easibot.agents.supervisor.ChatBedrock")
    def test_route_to_app_rationalization(self, mock_bedrock, mock_bedrock_llm):
        """Test routing to app rationalization specialist."""
        mock_bedrock.return_value = mock_bedrock_llm
        agent = SupervisorAgent()

        state = ConsultantState(
            messages=[
                HumanMessage(content="Help with application portfolio rationalization")
            ],
            offerings=["app-rationalization"],
            iteration_count=0,
            max_iterations=10,
        )

        result = agent.route(state)

        assert "next_specialist" in result
        assert result["next_specialist"] == "app_rationalization"
        assert result["iteration_count"] == 1

    @patch("easibot.agents.supervisor.ChatBedrock")
    def test_route_to_bcdr(self, mock_bedrock, mock_bedrock_llm):
        """Test routing to BC/DR specialist."""
        mock_bedrock.return_value = mock_bedrock_llm
        agent = SupervisorAgent()

        state = ConsultantState(
            messages=[HumanMessage(content="I need a disaster recovery plan")],
            offerings=["bcdr"],
            iteration_count=0,
            max_iterations=10,
        )

        result = agent.route(state)

        assert "next_specialist" in result
        assert result["next_specialist"] == "bcdr"
        assert result["iteration_count"] == 1

    @patch("easibot.agents.supervisor.ChatBedrock")
    def test_max_iterations_reached(self, mock_bedrock, mock_bedrock_llm):
        """Test that supervisor stops routing at max iterations."""
        mock_bedrock.return_value = mock_bedrock_llm
        agent = SupervisorAgent()

        state = ConsultantState(
            messages=[HumanMessage(content="What is cloud migration?")],
            offerings=[],
            iteration_count=10,
            max_iterations=10,
        )

        result = agent.route(state)

        assert result["next_specialist"] == "END"
        assert "messages" in result

    @patch("easibot.agents.supervisor.ChatBedrock")
    def test_no_user_message(self, mock_bedrock, mock_bedrock_llm):
        """Test handling when no user message is present."""
        mock_bedrock.return_value = mock_bedrock_llm
        agent = SupervisorAgent()

        state = ConsultantState(
            messages=[], offerings=[], iteration_count=0, max_iterations=10
        )

        result = agent.route(state)

        assert result["next_specialist"] == "END"
