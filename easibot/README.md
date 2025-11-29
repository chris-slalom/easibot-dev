# EASI Bot - Enterprise Architecture and Systems Integration Chatbot

Multi-agent LangGraph system for enterprise consulting with offering-specific specialists.

## Architecture

### Supervisor Pattern with Offering-Specific Specialists

```
Supervisor (Intent Router)
│
├── Research Specialist (Unified RAG)
├── Application Rationalization Specialist
├── Business Continuity/DR Specialist
├── Tech Strategy Specialist (future)
└── Cloud Modernization Specialist (future)
```

### Key Design Decisions

1. **Offering-Specific Specialists**: Each specialist understands their domain AND deliverables
2. **Unified RAG**: Single knowledge base with metadata filtering
3. **Supervisor Routing**: Intelligent routing based on engagement type
4. **Extensible**: Easy to add new specialists for new offerings

## Project Structure

```
easibot/
├── agent.py                 # Main LangGraph workflow
├── langgraph.json          # LangGraph configuration
├── pyproject.toml          # Dependencies
│
├── agents/                 # Specialist implementations
│   ├── supervisor.py       # Routes requests
│   ├── research.py         # Unified RAG search
│   ├── app_rationalization.py
│   └── bcdr.py
│
├── graph/                  # Graph definitions
│   └── state.py           # State schemas
│
├── config/                 # Configuration
│   └── settings.py        # Environment settings
│
├── tools/                  # Agent tools
│   └── rag_search.py      # S3/vector search (TODO)
│
├── nodes/                  # Graph node logic
│
└── handlers/               # AWS Lambda handlers
    └── lambda_handler.py  # Entry point (TODO)
```

## Specialists

### Research Specialist
- **Access**: Unified RAG (all offerings)
- **Role**: Information retrieval and synthesis
- **Outputs**: Research findings with sources

### App Rationalization Specialist
- **Offering**: Application portfolio analysis
- **Deliverables**:
  - Application inventory
  - Rationalization matrix (5R)
  - TCO analysis
  - Migration roadmap

### BC/DR Specialist
- **Offering**: Business continuity and disaster recovery
- **Deliverables**:
  - BC/DR strategy
  - RTO/RPO analysis
  - Risk assessment
  - Incident response runbooks

## Setup

### Install Dependencies

```bash
cd easibot
uv sync
```

### Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### Run Locally (Development)

```python
from easibot.agent import graph
from easibot.graph.state import ConsultantState

# Initialize state
state = ConsultantState(
    messages=[{"role": "user", "content": "Help me with application rationalization"}],
    offerings=["app-rationalization"],
)

# Run graph
result = graph.invoke(state)
print(result["messages"][-1].content)
```

## Adding New Specialists

To add a new offering specialist:

1. **Create specialist class** in `agents/new_specialist.py`:
```python
class NewSpecialist:
    def __init__(self):
        self.llm = ChatBedrock(...)
        self.system_prompt = """..."""

    def work(self, state: ConsultantState) -> dict:
        # Implementation
        pass
```

2. **Update supervisor routing** in `agents/supervisor.py`

3. **Add to graph** in `agent.py`:
```python
workflow.add_node("new_specialist", new_specialist.work)
```

4. **Update state types** in `graph/state.py` if needed

## Deployment

See [../agents_pulumi/README.md](../agents_pulumi/README.md) for deployment with Pulumi to AWS.

## Next Steps / TODO

- [ ] Implement actual RAG search against S3 (tools/rag_search.py)
- [ ] Add vector embeddings for semantic search
- [ ] Implement Lambda handler (handlers/lambda_handler.py)
- [ ] Add Tech Strategy specialist
- [ ] Add Cloud Modernization specialist
- [ ] Enhance supervisor routing with LLM-based decision making
- [ ] Add unit tests
- [ ] Add integration tests with mock AWS services
- [ ] Add deliverable formatting and export (PDF, DOCX)
- [ ] Implement human-in-the-loop for deliverable review
