"""Tests for the BC/DR specialist."""

from unittest.mock import patch

from langchain_core.messages import AIMessage, HumanMessage

from easibot.agents.bcdr import BCDRSpecialist
from easibot.graph.state import ConsultantState, Deliverable, ResearchFinding


class TestBCDRSpecialist:
    """Test cases for BCDRSpecialist."""

    @patch("easibot.agents.bcdr.ChatBedrock")
    def test_specialist_creation(self, mock_bedrock):
        """Test that BC/DR specialist can be instantiated."""
        agent = BCDRSpecialist()
        assert agent is not None
        assert agent.llm is not None
        assert agent.system_prompt is not None
        mock_bedrock.assert_called_once()

    @patch("easibot.agents.bcdr.ChatBedrock")
    def test_work_creates_deliverable(self, mock_bedrock, mock_bedrock_llm):
        """Test that specialist creates BC/DR deliverables."""
        mock_bedrock.return_value = mock_bedrock_llm
        agent = BCDRSpecialist()

        state = ConsultantState(
            messages=[HumanMessage(content="Create a disaster recovery plan")],
            offerings=["bcdr"],
            iteration_count=1,
            max_iterations=10,
        )

        result = agent.work(state)

        assert "messages" in result
        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)
        assert result["messages"][0].name == "bcdr_specialist"

        assert "deliverables" in result
        assert len(result["deliverables"]) == 1
        assert isinstance(result["deliverables"][0], Deliverable)
        assert result["deliverables"][0].offering == "bcdr"
        assert result["deliverables"][0].specialist == "bcdr"

        assert result["active_specialist"] == "bcdr"
        assert result["next_specialist"] == "END"

    @patch("easibot.agents.bcdr.ChatBedrock")
    def test_work_with_research_findings(self, mock_bedrock, mock_bedrock_llm):
        """Test specialist uses research findings for BC/DR planning."""
        mock_bedrock.return_value = mock_bedrock_llm
        agent = BCDRSpecialist()

        state = ConsultantState(
            messages=[HumanMessage(content="Develop RTO/RPO analysis")],
            offerings=["bcdr"],
            research_findings=[
                ResearchFinding(
                    source="BC/DR Framework",
                    content="RTO should align with business criticality.",
                    relevance_score=0.92,
                    metadata={"offering": "bcdr"},
                ),
                ResearchFinding(
                    source="Industry Standards",
                    content="RPO determines acceptable data loss window.",
                    relevance_score=0.89,
                    metadata={"offering": "bcdr"},
                ),
            ],
            iteration_count=2,
            max_iterations=10,
        )

        result = agent.work(state)

        # Verify LLM was invoked
        assert mock_bedrock_llm.invoke.called

        # Check deliverable
        assert "deliverables" in result
        assert len(result["deliverables"]) == 1
        assert result["deliverables"][0].type == "bc_dr_plan"

    @patch("easibot.agents.bcdr.ChatBedrock")
    def test_work_creates_bcdr_specific_deliverable(
        self, mock_bedrock, mock_bedrock_llm
    ):
        """Test that BC/DR deliverables have correct metadata."""
        mock_bedrock.return_value = mock_bedrock_llm
        agent = BCDRSpecialist()

        state = ConsultantState(
            messages=[HumanMessage(content="Create incident response runbook")],
            offerings=["bcdr"],
            iteration_count=1,
            max_iterations=10,
        )

        result = agent.work(state)

        deliverable = result["deliverables"][0]
        assert deliverable.title == "Business Continuity and Disaster Recovery Plan"
        assert deliverable.offering == "bcdr"
        assert deliverable.specialist == "bcdr"
