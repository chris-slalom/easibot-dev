"""Supervisor agent that routes requests to appropriate specialists."""

from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage

from easibot.config import settings
from easibot.graph.state import ConsultantState


class SupervisorAgent:
    """Supervisor that analyzes requests and routes to appropriate specialists.

    The supervisor determines which specialist(s) should handle the request based on:
    - Engagement type and offerings mentioned
    - Required deliverables
    - Complexity and scope of work
    """

    def __init__(self):
        """Initialize the supervisor with a Bedrock LLM."""
        self.llm = ChatBedrock(
            model_id=settings.bedrock_model_id,
            region_name=settings.bedrock_region,
        )

        self.system_prompt = """You are the Supervisor for an enterprise consulting firm's AI assistant.

Your role is to:
1. Analyze client requests and questions
2. Identify relevant offerings (app-rationalization, bcdr, tech-strategy, cloud-modernization)
3. Route to the appropriate specialist
4. Coordinate multiple specialists if needed

Available specialists:
- research: Searches knowledge base across all offerings
- app_rationalization: Application portfolio analysis, rationalization, TCO
- bcdr: Business Continuity and Disaster Recovery planning
- tech_strategy: Technology roadmaps, architecture assessments
- cloud_modernization: Cloud migration, AWS/Azure expertise

Routing guidelines:
- For information gathering: route to 'research'
- For specific offering work: route to that offering's specialist
- For complex cross-offering work: start with research, then route to primary specialist
- If uncertain: route to 'research' first

Respond with JSON: {"next_specialist": "specialist_name", "reasoning": "why"}"""

    def route(self, state: ConsultantState) -> dict:
        """Determine next specialist to handle the request.

        Args:
            state: Current conversation state

        Returns:
            Updated state with next_specialist set

        """
        # Get the latest user message
        user_message = next(
            (msg for msg in reversed(state["messages"]) if msg.type == "human"), None
        )

        if not user_message:
            return {"next_specialist": "END"}

        # Check iteration limit
        if state.get("iteration_count", 0) >= state.get("max_iterations", 10):
            return {
                "next_specialist": "END",
                "messages": [
                    SystemMessage(
                        content="Maximum iterations reached. Please refine your request."
                    )
                ],
            }

        # Build context for routing decision
        context_parts = [f"User request: {user_message.content}"]

        if state.get("offerings"):
            context_parts.append(
                f"Identified offerings: {', '.join(state['offerings'])}"
            )

        if state.get("research_findings"):
            context_parts.append(
                f"Research findings available: {len(state['research_findings'])} documents"
            )

        if state.get("active_specialist"):
            context_parts.append(f"Previous specialist: {state['active_specialist']}")

        context = "\n".join(context_parts)

        # Get routing decision from LLM
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=context),
        ]

        response = self.llm.invoke(messages)

        # Parse response (simplified - in production, use structured output)
        # For now, we'll use basic routing logic
        content_lower = user_message.content.lower()

        # Simple keyword-based routing (can be enhanced with LLM)
        if any(
            word in content_lower
            for word in ["search", "find", "research", "information", "what is"]
        ):
            next_specialist = "research"
        elif any(
            word in content_lower
            for word in ["application", "portfolio", "rationalization"]
        ):
            next_specialist = "app_rationalization"
        elif any(
            word in content_lower
            for word in ["disaster", "recovery", "continuity", "bcdr"]
        ):
            next_specialist = "bcdr"
        elif any(
            word in content_lower for word in ["strategy", "roadmap", "architecture"]
        ):
            next_specialist = "tech_strategy"
        elif any(
            word in content_lower for word in ["cloud", "aws", "azure", "migration"]
        ):
            next_specialist = "cloud_modernization"
        else:
            # Default to research for ambiguous requests
            next_specialist = "research"

        return {
            "next_specialist": next_specialist,
            "iteration_count": state.get("iteration_count", 0) + 1,
        }
