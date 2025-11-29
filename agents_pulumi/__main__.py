"""AWS Infrastructure for EASI chatbot.

This module defines AWS infrastructure including S3 buckets for storage.
"""

import pulumi
import pulumi_aws as aws
from pulumi import Config

# Load configuration
config = Config()
environment = config.get("environment") or "dev"
aws_region = config.get("aws:region") or "us-west-2"
project_name = pulumi.get_project()

# Tags to apply to all resources
common_tags = {
    "Project": project_name,
    "Environment": environment,
    "ManagedBy": "Pulumi",
}


# ============================================================================
# S3 Buckets
# ============================================================================

# Create S3 bucket for RAG (Retrieval-Augmented Generation) data
rag_bucket = aws.s3.Bucket(
    "easibot-rag",
    bucket="easibot-rag",
    tags={
        **common_tags,
        "Component": "RAG",
        "Purpose": "Document storage for RAG pipeline",
    },
)

# Block public access to the bucket (default secure settings)
rag_bucket_public_access_block = aws.s3.BucketPublicAccessBlock(
    "easibot-rag-public-access-block",
    bucket=rag_bucket.id,
    block_public_acls=True,
    block_public_policy=True,
    ignore_public_acls=True,
    restrict_public_buckets=True,
)


# Export resource identifiers and ARNs for use in other stacks or applications
pulumi.export("environment", environment)
pulumi.export("region", aws_region)

# S3 Buckets
pulumi.export("rag_bucket_name", rag_bucket.id)
pulumi.export("rag_bucket_arn", rag_bucket.arn)
