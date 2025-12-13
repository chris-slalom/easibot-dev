#!/usr/bin/env bash
# Base Dev Image Setup and Tests
set -e  # Exit on error

# Install dependencies
uv sync

# Run tests (non-blocking for devcontainer startup)
echo "Running tests..."
uv run nox -s test || echo "⚠️  Tests failed - fix before committing"

# Format and lint
uv run nox -s fmt
uv run nox -s lint -- --pyright --ruff

# config git for container
git config --global --add safe.directory /workspace

# Configure Git to use system CA certificates for SSL/TLS
git config --global http.sslCAInfo /etc/ssl/certs/ca-certificates.crt
git config --global http.sslVerify true

# Setup Pulumi state backend
echo "Setting up Pulumi state backend..."
PULUMI_STATE_BUCKET="easibot-pulumi-state"
AWS_REGION="${AWS_DEFAULT_REGION:-us-west-2}"

# Check if S3 bucket exists, create if it doesn't
if ! aws s3 ls "s3://${PULUMI_STATE_BUCKET}" 2>/dev/null; then
    echo "Creating Pulumi state bucket: ${PULUMI_STATE_BUCKET}"
    aws s3 mb "s3://${PULUMI_STATE_BUCKET}" --region "${AWS_REGION}"

    # Enable versioning on the state bucket for safety
    aws s3api put-bucket-versioning \
        --bucket "${PULUMI_STATE_BUCKET}" \
        --versioning-configuration Status=Enabled

    # Block public access to the state bucket
    aws s3api put-public-access-block \
        --bucket "${PULUMI_STATE_BUCKET}" \
        --public-access-block-configuration \
        "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

    echo "Pulumi state bucket created and secured"
else
    echo "Pulumi state bucket already exists: ${PULUMI_STATE_BUCKET}"
fi

# Login to Pulumi with S3 backend
echo "Logging into Pulumi S3 backend..."
pulumi login "s3://${PULUMI_STATE_BUCKET}"
echo "Pulumi setup complete"
