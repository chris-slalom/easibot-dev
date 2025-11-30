"""Main LangGraph workflow for EASI Bot consultant system."""

import logging
import os

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from easibot.agents import (
    AppRationalizationSpecialist,
    BCDRSpecialist,
    ResearchSpecialist,
    SupervisorAgent,
)
from easibot.graph.state import ConsultantState

logger = logging.getLogger(__name__)


def create_consultant_graph(*, enable_langfuse: bool | None = None):
    """Create the multi-agent consultant workflow graph.

    Args:
        enable_langfuse: Optional boolean to enable Langfuse tracing.
            If None, reads from ENABLE_LANGFUSE environment variable.

    Returns:
        Compiled LangGraph workflow with optional Langfuse tracing

    """
    # Initialize agents
    supervisor = SupervisorAgent()
    research = ResearchSpecialist()
    app_rat = AppRationalizationSpecialist()
    bcdr = BCDRSpecialist()

    # Create graph
    workflow = StateGraph(ConsultantState)

    # Add nodes
    workflow.add_node("supervisor", supervisor.route)
    workflow.add_node("research", research.research)
    workflow.add_node("app_rationalization", app_rat.work)
    workflow.add_node("bcdr", bcdr.work)

    # Add conditional routing from supervisor
    def route_to_specialist(state: ConsultantState) -> str:
        """Route to next specialist based on supervisor decision."""
        next_specialist = state.get("next_specialist", "END")
        if next_specialist == "supervisor":
            return "supervisor"  # Loop back to supervisor
        return next_specialist if next_specialist else "END"

    # Set entry point
    workflow.set_entry_point("supervisor")

    # Add edges from supervisor to specialists
    workflow.add_conditional_edges(
        "supervisor",
        route_to_specialist,
        {
            "research": "research",
            "app_rationalization": "app_rationalization",
            "bcdr": "bcdr",
            "supervisor": "supervisor",
            "END": END,
        },
    )

    # Add edges from specialists back to supervisor for potential re-routing
    workflow.add_conditional_edges(
        "research",
        route_to_specialist,
        {
            "supervisor": "supervisor",
            "app_rationalization": "app_rationalization",
            "bcdr": "bcdr",
            "END": END,
        },
    )

    workflow.add_edge("app_rationalization", END)
    workflow.add_edge("bcdr", END)

    # Add memory for conversation persistence
    memory = MemorySaver()

    # Compile the graph
    graph = workflow.compile(checkpointer=memory)

    # Optionally add Langfuse tracing
    if enable_langfuse is None:
        enable_langfuse = os.getenv("ENABLE_LANGFUSE", "false").lower() == "true"

    if enable_langfuse:
        try:
            from langfuse.langchain import CallbackHandler

            langfuse_handler = CallbackHandler()
            graph = graph.with_config({"callbacks": [langfuse_handler]})
        except ImportError:
            logger.warning("Langfuse not installed. Tracing disabled.")
        except Exception as e:
            logger.warning("Failed to initialize Langfuse: %s", e)

    return graph


# Create the graph instance
graph = create_consultant_graph()
