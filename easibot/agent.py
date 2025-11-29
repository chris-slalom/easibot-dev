"""Main LangGraph workflow for EASI Bot consultant system."""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from easibot.agents import (
    AppRationalizationSpecialist,
    BCDRSpecialist,
    ResearchSpecialist,
    SupervisorAgent,
)
from easibot.graph.state import ConsultantState


def create_consultant_graph():
    """Create the multi-agent consultant workflow graph.

    Returns:
        Compiled LangGraph workflow

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

    return graph


# Create the graph instance
graph = create_consultant_graph()
