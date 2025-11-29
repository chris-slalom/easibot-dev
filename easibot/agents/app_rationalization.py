"""Application Rationalization specialist."""

from langchain_aws import ChatBedrock
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from easibot.config import settings
from easibot.graph.state import ConsultantState, Deliverable


class AppRationalizationSpecialist:
    """Specialist for application portfolio rationalization.

    Deliverables:
    - Application inventory and assessment
    - Rationalization matrix (Retain/Retire/Replace/Rehost/Refactor)
    - TCO analysis
    - Migration roadmap
    - Business capability mapping
    """

    def __init__(self):
        """Initialize the application rationalization specialist."""
        self.llm = ChatBedrock(
            model_id=settings.bedrock_model_id,
            region_name=settings.bedrock_region,
        )

        self.system_prompt = """You are an Application Rationalization Specialist.

Your expertise includes:
- Application portfolio assessment and analysis
- Cost-benefit analysis and TCO calculations
- 5R rationalization framework (Retain/Retire/Replace/Rehost/Refactor)
- Business capability mapping
- Technical debt assessment
- Migration roadmap development

Standard deliverables you create:
1. Application Inventory: Complete catalog with tech stack, dependencies
2. Rationalization Matrix: 5R recommendations for each application
3. TCO Analysis: Current vs. future state costs
4. Migration Roadmap: Sequenced implementation plan with timelines
5. Risk Assessment: Dependencies, business impact, technical risks

When working on engagements:
- Start with understanding current state
- Use research findings from the knowledge base
- Apply rationalization framework systematically
- Provide clear, actionable recommendations
- Create structured deliverables

Offering-specific RAG filter: "app-rationalization"
"""

    def work(self, state: ConsultantState) -> dict:
        """Perform application rationalization work.

        Args:
            state: Current conversation state

        Returns:
            Updated state with deliverables and response

        """
        # Get context
        user_message = next(
            (msg for msg in reversed(state["messages"]) if msg.type == "human"), None
        )

        research_context = ""
        if state.get("research_findings"):
            research_context = "\n\nAvailable Research:\n"
            for finding in state["research_findings"][:3]:  # Top 3 findings
                research_context += f"- [{finding.source}] {finding.content}\n"

        # Build prompt
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"Request: {user_message.content if user_message else 'Continue work'}{research_context}"
            ),
        ]

        response = self.llm.invoke(messages)

        # Create deliverable (simplified - in production, structure this properly)
        deliverable = Deliverable(
            title="Application Rationalization Assessment",
            type="assessment",
            content=response.content,
            offering="app-rationalization",
            specialist="app_rationalization",
        )

        return {
            "messages": [
                AIMessage(
                    content=response.content,
                    name="app_rationalization_specialist",
                )
            ],
            "deliverables": [deliverable],
            "active_specialist": "app_rationalization",
            "next_specialist": "END",  # Work complete unless supervisor routes elsewhere
        }
