# Langfuse Integration for EASIBot

This document describes how to use Langfuse for observability, tracing, and debugging of the LangGraph-based EASIBot consultant system.

## Overview

Langfuse is an open-source LLM engineering platform that provides:
- **Tracing**: Visual execution traces of your agent workflows
- **Debugging**: Inspect inputs, outputs, and state at each step
- **Cost tracking**: Monitor token usage and LLM costs
- **Prompt management**: Version control for agent prompts (future feature)
- **Evaluations**: Quality metrics for agent outputs (future feature)

## Quick Start

### 1. Start Langfuse (Docker Compose)

Langfuse runs automatically when you start your dev container. The docker-compose configuration includes:
- **Langfuse UI**: http://localhost:3000
- **PostgreSQL database**: For Langfuse data storage
- **Pre-configured project**: `easibot-dev` with default keys

### 2. Access Langfuse Dashboard

1. Open http://localhost:3000 in your browser
2. Login with default credentials:
   - **Email**: `admin@easibot.local`
   - **Password**: `admin123`
3. You'll see the `easibot-dev` project with your traces

### 3. Enable Tracing in Your Code

Tracing is automatically enabled when `ENABLE_LANGFUSE=true` in your environment:

```python
from easibot.agent import create_consultant_graph

# Langfuse tracing is automatically enabled from environment variables
graph = create_consultant_graph()

# All invocations are now traced to Langfuse
result = graph.invoke(
    {"messages": [...], "offerings": ["app-rationalization"]},
    config={"configurable": {"thread_id": "my-conversation"}}
)
```

### 4. View Traces

After running your agent:
1. Go to http://localhost:3000
2. Navigate to **Traces** in the sidebar
3. Click on a trace to see:
   - Full execution timeline
   - Each agent node's inputs and outputs
   - Token usage and costs
   - Execution duration for each step

## Configuration

### Environment Variables

All configuration is in `.env.local` or can be set in your environment:

```bash
# Enable/disable Langfuse tracing
ENABLE_LANGFUSE=true

# Langfuse connection (default for Docker Compose)
LANGFUSE_HOST=http://langfuse:3000
LANGFUSE_PUBLIC_KEY=pk-lf-local
LANGFUSE_SECRET_KEY=sk-lf-local
```

### Programmatic Control

You can also control Langfuse programmatically:

```python
from easibot.agent import create_consultant_graph

# Explicitly enable Langfuse
graph = create_consultant_graph(enable_langfuse=True)

# Explicitly disable Langfuse
graph = create_consultant_graph(enable_langfuse=False)

# Use environment variable (default)
graph = create_consultant_graph()  # Reads ENABLE_LANGFUSE from env
```

## Advanced Usage

### Per-Invocation Configuration

You can override Langfuse settings per invocation:

```python
from langfuse.langchain import CallbackHandler

# Create a custom handler (e.g., for a different project)
langfuse_handler = CallbackHandler(
    public_key="pk-lf-production",
    secret_key="sk-lf-production",
    host="https://your-langfuse-instance.com"
)

# Use it for specific invocations
result = graph.invoke(
    input_state,
    config={
        "configurable": {"thread_id": "session-1"},
        "callbacks": [langfuse_handler]  # Override default handler
    }
)
```

### Session and User Tracking

Add metadata to your traces for better organization:

```python
from langfuse.langchain import CallbackHandler

langfuse_handler = CallbackHandler(
    session_id="customer-meeting-2024-01-15",
    user_id="john.doe@client.com",
    metadata={
        "client": "Acme Corp",
        "engagement_type": "app-rationalization",
        "consultant": "Jane Smith"
    }
)

result = graph.invoke(
    input_state,
    config={"callbacks": [langfuse_handler]}
)
```

### Disable Tracing for Tests

Tests automatically run without Langfuse tracing to keep them fast and isolated:

```python
# In tests, Langfuse is disabled by default
from easibot.agent import create_consultant_graph

def test_my_agent():
    graph = create_consultant_graph()  # No tracing in test environment
    result = graph.invoke(test_input)
    assert result["deliverables"]
```

## Docker Compose Services

The development environment includes these Langfuse-related services:

### langfuse-db
- **Image**: postgres:15-alpine
- **Purpose**: PostgreSQL database for Langfuse data
- **Data persistence**: Volume `langfuse-db-data`
- **Health check**: Ensures DB is ready before Langfuse starts

### langfuse
- **Image**: langfuse/langfuse:latest
- **Purpose**: Langfuse web UI and API
- **Port**: 3000 (http://localhost:3000)
- **Database**: Connected to langfuse-db
- **Initial setup**: Creates admin user and easibot-dev project

## Troubleshooting

### Langfuse UI not accessible

1. Check if containers are running:
   ```bash
   docker ps | grep langfuse
   ```

2. Check container logs:
   ```bash
   docker logs <langfuse-container-id>
   docker logs <langfuse-db-container-id>
   ```

3. Restart containers:
   ```bash
   docker-compose -f .devcontainer/docker-compose.yml restart langfuse langfuse-db
   ```

### Traces not appearing

1. Verify environment variables are set:
   ```bash
   echo $ENABLE_LANGFUSE
   echo $LANGFUSE_HOST
   ```

2. Check that Langfuse is enabled in your code:
   ```python
   import os
   print(os.getenv("ENABLE_LANGFUSE"))  # Should be "true"
   ```

3. Verify network connectivity from dev container:
   ```bash
   curl http://langfuse:3000
   ```

### Authentication errors

1. Check your API keys match the initialized project:
   - Go to http://localhost:3000
   - Navigate to **Settings** → **API Keys**
   - Verify keys match your `.env.local` file

2. Create new keys if needed:
   - Click **Create New Key** in the dashboard
   - Update `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` in `.env.local`

## Production Deployment

For AWS production deployment, you'll need:

1. **Deploy Langfuse on AWS**:
   - Use the [Langfuse Terraform AWS module](https://github.com/langfuse/langfuse-terraform-aws)
   - Or deploy to ECS/Fargate manually
   - Or use Langfuse Cloud (https://cloud.langfuse.com)

2. **Update environment variables**:
   ```bash
   LANGFUSE_HOST=https://your-langfuse.yourdomain.com
   LANGFUSE_PUBLIC_KEY=pk-lf-prod-xxxxx
   LANGFUSE_SECRET_KEY=sk-lf-prod-xxxxx
   ```

3. **Security considerations**:
   - Store API keys in AWS Secrets Manager
   - Use IAM roles for service authentication
   - Enable HTTPS for Langfuse endpoint
   - Restrict access to Langfuse UI

## Additional Resources

- [Langfuse Documentation](https://langfuse.com/docs)
- [Langfuse LangChain Integration](https://langfuse.com/docs/integrations/langchain)
- [Langfuse Python SDK](https://langfuse.com/docs/sdk/python)
- [Langfuse GitHub](https://github.com/langfuse/langfuse)
- [Self-Hosting Guide](https://langfuse.com/docs/deployment/self-host)
