ARG UV_VERSION=latest


FROM ghcr.io/astral-sh/uv:$UV_VERSION AS uv


FROM mcr.microsoft.com/vscode/devcontainers/base:debian

ENV PYTHONDONTWRITEBYTECODE=True \
    PYTHONUNBUFFERED=True \
    UV_LINK_MODE=copy

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    # For OpenCV etc...
    libgl1 libglib2.0-0 \
    # For AWS CLI
    awscli \
    # For Pulumi installation and certificate handling
    curl \
    ca-certificates \
    wget \
    # Update CA certificates to ensure SSL/TLS works properly
    && update-ca-certificates \
    # Install hadolint via curl (skip certificate verification due to network issues)
    && curl -fsSLk -o /bin/hadolint https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64 \
    && chmod +x /bin/hadolint \
    # Install Pulumi and move to /usr/local/bin so all users can access it
    && curl -fsSLk https://get.pulumi.com | sh \
    && mv /root/.pulumi/bin/* /usr/local/bin/ \
    && rm -rf /root/.pulumi \
    # To remove the image size, it is recommended refresh the package cache as follows
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/usr/local/bin:${PATH}"

COPY --from=uv --chown=vscode: /uv /uvx /bin/
