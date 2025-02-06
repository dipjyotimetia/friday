FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Install Python and pip first
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        curl \
        gcc \
        libc6-dev \
        python3 \
        python3-pip

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Install Ruff using pip
RUN python3 -m pip install ruff

# Install global npm packages
RUN npm install -g serve typescript

# Clean up
RUN apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*