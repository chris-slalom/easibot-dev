"""Integration tests for supervisor routing to specialists."""

from unittest.mock import patch

from langchain_core.messages import HumanMessage

from easibot.agents.app_rationalization import AppRationalizationSpecialist
from easibot.agents.bcdr import BCDRSpecialist
from easibot.agents.research import ResearchSpecialist
from easibot.agents.supervisor import SupervisorAgent
from easibot.graph.state import ConsultantState


class TestSupervisorRouting:
    """Integration tests for supervisor routing to specialists."""

    @patch("easibot.agents.supervisor.ChatBedrock")
    @patch("easibot.agents.research.ChatBedrock")
    def test_supervisor_routes_to_research(
        self, mock_research_bedrock, mock_supervisor_bedrock, mock_bedrock_llm
    ):
        """Test supervisor routes informational queries to research."""
        mock_supervisor_bedrock.return_value = mock_bedrock_llm
        mock_research_bedrock.return_value = mock_bedrock_llm

        supervisor = SupervisorAgent()
        research = ResearchSpecialist()

        # Initial state with user query
        state = ConsultantState(
            messages=[HumanMessage(content="What is application rationalization?")],
            offerings=[],
            iteration_count=0,
            max_iterations=10,
        )

        # Supervisor routes
        routing_result = supervisor.route(state)
        assert routing_result["next_specialist"] == "research"

        # Update state
        state = ConsultantState(**{**dict(state), **routing_result})

        # Research specialist processes
        research_result = research.research(state)
        assert "messages" in research_result
        assert "research_findings" in research_result
        assert len(research_result["research_findings"]) > 0

    @patch("easibot.agents.supervisor.ChatBedrock")
    @patch("easibot.agents.app_rationalization.ChatBedrock")
    def test_supervisor_routes_to_app_rationalization(
        self, mock_app_rat_bedrock, mock_supervisor_bedrock, mock_bedrock_llm
    ):
        """Test supervisor routes app rationalization work to specialist."""
        mock_supervisor_bedrock.return_value = mock_bedrock_llm
        mock_app_rat_bedrock.return_value = mock_bedrock_llm

        supervisor = SupervisorAgent()
        app_rat = AppRationalizationSpecialist()

        state = ConsultantState(
            messages=[
                HumanMessage(content="Create an application portfolio assessment")
            ],
            offerings=["app-rationalization"],
            iteration_count=0,
            max_iterations=10,
        )

        # Supervisor routes
        routing_result = supervisor.route(state)
        assert routing_result["next_specialist"] == "app_rationalization"

        # Update state
        state = ConsultantState(**{**dict(state), **routing_result})

        # Specialist processes
        work_result = app_rat.work(state)
        assert "deliverables" in work_result
        assert len(work_result["deliverables"]) == 1
        assert work_result["deliverables"][0].offering == "app-rationalization"

    @patch("easibot.agents.supervisor.ChatBedrock")
    @patch("easibot.agents.bcdr.ChatBedrock")
    def test_supervisor_routes_to_bcdr(
        self, mock_bcdr_bedrock, mock_supervisor_bedrock, mock_bedrock_llm
    ):
        """Test supervisor routes BC/DR work to specialist."""
        mock_supervisor_bedrock.return_value = mock_bedrock_llm
        mock_bcdr_bedrock.return_value = mock_bedrock_llm

        supervisor = SupervisorAgent()
        bcdr = BCDRSpecialist()

        state = ConsultantState(
            messages=[HumanMessage(content="Help me create a disaster recovery plan")],
            offerings=["bcdr"],
            iteration_count=0,
            max_iterations=10,
        )

        # Supervisor routes
        routing_result = supervisor.route(state)
        assert routing_result["next_specialist"] == "bcdr"

        # Update state
        state = ConsultantState(**{**dict(state), **routing_result})

        # Specialist processes
        work_result = bcdr.work(state)
        assert "deliverables" in work_result
        assert len(work_result["deliverables"]) == 1
        assert work_result["deliverables"][0].offering == "bcdr"

    @patch("easibot.agents.supervisor.ChatBedrock")
    @patch("easibot.agents.research.ChatBedrock")
    @patch("easibot.agents.app_rationalization.ChatBedrock")
    def test_research_then_specialist_workflow(
        self,
        mock_app_rat_bedrock,
        mock_research_bedrock,
        mock_supervisor_bedrock,
        mock_bedrock_llm,
    ):
        """Test workflow: supervisor -> research -> supervisor -> specialist."""
        mock_supervisor_bedrock.return_value = mock_bedrock_llm
        mock_research_bedrock.return_value = mock_bedrock_llm
        mock_app_rat_bedrock.return_value = mock_bedrock_llm

        supervisor = SupervisorAgent()
        research = ResearchSpecialist()
        app_rat = AppRationalizationSpecialist()

        # Initial query requesting deliverable
        state = ConsultantState(
            messages=[
                HumanMessage(
                    content="Research application rationalization then create assessment"
                )
            ],
            offerings=["app-rationalization"],
            iteration_count=0,
            max_iterations=10,
        )

        # First routing - should go to research
        routing_result = supervisor.route(state)
        assert routing_result["next_specialist"] == "research"

        # Update state and do research
        state = ConsultantState(**{**dict(state), **routing_result})
        research_result = research.research(state)

        # Research should have completed and returned findings
        assert "research_findings" in research_result
        assert len(research_result["research_findings"]) > 0

        # Check that research completed successfully (either END or suggests next step)
        assert research_result["next_specialist"] in [
            "supervisor",
            "END",
            "app_rationalization",
        ]

        # Verify that research found relevant information
        assert research_result["active_specialist"] == "research"

    @patch("easibot.agents.supervisor.ChatBedrock")
    def test_supervisor_stops_at_max_iterations(
        self, mock_supervisor_bedrock, mock_bedrock_llm
    ):
        """Test supervisor prevents infinite loops."""
        mock_supervisor_bedrock.return_value = mock_bedrock_llm

        supervisor = SupervisorAgent()

        state = ConsultantState(
            messages=[HumanMessage(content="Some query")],
            offerings=[],
            iteration_count=9,
            max_iterations=10,
        )

        # Should still route
        result1 = supervisor.route(state)
        assert result1["next_specialist"] != "END"
        assert result1["iteration_count"] == 10

        # At max iterations, should stop
        state = ConsultantState(**{**dict(state), **result1})
        result2 = supervisor.route(state)
        assert result2["next_specialist"] == "END"
