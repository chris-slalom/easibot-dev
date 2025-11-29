"""Research specialist with access to unified knowledge base."""

from langchain_aws import ChatBedrock
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from easibot.config import settings
from easibot.graph.state import ConsultantState, ResearchFinding


class ResearchSpecialist:
    """Research specialist that searches the unified knowledge base.

    This specialist has access to ALL offering documentation in the RAG bucket
    and can filter by offering metadata when needed.
    """

    def __init__(self):
        """Initialize the research specialist."""
        self.llm = ChatBedrock(
            model_id=settings.bedrock_model_id,
            region_name=settings.bedrock_region,
        )

        self.system_prompt = """You are a Research Specialist for an enterprise consulting firm.

Your role is to:
1. Search the knowledge base for relevant information
2. Synthesize findings from multiple sources
3. Provide context and recommendations based on documentation
4. Filter by offering when appropriate

When responding:
- Cite sources clearly
- Highlight key findings
- Suggest which specialist should handle follow-up work
- Be concise but comprehensive

If the request needs specialist expertise beyond research, recommend routing to:
- app_rationalization: For application portfolio work
- bcdr: For business continuity and disaster recovery
- tech_strategy: For strategic technology planning
- cloud_modernization: For cloud migration and optimization"""

    def research(self, state: ConsultantState) -> dict:
        """Perform research and return findings.

        Args:
            state: Current conversation state

        Returns:
            Updated state with research findings and response

        """
        # Get the latest user message
        user_message = next(
            (msg for msg in reversed(state["messages"]) if msg.type == "human"), None
        )

        if not user_message:
            return {}

        # TODO: Implement actual RAG search against S3 bucket
        # For now, returning placeholder research
        query = user_message.content

        # Simulate RAG search (to be implemented with actual vector search)
        findings = self._simulate_rag_search(query, state.get("offerings", []))

        # Build response with LLM
        context = f"Query: {query}\n\n"
        if findings:
            context += "Findings:\n"
            for i, finding in enumerate(findings, 1):
                context += f"{i}. [{finding.source}] {finding.content}\n"

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=context),
        ]

        response = self.llm.invoke(messages)

        # Determine if we should route to a specialist
        next_specialist = self._suggest_next_specialist(user_message.content)

        return {
            "messages": [
                AIMessage(
                    content=response.content,
                    name="research_specialist",
                )
            ],
            "research_findings": findings,
            "next_specialist": next_specialist,
            "active_specialist": "research",
        }

    def _simulate_rag_search(
        self, query: str, offerings: list[str]
    ) -> list[ResearchFinding]:
        """Simulate RAG search (placeholder for actual implementation).

        Args:
            query: Search query
            offerings: Optional offering filters

        Returns:
            List of research findings

        """
        # Placeholder - in production, this would:
        # 1. Embed the query
        # 2. Search vector database in S3
        # 3. Filter by offering metadata
        # 4. Return ranked results

        return [
            ResearchFinding(
                source="Application Rationalization Guide",
                content="Application rationalization involves evaluating portfolio to identify redundancies, optimize costs, and modernize systems.",
                relevance_score=0.85,
                metadata={"offering": "app-rationalization"},
            ),
            ResearchFinding(
                source="Best Practices Framework",
                content="Start with inventory assessment, analyze business capabilities, and prioritize based on strategic value.",
                relevance_score=0.78,
                metadata={"offering": "app-rationalization"},
            ),
        ]

    def _suggest_next_specialist(self, query: str) -> str:
        """Suggest next specialist based on query content.

        Args:
            query: User query

        Returns:
            Suggested next specialist or "supervisor" to let supervisor decide

        """
        query_lower = query.lower()

        # If the query asks for deliverables or specific work, route to specialist
        if any(
            word in query_lower
            for word in [
                "create",
                "develop",
                "build",
                "deliverable",
                "plan",
                "strategy",
            ]
        ):
            return "supervisor"  # Let supervisor route to appropriate specialist

        # Otherwise, research is complete
        return "END"
