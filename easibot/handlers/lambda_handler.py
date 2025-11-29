"""AWS Lambda handler for EASI Bot."""

import json
from typing import Any

from easibot.agent import graph
from easibot.graph.state import ConsultantState


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """AWS Lambda handler for EASI Bot requests.

    Args:
        event: Lambda event containing user message
        context: Lambda context

    Returns:
        Response with bot message

    Expected event format:
    {
        "message": "User message here",
        "offerings": ["app-rationalization"],  # optional
        "thread_id": "conversation-123",  # optional, for persistence
    }

    """
    try:
        # Extract request data
        user_message = event.get("message", "")
        offerings = event.get("offerings", [])
        thread_id = event.get("thread_id")

        if not user_message:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No message provided"}),
            }

        # Initialize state
        state = ConsultantState(
            messages=[{"role": "user", "content": user_message}],
            offerings=offerings,
        )

        # Run graph
        config = {"configurable": {"thread_id": thread_id}} if thread_id else {}
        result = graph.invoke(state, config=config)

        # Extract response
        last_message = result["messages"][-1]
        response_content = last_message.content

        # Extract deliverables if any
        deliverables = [
            {
                "title": d.title,
                "type": d.type,
                "offering": d.offering,
                "specialist": d.specialist,
            }
            for d in result.get("deliverables", [])
        ]

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": response_content,
                    "deliverables": deliverables,
                    "specialist": result.get("active_specialist"),
                }
            ),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }
