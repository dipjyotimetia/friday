#!/bin/bash

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Starting development environment setup..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "${RED}Homebrew not found. Installing Homebrew...${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Update Homebrew
echo "Updating Homebrew..."
brew update

# Install Python 3.12
echo "Installing Python 3.12..."
brew install python@3.12
brew link python@3.12

# Install pipx
echo "Installing pipx..."
brew install pipx
pipx ensurepath

# Install Poetry
echo "Installing Poetry..."
pipx install poetry

# Install Ruff for linting
echo "Installing Ruff..."
pipx install ruff

# Install Node.js
echo "Installing Node.js..."
brew install node@22

# Setup Poetry environment
echo "Setting up Poetry environment..."
poetry env use python3.12
poetry install

# Verify installations
echo -e "\n${GREEN}Verifying installations:${NC}"
python3.12 --version
poetry --version
ruff --version
node --version

echo -e "\n${GREEN}Development environment setup completed successfully!${NC}"

# Add environment to PATH
echo 'export PATH="$HOME/.local/bin:$HOME' >> ~/.zshrc
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc # Add Homebrew to PATH
source ~/.zshrc