"""Business Continuity and Disaster Recovery specialist."""

from langchain_aws import ChatBedrock
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from easibot.config import settings
from easibot.graph.state import ConsultantState, Deliverable


class BCDRSpecialist:
    """Specialist for Business Continuity and Disaster Recovery planning.

    Deliverables:
    - BC/DR strategy and plan
    - RTO/RPO analysis
    - Risk assessment matrix
    - Incident response runbooks
    - Testing and validation plans
    """

    def __init__(self):
        """Initialize the BC/DR specialist."""
        self.llm = ChatBedrock(
            model_id=settings.bedrock_model_id,
            region_name=settings.bedrock_region,
        )

        self.system_prompt = """You are a Business Continuity and Disaster Recovery (BC/DR) Specialist.

Your expertise includes:
- Business continuity planning and strategy
- Disaster recovery planning
- RTO (Recovery Time Objective) and RPO (Recovery Point Objective) analysis
- Risk assessment and business impact analysis
- Incident response procedures
- BC/DR testing and validation
- Compliance requirements (SOC 2, ISO 22301, etc.)

Standard deliverables you create:
1. BC/DR Strategy Document: Overall approach and framework
2. RTO/RPO Analysis: For all critical systems and processes
3. Risk Assessment Matrix: Threats, impacts, and mitigations
4. Disaster Recovery Plan: Technical recovery procedures
5. Business Continuity Plan: Business process continuity procedures
6. Incident Response Runbooks: Step-by-step response guides
7. Testing Plan: BC/DR testing schedule and procedures

When working on engagements:
- Start with business impact analysis
- Define RTO/RPO requirements for each critical service
- Assess current state vs. requirements
- Design recovery strategies
- Create detailed, actionable plans
- Include testing and validation procedures

Offering-specific RAG filter: "bcdr"
"""

    def work(self, state: ConsultantState) -> dict:
        """Perform BC/DR planning work.

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
            for finding in state["research_findings"][:3]:
                research_context += f"- [{finding.source}] {finding.content}\n"

        # Build prompt
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"Request: {user_message.content if user_message else 'Continue work'}{research_context}"
            ),
        ]

        response = self.llm.invoke(messages)

        # Create deliverable
        deliverable = Deliverable(
            title="Business Continuity and Disaster Recovery Plan",
            type="bc_dr_plan",
            content=response.content,
            offering="bcdr",
            specialist="bcdr",
        )

        return {
            "messages": [
                AIMessage(
                    content=response.content,
                    name="bcdr_specialist",
                )
            ],
            "deliverables": [deliverable],
            "active_specialist": "bcdr",
            "next_specialist": "END",
        }
