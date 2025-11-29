# EASI Bot Infrastructure

Infrastructure as Code for the Enterprise Architecture and Systems Integration (EASI) chatbot to assist consultants in delivering Tech Strategy projects.

## Prerequisites

- [Pulumi CLI](https://www.pulumi.com/docs/get-started/install/) (v3.209.0 or later)
- [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate credentials
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager

## Setup

### 1. Install Dependencies

This project uses `uv` for Python package management. Pulumi is configured to use the `uv` toolchain (see [Pulumi.yaml](Pulumi.yaml:6)).

```bash
cd agents_pulumi
uv sync
```

### 2. Configure AWS Credentials

Ensure your AWS credentials are configured:

```bash
aws configure
```

### 3. Pulumi State Backend

This project uses an S3 backend for state storage. The state is stored in the `easibot-pulumi-state` bucket.

**Note**: The state bucket is automatically created and configured during the first-time dev setup (see [first-time-dev-setup.sh](../first-time-dev-setup.sh)). The script will:
- Create the S3 bucket if it doesn't exist
- Enable versioning for state history
- Block all public access for security
- Log in to the Pulumi S3 backend

If you need to manually log in to the S3 backend:

```bash
pulumi login s3://easibot-pulumi-state
```

### 4. Set the Passphrase

The stack is encrypted with a passphrase. Set the environment variable:

```bash
export PULUMI_CONFIG_PASSPHRASE="easibot-dev"
```

**Note**: For production environments, use a secure password manager or secrets management service instead of hardcoding the passphrase.

### 5. Select the Stack

The project uses a `dev` stack:

```bash
pulumi stack select dev
```

If the stack doesn't exist yet, initialize it:

```bash
PULUMI_CONFIG_PASSPHRASE="easibot-dev" pulumi stack init dev
```

### 6. Configure AWS Region

Set the AWS region (if not already configured):

```bash
PULUMI_CONFIG_PASSPHRASE="easibot-dev" pulumi config set aws:region us-west-2
```

## Usage

All Pulumi commands require the `PULUMI_CONFIG_PASSPHRASE` environment variable to be set.

### Preview Changes

Preview infrastructure changes before deploying:

```bash
PULUMI_CONFIG_PASSPHRASE="easibot-dev" pulumi preview
```

### Deploy Infrastructure

Deploy the infrastructure to AWS:

```bash
PULUMI_CONFIG_PASSPHRASE="easibot-dev" pulumi up
```

To auto-approve without interactive confirmation:

```bash
PULUMI_CONFIG_PASSPHRASE="easibot-dev" pulumi up --yes
```

### View Stack Outputs

View the outputs from the deployed stack:

```bash
PULUMI_CONFIG_PASSPHRASE="easibot-dev" pulumi stack output
```

View a specific output:

```bash
PULUMI_CONFIG_PASSPHRASE="easibot-dev" pulumi stack output rag_bucket_name
```

### View Stack Resources

List all resources in the stack:

```bash
PULUMI_CONFIG_PASSPHRASE="easibot-dev" pulumi stack
```

### Destroy Infrastructure

Destroy all infrastructure managed by this stack:

```bash
PULUMI_CONFIG_PASSPHRASE="easibot-dev" pulumi destroy
```

## Infrastructure Components

This Pulumi project currently creates:

### S3 Buckets

- **easibot-rag**: S3 bucket for RAG (Retrieval-Augmented Generation) document storage
  - Public access completely blocked
  - Tagged with Project, Environment, ManagedBy, Component, and Purpose

## Configuration

### Stack Configuration

The `dev` stack is configured with:

- **AWS Region**: `us-west-2`
- **Environment**: `dev`

### Setting Configuration Values

Set configuration values using:

```bash
PULUMI_CONFIG_PASSPHRASE="easibot-dev" pulumi config set <key> <value>
```

For secrets (encrypted):

```bash
PULUMI_CONFIG_PASSPHRASE="easibot-dev" pulumi config set --secret <key> <value>
```

View current configuration:

```bash
PULUMI_CONFIG_PASSPHRASE="easibot-dev" pulumi config
```

## Project Structure

```
agents-pulumi/
├── Pulumi.yaml          # Project definition (uses uv toolchain)
├── Pulumi.dev.yaml      # Stack-specific configuration (gitignored)
├── __main__.py          # Infrastructure code
├── pyproject.toml       # Python dependencies managed by uv
├── uv.lock              # Dependency lock file
├── .venv/               # Virtual environment (gitignored)
├── .gitignore           # Git ignore patterns
└── README.md            # This file
```

## Development Tips

### Using uv with Pulumi

This project is configured to use `uv` as the Python toolchain (see [Pulumi.yaml](Pulumi.yaml:6)). This means:

- No separate virtualenv is created by Pulumi
- Dependencies are managed through [pyproject.toml](pyproject.toml)
- Run `uv sync` to install/update dependencies

### Environment Variables

To avoid typing the passphrase repeatedly, add to your shell profile (`.bashrc`, `.zshrc`, etc.):

```bash
export PULUMI_CONFIG_PASSPHRASE="easibot-dev"
```

Or use a `.env` file (ensure it's in `.gitignore`):

```bash
# .env
PULUMI_CONFIG_PASSPHRASE=easibot-dev
```

Then source it:

```bash
source .env
```

### State Management

The Pulumi state is stored in S3 (`s3://easibot-pulumi-state`). This allows:

- Team collaboration
- State persistence across environments
- Backup and versioning of state

**Important**: Never commit `Pulumi.dev.yaml` or any stack-specific configuration files that contain sensitive information.

## Troubleshooting

### Certificate Issues

If you encounter SSL/TLS certificate errors, ensure these environment variables are set:

```bash
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
export GIT_SSL_CAINFO=/etc/ssl/certs/ca-certificates.crt
```

These are already configured in the devcontainer setup.

### Missing Passphrase

If you see an error about missing passphrase:

```
error: could not create secrets manager: passphrase must be set
```

Ensure you've exported the `PULUMI_CONFIG_PASSPHRASE` environment variable.

## Additional Resources

- [Pulumi AWS Provider Documentation](https://www.pulumi.com/registry/packages/aws/)
- [Pulumi Python Documentation](https://www.pulumi.com/docs/languages-sdks/python/)
- [uv Documentation](https://github.com/astral-sh/uv)
