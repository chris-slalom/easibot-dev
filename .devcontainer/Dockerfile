ARG UV_VERSION=latest


FROM ghcr.io/astral-sh/uv:$UV_VERSION AS uv


FROM mcr.microsoft.com/vscode/devcontainers/base:debian

ENV PYTHONDONTWRITEBYTECODE=True \
    PYTHONUNBUFFERED=True \
    UV_LINK_MODE=copy

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    # For OpenCV etc...
    libgl1 libglib2.0-0 \
    # For Pulumi installation and certificate handling
    curl \
    ca-certificates \
    # Update CA certificates to ensure SSL/TLS works properly
    && update-ca-certificates \
    # To remove the image size, it is recommended refresh the package cache as follows
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # Install Pulumi (using -k to skip SSL verification due to network issues)
    && curl -fsSLk https://get.pulumi.com | sh

ENV PATH="/root/.pulumi/bin:${PATH}"

COPY --from=uv --chown=vscode: /uv /uvx /bin/
