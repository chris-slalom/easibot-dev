"""Tests for the Application Rationalization specialist."""

from unittest.mock import patch

from langchain_core.messages import AIMessage, HumanMessage

from easibot.agents.app_rationalization import AppRationalizationSpecialist
from easibot.graph.state import ConsultantState, Deliverable, ResearchFinding


class TestAppRationalizationSpecialist:
    """Test cases for AppRationalizationSpecialist."""

    @patch("easibot.agents.app_rationalization.ChatBedrock")
    def test_specialist_creation(self, mock_bedrock):
        """Test that app rationalization specialist can be instantiated."""
        agent = AppRationalizationSpecialist()
        assert agent is not None
        assert agent.llm is not None
        assert agent.system_prompt is not None
        mock_bedrock.assert_called_once()

    @patch("easibot.agents.app_rationalization.ChatBedrock")
    def test_work_creates_deliverable(self, mock_bedrock, mock_bedrock_llm):
        """Test that specialist creates deliverables."""
        mock_bedrock.return_value = mock_bedrock_llm
        agent = AppRationalizationSpecialist()

        state = ConsultantState(
            messages=[HumanMessage(content="Create an application inventory")],
            offerings=["app-rationalization"],
            iteration_count=1,
            max_iterations=10,
        )

        result = agent.work(state)

        assert "messages" in result
        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)
        assert result["messages"][0].name == "app_rationalization_specialist"

        assert "deliverables" in result
        assert len(result["deliverables"]) == 1
        assert isinstance(result["deliverables"][0], Deliverable)
        assert result["deliverables"][0].offering == "app-rationalization"
        assert result["deliverables"][0].specialist == "app_rationalization"

        assert result["active_specialist"] == "app_rationalization"
        assert result["next_specialist"] == "END"

    @patch("easibot.agents.app_rationalization.ChatBedrock")
    def test_work_with_research_findings(self, mock_bedrock, mock_bedrock_llm):
        """Test specialist uses research findings in response."""
        mock_bedrock.return_value = mock_bedrock_llm
        agent = AppRationalizationSpecialist()

        state = ConsultantState(
            messages=[HumanMessage(content="Create rationalization matrix")],
            offerings=["app-rationalization"],
            research_findings=[
                ResearchFinding(
                    source="Best Practices Guide",
                    content="Use 5R framework for rationalization.",
                    relevance_score=0.95,
                    metadata={"offering": "app-rationalization"},
                ),
                ResearchFinding(
                    source="TCO Analysis Template",
                    content="Calculate current vs future state costs.",
                    relevance_score=0.88,
                    metadata={"offering": "app-rationalization"},
                ),
            ],
            iteration_count=2,
            max_iterations=10,
        )

        result = agent.work(state)

        # Verify LLM was invoked (mock should be called)
        assert mock_bedrock_llm.invoke.called

        # Check that result contains expected fields
        assert "deliverables" in result
        assert len(result["deliverables"]) == 1
        assert result["deliverables"][0].type == "assessment"

    @patch("easibot.agents.app_rationalization.ChatBedrock")
    def test_work_without_user_message(self, mock_bedrock, mock_bedrock_llm):
        """Test specialist can work with continuation (no new user message)."""
        mock_bedrock.return_value = mock_bedrock_llm
        agent = AppRationalizationSpecialist()

        state = ConsultantState(
            messages=[],
            offerings=["app-rationalization"],
            iteration_count=1,
            max_iterations=10,
        )

        result = agent.work(state)

        # Should still produce deliverable even without user message
        assert "deliverables" in result
        assert len(result["deliverables"]) == 1
