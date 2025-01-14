#!/bin/bash

# Update package list and install prerequisites
brew update

# Install pipx
brew install pipx
pipx ensurepath

# Install Poetry
pipx install poetry

# Install Ruff
pipx install ruff

echo "Prerequisite software installed successfully."