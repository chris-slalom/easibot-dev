"""State definitions for the EASI Bot consultant workflow."""

from operator import add
from typing import Annotated, Literal

from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class ResearchFinding(BaseModel):
    """A research finding from the knowledge base."""

    source: str = Field(description="Source document or offering")
    content: str = Field(description="Relevant content found")
    relevance_score: float = Field(description="Relevance to query", ge=0.0, le=1.0)
    metadata: dict[str, str] = Field(default_factory=dict)


class Deliverable(BaseModel):
    """A deliverable artifact created by a specialist."""

    title: str = Field(description="Deliverable title")
    type: str = Field(description="Type of deliverable (e.g., roadmap, assessment)")
    content: str = Field(description="Deliverable content")
    offering: str = Field(description="Associated offering")
    specialist: str = Field(description="Specialist who created it")


class ConsultantState(MessagesState):
    """State for the EASI Bot multi-agent consultant workflow.

    Extends MessagesState to include conversation history plus custom fields
    for engagement context, routing, research, and deliverables.
    """

    # Engagement context
    offerings: list[str] = Field(
        default_factory=list,
        description="Relevant offerings (e.g., 'app-rationalization', 'bcdr')",
    )
    client_industry: str | None = Field(
        default=None, description="Client industry context"
    )

    # Routing and orchestration
    next_specialist: str | None = Field(
        default=None, description="Next specialist to route to"
    )
    active_specialist: str | None = Field(
        default=None, description="Currently active specialist"
    )

    # Research and knowledge
    research_findings: Annotated[list[ResearchFinding], add] = Field(
        default_factory=list, description="Accumulated research findings"
    )

    # Deliverables and artifacts
    deliverables: Annotated[list[Deliverable], add] = Field(
        default_factory=list, description="Created deliverables"
    )

    # Workflow control
    iteration_count: int = Field(
        default=0, description="Number of specialist iterations"
    )
    max_iterations: int = Field(default=10, description="Maximum iterations allowed")


# Specialist types
SpecialistType = Literal[
    "supervisor",
    "research",
    "app_rationalization",
    "bcdr",
    "tech_strategy",
    "cloud_modernization",
]
